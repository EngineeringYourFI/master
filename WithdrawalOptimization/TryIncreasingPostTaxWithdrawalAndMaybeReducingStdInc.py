# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc.py

import numpy as np
from ComputeTaxes import *

# Try reducing standard income and increasing LT cap gains to get more cash, if possible

def TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc(TotalCash,PreTax,PreTax457b,PostTax,Roth,Income,Taxes, Age,
                                                         TotalCashNeeded,YearCt,TaxRateInfo,FilingStatus):

    # Unpack needed dictionary items - for easier access, cleaner and easier to read code
    PostTaxBal = PostTax['Bal'][YearCt,:]
    PostTaxTot = PostTax['Total'][YearCt]
    PostTaxCG = PostTax['CG'][YearCt,:]
    PostTaxCGtotal = PostTax['CGtotal'][YearCt]
    IncTot = Income['Total'][YearCt]
    IncomeTotStd = Income['TotalStandard'][YearCt]
    IncTotLTcapGains = Income['TotalLTcapGains'][YearCt]
    PreTaxTotalWithdrawn = PreTax['TotalWithdrawn'][YearCt]
    PreTaxWithdrawn = PreTax['Withdrawn'][YearCt,:]
    PreTaxBal = PreTax['Bal'][YearCt,:]
    PreTaxTotal = PreTax['Total'][YearCt]
    PreTax457bTotalWithdrawn = PreTax457b['TotalWithdrawn'][YearCt]
    PreTax457bWithdrawn = PreTax457b['Withdrawn'][YearCt,:]
    PreTax457bBal = PreTax457b['Bal'][YearCt,:]
    PreTax457bTotal = PreTax457b['Total'][YearCt]
    RothBal = Roth['Bal'][YearCt,:]
    RothTotal = Roth['Total'][YearCt]
    RothConversionAmount = Roth['ConversionAmount']
    RothConversionPerson = Roth['ConversionPerson']
    RothConversionAge = Roth['ConversionAge']

    # Only employ this method if there are PreTax/PreTax457b withdrawals to undo AND PostTax Cap Gains to use
    if (PreTaxTotalWithdrawn > 0.009 or PreTax457bTotalWithdrawn > 0.009) and PostTaxCGtotal > 0.009:
        pass
    else: return # using pass and return to avoid indenting the entire rest of the method

    # print('Test2')

    NumPeople = len(PreTaxWithdrawn)

    # Determine step size to reduce PreTax/PreTax457b and increase PostTax LTCG by each time (until PreTax/PreTax457b
    # TotalWithdrawn less than Step away from 0., at which point undo the remaining withdrawal)
    DefaultStep = 100.
    MaxSupportedStep = np.minimum(PreTaxTotalWithdrawn+PreTax457bTotalWithdrawn,PostTaxCGtotal)
    if MaxSupportedStep < DefaultStep:
        Step = MaxSupportedStep
    else:
        Step = DefaultStep

    # Initialize here, recompute for each step through the loop
    RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

    # loop until cash need met
    # (or all PreTax and PreTax457b withdrawals reversed)
    # (or PostTax account empty)
    while RemainingCashNeeded > 0.009:

        # print('Test')

        # Withdraw from PostTax until LTCG matches Step (if possible)

        # Initialize as Step - for PostTax withdrawal
        RemainingStep = Step

        # First determine what percentage of lot is cap gains
        # CapGainPercentage = PostTaxCG / PostTax - doesn't account for PostTax[ct] = 0
        CapGainPercentage = np.zeros(len(PostTaxBal))
        for ct in range(len(CapGainPercentage)):
            if PostTaxBal[ct] > 0.:
                CapGainPercentage[ct] = PostTaxCG[ct] / PostTaxBal[ct]
            else:
                CapGainPercentage[ct] = np.nan

        # set lots in order from lowest % cap gains to highest, to maximize the chance there will be sufficient cash
        CGpercentOrder = np.argsort(CapGainPercentage)

        # Remove any indices in CGpercentOrder that correspond to CapGainPercentage = np.nan
        LotIndicesToRemove = np.where(np.isnan(CapGainPercentage))[0]
        for ct in range(len(LotIndicesToRemove)):
            CGpercentOrder = CGpercentOrder[CGpercentOrder != LotIndicesToRemove[ct]]

        # Loop over non-zero lots
        for ct in range(len(CGpercentOrder)):
            # if increase in LTCG = Step has not been achieved (RemainingStep > 0.) and this lot is non-zero
            if RemainingStep > 0.009 and PostTaxBal[CGpercentOrder[ct]] > 0.009:
                # if cap gains from this lot > RemainingStep, sell fraction of lot
                if PostTaxCG[CGpercentOrder[ct]] > RemainingStep:
                    # then compute % of cap gains needed to reach exactly RemainingStep
                    CapGainFraction = RemainingStep / PostTaxCG[CGpercentOrder[ct]]
                    # then sell that % of lot
                    # determine how much cash that sell generates
                    CashGenerated = np.round(PostTaxBal[CGpercentOrder[ct]] * CapGainFraction,2)
                    # determine how much capital gains that sell generates
                    CapGainGenerated = np.round(PostTaxCG[CGpercentOrder[ct]] * CapGainFraction,2)
                else: # sell entire lot
                    CashGenerated = PostTaxBal[CGpercentOrder[ct]]
                    CapGainGenerated = PostTaxCG[CGpercentOrder[ct]]

                # add CashGenerated to TotalCash, remove from PostTax balance
                TotalCash[YearCt] += CashGenerated
                PostTaxBal[CGpercentOrder[ct]] -= CashGenerated
                PostTaxTot -= CashGenerated

                # add CapGainGenerated to TotalLTcapGainsIncome and TotalIncome, remove from PostTaxCG and RemainingStep
                IncTotLTcapGains += CapGainGenerated
                IncTot += CapGainGenerated
                PostTaxCG[CGpercentOrder[ct]] -= CapGainGenerated
                PostTaxCGtotal -= CapGainGenerated
                RemainingStep -= CapGainGenerated

        # Recompute for each step through the loop - after PostTax withdrawal AND PreTax/PreTax457b withdrawal undo
        RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

        # Recompute Taxes, determine if increased
        TaxesDict = ComputeTaxes(TaxRateInfo,FilingStatus,IncomeTotStd,IncTotLTcapGains)
        TaxesTemp = TaxesDict['Total']

        # If Taxes not increased, no reason to reduce PreTax/PreTax457b withdrawals
        # TODO: might still need to do so for future version that accounts for ACA subsidies
        if (TaxesTemp - Taxes[YearCt]) < 0.01:
            continue # skip rest of this while loop iteration

        # If Taxes ARE increased, reduce PreTax/PreTax457b withdrawals

        print('Reducing PreTax/PreTax457b withdrawals')

        # Initialize as Step - for PreTax/PreTax457b withdrawal reversals
        RemainingStep = Step

        # Undo PreTax withdrawals first (if any)
        # loop over people
        for ct in range(NumPeople):
            if PreTaxWithdrawn[ct] > 0.009 and RemainingStep > 0.009:
                # if enough funds in ['Withdrawn'][YearCt,ct] to cover the entire RemainingStep
                if PreTaxWithdrawn[ct] >= RemainingStep:
                    # Add back to balance
                    PreTaxBal[ct] += RemainingStep
                    PreTaxTotal += RemainingStep
                    PreTaxWithdrawn[ct] -= RemainingStep
                    PreTaxTotalWithdrawn -= RemainingStep
                    if Age[YearCt,ct] < 60.: # Then the withdrawal was a Roth conversion, so undo that as well
                        RothBal[ct] -= RemainingStep
                        RothTotal -= RemainingStep
                        # Loop over Roth conversion arrays until found RothConversionAge and RothConversionPerson that
                        # match this person and age - starting from end of arrays
                        for ct2 in reversed(range(len(RothConversionAmount))):
                            if RothConversionPerson[ct2] == ct and RothConversionAge[ct2] == Age[YearCt,ct]:
                                RothConversionAmount[ct2] -= RemainingStep
                    else: # then wasn't a Roth conversion, and need to undo the cash withdrawal
                        TotalCash[YearCt] -= RemainingStep
                    # Remove from income
                    IncomeTotStd -= RemainingStep
                    IncTot -= RemainingStep
                    RemainingStep = 0.
                else: # undo withdrawal remaining in PreTaxWithdrawn[ct]
                    # Add back to balance
                    PreTaxBal[ct] += PreTaxWithdrawn[ct]
                    PreTaxTotal += PreTaxWithdrawn[ct]
                    if Age[YearCt,ct] < 60.: # Then the withdrawal was a Roth conversion, so undo that as well
                        RothBal[ct] -= PreTaxWithdrawn[ct]
                        RothTotal -= PreTaxWithdrawn[ct]
                        # Loop over Roth conversion arrays until found RothConversionAge and RothConversionPerson that
                        # match this person and age - starting from end of arrays
                        for ct2 in reversed(range(len(RothConversionAmount))):
                            if RothConversionPerson[ct2] == ct and RothConversionAge[ct2] == Age[YearCt,ct]:
                                RothConversionAmount[ct2] -= PreTaxWithdrawn[ct]
                    else: # then wasn't a Roth conversion, and need to undo the cash withdrawal
                        TotalCash[YearCt] -= PreTaxWithdrawn[ct]
                    # Remove from income
                    IncomeTotStd -= PreTaxWithdrawn[ct]
                    IncTot -= PreTaxWithdrawn[ct]
                    RemainingStep -= PreTaxWithdrawn[ct]
                    PreTaxTotalWithdrawn -= PreTaxWithdrawn[ct]
                    PreTaxWithdrawn[ct] = 0.

        # Next undo PreTax457b withdrawals (if any) if no more PreTax withdrawals to undo
        # loop over people
        for ct in range(NumPeople):
            if PreTax457bWithdrawn[ct] > 0.009 and RemainingStep > 0.009:
                # if enough funds in ['Withdrawn'][YearCt,ct] to cover the entire RemainingStep
                if PreTax457bWithdrawn[ct] >= RemainingStep:
                    # Add back to balance
                    PreTax457bBal[ct] += RemainingStep
                    PreTax457bTotal += RemainingStep
                    PreTax457bWithdrawn[ct] -= RemainingStep
                    PreTax457bTotalWithdrawn -= RemainingStep
                    # undo the cash withdrawal
                    TotalCash[YearCt] -= RemainingStep
                    # Remove from income
                    IncomeTotStd -= RemainingStep
                    IncTot -= RemainingStep
                    RemainingStep = 0.
                else: # undo withdrawal remaining in PreTax457bWithdrawn[ct]
                    # Add back to balance
                    PreTax457bBal[ct] += PreTax457bWithdrawn[ct]
                    PreTax457bTotal += PreTax457bWithdrawn[ct]
                    # undo the cash withdrawal
                    TotalCash[YearCt] -= PreTax457bWithdrawn[ct]
                    # Remove from income
                    IncomeTotStd -= PreTax457bWithdrawn[ct]
                    IncTot -= PreTax457bWithdrawn[ct]
                    RemainingStep -= PreTax457bWithdrawn[ct]
                    PreTax457bTotalWithdrawn -= PreTax457bWithdrawn[ct]
                    PreTax457bWithdrawn[ct] = 0.

        # Recompute Taxes
        TaxesDict = ComputeTaxes(TaxRateInfo,FilingStatus,IncomeTotStd,IncTotLTcapGains)
        Taxes[YearCt] = TaxesDict['Total']

        # Recompute for each step through the loop
        RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

        # If both PreTax and PreTax457b run out of withdrawals, or PostTax LTCG drop to zero, then can't do more
        if (PreTaxTotalWithdrawn < 0.009 and PreTax457bTotalWithdrawn < 0.009) or PostTaxCGtotal < 0.009:
            break

    # Recompute Taxes, just in case it's changed (e.g. if MaxStandardIncome set above standard deduction, reducing that
    # and increasing the LTCG could actually reduce taxes (and generate more cash as well, which is what’s needed))
    TaxesDict = ComputeTaxes(TaxRateInfo,FilingStatus,IncomeTotStd,IncTotLTcapGains)
    Taxes[YearCt] = TaxesDict['Total']

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    # PostTax['Bal'][YearCt,:] = PostTaxBal # mutable
    PostTax['Total'][YearCt] = PostTaxTot
    # PostTax['CG'][YearCt,:] = PostTaxCG # mutable
    PostTax['CGtotal'][YearCt] = PostTaxCGtotal
    Income['Total'][YearCt] = IncTot
    Income['TotalStandard'][YearCt] = IncomeTotStd
    Income['TotalLTcapGains'][YearCt] = IncTotLTcapGains
    PreTax['TotalWithdrawn'][YearCt] = PreTaxTotalWithdrawn
    # PreTax['Withdrawn'][YearCt,:] = PreTaxWithdrawn # mutable
    # PreTax['Bal'][YearCt,:] = PreTaxBal # mutable
    PreTax['Total'][YearCt] = PreTaxTotal
    PreTax457b['TotalWithdrawn'][YearCt] = PreTax457bTotalWithdrawn
    # PreTax457b['Withdrawn'][YearCt,:] = PreTax457bWithdrawn # mutable
    # PreTax457b['Bal'][YearCt,:] = PreTax457bBal # mutable
    PreTax457b['Total'][YearCt] = PreTax457bTotal
    # Roth['Bal'][YearCt,:] = RothBal # mutable
    Roth['Total'][YearCt] = RothTotal
    # Roth['ConversionAmount'] = RothConversionAmount # mutable

    debug = 1
