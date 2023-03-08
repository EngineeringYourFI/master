# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TPMwithdrawalsTemplate.py

import numpy as np
import copy
import os
import time
from TaxRateInfoInput import *
from ProjFinalBalance import *
from ComputeOutputs import *
from WritePrimaryOutput import *
from AppendVerboseOutput import *

# Run Tax and Penalty Minimization (TPM) withdrawal method for a single year
# Will output the withdrawals you should make that year for each account type

#############################################################################################################
# User Inputs

# Bring in income tax bracket info, used for inputs
# Note: confirm values in TaxRateInfoInput.py match the current year tax brackets and rates
TaxRateInfo = TaxRateInfoInput()

# Your tax filing status
FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

# If 'Single', 'HeadOfHousehold', 'MarriedFilingSeparately', or 'QualifyingWidow(er)', only one person's assets used
if FilingStatus == 'Single' or FilingStatus == 'HeadOfHousehold' or FilingStatus == 'MarriedFilingSeparately' or \
        FilingStatus == 'QualifyingWidow(er)':

    # Pre-tax accounts (Traditional IRA, 401(k), 403(b)) initial value
    PreTaxIV = 400000.
    # Pre-tax 457(b) account initial value (can be withdrawn without 10% penalty before 59.5)
    PreTax457bIV = 100000.
    # Roth account initial value
    # Note: include HSA accounts in Roth category, since it also grows tax-free and can be used without paying taxes if
    # spent on medical expenses (easy enough as you get older)
    RothIV = 80000.
    # Original contributions made to Roth account
    RothContributions = 40000.
    # Roth conversions from pre-tax accounts - list format, earliest to latest - leave empty if no previous conversions
    RothConversionAmount = [] #[1000., 2000.] #
    # Age at each conversion (all conversions for a single year lumped together here)
    RothConversionAge = [] #[38,39] #
    # Social security income for this year - taxed different, so don't place in OtherIncomeSources
    SocialSecurityPayments = 0. #17000
    # Current Age
    CurrentAge = 40
    # If born 1950 or earlier, RMDs start at age 72
    # If born from 1951 to 1958, RMDs start at age 73
    # If born in 1959, a technical error in the legislation means it’s unknown if RMDs must start at age 73 or 75.
    # Hopefully new legislation will clarify, but until then, you should probably use age 73 to be safe.
    # If born 1960 or later, RMDs start at age 75
    RMDsThisYear = False

# If 'MarriedFilingJointly', two people's assets used
# Note: always put older person first for each list below
if FilingStatus == 'MarriedFilingJointly':

    # Pre-tax accounts (Traditional IRA, 401(k), 403(b)) initial value
    PreTaxIV = [200000.,200000.]
    # Pre-tax 457(b) account initial value (can be withdrawn without 10% penalty before 59.5)
    PreTax457bIV = [50000.,50000.]
    # Roth account initial value
    # Note: include HSA accounts in Roth category, since it also grows tax-free and can be used without paying taxes if
    # spent on medical expenses (easy enough as you get older)
    RothIV = [40000.,40000.]
    # Original contributions made to Roth account
    RothContributions = [20000.,20000.]
    # Roth conversions from pre-tax accounts - list format, earliest to latest - leave empty if no previous conversions
    RothConversionAmount = [] #[1000., 2000.] #
    # Age at each conversion (all conversions for a single year lumped together here)
    RothConversionAge = [] #[38, 36] #
    # Which person did the conversion from their pre-tax to Roth account: 'Person 1' or 'Person 2'
    RothConversionPerson = [] #['Person 1','Person 2'] #
    # Social security income for this year - taxed different, so don't place in OtherIncomeSources
    SocialSecurityPayments = [0.,0.] #[17000,17000]
    # Current Age for both people
    CurrentAge = [40,38]
    # If born 1950 or earlier, RMDs start at age 72
    # If born from 1951 to 1958, RMDs start at age 73
    # If born in 1959, a technical error in the legislation means it’s unknown if RMDs must start at age 73 or 75.
    # Hopefully new legislation will clarify, but until then, you should probably use age 73 to be safe.
    # If born 1960 or later, RMDs start at age 75
    RMDsThisYear = [False,False]


