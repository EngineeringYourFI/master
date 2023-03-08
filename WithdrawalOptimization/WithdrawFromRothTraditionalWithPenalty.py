# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRothTraditionalWithPenalty.py

import numpy as np

def WithdrawFromRothTraditionalWithPenalty(TotalCashNeeded,Roth,TotalCash,TotalStandardIncome,TotalIncome,Age,Penalties):

    RemainingCashNeeded = TotalCashNeeded - TotalCash
    if RemainingCashNeeded > 0 and Age < 60.:
        if Roth >= RemainingCashNeeded:
            TotalCash += RemainingCashNeeded
            TotalStandardIncome += RemainingCashNeeded
            TotalIncome += RemainingCashNeeded
            Roth -= RemainingCashNeeded
            Penalties += np.round(0.1*RemainingCashNeeded,2)
        else: # withdraw the entire balance
            TotalCash += Roth
            TotalStandardIncome += Roth
            TotalIncome += Roth
            Penalties += 0.1*Roth
            Roth = 0.

    return Roth, TotalCash, TotalStandardIncome, TotalIncome, Penalties
