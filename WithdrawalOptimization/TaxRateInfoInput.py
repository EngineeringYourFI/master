# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TaxRateInfoInput.py

import numpy as np

# NOTE: QualifyingWidow(er) rates and brackets are identical to MarriedFilingJointly, so can just use those in
# ComputeTaxes method

def TaxRateInfoInput():

    # 2023 income tax rates (also applies for nonqualified dividends)
    Rates = np.array([0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37], dtype=float)

    # 2023 income tax brackets
    # Single
    SingleIncomeBracketMins = np.array([0,11000,44725,95375,182100,231250,578125], dtype=float)
    # MarriedFilingJointly
    MarriedFilingJointlyIncomeBracketMins = np.array([0,22000,89450,190750,364200,462500,693750], dtype=float)
    # MarriedFilingSeparately
    MarriedFilingSeparatelyIncomeBracketMins = np.array([0,11000,44725,95375,182100,231250,346875], dtype=float)
    # HeadOfHousehold
    HeadOfHouseholdIncomeBracketMins = np.array([0,15700,59850,95350,182100,231250,578100], dtype=float)

    # 2023 standard deductions
    SingleStandardDeduction = 13850.
    MarriedFilingJointlyStandardDeduction = 27700.
    MarriedFilingSeparatelyStandardDeduction = 13850.
    HeadOfHouseholdStandardDeduction = 20800.

    # 2023 long term cap gain rates (also applies for qualified dividends)
    CapGainsRatesLT = np.array([0.0, 0.15, 0.2], dtype=float)

    # 2023 long term cap gain tax brackets
    # Single
    SingleIncomeBracketLTcapGainsMins = np.array([0,44625,492300], dtype=float)
    # MarriedFilingJointly
    MarriedFilingJointlyIncomeBracketLTcapGainsMins = np.array([0,89250,553850], dtype=float)
    # MarriedFilingSeparately
    MarriedFilingSeparatelyIncomeBracketLTcapGainsMins = np.array([0,44625,276900], dtype=float)
    # HeadOfHousehold
    HeadOfHouseholdIncomeBracketLTcapGainsMins = np.array([0,59750,523050], dtype=float)


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
