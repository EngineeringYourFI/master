# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# ComputeRIB.py
import sys
import numpy as np

from AugmentWithFutureEarnings import *
from DetermineIfMinCreditsObtained import *
from DetermineTaxableIncome import *
from AdjustIncomeForInflation import *
from ComputeAIME import *
from ComputePIA import *
from AdjustPIAbyCOLA import *
from ComputeFRA import *
from EarlyLateAdjust import *

# Compute RIB (social security income, known officially as "Retirement Insurance Benefits")

def ComputeRIB(Income,StartingAge,BirthDate,Spouse):

    # Unpack needed dicts
    BirthYear = BirthDate['Year']

    # Augment Income array if future earnings expected
    AugmentWithFutureEarnings(Income,BirthDate,StartingAge) #Income =

    # Determine if the minimum 40 credits have been achieved, and thus eligible for SocSec
    MinCreditsObtained, TotalCredits = DetermineIfMinCreditsObtained(Income)
    if MinCreditsObtained == False:
        print('Sorry, not enough work credits earned for Social Security Income: you only have ' +
              '{:d}'.format(TotalCredits)+' of the 40 minimum needed.')
        sys.exit()

    # Determine if any years are over the maximum taxable income for social security taxes, and bring down the income to
    # that max if needed
    Income['TaxableIncome'] = DetermineTaxableIncome(Income)

    # Adjust this taxable income for inflation
    Income['AdjustedTaxableIncome'] = AdjustIncomeForInflation(Income,BirthYear)

    # Compute Average Indexed Monthly Earnings (AIME) - using highest 35 years of indexed (inflation-adjusted) earnings
    Income['AIME'] = ComputeAIME(Income)

    # Compute Primary Insurance Amount (PIA)
    PIA = ComputePIA(Income,BirthYear)

    # Adjust PIA with any relevant Cost of Living Adjustments (COLA)
    PIA = AdjustPIAbyCOLA(PIA,BirthYear)

    # Compute Full retirement age (FRA)
    FRA = ComputeFRA(BirthYear)

    # Early / late retirement adjustment (if taking RIB before or after FRA)
    RIBmonthly = EarlyLateAdjust(FRA,PIA,StartingAge)

    # Truncate to next lowest dollar
    RIBmonthly = np.floor(RIBmonthly)

    RIB = {'MonthlyIncome': RIBmonthly,
           'YearlyIncome': RIBmonthly*12.}

    return RIB
