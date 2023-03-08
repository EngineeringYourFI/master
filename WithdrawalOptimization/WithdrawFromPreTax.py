# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPreTax.py

import numpy as np

def WithdrawFromPreTax(Income,PreTax,TotalCash,Roth, Age,YearCt,PersonCt):

    # Unpack needed dictionary items - for easier access
    PreTaxBal = PreTax['Bal'][YearCt,PersonCt]
    Withdrawn = PreTax['Withdrawn'][YearCt,PersonCt] # should always be zero, I believe, but just in case
    IncTotStd = Income['TotalStandard'][YearCt]
    IncTot = Income['Total'][YearCt]
    IncMaxStd = Income['MaxStandard'][YearCt]
    RothBal = Roth['Bal'][YearCt,PersonCt]
    RothConversionAmount = Roth['ConversionAmount']
    RothConversionAge = Roth['ConversionAge']
    RothConversionPerson = Roth['ConversionPerson']

    # withdraw PreTax if room, conversion to Roth if not 60 yet
    RemainingStandardIncomeRoom = IncMaxStd - IncTotStd
    if RemainingStandardIncomeRoom > 0. and PreTaxBal > 0.:
        # if enough funds in PreTax to cover the entire remainder
        if PreTaxBal > RemainingStandardIncomeRoom:
            PreTaxBal -= RemainingStandardIncomeRoom
            if Age[YearCt,PersonCt] < 60.: # Conversion to roth
                RothBal += RemainingStandardIncomeRoom
                # capture conversion amount with age, to ensure not spent in less than 5 years
                RothConversionAmount = np.append(RothConversionAmount,RemainingStandardIncomeRoom)
                RothConversionAge = np.append(RothConversionAge,Age[YearCt,PersonCt])
                RothConversionPerson = np.append(RothConversionPerson,PersonCt)
            else: # use the cash - no penalties
                TotalCash[YearCt] += RemainingStandardIncomeRoom

            Withdrawn += RemainingStandardIncomeRoom
            IncTotStd += RemainingStandardIncomeRoom
            IncTot += RemainingStandardIncomeRoom
        else: # withdraw remaining balance
            if Age[YearCt,PersonCt] < 60.: # Conversion to roth
                RothBal += PreTaxBal
                # capture conversion amount with age, to ensure not spent in less than 5 years
                RothConversionAmount = np.append(RothConversionAmount,PreTaxBal)
                RothConversionAge = np.append(RothConversionAge,Age[YearCt,PersonCt])
                RothConversionPerson = np.append(RothConversionPerson,PersonCt)
            else: # use the cash - no penalties
                TotalCash[YearCt] += PreTaxBal

            Withdrawn += PreTaxBal
            IncTotStd += PreTaxBal
            IncTot += PreTaxBal
            PreTaxBal = 0.

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    PreTax['Bal'][YearCt,PersonCt] = PreTaxBal
    PreTax['Withdrawn'][YearCt,PersonCt] = Withdrawn
    Income['TotalStandard'][YearCt] = IncTotStd
    Income['Total'][YearCt] = IncTot
    Roth['Bal'][YearCt,PersonCt] = RothBal
    # unfortunately have to repack RothConversion arrays, because they are numpy arrays, and the np.append operation creates a
    # new array instead of appending in place (unlike a python list, which does - consider switching to Python lists)
    Roth['ConversionAmount'] = RothConversionAmount
    Roth['ConversionAge'] = RothConversionAge
    Roth['ConversionPerson'] = RothConversionPerson
