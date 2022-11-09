# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRothTraditionalWithPenalty.py

import numpy as np

def WithdrawFromRothTraditionalWithPenalty(TotalCashNeeded,Roth,TotalCash,Age,Penalties):

    # Withdrawal = CashNeeded + Penalty
    # Penalty = 0.1*Withdrawal
    # Withdrawal = CashNeeded + 0.1*Withdrawal
    #            = CashNeeded / 0.9
    # Penalty = 0.1 * CashNeeded / 0.9

    RemainingCashNeeded = TotalCashNeeded - TotalCash
    if RemainingCashNeeded > 0 and Age < 60.:
        # if Roth balance is >= (cash needed)/0.9 (i.e. enough to cover cash needed and 10% penalty on full withdrawal)
        if Roth >= np.round(RemainingCashNeeded/0.9,2):
            TotalCash += RemainingCashNeeded
            Roth -= np.round(RemainingCashNeeded/0.9,2)
            Penalties += np.round(0.1*RemainingCashNeeded/0.9,2)
        else: # withdraw the entire balance
            Penalties += 0.1*Roth
            TotalCash += 0.9*Roth
            Roth = 0.

    return Roth, TotalCash, Penalties
