# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFrom457bTraditional.py

def WithdrawFrom457bTraditional(TotalCashNeeded,TotalStandardIncome,PreTax457b,TotalCash,TotalIncome):

    # if still not enough cash, withdraw from 457b:
    RemainingCashNeeded = TotalCashNeeded - TotalCash
    if RemainingCashNeeded > 0 and PreTax457b > 0.:
        # if enough funds in 457b to cover the entire remainder
        if PreTax457b >= RemainingCashNeeded:
            PreTax457b -= RemainingCashNeeded
            TotalCash += RemainingCashNeeded
            TotalStandardIncome += RemainingCashNeeded
            TotalIncome += RemainingCashNeeded
        else: # withdraw remaining balance
            TotalCash += PreTax457b
            TotalStandardIncome += PreTax457b
            TotalIncome += PreTax457b
            PreTax457b = 0.

    return PreTax457b, TotalCash, TotalStandardIncome, TotalIncome