# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# SocialSecurityIncomeTemplate.py

import numpy as np
import copy
import os
import time

from ComputeRIB import *

# Compute Social Security Income, known officially as "Retirement Insurance Benefits" (RIB)
# For current or future years

#############################################################################################################
# User Inputs

# Case A from https://www.ssa.gov/oact/ProgData/retirebenefit1.html and https://www.ssa.gov/oact/ProgData/retirebenefit2.html

# Income for each year of working
# Note: must include all earnings through previous year, so that this tool knows the current year (provide zeros at the
# end if needed)
# IncomeYears = np.arange(1983,2023,1)
# IncomeArray = np.array([14249, 15134, 15828, 16349, 17446, 18362, 19149, 20095, 20908, 22053, 22311, 22980, 23974,
#                         25223, 26776, 28262, 29927, 31677, 32529, 32954, 33860, 35539, 36948, 38760, 40639, 41695,
#                         41187, 42283, 43735, 45231, 45941, 47709, 49511, 50214, 52096, 54138, 56326, 58082, 63425,
#                         65712], dtype=float)
# # Expected income (if any) after end of IncomeArray through the calendar year prior to starting RIB
# # If IncomeArray includes year before starting RIB, this input is not used.
# # If no expected income in that interval, set to 0.
# ExpectedFutureIncome = 0.
# #  How many years into the future you expect to earn that income:
# ExpectedFutureIncomeNumYears = 0.
# Note: if income history + ExpectedFutureIncomeNumYears goes beyond StartingAge below, ignore those expected earnings
# # Your age when you start collecting benefits - earliest is age 62 and one month, latest is age 70
# StartingAge = 62.
# # Year and Month you were born
# BirthYear = 1961
# BirthMonth = 1


# Case B from https://www.ssa.gov/oact/ProgData/retirebenefit1.html and https://www.ssa.gov/oact/ProgData/retirebenefit2.html
# IncomeYears = np.arange(1983,2023,1)
# IncomeArray = np.array([35700, 37800, 39600, 42000, 43800, 45000, 48000, 51300, 53400, 55500, 57600, 60600, 61200,
#                         62700, 65400, 68400, 72600, 76200, 80400, 84900, 87000, 87900, 90000, 94200, 97500, 102000,
#                         106800, 106800, 106800, 110100, 113700, 117000, 118500, 118500, 127200, 128400, 132900, 137700,
#                         142800, 147000], dtype=float) #
# ExpectedFutureIncome = 0.
# ExpectedFutureIncomeNumYears = 0.
# StartingAge = 66. + 6/12
# BirthYear = 1957
# BirthMonth = 1


# Case B mod - born 10 years later, earnings start 10 years later
IncomeYears = np.arange(1993,2023,1) # from first year of earnings through last year's earnings (2022 here)
IncomeArray = np.array([57600, 60600, 61200,
                        62700, 65400, 68400, 72600, 76200, 80400, 84900, 87000, 87900, 90000, 94200, 97500, 102000,
                        106800, 106800, 106800, 110100, 113700, 117000, 118500, 118500, 127200, 128400, 132900, 137700,
                        142800, 147000], dtype=float)
ExpectedFutureIncome = 150000.
ExpectedFutureIncomeNumYears = 11
StartingAge = 67. + 0/12
BirthYear = 1967
BirthMonth = 1 # 1 = Jan, 6 = June, 7 = July, 12 = Dec - so BirthYearPlusMonth = BirthYear + (BirthMonth-1)/12

# Spouse
SpouseFlag = False
# Your spouse's age relative to yours: 0 = same age, +1 = one year older than you, -1 = one year younger, etc.
SpouseRelativeAge = 0.

# From https://www.ssa.gov/oact/ProgData/nra.html:
# "1. Persons born on January 1 of any year should refer to the normal retirement age for the previous year."
# TODO: implement this logic
BornJan1 = False

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'
# Output to screen instead of file:
OutputToScreen = True

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Assemble dicts
Income = {'IncomeYears': IncomeYears,
          'IncomeArray': IncomeArray,
          'ExpectedFutureIncome': ExpectedFutureIncome,
          'ExpectedFutureIncomeNumYears': ExpectedFutureIncomeNumYears}
BirthDate = {'Year': BirthYear,
             'Month': BirthMonth} 
Spouse = {'Flag': SpouseFlag,
          'SpouseRelativeAge': SpouseRelativeAge}

#############################################################################################################

# Compute RIB (social security income, known officially as "Retirement Insurance Benefits")

RIB = ComputeRIB(Income,StartingAge,BirthDate,Spouse)

print('Social Security Monthly Income: $'+'{:.2f}'.format(np.round(RIB['MonthlyIncome'],2)))
print('Social Security Yearly Income: $'+'{:.2f}'.format(np.round(RIB['YearlyIncome'],2)))

if SpouseFlag:
    print('Social Security Monthly Income: $'+'{:.2f}'.format(np.round(RIB['SpouseMonthlyIncome'],2)))
    print('Social Security Yearly Income: $'+'{:.2f}'.format(np.round(RIB['SpouseYearlyIncome'],2)))

