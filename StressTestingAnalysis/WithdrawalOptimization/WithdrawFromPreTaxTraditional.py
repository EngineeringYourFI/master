# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPreTaxTraditional.py

def WithdrawFromPreTaxTraditional(TotalCashNeeded,TotalStandardIncome,PreTax,TotalCash,TotalIncome,Age):

    RemainingCashNeeded = TotalCashNeeded - TotalCash
    if RemainingCashNeeded > 0. and Age >= 60. and PreTax > 0.:
        # if enough funds in PreTaxTemp to cover the entire remainder
        if PreTax > RemainingCashNeeded:
            PreTax -= RemainingCashNeeded
            TotalCash += RemainingCashNeeded
            TotalStandardIncome += RemainingCashNeeded
            TotalIncome += RemainingCashNeeded
        else: # withdraw remaining balance
            TotalCash += PreTax
            TotalStandardIncome += PreTax
            TotalIncome += PreTax
            PreTax = 0.

    return PreTax, TotalCash, TotalStandardIncome, TotalIncome

