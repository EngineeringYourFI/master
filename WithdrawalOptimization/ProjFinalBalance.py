# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ProjFinalBalance.py

import numpy as np
import sys
import copy

from ComputeTaxes import ComputeTaxes
from TaxableSSconsolidated import TaxableSSconsolidated
from TaxableIncomeTargetMethodWithSSI import TaxableIncomeTargetMethodWithSSI
from NonAdjustableIncome import NonAdjustableIncome
from WithdrawFromAllPreTax import WithdrawFromAllPreTax
from WithdrawFromPostTax import WithdrawFromPostTax
from GetRemainingNeededCashNoTaxesOrPenalties import GetRemainingNeededCashNoTaxesOrPenalties
from GetRemainingNeededCashWithTaxesAndOrPenalties import GetRemainingNeededCashWithTaxesAndOrPenalties
from TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc import *
from ComputeSubsidy import *

# Expand width of output in console
import pandas as pd
desired_width = 1000 #320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

# Project final balance, from inputs (e.g. initial balances, tax rates, etc.)
def ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,NumYearsToProject, R, FilingStatus,
                     TPMwithdraw457bFirst):

    # number of people (1 or 2)
    NumPeople = np.size(IVdict['PreTaxIV'])

    # Initialize asset values
    PreTax = {'Bal': np.zeros((NumYearsToProject,NumPeople)),
              'Total': np.zeros(NumYearsToProject),
              'Withdrawn': np.zeros((NumYearsToProject,NumPeople)),
              'TotalWithdrawn': np.zeros(NumYearsToProject)}
    PreTax457b = {'Bal': np.zeros((NumYearsToProject,NumPeople)),
                  'Total': np.zeros(NumYearsToProject),
                  'Withdrawn': np.zeros((NumYearsToProject,NumPeople)),
                  'TotalWithdrawn': np.zeros(NumYearsToProject),
                  'TPMwithdraw457bFirst': TPMwithdraw457bFirst}
    PostTax = {'Bal': np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV']))),
               'Total': np.zeros(NumYearsToProject),
               'CG': np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV']))),
               'CGtotal': np.zeros(NumYearsToProject)}
    Roth = {'Bal': np.zeros((NumYearsToProject,NumPeople)),
            'Total': np.zeros(NumYearsToProject),
            'Contributions': np.zeros((NumYearsToProject,NumPeople))}
            # 'ConversionAmount': np.array([], dtype=float),
            # 'ConversionAge': np.array([], dtype=float), # the age of the person's account the conversion is done on
            # 'ConversionPerson': np.array([], dtype=int)} # person who does the conversion (0 = 1st person, 1 = 2nd person)
    CashCushion = np.zeros(NumYearsToProject)
    TotalAssets = np.zeros(NumYearsToProject)

    PreTax['Bal'][0,:] = IVdict['PreTaxIV']
    PreTax457b['Bal'][0,:] = IVdict['PreTax457bIV']
    PostTax['Bal'][0,:] = IVdict['PostTaxIV']
    PostTax['CG'][0,:] = IVdict['CurrentUnrealizedCapGains']
    Roth['Bal'][0,:] = IVdict['RothIV']
    Roth['Contributions'][0,:] = IVdict['RothContributions']
    Roth['ConversionAmount'] = IVdict['RothConversionAmount']
    Roth['ConversionAge'] = IVdict['RothConversionAge'] # the age of the person's account the conversion is done on
    Roth['ConversionPerson'] = IVdict['RothConversionPerson'] # person who does the conversion (0 = 1st person, 1 = 2nd person)
    CashCushion[0] = IVdict['CashCushion']

    # Initialize Yearly values

    Income = {'Total': np.zeros(NumYearsToProject),
              'TotalStandard': np.zeros(NumYearsToProject),
              'TotalLTcapGains': np.zeros(NumYearsToProject),
              'TotalSS': np.zeros(NumYearsToProject),
              'TaxableSS': np.zeros(NumYearsToProject),
              'MaxStandard': np.zeros(NumYearsToProject),
              'MaxTotal': np.zeros(NumYearsToProject)} # previously called SpecifiedIncome
    RMD = {'Bal': np.zeros((NumYearsToProject,np.size(CurrentAge))),
           'Total': np.zeros(NumYearsToProject),
           'RMDstartAge': RMDstartAge}
    Age = np.zeros((NumYearsToProject,np.size(CurrentAge)))
    Age[0,:] = CurrentAge
    TotalCash = np.zeros(NumYearsToProject)
    TotalCashNeeded = np.zeros(NumYearsToProject)
    Expenses = np.zeros(NumYearsToProject)
    Taxes = np.zeros(NumYearsToProject)
    TaxesGenPrevYear = np.zeros(NumYearsToProject)
    TaxesPaidPrevYear = np.zeros(NumYearsToProject)
    EstimatedTaxesPaidThisYear = np.zeros(NumYearsToProject)
    Penalties = np.zeros(NumYearsToProject)
    PenaltiesGenPrevYear = np.zeros(NumYearsToProject)
    PenaltiesPaidPrevYear = np.zeros(NumYearsToProject)
    EstimatedPenaltiesPaidThisYear = np.zeros(NumYearsToProject)

    TaxesGenPrevYear[0] = IVdict['TaxesGenPrevYear']
    TaxesPaidPrevYear[0] = IVdict['TaxesPaidPrevYear']
    PenaltiesGenPrevYear[0] = IVdict['PenaltiesGenPrevYear']
    PenaltiesPaidPrevYear[0] = IVdict['PenaltiesPaidPrevYear']

    OutOfMoneyAge = np.nan

    # ROI for post-tax remove dividend yield, since input ROI assumes reinvested dividends
    ROInoDividends = R - (IncDict['QualifiedDividendYield'] + IncDict['NonQualifiedDividendYield'])

    # Fill out Age array, in case money runs out - don't want Ages equal zero after that, for plot
    for ct1 in range(0,NumYearsToProject):
        if ct1 > 0:
            Age[ct1,:] = Age[ct1-1,:] + 1

    # loop over years
    for ct1 in range(0,NumYearsToProject):

        print('Year Count = ',ct1)

        # apply investment growth to accounts if not at first year
        if ct1 > 0:

            # tax advantaged accounts
            for ct2 in range(np.shape(PreTax['Bal'])[1]):
                PreTax['Bal'][ct1,ct2] = np.round(PreTax['Bal'][ct1-1,ct2]*(1+R),2)
                PreTax457b['Bal'][ct1,ct2] = np.round(PreTax457b['Bal'][ct1-1,ct2]*(1+R),2)
                Roth['Bal'][ct1,ct2] = np.round(Roth['Bal'][ct1-1,ct2]*(1+R),2)
            Roth['Contributions'][ct1,:] = Roth['Contributions'][ct1-1,:]
            CashCushion[ct1] = CashCushion[ct1-1]
            # loop over post-tax lots
            for ct2 in range(np.shape(PostTax['Bal'])[1]):
                # Compute gains, add to capital gains array
                PostTax['CG'][ct1,ct2] = PostTax['CG'][ct1-1,ct2] + np.round(PostTax['Bal'][ct1-1,ct2]*ROInoDividends,2)
                # then add to PostTax array
                PostTax['Bal'][ct1,ct2] = np.round(PostTax['Bal'][ct1-1,ct2]*(1+ROInoDividends),2)

            TaxesGenPrevYear[ct1] = Taxes[ct1-1]
            PenaltiesGenPrevYear[ct1] = Penalties[ct1-1]
            TaxesPaidPrevYear[ct1] = EstimatedTaxesPaidThisYear[ct1-1]
            PenaltiesPaidPrevYear[ct1] = EstimatedPenaltiesPaidThisYear[ct1-1]

        # Compute expenses for current year
        Expenses[ct1] = ExpDict['Exp'] + ExpDict['ExpRate']*float(ct1)
        for ct2 in range(len(ExpDict['FutureExpenseAdjustments'])):
            if Age[ct1,0] >= ExpDict['FutureExpenseAdjustmentsAge'][ct2]:
                Expenses[ct1] += ExpDict['FutureExpenseAdjustments'][ct2]

        # Taxes/Penalties

        # If taxes paid last year exceed what was owed, collect that refund
        if (TaxesPaidPrevYear[ct1] - TaxesGenPrevYear[ct1]) > 0.: # collect refund, place into new PostTax lot
            NewLot = np.zeros((np.shape(PostTax['Bal'])[0],1))
            NewLot[ct1,0] = TaxesPaidPrevYear[ct1] - TaxesGenPrevYear[ct1]
            PostTax['Bal'] = np.append(PostTax['Bal'],NewLot,1)
            PostTax['CG'] = np.append(PostTax['CG'],np.zeros((np.shape(PostTax['CG'])[0],1)),1)
            TaxesStillOwed = 0.
        else: # otherwise need to pay the amount owed this year
            TaxesStillOwed = TaxesGenPrevYear[ct1] - TaxesPaidPrevYear[ct1]

        # If penalties paid last year exceed what was owed, collect that refund
        if (PenaltiesPaidPrevYear[ct1] - PenaltiesGenPrevYear[ct1]) > 0.: # collect refund, place into new PostTax lot
            NewLot = np.zeros((np.shape(PostTax['Bal'])[0],1))
            NewLot[ct1,0] = PenaltiesPaidPrevYear[ct1] - PenaltiesGenPrevYear[ct1]
            PostTax['Bal'] = np.append(PostTax['Bal'],NewLot,1)
            PostTax['CG'] = np.append(PostTax['CG'],np.zeros((np.shape(PostTax['CG'])[0],1)),1)
            PenaltiesStillOwed = 0.
        else: # otherwise need to pay the amount owed this year
            PenaltiesStillOwed = PenaltiesGenPrevYear[ct1] - PenaltiesPaidPrevYear[ct1]

        # Taxes to pay this year, by default the amount you paid last year - assumes most years you'll pay about the
        # same or more taxes as the previous year. If not, then need to estimate tax owed in the same year you make the
        # withdrawal, to avoid overpaying taxes too early most years (which may unfortunately require expensive
        # iteration).
        if TaxesGenPrevYear[ct1] >= 0.:
            EstimatedTaxesPaidThisYear[ct1] = TaxesGenPrevYear[ct1]
        # Assuming that penalties do NOT work the same way as taxes: do not need to make estimated payments to the IRS
        # of penalties incurred from early retirement withdrawals. But if I ever find out otherwise, can easily switch
        # this back to using PenaltiesGenPrevYear[ct1].
        EstimatedPenaltiesPaidThisYear[ct1] = 0. #PenaltiesGenPrevYear[ct1]

        # Compute cash needed this year
        TotalCashNeeded[ct1] = Expenses[ct1] + TaxesStillOwed + PenaltiesStillOwed + EstimatedTaxesPaidThisYear[ct1] + \
                               EstimatedPenaltiesPaidThisYear[ct1]

        # Income

        # if np.all(Age[ct1,:] >= 65.):
        #     Income['MaxTotal'][ct1] = IncDict['SpecifiedIncomeAfterACA']
        # else:
        #     Income['MaxTotal'][ct1] = IncDict['SpecifiedIncome']
        Income['MaxTotal'][ct1] = IncDict['SpecifiedIncome']
        for ct2 in range(len(IncDict['SpecifiedIncomeChange'])):
            if Age[ct1,0] >= IncDict['AgeSpecifiedIncomeChangeWillStart'][ct2]:
                Income['MaxTotal'][ct1] += IncDict['SpecifiedIncomeChange'][ct2]

        Income['MaxStandard'][ct1] = IncDict['MaxStandardIncome']
        for ct2 in range(len(IncDict['MaxStandardIncomeChange'])):
            if Age[ct1,0] >= IncDict['AgeMaxStandardIncomeChangeWillStart'][ct2]:
                Income['MaxStandard'][ct1] += IncDict['MaxStandardIncomeChange'][ct2]

        # All "non-adjustable" income sources (i.e., we cannot modify the amounts, in the framework of this simulation),
        # including dividends, "other income", RMDs, and social security
        NonAdjustableIncome(TotalCash,Income,PreTax,PreTax457b,RMD, PostTax,IncDict,Age,ct1)

        # Below are "adjustable" income/cash sources - i.e. we can modify these income/cash values each year of the
        # simulation to achieve our goals.

        # Goals:
        # 1. Achieve exact specified total max income
        #     a. If not possible, try to have total income not exceed specified total max income
        # 2. Achieve standard income equal to max standard income (e.g. to maximize standard deduction if max standard
        # income = standard deduction)
        #     a. If not possible, try to have standard income not exceed max standard income
        # 3. Generate enough cash to cover TotalCashNeeded: TotalCash >= TotalCashNeeded
        # 4. Generate income and cash first from tax and penalty-free sources, then progress up from the lowest tax/
        # penalty options to the highest (i.e. starting with the standard deduction for standard income and 0% LT cap
        # gains bracket for LT cap gains, then up from lowest tax/penalty options to highest)

        if Income['TotalSS'][ct1] > 0.:

            # Run TaxableIncomeTargetMethodWithSSI
            # Note: any references to "SSI" stand for normal social security income (RIB), not Supplemental Security
            # Income (a different program that is also provided by the Social Security Administration).
            TaxableSSdesired, Income['MaxStandard'][ct1], Income['MaxTotal'][ct1] = \
                TaxableIncomeTargetMethodWithSSI(Income['TotalStandard'][ct1],Income['TotalLTcapGains'][ct1],
                                                 Income['TotalSS'][ct1],Income['MaxStandard'][ct1],
                                                 Income['MaxTotal'][ct1], FilingStatus) #Income['TaxableSS'][ct1]
            Income['TotalStandard'][ct1] += TaxableSSdesired
            Income['Total'][ct1] += TaxableSSdesired

        # Withdraw from PreTax accounts (PreTax and PreTax457b)
        WithdrawFromAllPreTax(PreTax,PreTax457b,Income,TotalCash,Roth, Age,ct1)

        # Withdraw from post-tax lots
        WithdrawFromPostTax(PostTax,TotalCash,Income, TotalCashNeeded[ct1],IVdict,ct1)

        # Compute TaxableSS, based on income from WithdrawFromAllPreTax and WithdrawFromPostTax
        if Income['TotalSS'][ct1] > 0.:
            NonSSstandardIncome = Income['TotalStandard'][ct1] - TaxableSSdesired
            Income['TaxableSS'][ct1] = TaxableSSconsolidated(NonSSstandardIncome + Income['TotalLTcapGains'][ct1],
                                                             Income['TotalSS'][ct1], FilingStatus)
            if np.abs(Income['TaxableSS'][ct1] - TaxableSSdesired) >= 0.01:
                Income['TotalStandard'][ct1] = NonSSstandardIncome + Income['TaxableSS'][ct1]
                Income['Total'][ct1] = Income['TotalStandard'][ct1] + Income['TotalLTcapGains'][ct1]

        # Compute Taxes
        TaxesDict = ComputeTaxes(TaxRateInfo,FilingStatus,Income['TotalStandard'][ct1],Income['TotalLTcapGains'][ct1])
        Taxes[ct1] = TaxesDict['Total']

        if TotalCash[ct1] < TotalCashNeeded[ct1]:
            # Get cash with no taxes or penalties to meet TotalCashNeeded, if needed
            GetRemainingNeededCashNoTaxesOrPenalties(TotalCash,Roth,CashCushion, TotalCashNeeded[ct1],Age,ct1)

        if IncDict['TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag']:
            if TotalCash[ct1] < TotalCashNeeded[ct1]:
                # Try reducing standard income & increasing LT cap gains by same amount to get more cash, if possible
                TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc(TotalCash,PreTax,PreTax457b,PostTax,Roth,Income,
                                                                     Taxes, Age,TotalCashNeeded[ct1],ct1,TaxRateInfo,
                                                                     FilingStatus)


        if TotalCash[ct1] < TotalCashNeeded[ct1]:
            # If unable to obtain enough cash without additional taxes or penalties, proceed with sources that WILL
            # generate additional taxes and/or penalties
            GetRemainingNeededCashWithTaxesAndOrPenalties(PreTax,PreTax457b,PostTax,Roth,Income,TotalCash,Taxes,
                                                          Penalties,IVdict,TaxRateInfo,FilingStatus,TotalCashNeeded[ct1],Age,
                                                          ct1)

        # if TotalCash still less than TotalCashNeeded, you've run out of money!
        if TotalCashNeeded[ct1] - TotalCash[ct1] >= 0.01:
            print('Ran out of money!')
            print('Age = '+str(Age[ct1,0]))
            OutOfMoneyAge = Age[ct1,0]
            break

        # After obtaining cash needed:

        # if ExcessCash > 0, need to reinvest
        ExcessCash = TotalCash[ct1] - TotalCashNeeded[ct1]
        if ExcessCash >= 0.01:
            # put remainder of cash into new lot (column) within PostTax since purchasing a new lot
            NewLot = np.zeros((np.shape(PostTax['Bal'])[0],1))
            NewLot[ct1,0] = ExcessCash
            PostTax['Bal'] = np.append(PostTax['Bal'],NewLot,1)
            # Also expand PostTax['CG'] array for new lot, with cap gain = 0 (since newly purchased)
            PostTax['CG'] = np.append(PostTax['CG'],np.zeros((np.shape(PostTax['CG'])[0],1)),1)

        # Adjust tax bill for next year if total income not achieved, and have ACA health insurance (since subsidies
        # will change) (which also means checking to see if either person still under 65, and thus not eligible for
        # Medicare)
        # if Income['Total'][ct1] != Income['MaxTotal'][ct1] and IncDict['AdjustTaxBillIfIncomeForACAsubsidiesNotMet'] \
        #         and Age[ct1,-1] < 65.:
        debug = 1
        # if Income['Total'][ct1] != IncDict['ExpectedIncomeForACAsubsidies'] and \
        #         IncDict['AdjustTaxBillIfIncomeForACAsubsidiesNotMet'] and Age[ct1,-1] < 65.:
        if np.abs(Income['Total'][ct1] - IncDict['ExpectedIncomeForACAsubsidies']) > 0.009 and \
                IncDict['AdjustTaxBillIfIncomeForACAsubsidiesNotMet'] and Age[ct1,-1] < 65.:

            # Compute subsidy using expected income IncDict['ExpectedIncomeForACAsubsidies']
            NominalSubsidy = ComputeSubsidy(IncDict['ExpectedIncomeForACAsubsidies'],IncDict['NumPeopleOnACA'],
                                            IncDict['Residence'],IncDict['BenchmarkPrice'])
            # Compute subsidy for actual total income
            NewSubsidy = ComputeSubsidy(Income['Total'][ct1],IncDict['NumPeopleOnACA'],IncDict['Residence'],
                                        IncDict['BenchmarkPrice'])
            SubsidyDelta = np.round(NewSubsidy - NominalSubsidy,2)
            # An increase in subsidy (SubsidyDelta increases) means a decrease in taxes owed the next year (or increases
            # the refund), so subtract SubsidyDelta from Taxes[ct1] (taxes generated, which will be paid next year)
            # And a decrease in subsidy produces a negative SubsidyDelta, so subtracting that negative number will
            # increase Taxes[ct1]
            Taxes[ct1] -= SubsidyDelta


        # Compute total PostTax
        PostTax['Total'][ct1] = np.sum(PostTax['Bal'][ct1,:])

        # Compute total cap gains
        PostTax['CGtotal'][ct1] = np.sum(PostTax['CG'][ct1,:])

        # Compute total assets
        TotalAssets[ct1] = PostTax['Total'][ct1] + PreTax['Total'][ct1] + PreTax457b['Total'][ct1] + Roth['Total'][ct1]\
                           + CashCushion[ct1]

    # assemble output dictionary
    ProjArrays = {'PreTax': PreTax['Bal'],
                  'PreTaxTotal': PreTax['Total'],
                  'PreTax457b': PreTax457b['Bal'],
                  'PreTax457bTotal': PreTax457b['Total'],
                  'PostTax': PostTax['Bal'],
                  'PostTaxCG': PostTax['CG'],
                  'Roth': Roth['Bal'],
                  'RothTotal': Roth['Total'],
                  'RothContributions': Roth['Contributions'],
                  'RothConversionAmount': Roth['ConversionAmount'],
                  'RothConversionAge': Roth['ConversionAge'],
                  'RothConversionPerson': Roth['ConversionPerson'],
                  'CashCushion': CashCushion,
                  'PostTaxTotal': PostTax['Total'],
                  'CapGainsTotal': PostTax['CGtotal'],
                  'TotalAssets': TotalAssets,
                  'Age': Age,
                  'OutOfMoneyAge': OutOfMoneyAge,
                  'TotalCash': TotalCash,
                  'TotalCashNeeded': TotalCashNeeded,
                  'TotalStandardIncome': Income['TotalStandard'],
                  'TotalLTcapGainsIncome': Income['TotalLTcapGains'],
                  'TotalSSincome': Income['TotalSS'],
                  'TotalIncome': Income['Total'],
                  'Expenses': Expenses,
                  'SpecifiedIncome': Income['MaxTotal'],
                  'Taxes': Taxes,
                  'Penalties': Penalties,
                  'RMD': RMD['Bal'],
                  'RMDtotal': RMD['Total']}

    return ProjArrays
