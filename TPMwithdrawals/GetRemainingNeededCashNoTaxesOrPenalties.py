# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# GetRemainingNeededCashNoTaxesOrPenalties.py

import numpy as np
from WithdrawFromRoth import WithdrawFromRoth

# Get cash with no taxes or penalties to meet TotalCashNeeded, if needed

def GetRemainingNeededCashNoTaxesOrPenalties(TotalCash,Roth,CashCushion, TotalCashNeeded,Age,YearCt):

    # Unpack needed dictionary items - for easier access
    RothTotal = Roth['Total'][YearCt]
    RothBal = Roth['Bal'][YearCt,:]
    NumPeople = len(Roth['Bal'][YearCt,:])

    # if TotalCash less than TotalCashNeeded, next need to pull from Roth
    if TotalCash[YearCt] < TotalCashNeeded:
        # loop over people
        for ct in range(NumPeople):
            WithdrawFromRoth(Roth,TotalCash, TotalCashNeeded,Age,YearCt,ct)
        RothTotal = np.sum(RothBal) # RothBal connected to Roth['Bal'][YearCt,:], modified in WithdrawFromRoth

    # if TotalCash less than TotalCashNeeded, next need to pull from Cash Cushion
    if TotalCash[YearCt] < TotalCashNeeded:
        RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]
        # if cash cushion covers expenses:
        if CashCushion[YearCt] > RemainingCashNeeded:
            TotalCash[YearCt] += RemainingCashNeeded
            CashCushion[YearCt] -= RemainingCashNeeded
        else:
            # then just withdraw remaining balance
            TotalCash[YearCt] += CashCushion[YearCt]
            CashCushion[YearCt] = 0.

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    Roth['Total'][YearCt] = RothTotal
