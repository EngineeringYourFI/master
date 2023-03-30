# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/what-income-should-you-target-after-fire-with-obamacare/)

# IncomeVariationACAsubsidyImpactTemplate.py

import numpy as np
import copy
import os
import time

from WithdrawalOptimization.TaxRateInfoInput import *
from WithdrawalOptimization.SupportMethods import MultiPlot
from WithdrawalOptimization.ProjFinalBalance import *
from WithdrawalOptimization.ComputeTaxes import *

# Vary total max income to determine the impact of ACA subsidy changes on final projection results

#############################################################################################################
# Inputs

# Bring in 2023 income tax bracket info, used for inputs (modify if beyond 2023)
TaxRateInfo = TaxRateInfoInput()

Scenario = 'MarriedFilingJointly'
# Scenario = 'Single'

if Scenario == 'MarriedFilingJointly':
    # Pre-tax assets initial value
    # always put older person first
    PreTaxIV = np.array([200000.,200000.], dtype=float)
    # 457b can be withdrawn without 10% penalty before 59.5
    PreTax457bIV = np.array([50000.,50000.], dtype=float)

    # Note: include HSA accounts in Roth category, since it also grows tax-free and can be used without paying taxes if
    # spent on medical expenses (easy enough as you get older)
    # always put older person first
    RothIV = np.array([40000.+10000.,40000.+10000.], dtype=float)
    RothContributions = np.array([20000.+10000.,20000.+10000.], dtype=float)
    # Roth conversions from pre-tax accounts - list format, earliest to latest - leave empty if no previous conversions
    RothConversionAmount = np.array([], dtype=float)
    # Age at each conversion (all conversions for a single year lumped together here)
    RothConversionAge = np.array([], dtype=float)
    # Which person did the conversion from their pre-tax to Roth account: 'Person 1' = 0 or 'Person 2' = 1
    RothConversionPerson = np.array([], dtype=int)

    # Social security - taxed different, so don't place in OtherIncomeSources
    # always put older person first
    SocialSecurityPayments = np.array([17000,17000], dtype=float) # Scenario 1, MarriedFilingJointly
    AgeSSwillStart = np.array([67,67], dtype=float) # Scenario 1, MarriedFilingJointly
    # Note: Once you've reached full retirement age (67 if born after 1960), you can earn as much as you want with no
    # penalties. Before your full retirement age, you can earn up to $19,560 per year (as of 2022) without having your
    # Social Security payments reduced. Bad news: If you earn over this limit, your benefits will be cut. Good news:
    # When you reach full retirement age, any withheld benefits will be returned to you in the form of higher monthly
    # payments.
    # https://investor.vanguard.com/investor-resources-education/article/top-questions-about-social-security

    # Maximum standard income to achieve (not LT cap gains)
    MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction']

    # Total income need to achieve, e.g. for maximizing ACA subsidies
    # (eventually include ACA subsidy model to further optimize)
    SpecifiedIncome = 50000.

    # When old enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap
    # gains bracket
    SpecifiedIncomeChange = np.array([TaxRateInfo['MarriedFilingJointlyStandardDeduction'] +
                                      TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1] -
                                      SpecifiedIncome], dtype=float)
    # The age of the older person when this change occurs
    # So if the younger person is 2 years younger than the older person, set to 65 + 2, for when both people will be on
    # medicare and no longer worried about ACA subsidies
    AgeSpecifiedIncomeChangeWillStart = np.array([67], dtype=float)

    # Always put older person first
    CurrentAge = np.array([40,38]) # Scenario 1, MarriedFilingJointly

    # If born 1950 or earlier, RMDs start at age 72
    # If born from 1951 to 1958, RMDs start at age 73
    # If born in 1959, a technical error in the legislation means it’s unknown if RMDs must start at age 73 or 75. Hopefully
    # new legislation will clarify, but until then, you should probably use age 73 to be safe.
    # If born 1960 or later, RMDs start at age 75
    RMDstartAge = np.array([75,75], dtype=float)

    FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

    # In case SpecifiedIncome (total income goal) is not achieved, or must be exceeded to achieve total cash needed, you
    # can provide values that will allow you to compute the change in ACA health insurance subsidies. That will then be
    # added to the Taxes total (positive or negative) for that year, because that will change how much you owe/are
    # refunded the next year
    AdjustTaxBillIfIncomeForACAsubsidiesNotMet = True
    ExpectedIncomeForACAsubsidies = 50000. # nominally the same as SpecifiedIncome
    Residence = 'Contiguous' #'Alaska' #'Hawaii' #
    # For family of 4
    NumPeopleOnACA = 4.
    # Annual cost of benchmark plan (second-cheapest Silver level plan in your area and for your situation)
    BenchmarkPrice=1458.76*12.


