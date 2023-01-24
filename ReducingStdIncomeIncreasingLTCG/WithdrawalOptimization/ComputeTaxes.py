# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeTaxes.py

import numpy as np
import copy
import sys

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

    # Also create local copies of the rate arrays, in case they are modified (otherwise the arrays will be modified
    # inside the mutable TaxRateInfo dictionary, affecting subsequent runs of the ComputeTaxes method).
    Rates = copy.deepcopy(TaxRateInfo['Rates'])
    CapGainsRatesLT = copy.deepcopy(TaxRateInfo['CapGainsRatesLT'])

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

    TaxableTotalIncome = TaxableStandardIncome + TaxableLTcapGains

    # Compute taxes on standard income
    # np.searchsorted returns the index of the Min value beyond TaxableStandardIncome (and +1 beyond the last index if
    # greater than the last value) i.e. the index of the max value of the top bracket
    StdIncTopTaxBracket = np.searchsorted(IncomeBracketMins,TaxableStandardIncome)
    TaxesOnStandardIncome = 0 # init
    for ct in range(0,StdIncTopTaxBracket):
        # if it's before the top bracket
        if ct < (StdIncTopTaxBracket-1):
            TaxesOnStandardIncome += Rates[ct]*(IncomeBracketMins[ct+1]-IncomeBracketMins[ct])
        else: # top bracket
            TaxesOnStandardIncome += Rates[ct]*(TaxableStandardIncome - IncomeBracketMins[ct])
            if ct < (len(IncomeBracketMins)-1):
                StdIncTopTaxBracketSpaceRemaining = IncomeBracketMins[ct+1]-TaxableStandardIncome
            else:
                StdIncTopTaxBracketSpaceRemaining = np.nan
    # if TaxableStandardIncome = 0 and thus StdIncTopTaxBracket = 0, then it's not really "in" a bracket
    if StdIncTopTaxBracket == 0:
        StdIncTopTaxBracketSpaceRemaining = np.nan


    # Before computing LT cap gain taxes, first compute the top LT cap gain tax bracket with both standard income & LTCG
    # NOTE: assumes there are three LT cap gain brackets - if that changes in the future, must modify and/or generalize
    LTCGtopTaxBracket = np.searchsorted(IncomeBracketLTcapGainsMins,TaxableTotalIncome)
    # Lumping 0 and 1 together, since the first bracket is 0%:
    if LTCGtopTaxBracket == 0 or LTCGtopTaxBracket == 1:
        LTCGtopTaxBracketSpaceRemaining = IncomeBracketLTcapGainsMins[1] - TaxableTotalIncome
    elif LTCGtopTaxBracket == 2:
        LTCGtopTaxBracketSpaceRemaining = IncomeBracketLTcapGainsMins[2] - TaxableTotalIncome
    else:
        LTCGtopTaxBracketSpaceRemaining = np.nan

    # Compute taxes on LT Cap Gains
    # Standard income fills up brackets first, then LT cap gains
    # So, to account for that, appropriately modify the brackets for computing LT cap gains tax
    # NOTE: assumes there are three LT cap gain brackets - if that changes in the future, must modify and/or generalize
    # Find location of standard income in LT cap gain income brackets
    ind = np.searchsorted(IncomeBracketLTcapGainsMins,TaxableStandardIncome)
    # if ind == 0, TaxableStandardIncome is zero, and thus no need to modify the LT cap gain brackets
    if ind == 1:
        # Standard income still in 0% bracket
        # just move down 15% and 20% bracket mins
        IncomeBracketLTcapGainsMins[1] -= TaxableStandardIncome
        IncomeBracketLTcapGainsMins[2] -= TaxableStandardIncome
    if ind == 2:
        # Standard income above 0% bracket - so delete
        IncomeBracketLTcapGainsMins = np.delete(IncomeBracketLTcapGainsMins,0)
        CapGainsRatesLT = np.delete(CapGainsRatesLT,0)
        IncomeBracketLTcapGainsMins[0] = 0.
        IncomeBracketLTcapGainsMins[1] -= TaxableStandardIncome
    if ind == 3:
        # Standard income above 0% and 15% brackets - so delete both
        IncomeBracketLTcapGainsMins = np.delete(IncomeBracketLTcapGainsMins,[0,1])
        CapGainsRatesLT = np.delete(CapGainsRatesLT,[0,1])
        IncomeBracketLTcapGainsMins[0] = 0.

    # for ct in range(len(IncomeBracketLTcapGainsMins)):
    # Now with LT cap gain brackets modified to include effect of standard income, compute taxes on LT cap gains
    ind = np.searchsorted(IncomeBracketLTcapGainsMins,TaxableLTcapGains)
    TaxesOnLTcapGains = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            TaxesOnLTcapGains += CapGainsRatesLT[ct]*(IncomeBracketLTcapGainsMins[ct+1] -
                                                      IncomeBracketLTcapGainsMins[ct])
        else: # top bracket
            TaxesOnLTcapGains += CapGainsRatesLT[ct]*(TaxableLTcapGains - IncomeBracketLTcapGainsMins[ct])

    # Construct output dictionary
    Taxes = {'Total': TaxesOnStandardIncome + TaxesOnLTcapGains,
             'StdInc': TaxesOnStandardIncome,
             'LTCG': TaxesOnLTcapGains,
             'StdIncTopTaxBracket': StdIncTopTaxBracket,
             'StdIncTopTaxBracketSpaceRemaining': StdIncTopTaxBracketSpaceRemaining,
             'LTCGtopTaxBracket': LTCGtopTaxBracket,
             'LTCGtopTaxBracketSpaceRemaining': LTCGtopTaxBracketSpaceRemaining}

    return Taxes