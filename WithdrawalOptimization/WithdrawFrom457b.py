# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFrom457b.py

def WithdrawFrom457b(MaxStandardIncome,TotalStandardIncome,PreTax457b,TotalCash,TotalIncome):

    # withdraw 457b if room:
    RemainingStandardIncomeRoom = MaxStandardIncome - TotalStandardIncome
    if RemainingStandardIncomeRoom > 0. and PreTax457b > 0.:
        # if enough funds in 457b to cover the entire remainder
        if PreTax457b >= RemainingStandardIncomeRoom:
            PreTax457b -= RemainingStandardIncomeRoom
            TotalCash += RemainingStandardIncomeRoom
            TotalStandardIncome += RemainingStandardIncomeRoom
            TotalIncome += RemainingStandardIncomeRoom
        else: # withdraw remaining balance
            TotalCash += PreTax457b
            TotalStandardIncome += PreTax457b
            TotalIncome += PreTax457b
            PreTax457b = 0.

    return PreTax457b, TotalCash, TotalStandardIncome, TotalIncome
