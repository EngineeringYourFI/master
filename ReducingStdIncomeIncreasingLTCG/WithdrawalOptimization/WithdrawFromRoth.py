# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRoth.py

import numpy as np

def WithdrawFromRoth(Roth,TotalCash, TotalCashNeeded,Age,YearCt,PersonCt):

    # Unpack needed dictionary items - for easier access
    RothBal = Roth['Bal'][YearCt,PersonCt]
    RothContributions = Roth['Contributions'][YearCt,PersonCt]
    RothRollAmount = Roth['RolloverAmount']
    RothRollAge = Roth['RolloverAge']
    RothRollPerson = Roth['RolloverPerson']

    # compute cash needed
    RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

    if RemainingCashNeeded > 0.:
        # first determine if Age >= 60
        if Age[YearCt,PersonCt] >= 60.:
            # pull from entire balance without worrying about anything - no penalties or taxes
            # if Roth balance greater than remaining cash needed:
            if RothBal > RemainingCashNeeded:
                TotalCash[YearCt] += RemainingCashNeeded
                RothBal -= RemainingCashNeeded
            else: # withdraw the entire balance
                TotalCash[YearCt] += RothBal
                RothBal = 0.
        else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth and rollovers less than 5 years old if possible
            # first try to pull from original contributions
            # and to avoid a scenerio where contributions are greater than balance (e.g. if ROI is negative), use the
            # min of contributions vs bal
            MinVal = min(RothContributions,RothBal)
            # if MinVal covers entire remaining cash needed:
            if MinVal > RemainingCashNeeded:
                TotalCash[YearCt] += RemainingCashNeeded
                RothContributions -= RemainingCashNeeded
                RothBal -= RemainingCashNeeded
            else:
                # then just withdraw MinVal
                TotalCash[YearCt] += MinVal
                RothBal -= MinVal
                RothContributions -= MinVal

                # Then recompute cash needed
                RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

                # since original contributions not enough, next pull from rollovers if they were made at least 5
                # years ago
                # loop over all rollovers
                for ct in range(len(RothRollAmount)):
                    # if rollover non-zero, at least 5 years old, corresponds to this person, and still need cash:
                    if (RothRollAmount[ct] > 0.) and (Age[YearCt,PersonCt] >= RothRollAge[ct] + 5) and \
                            (RothRollPerson[ct] == PersonCt) and (RemainingCashNeeded > 0.):
                        # and to avoid a scenerio where rollover is greater than balance (e.g. if ROI is negative), use
                        # the min of rollover vs bal
                        MinVal = min(RothRollAmount[ct],RothBal)
                        # if MinVal covers entire remaining cash needed:
                        if MinVal > RemainingCashNeeded:
                            TotalCash[YearCt] += RemainingCashNeeded
                            RothRollAmount[ct] -= RemainingCashNeeded
                            RothBal -= RemainingCashNeeded
                            # Then recompute cash needed
                            RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]
                        else:
                            # then just withdraw MinVal
                            TotalCash[YearCt] += MinVal
                            RothBal -= MinVal
                            RothRollAmount[ct] -= MinVal
                            # Then recompute cash needed
                            RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

    # Repack any modified immutable dictionary items (mutable items such as arrays/lists will already be modified)
    Roth['Bal'][YearCt,PersonCt] = RothBal
    Roth['Contributions'][YearCt,PersonCt] = RothContributions

