# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TaxRateInfoInput.py

import numpy as np

# NOTE: QualifyingWidow(er) rates and brackets are identical to MarriedFilingJointly, so can just use those in
# ComputeTaxes method

def TaxRateInfoInput():

    # 2022 income tax rates (also applies for nonqualified dividends)
    Rates = np.array([0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37], dtype=float)

    # 2022 income tax brackets
    # Single
    SingleIncomeBracketMins = np.array([0,10275,41775,89075,170050,215950,539900], dtype=float)
    # MarriedFilingJointly
    MarriedFilingJointlyIncomeBracketMins = np.array([0,20550,83550,178150,340100,431900,647850], dtype=float)
    # MarriedFilingSeparately
    MarriedFilingSeparatelyIncomeBracketMins = np.array([0,10275,41775,89075,170050,215950,323925], dtype=float)
    # HeadOfHousehold
    HeadOfHouseholdIncomeBracketMins = np.array([0,14650,55900,89050,170050,215950,539900], dtype=float)

    # 2022 standard deductions
    SingleStandardDeduction = 12950.
    MarriedFilingJointlyStandardDeduction = 25900.
    MarriedFilingSeparatelyStandardDeduction = 12950.
    HeadOfHouseholdStandardDeduction = 19400.

    # 2022 long term cap gain rates (also applies for qualified dividends)
    CapGainsRatesLT = np.array([0.0, 0.15, 0.2], dtype=float)

    # 2022 long term cap gain tax brackets
    # Single
    SingleIncomeBracketLTcapGainsMins = np.array([0,41675,459750], dtype=float)
    # MarriedFilingJointly
    MarriedFilingJointlyIncomeBracketLTcapGainsMins = np.array([0,83350,517200], dtype=float)
    # MarriedFilingSeparately
    MarriedFilingSeparatelyIncomeBracketLTcapGainsMins = np.array([0,41675,258600], dtype=float)
    # HeadOfHousehold
    HeadOfHouseholdIncomeBracketLTcapGainsMins = np.array([0,55800,488500], dtype=float)


    TaxRateInfo = {'Rates': Rates,
                   'SingleIncomeBracketMins': SingleIncomeBracketMins,
                   'MarriedFilingJointlyIncomeBracketMins': MarriedFilingJointlyIncomeBracketMins,
                   'MarriedFilingSeparatelyIncomeBracketMins': MarriedFilingSeparatelyIncomeBracketMins,
                   'HeadOfHouseholdIncomeBracketMins': HeadOfHouseholdIncomeBracketMins,
                   'SingleStandardDeduction': SingleStandardDeduction,
                   'MarriedFilingJointlyStandardDeduction': MarriedFilingJointlyStandardDeduction,
                   'MarriedFilingSeparatelyStandardDeduction': MarriedFilingSeparatelyStandardDeduction,
                   'HeadOfHouseholdStandardDeduction': HeadOfHouseholdStandardDeduction,
                   'CapGainsRatesLT': CapGainsRatesLT,
                   'SingleIncomeBracketLTcapGainsMins': SingleIncomeBracketLTcapGainsMins,
                   'MarriedFilingJointlyIncomeBracketLTcapGainsMins': MarriedFilingJointlyIncomeBracketLTcapGainsMins,
                   'MarriedFilingSeparatelyIncomeBracketLTcapGainsMins': MarriedFilingSeparatelyIncomeBracketLTcapGainsMins,
                   'HeadOfHouseholdIncomeBracketLTcapGainsMins': HeadOfHouseholdIncomeBracketLTcapGainsMins}

    return TaxRateInfo
