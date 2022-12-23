# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPreTax.py

import numpy as np

def WithdrawFromPreTax(Income,PreTax,TotalCash,Roth, Age,YearCt,PersonCt):

    # Unpack needed dictionary items - for easier access
    PreTaxBal = PreTax['Bal'][YearCt,PersonCt]
    IncTotStd = Income['TotalStandard'][YearCt]
    IncTot = Income['Total'][YearCt]
    IncMaxStd = Income['MaxStandard'][YearCt]
    RothBal = Roth['Bal'][YearCt,PersonCt]
    RothRollAmount = Roth['RolloverAmount']
    RothRollAge = Roth['RolloverAge']
    RothRollPerson = Roth['RolloverPerson']

    # withdraw PreTax if room, rollover to Roth if not 60 yet
    RemainingStandardIncomeRoom = IncMaxStd - IncTotStd
    if RemainingStandardIncomeRoom > 0. and PreTaxBal > 0.:
        # if enough funds in PreTax to cover the entire remainder
        if PreTaxBal > RemainingStandardIncomeRoom:
            PreTaxBal -= RemainingStandardIncomeRoom
            if Age[YearCt,PersonCt] < 60.: # Rollover to roth
                RothBal += RemainingStandardIncomeRoom
                # capture rollover amount with age, to ensure not spent in less than 5 years
                RothRollAmount = np.append(RothRollAmount,RemainingStandardIncomeRoom)
                RothRollAge = np.append(RothRollAge,Age[YearCt,PersonCt])
                RothRollPerson = np.append(RothRollPerson,PersonCt)
            else: # use the cash - no penalties
                TotalCash[YearCt] += RemainingStandardIncomeRoom

            IncTotStd += RemainingStandardIncomeRoom
            IncTot += RemainingStandardIncomeRoom
        else: # withdraw remaining balance
            if Age[YearCt,PersonCt] < 60.: # Rollover to roth
                RothBal += PreTaxBal
                # capture rollover amount with age, to ensure not spent in less than 5 years
                RothRollAmount = np.append(RothRollAmount,PreTaxBal)
                RothRollAge = np.append(RothRollAge,Age[YearCt,PersonCt])
                RothRollPerson = np.append(RothRollPerson,PersonCt)
            else: # use the cash - no penalties
                TotalCash[YearCt] += PreTaxBal

            IncTotStd += PreTaxBal
            IncTot += PreTaxBal
            PreTaxBal = 0.

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    PreTax['Bal'][YearCt,PersonCt] = PreTaxBal
    Income['TotalStandard'][YearCt] = IncTotStd
    Income['Total'][YearCt] = IncTot
    Roth['Bal'][YearCt,PersonCt] = RothBal
    # unfortunately have to repack RothRoll arrays, because they are numpy arrays, and the np.append operation creates a
    # new array instead of appending in place (unlike a python list, which does - consider switching to Python lists)
    Roth['RolloverAmount'] = RothRollAmount
    Roth['RolloverAge'] = RothRollAge
    Roth['RolloverPerson'] = RothRollPerson

