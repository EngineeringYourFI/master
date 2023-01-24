# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFrom457bDelta.py

def WithdrawFrom457bDelta(PreTax457b,Income,TotalCash,Step,YearCt,PersonCt,Execute):

    # Unpack needed dictionary items - for easier access
    Bal = PreTax457b['Bal'][YearCt,PersonCt]
    if Execute:
        IncTot = Income['Total'][YearCt]
        IncTotStd = Income['TotalStandard'][YearCt]

    if Bal > Step:
        Withdrawal = Step
    else:
        Withdrawal = Bal

    if Execute:

        # withdraw 457b if non-empty
        if Bal > 0.:
            # if enough funds in 457b to cover the entire remainder
            if Bal >= Step:
                TotalCash[YearCt] += Step
                IncTotStd += Step
                IncTot += Step
                Bal -= Step
            else: # withdraw remaining balance
                TotalCash[YearCt] += Bal
                IncTotStd += Bal
                IncTot += Bal
                Bal = 0.

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    if Execute:
        PreTax457b['Bal'][YearCt,PersonCt] = Bal
        Income['TotalStandard'][YearCt] = IncTotStd
        Income['Total'][YearCt] = IncTot

    return Withdrawal