if Scenario == 'Single':
    PreTaxIV = np.array([400000.], dtype=float)
    PreTax457bIV = np.array([100000.], dtype=float)
    RothIV = np.array([80000.+20000.], dtype=float)
    RothContributions = np.array([40000.+20000.], dtype=float)
    RothConversionAmount = np.array([], dtype=float)
    RothConversionAge = np.array([], dtype=float)
    RothConversionPerson = np.array([], dtype=int)
    SocialSecurityPayments = np.array([17000], dtype=float)
    AgeSSwillStart = np.array([67], dtype=float)
    MaxStandardIncome = TaxRateInfo['SingleStandardDeduction']
    SpecifiedIncome = 39000.
    SpecifiedIncomeChange = np.array([TaxRateInfo['SingleStandardDeduction'] +
                                      TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1] - SpecifiedIncome],
                                     dtype=float)
    AgeSpecifiedIncomeChangeWillStart = np.array([65], dtype=float)
    CurrentAge = np.array([40])
    RMDstartAge = np.array([75], dtype=float)
    FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'
    AdjustTaxBillIfIncomeForACAsubsidiesNotMet = True #False #
    ExpectedIncomeForACAsubsidies = 40000.
    NumPeopleOnACA = 1.
    BenchmarkPrice=454.*12.
    Residence = 'Contiguous' #'Alaska' #'Hawaii' #

# Every lot in post-tax account, to know what cap gains are on each
PostTaxIV = np.array([50000., 50000., 50000., 50000., 50000., 50000., 50000., 50000.], dtype=float)
# current unrealized cap gains on each lot
CurrentUnrealizedCapGains = np.array([15000., 15000., 15000., 15000., 15000., 15000., 15000., 15000.], dtype=float)
# NOTE: after the first year, withdrawal code will assume all cap gains are long term cap gains, to simplify the logic.
# If there ARE any lots purchased the first year of retirement (e.g. you did some tax loss harvesting and then decided
# to retire that same year), set relevant value in LotPurchasedFirstYear to True.
# Only a concern for first year of analysis loop, to avoid short term cap gains if possible
LotPurchasedFirstYear = np.array([False,False,False,False,False,False,False,True])

# Moving cash to Roth (increasing balance and contributions, so can still easily pull from the account just like a cash
# account) to prevent complications with 0% interest on cash that can happen when some scenarios dip into the cash
# account vs those that don't
CashCushion = 0.

# TotalIV = PreTaxIV + PreTax457bIV + np.sum(PostTaxIV) + RothIV + CashCushion

# Retirement Income
# Dividends
QualifiedDividendYield = 0.016 # based on 5-year average dividend yield of VTSAX
NonQualifiedDividendYield = 0.0 # assume negligible

# Other income
OtherIncomeSources = np.array([], dtype=float) # e.g. pension, in current dollars
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)  # using first person in CurrentAge array

# Change to MaxStandardIncome at any particular age / year
MaxStandardIncomeChange = np.array([], dtype=float)
AgeMaxStandardIncomeChangeWillStart = np.array([], dtype=float)  # using first person in CurrentAge array #73

# Retirement Expenses - in current year dollars, as is everything else in this simulation
Exp = 40000.
ExpRate = 0. # How much expenses (in current day dollars) change each year

# Future expense adjustments (e.g. a mortgage is paid off)
FutureExpenseAdjustments = np.array([-800.*12], dtype=float)
FutureExpenseAdjustmentsAge = np.array([66], dtype=float) # using first person in CurrentAge array

NumYearsToProject = 52 #26 #

# Taxes and Penalties generated from income in year prior to starting simulation
TaxesGenPrevYear = 0.
PenaltiesGenPrevYear = 0.
# Taxes and Penalties paid in year prior to starting simulation
# (if more than generated, you'll get refund at start; if less than generated, you'll owe taxes at start)
TaxesPaidPrevYear = 0.
PenaltiesPaidPrevYear = 0.

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Flag dictating whether to run TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc method or not
# This method has not yet produced better results for any scenario attempted - but it's available if desired
# And it might produce better results when an ACA premiums/subsidies model is in place
TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag = False

# TPM Method - Withdraw from 457b or Pretax first
TPMwithdraw457bFirst = True