# Every lot in taxable account
PostTaxIV = [50000., 50000., 50000., 50000., 50000., 50000., 50000., 50000.]
# Current unrealized cap gains on each lot
CurrentUnrealizedCapGains = [15000., 15000., 15000., 15000., 15000., 15000., 15000., 15000.]
# Specify any lots that are less than a year old - which we'll want to avoid if possible to avoid short term cap gains
LotLessThanOneYearOld = [False,False,False,False,False,False,False,True]

# Cash balance (bank accounts, etc.)
CashCushion = 20000.

# Dividends
# Note: good way to estimate yield is divide the qualified and non-qualified dividend income you received from taxable
# account investments the previous year and divide by the taxable account balance at the end of the year
QualifiedDividendYield = 0.016 #0. # based on 5-year average dividend yield of VTSAX
NonQualifiedDividendYield = 0.0 # assume negligible

# Other income sources. E.g., a pension. Put in comma separated list within brackets.
OtherIncomeSources = []

# Maximum standard income to achieve (don't include LT cap gains)
# Recommend targeting the top of your standard deduction (MaxStandardIncomeUseStdDed = True)
MaxStandardIncomeUseStdDed = True
# If you'd rather use a different value, set MaxStandardIncomeUseStdDed = False and provide value below:
# (not aware of a good reason to do this, but there might be)
if MaxStandardIncomeUseStdDed == False:
    MaxStandardIncome = 0.

# Total income to achieve (including LT cap gains)
# If you have ACA (Obamacare) medical insurance, set total income to maximize ACA subsidies:
MaxTotalIncome = 50000.
# If no other reason to target a particular income (e.g., have Medicare or some other form of medical insurance),
# recommend targeting top of 0% long term capital gains bracket:
MaxTotalIncomeUseTopOf0PercentLTcapGainsBracket = False # Will override MaxTotalIncome provided above

# Annual Expenses
Exp = 40000.

# Note: look at your tax return for these values
# Taxes and Penalties generated from income last year - needed for estimated tax payments
TaxesGenPrevYear = 0.
PenaltiesGenPrevYear = 0.
# Taxes and Penalties paid last year
# (if more than generated, you'll get refund this year; if less than generated, you'll owe taxes this year)
TaxesPaidPrevYear = 0.
PenaltiesPaidPrevYear = 0.

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Flag dictating whether to run TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc method or not
# This method has not yet produced better results for any scenario attempted - but it's available if desired
# And it might produce better results when an ACA premiums/subsidies model is in place
# Recommended setting: False
TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag = False

# TPM Method - Withdraw from 457b or Pretax first
# Recommended setting: True
TPMwithdraw457bFirst = True

# Output extra information about the withdrawals, income, etc.
VerboseMode = True

#############################################################################################################

# Translate inputs as needed for use in ProjFinalBalance

