# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPreTaxTraditionalWithPenalty.py

import numpy as np

def WithdrawFromPreTaxTraditionalWithPenalty(TotalCashNeeded,TotalStandardIncome,PreTax,TotalCash,TotalIncome,Age,
                                             Penalties):

    RemainingCashNeeded = TotalCashNeeded - TotalCash
    if RemainingCashNeeded > 0. and Age < 60. and PreTax > 0.:
        if PreTax >= RemainingCashNeeded:
            TotalCash += RemainingCashNeeded
            TotalStandardIncome += RemainingCashNeeded
            TotalIncome += RemainingCashNeeded
            PreTax -= RemainingCashNeeded
            Penalties += np.round(0.1*RemainingCashNeeded,2)
        else: # withdraw remaining balance
            TotalCash += PreTax
            TotalStandardIncome += PreTax
            TotalIncome += PreTax
            Penalties += 0.1*PreTax
            PreTax = 0.

    return PreTax, TotalCash, TotalStandardIncome, TotalIncome, Penalties

