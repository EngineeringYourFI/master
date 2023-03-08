# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRoth.py

import numpy as np

def WithdrawFromRoth(Roth,TotalCash, TotalCashNeeded,Age,YearCt,PersonCt):

    # Unpack needed dictionary items - for easier access
    RothBal = Roth['Bal'][YearCt,PersonCt]
    RothContributions = Roth['Contributions'][YearCt,PersonCt]
    RothConversionAmount = Roth['ConversionAmount']
    RothConversionAge = Roth['ConversionAge']
    RothConversionPerson = Roth['ConversionPerson']

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
        else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth and conversions less than 5 years old if possible
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

                # since original contributions not enough, next pull from conversions if they were made at least 5
                # years ago
                # loop over all Conversions
                for ct in range(len(RothConversionAmount)):
                    # if Conversion non-zero, at least 5 years old, corresponds to this person, and still need cash:
                    if (RothConversionAmount[ct] > 0.) and (Age[YearCt,PersonCt] >= RothConversionAge[ct] + 5) and \
                            (RothConversionPerson[ct] == PersonCt) and (RemainingCashNeeded > 0.):
                        # and to avoid a scenerio where conversion is greater than balance (e.g. if ROI is negative), use
                        # the min of conversion vs bal
                        MinVal = min(RothConversionAmount[ct],RothBal)
                        # if MinVal covers entire remaining cash needed:
                        if MinVal > RemainingCashNeeded:
                            TotalCash[YearCt] += RemainingCashNeeded
                            RothConversionAmount[ct] -= RemainingCashNeeded
                            RothBal -= RemainingCashNeeded
                            # Then recompute cash needed
                            RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]
                        else:
                            # then just withdraw MinVal
                            TotalCash[YearCt] += MinVal
                            RothBal -= MinVal
                            RothConversionAmount[ct] -= MinVal
                            # Then recompute cash needed
                            RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

    # Repack any modified immutable dictionary items (mutable items such as arrays/lists will already be modified)
    Roth['Bal'][YearCt,PersonCt] = RothBal
    Roth['Contributions'][YearCt,PersonCt] = RothContributions