# Convert any lists to numpy arrays
if type(PreTaxIV) is list: PreTaxIV = np.array(PreTaxIV, dtype=float)
else: PreTaxIV = np.array([PreTaxIV], dtype=float)
if type(PreTax457bIV) is list: PreTax457bIV = np.array(PreTax457bIV, dtype=float)
else: PreTax457bIV = np.array([PreTax457bIV], dtype=float)
if type(RothIV) is list: RothIV = np.array(RothIV, dtype=float)
else: RothIV = np.array([RothIV], dtype=float)
if type(RothContributions) is list: RothContributions = np.array(RothContributions, dtype=float)
else: RothContributions = np.array([RothContributions], dtype=float)
if type(SocialSecurityPayments) is list: SocialSecurityPayments = np.array(SocialSecurityPayments, dtype=float)
else: SocialSecurityPayments = np.array([SocialSecurityPayments], dtype=float)
if type(CurrentAge) is list: CurrentAge = np.array(CurrentAge, dtype=float)
else: CurrentAge = np.array([CurrentAge], dtype=float)
if type(PostTaxIV) is list: PostTaxIV = np.array(PostTaxIV, dtype=float)
else: PostTaxIV = np.array([PostTaxIV], dtype=float)
if type(CurrentUnrealizedCapGains) is list: CurrentUnrealizedCapGains = np.array(CurrentUnrealizedCapGains, dtype=float)
else: CurrentUnrealizedCapGains = np.array([CurrentUnrealizedCapGains], dtype=float)
if type(LotLessThanOneYearOld) is list: LotLessThanOneYearOld = np.array(LotLessThanOneYearOld)
else: LotLessThanOneYearOld = np.array([LotLessThanOneYearOld])
if type(OtherIncomeSources) is list: OtherIncomeSources = np.array(OtherIncomeSources, dtype=float)
else: OtherIncomeSources = np.array([OtherIncomeSources], dtype=float)
if type(RMDsThisYear) is list: RMDsThisYear = np.array(RMDsThisYear)
else: RMDsThisYear = np.array([RMDsThisYear])

# Convert Roth conversion values, including to numpy arrays
RothConversionAmount = np.array(RothConversionAmount, dtype=float)
RothConversionAge = np.array(RothConversionAge, dtype=float)
if FilingStatus == 'MarriedFilingJointly':
    RothConversionPersonTemp = copy.deepcopy(RothConversionPerson)
    RothConversionPerson = np.zeros(len(RothConversionPersonTemp), dtype=int)
    for ct in range(len(RothConversionPerson)):
        if RothConversionPersonTemp[ct] == 'Person 2':
            RothConversionPerson[ct] = 1
else:
    RothConversionPerson = np.zeros(len(RothConversionAmount), dtype=int)

# Convert RMDsThisYear to RMDstartAge
RMDstartAge = np.ones(len(RMDsThisYear))*1000. # initialize with large number, to ensure it will not be used if no RMDs
for ct in range(len(RMDsThisYear)):
    if RMDsThisYear[ct]:
        RMDstartAge[ct] = CurrentAge[ct]

# Set AgeSSwillStart to current age if SocialSecurityPayments are non-zero
AgeSSwillStart = np.ones(len(RMDsThisYear))*1000. # initialize with large number, to ensure it will not be used if no SS
for ct in range(len(SocialSecurityPayments)):
    if SocialSecurityPayments[ct] > 0.:
        AgeSSwillStart[ct] = CurrentAge[ct]

# Equivalent array for use in ProjFinalBalance
LotPurchasedFirstYear = copy.deepcopy(LotLessThanOneYearOld)

# Use standard deduction for max standard income
if MaxStandardIncomeUseStdDed == True:
    if FilingStatus == 'Single':
        MaxStandardIncome = TaxRateInfo['SingleStandardDeduction']
    if FilingStatus == 'MarriedFilingJointly':
        MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction']
    if FilingStatus == 'HeadOfHousehold':
        MaxStandardIncome = TaxRateInfo['HeadOfHouseholdStandardDeduction']
    if FilingStatus == 'MarriedFilingSeparately':
        MaxStandardIncome = TaxRateInfo['MarriedFilingSeparatelyStandardDeduction']
    if FilingStatus == 'QualifyingWidow(er)':
        MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction']

if MaxTotalIncomeUseTopOf0PercentLTcapGainsBracket == True:
    if FilingStatus == 'Single':
        SpecifiedIncome = TaxRateInfo['SingleStandardDeduction'] + TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1]
    if FilingStatus == 'MarriedFilingJointly':
        SpecifiedIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] + \
                          TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]
    if FilingStatus == 'HeadOfHousehold':
        SpecifiedIncome = TaxRateInfo['HeadOfHouseholdStandardDeduction'] + \
                          TaxRateInfo['HeadOfHouseholdIncomeBracketLTcapGainsMins'][1]
    if FilingStatus == 'MarriedFilingSeparately':
        SpecifiedIncome = TaxRateInfo['MarriedFilingSeparatelyStandardDeduction'] + \
                          TaxRateInfo['MarriedFilingSeparatelyIncomeBracketLTcapGainsMins'][1]
    if FilingStatus == 'QualifyingWidow(er)': #(same as 'MarriedFilingJointly')
        SpecifiedIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] + \
                          TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]
