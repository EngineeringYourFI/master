# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ProjFinalBalance.py

import numpy as np
# import copy
# import os
# import matplotlib.pyplot as plt
# from scipy import optimize

from SupportMethods import ComputeTaxes
from TaxableSS import TaxableSS
from ComputeMaxNonSSstandardIncome import ComputeMaxNonSSstandardIncome
from ComputeMaxCapGains import ComputeMaxCapGains

# Expand width of output in console
import pandas as pd
desired_width = 1000 #320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

# Project final balance, from inputs (e.g. initial balances, tax rates, etc.)
def ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, SingleOrMarried):

    # Initialize asset values
    PreTax = np.zeros(NumYearsToProject)
    PreTax457b = np.zeros(NumYearsToProject)
    PostTax = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    PostTaxCG = np.zeros((NumYearsToProject,np.size(IVdict['PostTaxIV'])))
    Roth = np.zeros(NumYearsToProject)
    RothContributions = np.zeros(NumYearsToProject)
    RothRolloverAmount = np.array([], dtype=float)
    RothRolloverAge = np.array([], dtype=float)
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
    SpecifiedIncome = np.zeros(NumYearsToProject)
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

        # Income

        if np.all(Age[ct1,:] >= 65.):
            SpecifiedIncome[ct1] = IncDict['SpecifiedIncomeAfterACA']
        else:
            SpecifiedIncome[ct1] = IncDict['SpecifiedIncome']

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
        # Must do after dividend and other income, because must account for the impact on standard income when computing
        # the remaining standard income needed for particular taxable SS income, and perhaps amount of cap gain needed
        # to ensure total standard income does not exceed IncDict['MaxStandardIncome']
        TotalSS = 0.
        for ct2 in range(len(IncDict['SocialSecurityPayments'])):
            if Age[ct1,ct2] >= IncDict['AgeSSwillStart'][ct2]:
                TotalSS += IncDict['SocialSecurityPayments'][ct2]

        if TotalSS > 0.:

            TotalCash[ct1] += TotalSS

            # Determine how much room left for taxable SS income in IncDict['MaxStandardIncome']
            RemainingStandardIncomeRoom = IncDict['MaxStandardIncome'] - TotalStandardIncome[ct1]

            # Solve for max non-SS standard income that will, when added to taxable SS income, equal
            # RemainingStandardIncomeRoom
            MaxNonSSstandardIncome = ComputeMaxNonSSstandardIncome(TotalSS,SpecifiedIncome[ct1],
                                                                   RemainingStandardIncomeRoom,SingleOrMarried)
            # determine how much of social security income will be taxable
            TaxableSSincome = RemainingStandardIncomeRoom - MaxNonSSstandardIncome
            # Should be the same:
            # TaxableSSincome = TaxableSS(MaxNonSSstandardIncome,TotalSS,SpecifiedIncome[ct1] -
            #                             IncDict['MaxStandardIncome'],SingleOrMarried)

            # if MaxNonSSstandardIncome is negative, that means TaxableSSincome is GREATER than
            # RemainingStandardIncomeRoom (i.e. how much room left in standard deduction)
            if MaxNonSSstandardIncome < 0.:
                # first determine if it's possible to lower cap gains enough to get TaxableSSincome less than
                # RemainingStandardIncomeRoom:
                TaxableSSincomeNoOtherIncome = TaxableSS(0.,TotalSS,0.,SingleOrMarried)

                # if so, then determine what cap gains will result in TaxableSSincome = RemainingStandardIncomeRoom
                if TaxableSSincomeNoOtherIncome < RemainingStandardIncomeRoom:
                    MaxCapGains = np.round(ComputeMaxCapGains(TotalSS,RemainingStandardIncomeRoom,SingleOrMarried),2)
                    # TaxableSSincome should now equal RemainingStandardIncomeRoom
                    TaxableSSincome = np.round(TaxableSS(0.,TotalSS,MaxCapGains,SingleOrMarried),2)
                    # Reset SpecifiedIncome[ct1] to account for the lower cap gains
                    SpecifiedIncome[ct1] = TotalStandardIncome[ct1] + TaxableSSincome + MaxCapGains

            TotalSSincome[ct1] = TotalSS
            TotalStandardIncome[ct1] += TaxableSSincome
            TotalIncome[ct1] += TaxableSSincome


        # make withdrawals as needed to achieve specified income

        # withdraw 457b if room:
        RemainingStandardIncomeRoom = IncDict['MaxStandardIncome'] - TotalStandardIncome[ct1]
        if RemainingStandardIncomeRoom > 0:
            # if enough funds in 457b to cover the entire remainder
            if PreTax457b[ct1] >= RemainingStandardIncomeRoom:
                PreTax457b[ct1] -= RemainingStandardIncomeRoom
                TotalCash[ct1] += RemainingStandardIncomeRoom
                TotalStandardIncome[ct1] += RemainingStandardIncomeRoom
                TotalIncome[ct1] += RemainingStandardIncomeRoom
            else: # withdraw remaining balance
                TotalCash[ct1] += PreTax457b[ct1]
                TotalStandardIncome[ct1] += PreTax457b[ct1]
                TotalIncome[ct1] += PreTax457b[ct1]
                PreTax457b[ct1] = 0.

        # withdraw PreTax if room, rollover to Roth if not 60 yet
        RemainingStandardIncomeRoom = IncDict['MaxStandardIncome'] - TotalStandardIncome[ct1]
        if RemainingStandardIncomeRoom > 0.:
            # if enough funds in PreTax to cover the entire remainder
            if PreTax[ct1] > RemainingStandardIncomeRoom:
                PreTax[ct1] -= RemainingStandardIncomeRoom

                if Age[ct1,0] < 60.: # Rollover to roth
                    Roth[ct1] += RemainingStandardIncomeRoom
                    # capture rollover amount with age, to ensure not spent in less than 5 years
                    RothRolloverAmount = np.append(RothRolloverAmount,RemainingStandardIncomeRoom)
                    RothRolloverAge = np.append(RothRolloverAge,Age[ct1,0])
                else: # use the cash - no penalties
                    TotalCash[ct1] += RemainingStandardIncomeRoom

                TotalStandardIncome[ct1] += RemainingStandardIncomeRoom
                TotalIncome[ct1] += RemainingStandardIncomeRoom
            else: # withdraw remaining balance
                if Age[ct1,0] < 60.: # Rollover to roth
                    Roth[ct1] += PreTax[ct1]
                    # capture rollover amount with age, to ensure not spent in less than 5 years
                    RothRolloverAmount = np.append(RothRolloverAmount,PreTax[ct1])
                    RothRolloverAge = np.append(RothRolloverAge,Age[ct1,0])
                else: # use the cash - no penalties
                    TotalCash[ct1] += PreTax[ct1]

                TotalStandardIncome[ct1] += PreTax[ct1]
                TotalIncome[ct1] += PreTax[ct1]
                PreTax[ct1] = 0.

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
                TaxableSSincome = TaxableSS(NonSSstandardIncome,TotalSS,TotalLTcapGainsIncome[ct1],SingleOrMarried)
                # recompute TotalStandardIncome[ct1]
                TotalStandardIncome[ct1] = NonSSstandardIncome + TaxableSSincome

        # Taxes

        # Compute Taxes
        Taxes[ct1] = ComputeTaxes(TaxRateInfo,Age[ct1,:],SingleOrMarried,TotalStandardIncome[ct1],
                                  TotalLTcapGainsIncome[ct1])

        # subtract taxes from TotalCash
        CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]

        # if CashMinusTaxes less than Expenses, next need to pull from Roth
        if CashMinusTaxes < Expenses[ct1]:
            RemainingCashNeeded = Expenses[ct1] - CashMinusTaxes

            # first determine if Age >= 60
            if Age[ct1,0] >= 60.:
                # pull from entire balance without worrying about anything - no penalties or taxes
                # if Roth balance greater than remaining cash needed:
                if Roth[ct1] > RemainingCashNeeded:
                    TotalCash[ct1] += RemainingCashNeeded
                    Roth[ct1] -= RemainingCashNeeded
                else: # withdraw the entire balance
                    TotalCash[ct1] += Roth[ct1]
                    Roth[ct1] = 0.
            else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth and rollovers less than 5 years old if possible
                # first try to pull from original contributions
                # if contributions cover entire remaining cash needed:
                if RothContributions[ct1] > RemainingCashNeeded:
                    TotalCash[ct1] += RemainingCashNeeded
                    RothContributions[ct1] -= RemainingCashNeeded
                    Roth[ct1] -= RemainingCashNeeded
                else:
                    # then just withdraw remaining contributions
                    TotalCash[ct1] += RothContributions[ct1]
                    Roth[ct1] -= RothContributions[ct1]
                    RothContributions[ct1] = 0.

                    # Then recompute cash needed
                    CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]
                    RemainingCashNeeded = Expenses[ct1] - CashMinusTaxes

                    # since original contributions not enough, next pull from rollovers if they were made at least 5
                    # years ago
                    # loop over all rollovers
                    for ct2 in range(len(RothRolloverAmount)):
                        # if rollover non-zero and at least 5 years old
                        if (RothRolloverAmount[ct2] > 0.) and (Age[ct1,0] >= RothRolloverAge[ct2] + 5) and \
                                (RemainingCashNeeded > 0.):
                            # if rollover covers entire remaining cash needed:
                            if RothRolloverAmount[ct2] > RemainingCashNeeded:
                                TotalCash[ct1] += RemainingCashNeeded
                                RothRolloverAmount[ct2] -= RemainingCashNeeded
                                Roth[ct1] -= RemainingCashNeeded
                                # Then recompute cash needed
                                CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]
                                RemainingCashNeeded = Expenses[ct1] - CashMinusTaxes
                            else:
                                # then just withdraw remaining rollover amount
                                TotalCash[ct1] += RothRolloverAmount[ct2]
                                Roth[ct1] -= RothRolloverAmount[ct2]
                                RothRolloverAmount[ct2] = 0.
                                # Then recompute cash needed
                                CashMinusTaxes = TotalCash[ct1] - Taxes[ct1]
                                RemainingCashNeeded = Expenses[ct1] - CashMinusTaxes

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
