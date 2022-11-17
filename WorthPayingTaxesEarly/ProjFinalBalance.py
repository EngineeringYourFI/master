# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ProjFinalBalance.py

import numpy as np
import sys

from SupportMethods import ComputeTaxes
from TaxableSSconsolidated import TaxableSSconsolidated
from TaxableIncomeTargetMethodWithSSI import TaxableIncomeTargetMethodWithSSI
from WithdrawFrom457b import WithdrawFrom457b
from WithdrawFromPreTax import WithdrawFromPreTax
from WithdrawFromRoth import WithdrawFromRoth
from ComputeRMD import ComputeRMD

# Expand width of output in console
import pandas as pd
desired_width = 1000 #320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

# Project final balance, from inputs (e.g. initial balances, tax rates, etc.)
def ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                     TPMwithdraw457bFirst):

    # number of people (1 or 2)
    NumPeople = np.size(IVdict['PreTaxIV'])

    # Initialize asset values
    PreTax = np.zeros((NumYearsToProject,NumPeople))
    PreTax457b = np.zeros((NumYearsToProject,NumPeople))
    PostTax = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    PostTaxCG = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    Roth = np.zeros((NumYearsToProject,NumPeople))
    RothContributions = np.zeros((NumYearsToProject,NumPeople))

    RothRolloverAmount = np.array([], dtype=float) # The rollover amount
    RothRolloverAge = np.array([], dtype=float) # the age of the person's account the rollover is done on
    RothRolloverPerson = np.array([], dtype=int) # the person who does the rollover (0 = 1st person, 1 = 2nd person)
    CashCushion = np.zeros(NumYearsToProject)
    PreTaxTotal = np.zeros(NumYearsToProject)
    PreTax457bTotal = np.zeros(NumYearsToProject)
    PostTaxTotal = np.zeros(NumYearsToProject)
    CapGainsTotal = np.zeros(NumYearsToProject)
    RothTotal = np.zeros(NumYearsToProject)
    TotalAssets = np.zeros(NumYearsToProject)

    PreTax[0,:] = IVdict['PreTaxIV']
    PreTax457b[0,:] = IVdict['PreTax457bIV']
    PostTax[0,:] = IVdict['PostTaxIV']
    PostTaxCG[0,:] = IVdict['CurrentUnrealizedCapGains']
    Roth[0,:] = IVdict['RothIV']
    RothContributions[0,:] = IVdict['RothContributions']
    CashCushion[0] = IVdict['CashCushion']

    # Initialize Yearly values
    Age = np.zeros((NumYearsToProject,np.size(CurrentAge)))
    Age[0,:] = CurrentAge
    RMD = np.zeros((NumYearsToProject,np.size(CurrentAge)))
    TotalCash = np.zeros(NumYearsToProject)
    TotalStandardIncome = np.zeros(NumYearsToProject)
    TotalLTcapGainsIncome = np.zeros(NumYearsToProject)
    TotalSSincome = np.zeros(NumYearsToProject)
    TotalIncome = np.zeros(NumYearsToProject)
    Expenses = np.zeros(NumYearsToProject)
    MaxStandardIncome = np.zeros(NumYearsToProject)
    SpecifiedIncome = np.zeros(NumYearsToProject)
    Taxes = np.zeros(NumYearsToProject)
    Penalties = np.zeros(NumYearsToProject)
    RMDtotal = np.zeros(NumYearsToProject)

    # Testing
    # Taxes = ComputeTaxes(TaxRateInfo,'Single',76540.15,0)  #78102.19
    # debug = 1

    # loop over years
    for ct1 in range(0,NumYearsToProject):

        # Testing
        # if ct1 == 8:
        #     debug = 1

        # apply investment growth to accounts if not at first year
        if ct1 > 0:
            Age[ct1,:] = Age[ct1-1,:] + 1

            # tax advantaged accounts
            for ct2 in range(np.shape(PreTax)[1]):
                PreTax[ct1,ct2] = np.round(PreTax[ct1-1,ct2]*(1+R),2)
                PreTax457b[ct1,ct2] = np.round(PreTax457b[ct1-1,ct2]*(1+R),2)
                Roth[ct1,ct2] = np.round(Roth[ct1-1,ct2]*(1+R),2)
            RothContributions[ct1,:] = RothContributions[ct1-1,:]
            CashCushion[ct1] = CashCushion[ct1-1]
            # loop over post-tax lots
            for ct2 in range(np.shape(PostTax)[1]):
                # Compute gains, add to capital gains array
                PostTaxCG[ct1,ct2] = PostTaxCG[ct1-1,ct2] + np.round(PostTax[ct1-1,ct2]*R,2)
                # then add to PostTax array
                PostTax[ct1,ct2] = np.round(PostTax[ct1-1,ct2]*(1+R),2)

        # Compute expenses for current year
        Expenses[ct1] = ExpDict['Exp']
        for ct2 in range(len(ExpDict['FutureExpenseAdjustments'])):
            if Age[ct1,0] >= ExpDict['FutureExpenseAdjustmentsAge'][ct2]:
                Expenses[ct1] += ExpDict['FutureExpenseAdjustments'][ct2]

        # Income

        if np.all(Age[ct1,:] >= 65.):
            SpecifiedIncome[ct1] = IncDict['SpecifiedIncomeAfterACA']
        else:
            SpecifiedIncome[ct1] = IncDict['SpecifiedIncome']

        MaxStandardIncome[ct1] = IncDict['MaxStandardIncome']
        for ct2 in range(len(IncDict['MaxStandardIncomeChange'])):
            if Age[ct1,0] >= IncDict['AgeMaxStandardIncomeChangeWillStart'][ct2]:
                MaxStandardIncome[ct1] += IncDict['MaxStandardIncomeChange'][ct2]

        # Dividends
        TotalCash[ct1] += IncDict['CurrentAnnualQualifiedDividends'] + IncDict['CurrentAnnualNonQualifiedDividends']
        TotalStandardIncome[ct1] += IncDict['CurrentAnnualNonQualifiedDividends']
        TotalLTcapGainsIncome[ct1] += IncDict['CurrentAnnualQualifiedDividends']
        TotalIncome[ct1] += IncDict['CurrentAnnualQualifiedDividends'] + IncDict['CurrentAnnualNonQualifiedDividends']

        # Other income
        for ct2 in range(len(IncDict['OtherIncomeSources'])):
            if Age[ct1,0] >= IncDict['AgeOtherIncomeSourcesWillStart'][ct2]:
                TotalCash[ct1] += IncDict['OtherIncomeSources'][ct2]
                # assuming all "other income sources" are taxed as standard income (vs LT cap gains, social security, etc.)
                TotalStandardIncome[ct1] += IncDict['OtherIncomeSources'][ct2]
                TotalIncome[ct1] += IncDict['OtherIncomeSources'][ct2]

        # If after other income the TotalStandardIncome or TotalIncome exceeds the user set MaxStandardIncome or
        # SpecifiedIncome, the user should reevaluate the MaxStandardIncome and/or SpecifiedIncome
        if TotalStandardIncome[ct1] > MaxStandardIncome[ct1]:
            print('TotalStandardIncome[ct1] > MaxStandardIncome[ct1]: Reassess MaxStandardIncome.')
            sys.exit()
        if TotalIncome[ct1] > SpecifiedIncome[ct1]:
            print('TotalIncome[ct1] > SpecifiedIncome[ct1]: Reassess SpecifiedIncome.')
            sys.exit()

        # Required Minimum Distributions (RMDs)
        for ct2 in range(np.shape(PreTax)[1]):
            if Age[ct1,ct2] >= 72.:
                # PreTax
                RMDpretax, WR = ComputeRMD(PreTax[ct1,ct2],Age[ct1,ct2])
                # 457b
                RMD457b, WR = ComputeRMD(PreTax457b[ct1,ct2],Age[ct1,ct2])
                # Sum of all pretax accounts
                RMD[ct1,ct2] = RMDpretax + RMD457b
                # add to cash and income totals
                TotalCash[ct1] += RMD[ct1,ct2]
                TotalStandardIncome[ct1] += RMD[ct1,ct2]
                TotalIncome[ct1] += RMD[ct1,ct2]
                # remove from pretax accounts
                PreTax[ct1,ct2] -= RMDpretax
                PreTax457b[ct1,ct2] -= RMD457b

        RMDtotal[ct1] = np.sum(RMD[ct1,:])

        # Social security
        # Must do after dividend and other income, because must account for the impact on standard income when computing
        # the remaining standard income needed for particular taxable SS income, and perhaps amount of cap gain needed
        # to ensure total standard income does not exceed MaxStandardIncome[ct1] (if possible)
        TotalSS = 0.
        for ct2 in range(len(IncDict['SocialSecurityPayments'])):
            if Age[ct1,ct2] >= IncDict['AgeSSwillStart'][ct2]:
                TotalSS += IncDict['SocialSecurityPayments'][ct2]

        if TotalSS > 0.:

            TotalCash[ct1] += TotalSS

            # Run TaxableIncomeTargetMethodWithSSI
            TaxableSSincome, MaxStandardIncome[ct1], SpecifiedIncome[ct1] = \
                TaxableIncomeTargetMethodWithSSI(TotalStandardIncome[ct1], TotalLTcapGainsIncome[ct1], TotalSS,
                                                 MaxStandardIncome[ct1], SpecifiedIncome[ct1], FilingStatus)

            TotalSSincome[ct1] = TotalSS
            TotalStandardIncome[ct1] += TaxableSSincome
            TotalIncome[ct1] += TaxableSSincome

            # In case this ever happens:
            if TotalStandardIncome[ct1] > MaxStandardIncome[ct1]:
                print('TotalStandardIncome[ct1] > MaxStandardIncome[ct1]: Should not happen, figure out what to do in '
                      'this situation (if ever encountered).')
                sys.exit()
            if np.round(TotalIncome[ct1],2) > np.round(SpecifiedIncome[ct1],2): #have to do round to avoid annoying numerical issue
                print('TotalIncome[ct1] > SpecifiedIncome[ct1]: Should not happen, figure out what to do in '
                      'this situation (if ever encountered).')
                sys.exit()

        # make withdrawals as needed to achieve specified income

        if TPMwithdraw457bFirst:
            # withdraw 457b if room
            # loop over all 457b accounts (one or two)
            for ct2 in range(np.shape(PreTax457b)[1]):
                PreTax457b[ct1,ct2],TotalCash[ct1],TotalStandardIncome[ct1],TotalIncome[ct1] = \
                    WithdrawFrom457b(MaxStandardIncome[ct1],TotalStandardIncome[ct1],PreTax457b[ct1,ct2],
                                     TotalCash[ct1],TotalIncome[ct1])
            PreTax457bTotal[ct1] = np.sum(PreTax457b[ct1,:])

        # withdraw PreTax if room, rollover to Roth if not 60 yet
        # loop over all PreTax accounts (one or two in general)
        for ct2 in range(np.shape(PreTax)[1]):
            PreTax[ct1,ct2],TotalCash[ct1],TotalStandardIncome[ct1],TotalIncome[ct1],Roth[ct1,ct2],RothRolloverAmount,\
            RothRolloverAge,RothRolloverPerson = WithdrawFromPreTax(MaxStandardIncome[ct1],
                                                                    TotalStandardIncome[ct1], PreTax[ct1,ct2],
                                                                    TotalCash[ct1],TotalIncome[ct1],Age[ct1,ct2],
                                                                    Roth[ct1,ct2], RothRolloverAmount, RothRolloverAge,
                                                                    RothRolloverPerson, ct2)
        PreTaxTotal[ct1] = np.sum(PreTax[ct1,:])
        RothTotal[ct1] = np.sum(Roth[ct1,:])

        if TPMwithdraw457bFirst == False:
            # withdraw 457b if room
            # loop over all 457b accounts (one or two in general)
            for ct2 in range(np.shape(PreTax457b)[1]):
                PreTax457b[ct1,ct2],TotalCash[ct1],TotalStandardIncome[ct1],TotalIncome[ct1] = \
                    WithdrawFrom457b(MaxStandardIncome[ct1],TotalStandardIncome[ct1],PreTax457b[ct1,ct2],
                                     TotalCash[ct1],TotalIncome[ct1])
            PreTax457bTotal[ct1] = np.sum(PreTax457b[ct1,:])

        # withdraw post-tax:

        # First determine what percentage of lot is cap gains
        # CapGainPercentage = PostTaxCG[ct1,:] / PostTax[ct1,:] - doesn't account for PostTax[ct1,ct2] = 0
        CapGainPercentage = np.zeros(len(PostTax[ct1,:]))
        for ct2 in range(len(CapGainPercentage)):
            if PostTax[ct1,ct2] > 0.:
                CapGainPercentage[ct2] = PostTaxCG[ct1,ct2] / PostTax[ct1,ct2]
            else:
                CapGainPercentage[ct2] = np.nan

        if TotalCash[ct1] < Expenses[ct1]: # approximation, b/c taxes haven't been computed yet, but likely good enough
            # set lots in order from lowest % cap gains to highest, to maximize the chance there will be sufficient
            # cash for expenses
            CGpercentOrder = np.argsort(CapGainPercentage)
        else:
            # set lots in order from highest % cap gains to highest, to minimize the excess cash generated, since
            # already have enough
            CGpercentOrder = np.argsort(CapGainPercentage)[::-1]

        # if first year, remove any indices in CGpercentOrder that correspond to LotPurchasedFirstYear = True
        if ct1 == 0:
            LotIndicesToRemove = np.where(IVdict['LotPurchasedFirstYear'])[0]
            # remove those indices
            for ct2 in range(len(LotIndicesToRemove)):
                CGpercentOrder = CGpercentOrder[CGpercentOrder != LotIndicesToRemove[ct2]]

        # Then remove any indices in CGpercentOrder that correspond to CapGainPercentage = np.nan
        LotIndicesToRemove = np.where(np.isnan(CapGainPercentage))[0]
        # remove those indices
        for ct2 in range(len(LotIndicesToRemove)):
            CGpercentOrder = CGpercentOrder[CGpercentOrder != LotIndicesToRemove[ct2]]

        # Loop over non-zero lots
        for ct2 in range(len(CGpercentOrder)):
            # if total income specified has not been achieved and this lot (PostTax[ct1,ct2]) is non-zero
            # (subtracting 0.1 in case rounding below causes TotalIncome to just barely not get to SpecifiedIncome
            if (TotalIncome[ct1] < (SpecifiedIncome[ct1]-0.1)) and (PostTax[ct1,CGpercentOrder[ct2]] > 0.):
                # if cap gains from this lot + TotalIncome > SpecifiedIncome, sell fraction of lot
                if (PostTaxCG[ct1,CGpercentOrder[ct2]] + TotalIncome[ct1]) > SpecifiedIncome[ct1]:
                    # then compute % of cap gains needed to reach exactly SpecifiedIncome
                    CapGainFraction = (SpecifiedIncome[ct1] - TotalIncome[ct1]) / PostTaxCG[ct1,CGpercentOrder[ct2]]
                    # then sell that % of lot
                    # determine how much cash that sell generates
                    CashGenerated = np.round(PostTax[ct1,CGpercentOrder[ct2]] * CapGainFraction,2)
                    # determine how much capital gains that sell generates
                    CapGainGenerated = np.round(PostTaxCG[ct1,CGpercentOrder[ct2]] * CapGainFraction,2)

                else: # sell entire lot
                    CashGenerated = PostTax[ct1,CGpercentOrder[ct2]]
                    CapGainGenerated = PostTaxCG[ct1,CGpercentOrder[ct2]]

                # add CashGenerated to TotalCash, remove from PostTax balance
                TotalCash[ct1] += CashGenerated
                PostTax[ct1,CGpercentOrder[ct2]] -= CashGenerated

                # add CapGainGenerated to TotalLTcapGainsIncome and TotalIncome, remove from PostTaxCG
                TotalLTcapGainsIncome[ct1] += CapGainGenerated
                TotalIncome[ct1] += CapGainGenerated
                PostTaxCG[ct1,CGpercentOrder[ct2]] -= CapGainGenerated

        # If SS income, check to see if TotalIncome[ct1] = SpecifiedIncome[ct1]
        # If not, then it might not have been possible to achieve sufficient other standard income or capital gains,
        # which means that the amount of taxable SS income may be different, so that needs to be adjusted
        if TotalSS > 0.:
            if TotalIncome[ct1] < (SpecifiedIncome[ct1]-0.1):
                NonSSstandardIncome = TotalStandardIncome[ct1]-TaxableSSincome
                # recompute TaxableSSincome
                TaxableSSincome = TaxableSSconsolidated(NonSSstandardIncome+TotalLTcapGainsIncome[ct1],TotalSS,
                                                        FilingStatus)
                # recompute TotalStandardIncome[ct1]
                TotalStandardIncome[ct1] = NonSSstandardIncome + TaxableSSincome
                print('TaxableSSincome Adjusted because TotalIncome < SpecifiedIncome (investigate and make sure this '
                      'is correct)')

        # Taxes

        # Compute Taxes
        Taxes[ct1] = ComputeTaxes(TaxRateInfo,FilingStatus,TotalStandardIncome[ct1],TotalLTcapGainsIncome[ct1])

        # subtract taxes from TotalCash
        CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]

        # if CashMinusTaxes less than Expenses, next need to pull from Roth
        if CashMinusTaxes < Expenses[ct1]:
            # loop over people
            for ct2 in range(np.shape(Roth)[1]):
                Roth[ct1,ct2], TotalCash[ct1], RothContributions[ct1,ct2], RothRolloverAmount = \
                    WithdrawFromRoth(Expenses[ct1],Age[ct1,ct2],Roth[ct1,ct2],TotalCash[ct1],
                                     RothContributions[ct1,ct2],Taxes[ct1],RothRolloverAmount,RothRolloverAge,
                                     RothRolloverPerson,ct2)
            RothTotal[ct1] = np.sum(Roth[ct1,:])

        # recompute CashMinusTaxes
        CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]

        # if still not enough cash, next need to pull from CashCushion
        if CashMinusTaxes < Expenses[ct1]:
            RemainingCashNeeded = Expenses[ct1] - CashMinusTaxes
            # if cash cushion covers expenses:
            if CashCushion[ct1] > RemainingCashNeeded:
                TotalCash[ct1] += RemainingCashNeeded
                CashCushion[ct1] -= RemainingCashNeeded
            else:
                # then just withdraw remaining balance
                TotalCash[ct1] += CashCushion[ct1]
                CashCushion[ct1] = 0.

        # recompute CashMinusTaxes
        CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]

        # TODO: all steps below
        # TODO: all steps below will require iteration to determine how much total withdrawal is needed to not only
        #  generate the cash needed, but also to pay for the penalties/taxes generated by the withdrawal - see
        #  ProjFinalBalanceTraditional.py
        # TODO: also stop the iteration loop if completely out of money

        # for all steps that involve selling taxable lots, sort the lots from lowest to highest percentage LT cap gain
        # and sell them in that order to minimize taxes.

        # Under 60, after pulling from cash account and still need more cash:
        # Sell remaining taxable lots that have LT cap gain percentage less than 66%: less than 10% effective tax
        # Pull from Roth growth or rollovers less than 5 years old: 10% penalty
        # Pull from 457(b) in 10% tax bracket (could also do this before pulling from Roth growth, same effective tax/penalty rate of 10%)
        # Sell remaining taxable lots that have LT cap gain percentage less than 80%: 10% to 12% effective tax
        # Pull from 457(b) in 12% tax bracket
        # Sell remaining taxable lots: 12% to 20% effective tax, given max 20% cap gains tax
        # Pull from pre-tax in 10% tax bracket: 10% taxes + 10% penalty = 20% effective tax/penalty rate
        # Pull from 457(b) in 22% tax bracket
        # Pull from pre-tax in 12% tax bracket: 12% taxes + 10% penalty = 22% effective tax/penalty rate
        # Pull from 457(b) in 24% tax bracket
        # Pull from 457(b) in 32% tax bracket
        # Pull from pre-tax in 22% tax bracket: 22% taxes + 10% penalty = 32% effective tax/penalty rate
        # Pull from pre-tax in 24% tax bracket: 24% taxes + 10% penalty = 34% effective tax/penalty rate
        # Pull from 457(b) in 35% tax bracket
        # Pull from 457(b) in 37% tax bracket (all remaining funds)
        # Pull from pre-tax in 32% tax bracket: 32% taxes + 10% penalty = 42% effective tax/penalty rate
        # Pull from pre-tax in 35% tax bracket: 35% taxes + 10% penalty = 45% effective tax/penalty rate
        # Pull from pre-tax in 37% tax bracket: 37% taxes + 10% penalty = 47% effective tax/penalty rate (all remaining funds)

        # Over 60, after pulling from cash account and still need more cash:
        # Sell remaining taxable lots that have LT cap gain percentage less than 66%: less than 10% effective tax
        # Pull from 457(b) in 10% tax bracket
        # Sell remaining taxable lots that have LT cap gain percentage less than 80%: 10% to 12% effective tax
        # Pull from 457(b) or pre-tax in 12% tax bracket
        # Sell remaining taxable lots: 12% to 20% effective tax, given max 20% cap gains tax
        # Pull remaining funds from 457(b) or pre-tax (all remaining tax brackets, starting at 22%)


        # if CashMinusTaxes still less than Expenses, you've run out of money!
        if CashMinusTaxes < Expenses[ct1]:
            print('Ran out of money!')
            break

        # subtract expenses from CashMinusTaxes
        CashMinusTaxesMinusExpenses = CashMinusTaxes - Expenses[ct1]

        # if extra cash, put remainder of cash into new lot (column) within PostTax since purchasing a new lot
        if CashMinusTaxesMinusExpenses > 0.:
            NewLot = np.zeros((np.shape(PostTax)[0],1))
            NewLot[ct1,0] = CashMinusTaxesMinusExpenses
            PostTax = np.append(PostTax,NewLot,1)
            # Also expand PostTaxCG array for new lot, with cap gain = 0 (since newly purchased)
            PostTaxCG = np.append(PostTaxCG,np.zeros((np.shape(PostTaxCG)[0],1)),1)

        # Compute total PostTax
        PostTaxTotal[ct1] = np.sum(PostTax[ct1,:])

        # Compute total cap gains
        CapGainsTotal[ct1] = np.sum(PostTaxCG[ct1,:])

        # Compute total assets
        TotalAssets[ct1] = PostTaxTotal[ct1] + PreTaxTotal[ct1] + PreTax457bTotal[ct1] + RothTotal[ct1] + CashCushion[ct1]

    # assemble output dictionary
    ProjArrays = {'PreTax': PreTax,
                  'PreTaxTotal': PreTaxTotal,
                  'PreTax457b': PreTax457b,
                  'PreTax457bTotal': PreTax457bTotal,
                  'PostTax': PostTax,
                  'PostTaxCG': PostTaxCG,
                  'Roth': Roth,
                  'RothTotal': RothTotal,
                  'CashCushion': CashCushion,
                  'PostTaxTotal': PostTaxTotal,
                  'CapGainsTotal': CapGainsTotal,
                  'TotalAssets': TotalAssets,
                  'Age': Age,
                  'TotalCash': TotalCash,
                  'TotalStandardIncome': TotalStandardIncome,
                  'TotalLTcapGainsIncome': TotalLTcapGainsIncome,
                  'TotalSSincome': TotalSSincome,
                  'TotalIncome': TotalIncome,
                  'Expenses': Expenses,
                  'SpecifiedIncome': SpecifiedIncome,
                  'Taxes': Taxes,
                  'Penalties': Penalties,
                  'RMDtotal': RMDtotal}

    return ProjArrays
