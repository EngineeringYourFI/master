# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFrom457b.py

def WithdrawFrom457b(Income,PreTax457b,TotalCash, YearCt,PersonCt):

    # Unpack needed dictionary items - for easier access
    Bal = PreTax457b['Bal'][YearCt,PersonCt]
    IncTotStd = Income['TotalStandard'][YearCt]
    IncTot = Income['Total'][YearCt]
    IncMaxStd = Income['MaxStandard'][YearCt]

    # withdraw 457b if room:
    RemainingStandardIncomeRoom = IncMaxStd - IncTotStd
    if RemainingStandardIncomeRoom > 0. and Bal > 0.:
        # if enough funds in 457b to cover the entire remainder
        if Bal >= RemainingStandardIncomeRoom:
            Bal -= RemainingStandardIncomeRoom
            TotalCash[YearCt] += RemainingStandardIncomeRoom
            IncTotStd += RemainingStandardIncomeRoom
            IncTot += RemainingStandardIncomeRoom
        else: # withdraw remaining balance
            TotalCash[YearCt] += Bal
            IncTotStd += Bal
            IncTot += Bal
            Bal = 0.

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    PreTax457b['Bal'][YearCt,PersonCt] = Bal
    Income['TotalStandard'][YearCt] = IncTotStd
    Income['Total'][YearCt] = IncTot