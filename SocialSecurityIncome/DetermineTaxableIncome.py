# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# DetermineTaxableIncome.py

import numpy as np

# Determine if any years are over the maximum taxable income for social security taxes, and bring down the income to
# that max if needed

# https://www.ssa.gov/oact/cola/cbb.html
# "This limit changes each year with changes in the national average wage index. We call this annual limit the
# contribution and benefit base. This amount is also commonly referred to as the taxable maximum. For earnings in 2023,
# this base is $160,200."

def DetermineTaxableIncome(Income):

    # Unpack needed dicts
    IncomeYears = Income['IncomeYears']
    IncomeArray = Income['IncomeArray']

    # Contribution and benefit bases, 1937-2023
    # Table provided at https://www.ssa.gov/oact/cola/cbb.html
    YearsArray = list(range(1937, 2026))
    CBB = np.zeros(len(YearsArray))
    CBB[0:14] = 3000.
    CBB[14:18] = 3600.
    CBB[18:22] = 4200.
    CBB[22:29] = 4800.
    CBB[29:31] = 6600.
    CBB[31:35] = 7800.
    CBB[35:] = [9000., 10800., 13200., 14100., 15300., 16500., 17700., 22900., 25900., 29700., 32400., 35700., 37800.,
                  39600., 42000., 43800., 45000., 48000., 51300., 53400., 55500., 57600., 60600., 61200., 62700.,
                  65400., 68400., 72600., 76200., 80400., 84900., 87000., 87900., 90000., 94200., 97500., 102000.,
                  106800., 106800., 106800., 110100., 113700., 117000., 118500., 118500., 127200., 128400., 132900.,
                  137700., 142800., 147000., 160200., 168600., 176100.]

    # Initialize
    TaxableIncome = np.zeros(len(IncomeArray))

    # Loop over income years, compute taxable income for each
    for ct in range(len(IncomeArray)):

        # Determine Contribution and Benefit Base (CBB) for this year
        Year = IncomeYears[ct]
        # If year is within YearsArray, grab corresponding index:
        if Year <= YearsArray[-1]:
            ind = YearsArray.index(Year)
        else: # use the credit cost for the final year listed
            ind = len(YearsArray) - 1
        CBBthisYear = CBB[ind]

        if IncomeArray[ct] > CBBthisYear:
            TaxableIncome[ct] = CBBthisYear
        else:
            TaxableIncome[ct] = IncomeArray[ct]

    return TaxableIncome