# Generate and Plot Flags
VaryingSpecifiedIncomeGenerate = True
VaryingSpecifiedIncomeValuesToFile = True
VaryingSpecifiedIncomePlot = True

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
           'TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag':
               TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag,
           'AdjustTaxBillIfIncomeForACAsubsidiesNotMet': AdjustTaxBillIfIncomeForACAsubsidiesNotMet,
           'ExpectedIncomeForACAsubsidies': ExpectedIncomeForACAsubsidies,
           'NumPeopleOnACA': NumPeopleOnACA,
           'BenchmarkPrice': BenchmarkPrice,
           'Residence': Residence}

ExpDict = {'Exp': Exp,
           'ExpRate': ExpRate,
           'FutureExpenseAdjustments': FutureExpenseAdjustments,
           'FutureExpenseAdjustmentsAge': FutureExpenseAdjustmentsAge}

#############################################################################################################

# Default plotting parameters, using dictionary (can modify if needed)
DefaultPlotDict = \
    {'FigWidth': 10.8, 'FigHeight': 10.8,
     'LineStyle': '-', 'LineWidth': 3,
     'MarkerSize': 10,
     'CopyrightX': 0.01, 'CopyrightY': 1-0.01, 'CopyrightText': 'EngineeringYourFI.com', 'CopyrightFontSize': 20,
     'CopyrightVertAlign': 'top',
     'ylabelFontSize': 30, 'xlabelFontSize': 30,
     'Title_xoffset': 0.5, 'Title_yoffset': 1.04,
     'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20, 'LegendOn': True,
     'PlotSecondaryLines': False}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Run ProjFinalBalance for each specified income, capture final results for plotting