else: # the user specified the max total income directly
    SpecifiedIncome = MaxTotalIncome



# Run for just the first year
NumYearsToProject = 1

# Not used, but needed for ProjFinalBalance to run:
MaxStandardIncomeChange = np.array([], dtype=float)
AgeMaxStandardIncomeChangeWillStart = np.array([], dtype=float)
SpecifiedIncomeChange = np.array([], dtype=float)
AgeSpecifiedIncomeChangeWillStart = np.array([], dtype=float)
ExpRate = 0.
FutureExpenseAdjustments = np.array([], dtype=float)
FutureExpenseAdjustmentsAge = np.array([], dtype=float)
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)
R = 0.

#############################################################################################################

# Capturing inputs in relevant dictionaries

IVdict = {'PreTaxIV': PreTaxIV,
          'PreTax457bIV': PreTax457bIV,
          'PostTaxIV': PostTaxIV,
          'CurrentUnrealizedCapGains': CurrentUnrealizedCapGains,
          'LotPurchasedFirstYear': LotPurchasedFirstYear,
          'RothIV': RothIV,
          'RothContributions': RothContributions,
          'RothConversionAmount': RothConversionAmount,
          'RothConversionAge': RothConversionAge,
          'RothConversionPerson': RothConversionPerson,
          'CashCushion': CashCushion,
          'TaxesGenPrevYear': TaxesGenPrevYear,
          'TaxesPaidPrevYear': TaxesPaidPrevYear,
          'PenaltiesGenPrevYear': PenaltiesGenPrevYear,
          'PenaltiesPaidPrevYear': PenaltiesPaidPrevYear}

IncDict = {'QualifiedDividendYield': QualifiedDividendYield,
           'NonQualifiedDividendYield': NonQualifiedDividendYield,
           'SocialSecurityPayments': SocialSecurityPayments,
           'AgeSSwillStart': AgeSSwillStart,
           'OtherIncomeSources': OtherIncomeSources,
           'AgeOtherIncomeSourcesWillStart': AgeOtherIncomeSourcesWillStart,
           'MaxStandardIncome': MaxStandardIncome,
           'MaxStandardIncomeChange': MaxStandardIncomeChange,
           'AgeMaxStandardIncomeChangeWillStart': AgeMaxStandardIncomeChangeWillStart,
           'SpecifiedIncome': SpecifiedIncome,
           'SpecifiedIncomeChange': SpecifiedIncomeChange,
           'AgeSpecifiedIncomeChangeWillStart': AgeSpecifiedIncomeChangeWillStart,
           'TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag': TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag}

ExpDict = {'Exp': Exp,
           'ExpRate': ExpRate,
           'FutureExpenseAdjustments': FutureExpenseAdjustments,
           'FutureExpenseAdjustmentsAge': FutureExpenseAdjustmentsAge}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Single run of ProjFinalBalance

t0 = time.time()

ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,NumYearsToProject, R,
                              FilingStatus,TPMwithdraw457bFirst)

t1 = time.time()
SimTime = t1-t0
print('Run Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################

# Compute relevant outputs (e.g. withdrawals, final asset values, etc.)

OutputDict = ComputeOutputs(ProjArrays,IVdict,FilingStatus,IncDict)

#############################################################################################################

# Print relevant outputs to output file

# WritePrimaryOutput(OutputFile,ProjArrays,IVdict,FilingStatus,IncDict)
WritePrimaryOutput(OutputFile,OutputDict,FilingStatus)

if VerboseMode:
    AppendVerboseOutput(OutputFile,OutputDict,FilingStatus)

