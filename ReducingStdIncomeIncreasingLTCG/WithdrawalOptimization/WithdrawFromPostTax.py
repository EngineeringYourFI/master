# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPostTax.py

import numpy as np

# Withdraw from post-tax lots

def WithdrawFromPostTax(PostTax,TotalCash,Income, TotalCashNeeded,IVdict,YearCt):

    # Unpack needed dictionary items - for easier access
    PostTaxBal = PostTax['Bal'][YearCt,:]
    PostTaxCG = PostTax['CG'][YearCt,:]
    LotPurchasedFirstYear = IVdict['LotPurchasedFirstYear']
    IncTot = Income['Total'][YearCt]
    IncMaxTot = Income['MaxTotal'][YearCt]
    IncTotLTcapGains = Income['TotalLTcapGains'][YearCt]

    # First determine what percentage of lot is cap gains
    # CapGainPercentage = PostTaxCG / PostTax - doesn't account for PostTax[ct] = 0
    CapGainPercentage = np.zeros(len(PostTaxBal))
    for ct in range(len(CapGainPercentage)):
        if PostTaxBal[ct] > 0.:
            CapGainPercentage[ct] = PostTaxCG[ct] / PostTaxBal[ct]
        else:
            CapGainPercentage[ct] = np.nan

    if TotalCash[YearCt] < TotalCashNeeded: # approximation, b/c taxes haven't been computed yet, but likely good enough
        # set lots in order from lowest % cap gains to highest, to maximize the chance there will be sufficient
        # cash for expenses+taxes+penalties
        CGpercentOrder = np.argsort(CapGainPercentage)
    else:
        # set lots in order from highest % cap gains to highest, to minimize the excess cash generated, since
        # already have enough
        CGpercentOrder = np.argsort(CapGainPercentage)[::-1]

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
        # if total income specified has not been achieved and this lot is non-zero
        # (subtracting 0.1 in case rounding below causes TotalIncome to just barely not get to SpecifiedIncome
        if (IncTot < (IncMaxTot-0.1)) and (PostTaxBal[CGpercentOrder[ct]] > 0.):
            # if cap gains from this lot + TotalIncome > SpecifiedIncome, sell fraction of lot
            if (PostTaxCG[CGpercentOrder[ct]] + IncTot) > IncMaxTot:
                # then compute % of cap gains needed to reach exactly SpecifiedIncome
                CapGainFraction = (IncMaxTot - IncTot) / PostTaxCG[CGpercentOrder[ct]]
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

            # add CapGainGenerated to TotalLTcapGainsIncome and TotalIncome, remove from PostTaxCG
            IncTotLTcapGains += CapGainGenerated
            IncTot += CapGainGenerated
            PostTaxCG[CGpercentOrder[ct]] -= CapGainGenerated

    # Compute totals
    PostTax['Total'][YearCt] = np.sum(PostTax['Bal'][YearCt,:])
    PostTax['CGtotal'][YearCt] = np.sum(PostTax['CG'][YearCt,:])

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    Income['Total'][YearCt] = IncTot
    Income['TotalLTcapGains'][YearCt] = IncTotLTcapGains
