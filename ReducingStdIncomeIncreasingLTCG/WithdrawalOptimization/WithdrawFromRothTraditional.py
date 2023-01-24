# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRothTraditional.py

def WithdrawFromRothTraditional(TotalCashNeeded,Roth,RothContributions,TotalCash,Age):

    # compute cash needed
    RemainingCashNeeded = TotalCashNeeded - TotalCash

    if RemainingCashNeeded > 0. and Roth > 0.:
        if Age >= 60.:
            # pull from entire balance without worrying about anything - no penalties or taxes
            # if Roth balance greater than remaining cash needed:
            if Roth > RemainingCashNeeded:
                TotalCash += RemainingCashNeeded
                Roth -= RemainingCashNeeded
            else: # withdraw the entire balance
                TotalCash += Roth
                Roth = 0.
        else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth if possible
            # so only pull from original contributions
            # not doing RothTemp rollovers from PreTaxTemp in this method, using PreTaxTemp withdrawals
            # immediately for expenses
            # and to avoid a scenerio where contributions are greater than balance (e.g. if ROI is negative), use the
            # min of contributions vs bal
            MinVal = min(RothContributions,Roth)
            # if contributions cover entire remaining cash needed:
            if MinVal > RemainingCashNeeded:
                TotalCash += RemainingCashNeeded
                RothContributions -= RemainingCashNeeded
                Roth -= RemainingCashNeeded
            else:
                # then just withdraw MinVal #remaining contributions
                TotalCash += MinVal #RothContributions
                Roth -= MinVal # RothContributions
                RothContributions -= MinVal #= 0.

    return Roth, RothContributions, TotalCash
