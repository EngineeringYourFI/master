# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ProjFinalBalanceTraditional.py

import numpy as np
import copy
# import os
# import matplotlib.pyplot as plt
# from scipy import optimize

from SupportMethods import ComputeTaxes
from TaxableSS import TaxableSS

# Expand width of output in console
import pandas as pd
desired_width = 1000 #320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

# Use standard / traditional method for retirement withdrawal order: PostTax until depleted, PreTax until depleted, Roth
def ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, SingleOrMarried):

    # Initialize asset values
    PreTax = np.zeros(NumYearsToProject)
    PreTax457b = np.zeros(NumYearsToProject)
    PostTax = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    PostTaxCG = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    Roth = np.zeros(NumYearsToProject)
    RothContributions = np.zeros(NumYearsToProject)
    CashCushion = np.zeros(NumYearsToProject)
    PostTaxTotal = np.zeros(NumYearsToProject)
    CapGainsTotal = np.zeros(NumYearsToProject)
    TotalAssets = np.zeros(NumYearsToProject)

    PreTax[0] = IVdict['PreTaxIV']
    PreTax457b[0] = IVdict['PreTax457bIV']
    PostTax[0,:] = IVdict['PostTaxIV']
    PostTaxCG[0,:] = IVdict['CurrentUnrealizedCapGains']
    Roth[0] = IVdict['RothIV']
    RothContributions[0] = IVdict['RothContributions']
    CashCushion[0] = IVdict['CashCushion']

    # Initialize Yearly values
    Age = np.zeros((NumYearsToProject,np.size(CurrentAge)))
    Age[0,:] = CurrentAge
    TotalCash = np.zeros(NumYearsToProject)
    TotalStandardIncome = np.zeros(NumYearsToProject)
    TotalLTcapGainsIncome = np.zeros(NumYearsToProject)
    TotalSSincome = np.zeros(NumYearsToProject)
    TotalIncome = np.zeros(NumYearsToProject)
    Expenses = np.zeros(NumYearsToProject)
    SpecifiedIncome = np.zeros(NumYearsToProject) #not used in this method, but it does make plotting consistent
    Taxes = np.zeros(NumYearsToProject)
    Penalties = np.zeros(NumYearsToProject)

    # loop over years
    for ct1 in range(0,NumYearsToProject):

        # apply investment growth to accounts if not at first year
        if ct1 > 0:
            Age[ct1,:] = Age[ct1-1,:] + 1
            PreTax[ct1] = np.round(PreTax[ct1-1]*(1+R),2)
            PreTax457b[ct1] = np.round(PreTax457b[ct1-1]*(1+R),2)
            Roth[ct1] = np.round(Roth[ct1-1]*(1+R),2)
            RothContributions[ct1] = RothContributions[ct1-1]
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

        # Initialize cash needed - initially assume no taxes
        TotalCashNeeded = Expenses[ct1]

        # If withdrawals trigger taxes, then withdrawals will need to be larger to cover taxes, which means more taxes, etc.
        # Loop until converged on a withdrawal amount that covers both expenses and the amount of taxes paid for that withdrawal
        Done = False
        while Done == False:

            # Initialize resetable quantities in while loop
            TotalCash[ct1] = 0.
            TotalStandardIncome[ct1] = 0.
            TotalLTcapGainsIncome[ct1] = 0.
            TotalIncome[ct1] = 0.
            TotalSSincome[ct1] = 0.

            # Only use Temp values for assets until while loop complete
            PostTaxTemp = copy.deepcopy(PostTax)
            PostTaxCGTemp = copy.deepcopy(PostTaxCG)
            PreTaxTemp = copy.deepcopy(PreTax)
            PreTax457bTemp = copy.deepcopy(PreTax457b)
            RothTemp = copy.deepcopy(Roth)
            RothContributionsTemp = copy.deepcopy(RothContributions)
            CashCushionTemp = copy.deepcopy(CashCushion)


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

            # Social security
            TotalSS = 0.
            for ct2 in range(len(IncDict['SocialSecurityPayments'])):
                if Age[ct1,ct2] >= IncDict['AgeSSwillStart'][ct2]:
                    TotalSS += IncDict['SocialSecurityPayments'][ct2]

            if TotalSS > 0.:
                TotalCash[ct1] += TotalSS
                TotalSSincome[ct1] = TotalSS

            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]

            # make withdrawals as needed from PostTaxTemp lots to obtain cash needed for expenses

            # First determine what percentage of lot is cap gains
            CapGainPercentage = np.zeros(len(PostTaxTemp[ct1,:]))
            for ct2 in range(len(CapGainPercentage)):
                if PostTaxTemp[ct1,ct2] > 0.:
                    CapGainPercentage[ct2] = PostTaxCGTemp[ct1,ct2] / PostTaxTemp[ct1,ct2]
                else:
                    CapGainPercentage[ct2] = np.nan

            # set lots in order from highest % cap gains to highest, since most people likely have the default FIFO cost basis
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
                # if total cash needed has not been achieved and this lot is non-zero
                if (RemainingCashNeeded > 0.) and (PostTaxTemp[ct1,CGpercentOrder[ct2]] > 0.):
                    # if assets from this lot > RemainingCashNeeded, sell fraction of lot
                    if (PostTaxTemp[ct1,CGpercentOrder[ct2]]) > RemainingCashNeeded:
                        # then compute % of lot needed to reach exactly RemainingCashNeeded
                        Fraction = RemainingCashNeeded / PostTaxTemp[ct1,CGpercentOrder[ct2]]
                        # then sell that % of lot
                        # determine how much cash that sell generates
                        CashGenerated = np.round(PostTaxTemp[ct1,CGpercentOrder[ct2]] * Fraction,2)
                        # determine how much capital gains that sell generates
                        CapGainGenerated = np.round(PostTaxCGTemp[ct1,CGpercentOrder[ct2]] * Fraction,2)

                    else: # sell entire lot
                        CashGenerated = PostTaxTemp[ct1,CGpercentOrder[ct2]]
                        CapGainGenerated = PostTaxCGTemp[ct1,CGpercentOrder[ct2]]

                    # add CashGenerated to TotalCash, remove from PostTaxTemp balance
                    TotalCash[ct1] += CashGenerated
                    PostTaxTemp[ct1,CGpercentOrder[ct2]] -= CashGenerated

                    # add CapGainGenerated to TotalLTcapGainsIncome and TotalIncome, remove from PostTaxCGTemp
                    TotalLTcapGainsIncome[ct1] += CapGainGenerated
                    TotalIncome[ct1] += CapGainGenerated
                    PostTaxCGTemp[ct1,CGpercentOrder[ct2]] -= CapGainGenerated

                    # recompute RemainingCashNeeded
                    RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]


            # if still not enough cash, withdraw from 457b:
            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]
            if RemainingCashNeeded > 0:
                # if enough funds in 457b to cover the entire remainder
                if PreTax457bTemp[ct1] >= RemainingCashNeeded:
                    PreTax457bTemp[ct1] -= RemainingCashNeeded
                    TotalCash[ct1] += RemainingCashNeeded
                    TotalStandardIncome[ct1] += RemainingCashNeeded
                    TotalIncome[ct1] += RemainingCashNeeded
                else: # withdraw remaining balance
                    TotalCash[ct1] += PreTax457bTemp[ct1]
                    TotalStandardIncome[ct1] += PreTax457bTemp[ct1]
                    TotalIncome[ct1] += PreTax457bTemp[ct1]
                    PreTax457bTemp[ct1] = 0.

            # if still not enough cash and over 60, withdraw from PreTaxTemp
            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]
            if (RemainingCashNeeded > 0.) and (Age[ct1,0] >= 60.):
                # if enough funds in PreTaxTemp to cover the entire remainder
                if PreTaxTemp[ct1] > RemainingCashNeeded:
                    PreTaxTemp[ct1] -= RemainingCashNeeded
                    TotalCash[ct1] += RemainingCashNeeded
                    TotalStandardIncome[ct1] += RemainingCashNeeded
                    TotalIncome[ct1] += RemainingCashNeeded
                else: # withdraw remaining balance
                    TotalCash[ct1] += PreTaxTemp[ct1]
                    TotalStandardIncome[ct1] += PreTaxTemp[ct1]
                    TotalIncome[ct1] += PreTaxTemp[ct1]
                    PreTaxTemp[ct1] = 0.

            # if still not enough cash, withdraw from RothTemp
            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]
            if RemainingCashNeeded > 0:
                # first determine if Age >= 60
                if Age[ct1,0] >= 60.:
                    # pull from entire balance without worrying about anything - no penalties or taxes
                    # if RothTemp balance greater than remaining cash needed:
                    if RothTemp[ct1] > RemainingCashNeeded:
                        TotalCash[ct1] += RemainingCashNeeded
                        RothTemp[ct1] -= RemainingCashNeeded
                    else: # withdraw the entire balance
                        TotalCash[ct1] += RothTemp[ct1]
                        RothTemp[ct1] = 0.
                else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth if possible
                    # so only pull from original contributions
                    # not doing RothTemp rollovers from PreTaxTemp in this method, using PreTaxTemp withdrawals
                    # immediately for expenses
                    # if contributions cover entire remaining cash needed:
                    if RothContributionsTemp[ct1] > RemainingCashNeeded:
                        TotalCash[ct1] += RemainingCashNeeded
                        RothContributionsTemp[ct1] -= RemainingCashNeeded
                        RothTemp[ct1] -= RemainingCashNeeded
                    else:
                        # then just withdraw remaining contributions
                        TotalCash[ct1] += RothContributionsTemp[ct1]
                        RothTemp[ct1] -= RothContributionsTemp[ct1]
                        RothContributionsTemp[ct1] = 0.


            # if still not enough cash, pull from CashCushionTemp
            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]
            if RemainingCashNeeded > 0.:
                # if cash cushion covers expenses:
                if CashCushionTemp[ct1] > RemainingCashNeeded:
                    TotalCash[ct1] += RemainingCashNeeded
                    CashCushionTemp[ct1] -= RemainingCashNeeded
                else:
                    # then just withdraw remaining balance
                    TotalCash[ct1] += CashCushionTemp[ct1]
                    CashCushionTemp[ct1] = 0.

            # if still not enough cash and less than 60, next need to pull from RothTemp growth (taking 10% penalty,
            # but at least no taxes)
            RemainingCashNeeded = TotalCashNeeded - TotalCash[ct1]
            if RemainingCashNeeded > 0:
                if Age[ct1,0] < 60.:
                    # if RothTemp balance is >= 1.1*(cash needed) (i.e. enough to cover cash needed and 10% penalty)
                    if RothTemp[ct1] >= np.round(1.1*RemainingCashNeeded,2):
                        Penalties[ct1] += 0.1*RemainingCashNeeded
                        TotalCash[ct1] += RemainingCashNeeded
                        RothTemp[ct1] -= np.round(1.1*RemainingCashNeeded,2)
                    else: # withdraw the entire balance
                        Penalties[ct1] += 0.1*RothTemp[ct1]
                        TotalCash[ct1] += np.round(RothTemp[ct1]/1.1,2)
                        RothTemp[ct1] = 0.

            # TODO: if still not enough cash and Age < 60, next pull from PreTaxTemp (paying taxes AND 10% penalty)

            # if CashMinusTaxes still less than TotalCashNeeded, you've run out of money!
            if TotalCash[ct1] < TotalCashNeeded:
                print('Ran out of money!')
                break


            # After obtaining cash needed:

            # determine how much of social security income will be taxable
            if TotalSS > 0.:
                TaxableSSincome = TaxableSS(TotalStandardIncome[ct1],TotalSS,TotalLTcapGainsIncome[ct1],SingleOrMarried)
                # Add to TotalStandardIncome[ct1] and TotalIncome[ct1]:
                TotalStandardIncome[ct1] += TaxableSSincome
                TotalIncome[ct1] += TaxableSSincome

            # Compute taxes
            Taxes[ct1] = np.round(ComputeTaxes(TaxRateInfo,Age[ct1,:],SingleOrMarried,TotalStandardIncome[ct1],
                                               TotalLTcapGainsIncome[ct1]),2)

            # subtract taxes from TotalCash
            CashMinusTaxes = np.round(TotalCash[ct1] - Taxes[ct1],2)

            # If expenses greater than CashMinusTaxes, then need to increase TotalCashNeeded and loop again
            # TODO: also stop the loop if completely out of money
            CashShortfall = np.round(Expenses[ct1] - CashMinusTaxes,2)
            if CashShortfall > 0.:
                # add CashShortfall to TotalCashNeeded and loop again
                TotalCashNeeded += CashShortfall
            else:
                # then done with while loop - either converged to CashMinusTaxes = Expenses, or CashMinusTaxes > Expenses
                Done = True

                # if CashMinusTaxes greater than Expenses, also need to reinvest excess cash
                # (e.g. if SS income + dividends exceed expenses)
                CashMinusTaxesMinusExpenses = CashMinusTaxes - Expenses[ct1]
                if CashMinusTaxesMinusExpenses > 0.01:
                    # put remainder of cash into new lot (column) within PostTax since purchasing a new lot
                    NewLot = np.zeros((np.shape(PostTaxTemp)[0],1))
                    NewLot[ct1,0] = CashMinusTaxesMinusExpenses
                    PostTaxTemp = np.append(PostTaxTemp,NewLot,1)
                    # Also expand PostTaxCG array for new lot, with cap gain = 0 (since newly purchased)
                    PostTaxCGTemp = np.append(PostTaxCGTemp,np.zeros((np.shape(PostTaxCGTemp)[0],1)),1)



        # Now that done with while loop, save asset status
        PostTax = copy.deepcopy(PostTaxTemp)
        PostTaxCG = copy.deepcopy(PostTaxCGTemp)
        PreTax = copy.deepcopy(PreTaxTemp)
        PreTax457b = copy.deepcopy(PreTax457bTemp)
        Roth = copy.deepcopy(RothTemp)
        RothContributions = copy.deepcopy(RothContributionsTemp)
        CashCushion = copy.deepcopy(CashCushionTemp)

        # Compute total PostTax
        PostTaxTotal[ct1] = np.sum(PostTax[ct1,:])

        # Compute total cap gains
        CapGainsTotal[ct1] = np.sum(PostTaxCG[ct1,:])

        # Compute total assets
        TotalAssets[ct1] = PostTaxTotal[ct1] + PreTax[ct1] + PreTax457b[ct1] + Roth[ct1] + CashCushion[ct1]

    # assemble output dictionary
    ProjArrays = {'PreTax': PreTax,
                  'PreTax457b': PreTax457b,
                  'PostTax': PostTax,
                  'PostTaxCG': PostTaxCG,
                  'Roth': Roth,
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
                  'Penalties': Penalties}

    return ProjArrays
