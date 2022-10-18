# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeTaxes.py

import numpy as np
import copy

# Compute total taxes due from both standard income and long term cap gains / qualified dividends
def ComputeTaxes(TaxRateInfo,FilingStatus,TotalStandardIncome,TotalLTcapGainsIncome):

    # Use appropriate standard deduction, tax brackets
    if FilingStatus=='Single':
        StandardDeduction = TaxRateInfo['SingleStandardDeduction']
        # tax bracket mins are mutable objects (numpy arrays) within TaxRateInfo, so must make copies to avoid changing
        # accidentally (which would change them outside this function)
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['SingleIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['SingleIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='MarriedFilingJointly' or FilingStatus=='QualifyingWidow(er)':
        StandardDeduction = TaxRateInfo['MarriedFilingJointlyStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['MarriedFilingJointlyIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='MarriedFilingSeparately':
        StandardDeduction = TaxRateInfo['MarriedFilingSeparatelyStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['MarriedFilingSeparatelyIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['MarriedFilingSeparatelyIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='HeadOfHousehold':
        StandardDeduction = TaxRateInfo['HeadOfHouseholdStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['HeadOfHouseholdIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['HeadOfHouseholdIncomeBracketLTcapGainsMins'])
    else:
        print('Filing Status not recognized. Exiting.')
        sys.exit()

    # Remove standard deduction from standard income to get taxable standard income
    # (and from LT cap gains if needed - though hopefully it's never wasted that way)
    if TotalStandardIncome >= StandardDeduction:
        TaxableStandardIncome = TotalStandardIncome - StandardDeduction
        TaxableLTcapGains = TotalLTcapGainsIncome
    elif (TotalStandardIncome + TotalLTcapGainsIncome) >= StandardDeduction:
        TaxableStandardIncome = 0
        TaxableLTcapGains = TotalLTcapGainsIncome - (StandardDeduction - TotalStandardIncome)
    else:
        TaxableStandardIncome = 0
        TaxableLTcapGains = 0

    # Compute taxes on standard income
    # np.searchsorted returns the index of the Min value beyond TaxableStandardIncome (and +1 beyond the last index if
    # greater than the last value) i.e. the index of the max value of the top bracket
    ind = np.searchsorted(IncomeBracketMins,TaxableStandardIncome)
    TaxesOnStandardIncome = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            TaxesOnStandardIncome += TaxRateInfo['Rates'][ct]*(IncomeBracketMins[ct+1]-IncomeBracketMins[ct])
        else: # top bracket
            TaxesOnStandardIncome += TaxRateInfo['Rates'][ct]*(TaxableStandardIncome - IncomeBracketMins[ct])

    # Compute taxes on LT Cap Gains
    ind = np.searchsorted(IncomeBracketLTcapGainsMins,TaxableLTcapGains)
    TaxesOnLTcapGains = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            TaxesOnLTcapGains += TaxRateInfo['CapGainsRatesLT'][ct]*(IncomeBracketLTcapGainsMins[ct+1] -
                                                                     IncomeBracketLTcapGainsMins[ct])
        else: # top bracket
            TaxesOnLTcapGains += TaxRateInfo['CapGainsRatesLT'][ct]*(TaxableLTcapGains -
                                                                     IncomeBracketLTcapGainsMins[ct])

    return TaxesOnStandardIncome + TaxesOnLTcapGains
