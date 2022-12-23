# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPostTaxDelta.py

import numpy as np

# Withdraw increment from post-tax lots, return LT cap gain to assess in GetRemainingNeededCashWithTaxesAndOrPenalties
# If Execute flag on, actually withdraw from PostTax account
def WithdrawFromPostTaxDelta(PostTax,Step,TotalCash,Income,IVdict,YearCt,Execute):

    # Unpack needed dictionary items - for easier access
    PostTaxBal = PostTax['Bal'][YearCt,:]
    PostTaxCG = PostTax['CG'][YearCt,:]
    LotPurchasedFirstYear = IVdict['LotPurchasedFirstYear']
    if Execute:
        IncTot = Income['Total'][YearCt]
        IncTotLTcapGains = Income['TotalLTcapGains'][YearCt]

    # Initialize
    TotalWithdrawal = 0.
    TotalLTCG = 0.

    # First determine what percentage of lot is cap gains
    # CapGainPercentage = PostTaxCG / PostTax - doesn't account for PostTax[ct] = 0
    CapGainPercentage = np.zeros(len(PostTaxBal))
    for ct in range(len(CapGainPercentage)):
        if PostTaxBal[ct] > 0.:
            CapGainPercentage[ct] = PostTaxCG[ct] / PostTaxBal[ct]
        else:
            CapGainPercentage[ct] = np.nan

    # Sort the lots from lowest to highest percentage LT cap gain and sell them in that order to minimize LT cap gain
    CGpercentOrder = np.argsort(CapGainPercentage)

    # if first year, remove any indices in CGpercentOrder that correspond to LotPurchasedFirstYear = True
    if YearCt == 0:
        LotIndicesToRemove = np.where(LotPurchasedFirstYear)[0]
        # remove those indices
        for ct in range(len(LotIndicesToRemove)):
            CGpercentOrder = CGpercentOrder[CGpercentOrder != LotIndicesToRemove[ct]]

    # Then remove any indices in CGpercentOrder that correspond to CapGainPercentage = np.nan
    LotIndicesToRemove = np.where(np.isnan(CapGainPercentage))[0]
    # remove those indices
    for ct in range(len(LotIndicesToRemove)):
        CGpercentOrder = CGpercentOrder[CGpercentOrder != LotIndicesToRemove[ct]]

    # Loop over non-zero lots
    for ct in range(len(CGpercentOrder)):
        RemainingCashNeeded = Step - TotalWithdrawal
        # If RemainingCashNeeded above zero (0.1 in case rounding below causes issues) and this lot (PostTax[ct1,ct2])
        # is non-zero
        if (RemainingCashNeeded > 0.1) and (PostTaxBal[CGpercentOrder[ct]] > 0.):
            # if lot > RemainingCashNeeded, sell fraction of lot
            if (PostTaxBal[CGpercentOrder[ct]]) > RemainingCashNeeded:
                # Compute % of lot needed to reach exactly RemainingCashNeeded
                Fraction = RemainingCashNeeded / PostTaxBal[CGpercentOrder[ct]]
                # Then sell that % of lot
                # Determine how much cash that sell generates (should be same as RemainingCashNeeded)
                CashGenerated = np.round(PostTaxBal[CGpercentOrder[ct]] * Fraction,2)
                # Determine how much capital gains that sell generates
                CapGainGenerated = np.round(PostTaxCG[CGpercentOrder[ct]] * Fraction,2)
            else: # sell entire lot
                CashGenerated = PostTaxBal[CGpercentOrder[ct]]
                CapGainGenerated = PostTaxCG[CGpercentOrder[ct]]

            # add CashGenerated to TotalWithdrawal
            TotalWithdrawal += CashGenerated
            TotalLTCG += CapGainGenerated

            if Execute:
                # add CashGenerated to TotalCash, remove from PostTax balance
                TotalCash[YearCt] += CashGenerated
                PostTaxBal[CGpercentOrder[ct]] -= CashGenerated
                # add CapGainGenerated to TotalLTcapGainsIncome and TotalIncome, remove from PostTaxCG
                IncTotLTcapGains += CapGainGenerated
                IncTot += CapGainGenerated
                PostTaxCG[CGpercentOrder[ct]] -= CapGainGenerated

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    if Execute:
        Income['Total'][YearCt] = IncTot
        Income['TotalLTcapGains'][YearCt] = IncTotLTcapGains

    return TotalWithdrawal, TotalLTCG