if VaryingSpecifiedIncomeGenerate:

    # Single scenario
    if Scenario == 'Single':
        MinSpecifiedIncome = 13590. # 100% of 2022 FPL for Contiguous
        # Max: top of 0% LTCG tax bracket
        MaxSpecifiedIncome = TaxRateInfo['SingleStandardDeduction']+TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1]

    # Married scenario
    if Scenario == 'MarriedFilingJointly':
        # family of 4
        MinSpecifiedIncome = 13590. + 3.*4720. # 100% of 2022 FPL for Contiguous
        # Max: top of 0% LTCG tax bracket
        MaxSpecifiedIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] + \
                             TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]

    SpecifiedIncomeArray = np.arange(MinSpecifiedIncome,MaxSpecifiedIncome,1000.)
    TotalAssetsArray = np.zeros(len(SpecifiedIncomeArray))
    PostTaxTotalArray = np.zeros(len(SpecifiedIncomeArray))
    PreTaxTotalArray = np.zeros(len(SpecifiedIncomeArray))
    PreTax457bTotalArray = np.zeros(len(SpecifiedIncomeArray))
    RothTotalArray = np.zeros(len(SpecifiedIncomeArray))
    CashCushionArray = np.zeros(len(SpecifiedIncomeArray))
    CapGainsTotalArray = np.zeros(len(SpecifiedIncomeArray))
    TaxesArray = np.zeros(len(SpecifiedIncomeArray))
    PenaltiesArray = np.zeros(len(SpecifiedIncomeArray))
    RMDtotalArray = np.zeros(len(SpecifiedIncomeArray))

    t0 = time.time()

    for ct in range(len(SpecifiedIncomeArray)):

        IncDict['SpecifiedIncome'] = SpecifiedIncomeArray[ct]
        if Scenario == 'Single':
            IncDict['SpecifiedIncomeChange'] = np.array([TaxRateInfo['SingleStandardDeduction'] +
                                                         TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1] -
                                                         IncDict['SpecifiedIncome']],dtype=float)
        if Scenario == 'MarriedFilingJointly':
            IncDict['SpecifiedIncomeChange'] = np.array([TaxRateInfo['MarriedFilingJointlyStandardDeduction'] +
                                                         TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1] -
                                                         IncDict['SpecifiedIncome']],dtype=float)

        ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,NumYearsToProject, R,
                                          FilingStatus,TPMwithdraw457bFirst)

        # Capture relevant values for plotting
        TotalAssetsArray[ct] = ProjArrays['TotalAssets'][-1]
        PostTaxTotalArray[ct] = ProjArrays['PostTaxTotal'][-1]
        PreTaxTotalArray[ct] = ProjArrays['PreTaxTotal'][-1]
        PreTax457bTotalArray[ct] = ProjArrays['PreTax457bTotal'][-1]
        RothTotalArray[ct] = ProjArrays['RothTotal'][-1]
        CashCushionArray[ct] = ProjArrays['CashCushion'][-1]
        CapGainsTotalArray[ct] = ProjArrays['CapGainsTotal'][-1]
        TaxesArray[ct] = np.sum(ProjArrays['Taxes'])
        PenaltiesArray[ct] = np.sum(ProjArrays['Penalties'])
        RMDtotalArray[ct] = np.sum(ProjArrays['RMDtotal'])

    t1 = time.time()
    SimTime = t1-t0
    print('Sim Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################

# Print relevant numbers to output file (e.g. final asset values, etc.)

if VaryingSpecifiedIncomeValuesToFile:

    file=open(OutputFile,'w')
    file.write('IncomeVariationACAsubsidyImpact.py\n\n')

    file.write('Total Finals: \n')
    for ct in range(len(TotalAssetsArray)):
        if ct == (len(TotalAssetsArray) - 1):
            file.write('{:.2f}'.format(TotalAssetsArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(TotalAssetsArray[ct])+', ')

    file.write('\n')
    file.write('PostTax Total Finals: \n')
    for ct in range(len(PostTaxTotalArray)):
        if ct == (len(PostTaxTotalArray) - 1):
            file.write('{:.2f}'.format(PostTaxTotalArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(PostTaxTotalArray[ct])+', ')

    file.write('\n')
    file.write('PreTax Total Finals: \n')
    for ct in range(len(PreTaxTotalArray)):
        if ct == (len(PreTaxTotalArray) - 1):
            file.write('{:.2f}'.format(PreTaxTotalArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(PreTaxTotalArray[ct])+', ')

    file.write('\n')
    file.write('PreTax457b Total Finals: \n')
    for ct in range(len(PreTax457bTotalArray)):
        if ct == (len(PreTax457bTotalArray) - 1):
            file.write('{:.2f}'.format(PreTax457bTotalArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(PreTax457bTotalArray[ct])+', ')

    file.write('\n')
    file.write('Roth Total Finals: \n')
    for ct in range(len(RothTotalArray)):
        if ct == (len(RothTotalArray) - 1):
            file.write('{:.2f}'.format(RothTotalArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(RothTotalArray[ct])+', ')

    file.write('\n')
    file.write('Cash Cushion Total Finals: \n')
    for ct in range(len(CashCushionArray)):
        if ct == (len(CashCushionArray) - 1):
            file.write('{:.2f}'.format(CashCushionArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(CashCushionArray[ct])+', ')

    file.write('\n')
    file.write('Cap Gains Total Finals: \n')
    for ct in range(len(CapGainsTotalArray)):
        if ct == (len(CapGainsTotalArray) - 1):
            file.write('{:.2f}'.format(CapGainsTotalArray[ct])+'\n')
        else:
            file.write('{:.2f}'.format(CapGainsTotalArray[ct])+', ')

    file.close()

#############################################################################################################

# Plot asset results from varying specified income
if VaryingSpecifiedIncomePlot:

    # TotalAssetsArray, PostTaxTotalArray, PreTaxTotalArray, PreTax457bTotalArray, RothTotalArray, CashCushionArray,
    # CapGainsTotalArray
    # Nominally not plotting: TaxesArray, PenaltiesArray, RMDtotalArray
    NumPlots = 7

    AssetsArray = np.zeros((NumPlots,len(TotalAssetsArray)))
    AssetsArray[0,:] = TotalAssetsArray/1.e6
    AssetsArray[1,:] = PostTaxTotalArray/1.e6
    AssetsArray[2,:] = PreTaxTotalArray/1.e6
    AssetsArray[3,:] = PreTax457bTotalArray/1.e6
    AssetsArray[4,:] = RothTotalArray/1.e6
    AssetsArray[5,:] = CashCushionArray/1.e6
    AssetsArray[6,:] = CapGainsTotalArray/1.e6

    PlotLabelArray = ['Total','PostTaxTotal','PreTax','PreTax457b','Roth','CashCushion','CapGains']
    PlotColorArray = ['k','r','b','g','c','m','limegreen']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': SpecifiedIncomeArray/1000.,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(TotalAssetsArray/1.e6)+1., #'ymin': 14.5, 'ymax': 15.9, #
         'xmin': SpecifiedIncomeArray[0]/1000., 'xmax': SpecifiedIncomeArray[-1]/1000.,
         'ylabel': 'Asset Balance [2022 $M]',
         'xlabel': 'Specified Income [2023 $K]',
         'TitleText': 'Asset Balances vs Specified Income',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'VaryingSpecifiedIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


