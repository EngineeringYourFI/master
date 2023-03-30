# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawalOptimizationTemplate.py

import numpy as np
import copy
import os
import time

from TaxRateInfoInput import TaxRateInfoInput
from SupportMethods import MultiPlot
from ProjFinalBalance import ProjFinalBalance
from ProjFinalBalanceTraditional import ProjFinalBalanceTraditional
from ComputeTaxes import ComputeTaxes

# Compute optimal withdrawal method/sequence of assets to minimize taxes, maximize ACA subsidies, ensure sufficient
# funds always available, and maximize long term growth of assets

#############################################################################################################
# Inputs

# Bring in 2023 income tax bracket info, used for inputs (modify if beyond 2023)
TaxRateInfo = TaxRateInfoInput()

# Scenario = 'MarriedFilingJointly'
Scenario = 'Single'

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

    # # When old enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap
    # # gains bracket
    # Legacy variable:
    # SpecifiedIncomeAfterACA = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] + \
    #                           TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]
    # Use more general purpose capability to change this income value
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

    # In case SpecifiedIncome (total income goal) is not acheived, or must be exceeded to acheive total cash needed, you
    # can provide values that will allow you to compute the change in ACA health insurance subsidies. That will then be
    # added to the Taxes total (positive or negative) for that year, because that will change how much you owe/are
    # refunded the next year
    AdjustTaxBillIfIncomeForACAsubsidiesNotMet = True
    ExpectedIncomeForACAsubsidies = 50000. # nominally the same as SpecifiedIncome
    NumPeopleOnACA = 4
    # Annual cost of benchmark plan (second-cheapest Silver level plan in your area and for your situation)
    BenchmarkPrice = 1458.76*12.
    Residence = 'Contiguous' #'Alaska' #'Hawaii' #


if Scenario == 'Single':
    PreTaxIV = np.array([400000.], dtype=float)
    PreTax457bIV = np.array([100000.], dtype=float)
    # PreTaxIV = np.array([400000.+100000.], dtype=float)
    # PreTax457bIV = np.array([0.], dtype=float)
    RothIV = np.array([80000.+20000.], dtype=float)
    RothContributions = np.array([40000.+20000.], dtype=float)
    RothConversionAmount = np.array([], dtype=float)
    RothConversionAge = np.array([], dtype=float)
    RothConversionPerson = np.array([], dtype=int)
    SocialSecurityPayments = np.array([17000], dtype=float)
    AgeSSwillStart = np.array([67], dtype=float)
    MaxStandardIncome = TaxRateInfo['SingleStandardDeduction']
    # SpecifiedIncomeAfterACA = TaxRateInfo['SingleStandardDeduction']+TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1]
    SpecifiedIncome = 40000.
    SpecifiedIncomeChange = np.array([TaxRateInfo['SingleStandardDeduction'] +
                                      TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1] - SpecifiedIncome],
                                     dtype=float)
    AgeSpecifiedIncomeChangeWillStart = np.array([65], dtype=float)
    CurrentAge = np.array([40])
    RMDstartAge = np.array([75], dtype=float)
    FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'
    AdjustTaxBillIfIncomeForACAsubsidiesNotMet = True #False #
    ExpectedIncomeForACAsubsidies = 40000. #50000.
    NumPeopleOnACA = 1
    BenchmarkPrice = 454.*12.
    Residence = 'Contiguous' #'Alaska' #'Hawaii' #

# Every lot in post-tax account, to know what cap gains are on each
PostTaxIV = np.array([50000., 50000., 50000., 50000., 50000., 50000., 50000., 50000.], dtype=float)
# current unrealized cap gains on each lot
# CurrentUnrealizedCapGains = np.array([15000., 15000., 15000., 15000., 15000., 15000., 15000., 15000.], dtype=float)
CurrentUnrealizedCapGains = np.array([40000., 40000., 40000., 40000., 40000., 40000., 40000., 40000.], dtype=float) #*2.
# NOTE: after the first year, withdrawal code will assume all cap gains are long term cap gains, to simplify the logic.
# If there ARE any lots purchased the first year of retirement (e.g. you did some tax loss harvesting and then decided
# to retire that same year), set relevant value in LotPurchasedFirstYear to True.
# Only a concern for first year of analysis loop, to avoid short term cap gains if possible
LotPurchasedFirstYear = np.array([False,False,False,False,False,False,False,True])

# Moving cash to Roth (increasing balance and contributions, so can still easily pull from the account just like a cash
# account) to prevent complications with 0% interest on cash that can happen when some scenarios dip into the cash
# account vs those that don't
CashCushion = 0. #20000. #

# TotalIV = PreTaxIV + PreTax457bIV + np.sum(PostTaxIV) + RothIV + CashCushion

# Retirement Income
# Dividends
# CurrentAnnualQualifiedDividends = 10000. # Scenario 1 & 2
# CurrentAnnualNonQualifiedDividends = 100. # Scenario 1 & 2
QualifiedDividendYield = 0.016 #0. # based on 5-year average dividend yield of VTSAX
NonQualifiedDividendYield = 0.0 # assume negligible

# Other income
OtherIncomeSources = np.array([], dtype=float) # e.g. pension, in current dollars
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)  # using first person in CurrentAge array

# Change to MaxStandardIncome at any particular age / year
MaxStandardIncomeChange = np.array([], dtype=float) #10000
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

# Tax and Penalty Minimization (TPM) Withdrawal Method or Traditional Withdrawal Method
TPMorTraditionalWithdrawal = 'TPM' #'Traditional' #'Both' #

# Flag dictating whether to run TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc method or not
# This method has not yet produced better results for any scenario attempted - but it's available if desired
# And it might produce better results when an ACA premiums/subsidies model is in place
TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag = False

# TPM Method - Withdraw from 457b or Pretax first
TPMwithdraw457bFirst = True

# Plot flags
AssetBalancesVsAge = True
YearlyValuesVsAge = True
YearlyValuesNoTotalCashVsAge = True
AssetBalancesVsAgeTPMvsTraditionalDiff = False
YearlyValuesVsAgeTPMvsTraditionalDiff = False

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

# Single run of ProjFinalBalance

t0 = time.time()

if TPMorTraditionalWithdrawal == 'TPM':
    ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,NumYearsToProject, R,
                                  FilingStatus,TPMwithdraw457bFirst)
elif TPMorTraditionalWithdrawal == 'Traditional':
    ProjArrays = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,
                                             NumYearsToProject, R,FilingStatus)
elif TPMorTraditionalWithdrawal == 'Both':
    ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,NumYearsToProject, R,
                                  FilingStatus,TPMwithdraw457bFirst)
    ProjArraysTraditional = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,RMDstartAge,
                                                        NumYearsToProject, R,FilingStatus)

t1 = time.time()
SimTime = t1-t0
print('Projection Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################

# Print relevant numbers to output file (e.g. final asset values, etc.)

file=open(OutputFile,'w')
file.write('WithdrawalOptimizationTemplate.py\n\n')

file.write('Total Final: $'+'{:.2f}'.format(ProjArrays['TotalAssets'][-1])+'\n')
file.write('PostTaxTotal Final: $'+'{:.2f}'.format(ProjArrays['PostTaxTotal'][-1])+'\n')
file.write('PreTax Final: $'+'{:.2f}'.format(ProjArrays['PreTaxTotal'][-1])+'\n')
file.write('PreTax457b Final: $'+'{:.2f}'.format(ProjArrays['PreTax457bTotal'][-1])+'\n')
file.write('Roth Final: $'+'{:.2f}'.format(ProjArrays['RothTotal'][-1])+'\n')
file.write('CashCushion Final: $'+'{:.2f}'.format(ProjArrays['CashCushion'][-1])+'\n')
file.write('CapGainsTotal Final: $'+'{:.2f}'.format(ProjArrays['CapGainsTotal'][-1])+'\n')
file.write('Taxes Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Taxes']))+'\n')
file.write('Penalties Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Penalties']))+'\n')
file.write('RMDs Total: $'+'{:.2f}'.format(np.sum(ProjArrays['RMDtotal']))+'\n\n')
file.write('Sim Time: '+'{:.2f}'.format(SimTime)+' seconds\n')
if np.isnan(ProjArrays['OutOfMoneyAge']) == False:
    file.write('Age money ran out: '+'{:.0f}'.format(ProjArrays['OutOfMoneyAge'])+'\n')
file.close()

#############################################################################################################

# Plot asset results
if AssetBalancesVsAge:

    NumPlots = 7 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion, CapGainsTotal
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = ProjArrays['TotalAssets']/1.e6
    AssetsArray[1,:] = ProjArrays['PostTaxTotal']/1.e6
    AssetsArray[2,:] = ProjArrays['PreTaxTotal']/1.e6
    AssetsArray[3,:] = ProjArrays['PreTax457bTotal']/1.e6
    AssetsArray[4,:] = ProjArrays['RothTotal']/1.e6
    AssetsArray[5,:] = ProjArrays['CashCushion']/1.e6
    AssetsArray[6,:] = ProjArrays['CapGainsTotal']/1.e6

    PlotLabelArray = ['Total, Final $'+'{:.3f}M'.format(ProjArrays['TotalAssets'][-1]/1.e6),'PostTaxTotal','PreTax',
                      'PreTax457b','Roth','CashCushion','CapGains']
    PlotColorArray = ['k','r','b','g','c','m','limegreen']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'][:,0],
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ProjArrays['TotalAssets']/1.e6)+1.,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Asset Balance [2022 $M]',
         'xlabel': 'Age',
         'TitleText': 'Asset Balances vs Age, Annual ROI 7%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AssetBalancesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot yearly results
if YearlyValuesVsAge:

    # TotalStandardIncome, TotalLTcapGainsIncome, TotalSSincome, TotalIncome, TotalCash, Expenses,
    # Taxes, Penalties, RMDs # removed: SpecifiedIncome,
    NumPlots = 9 #10
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['TotalStandardIncome'])))
    # ValuesArray[0,:] = ProjArrays['SpecifiedIncome']/1000.
    ValuesArray[0,:] = ProjArrays['TotalStandardIncome']/1000.
    ValuesArray[1,:] = ProjArrays['TotalLTcapGainsIncome']/1000.
    ValuesArray[2,:] = ProjArrays['TotalSSincome']/1000.
    ValuesArray[3,:] = ProjArrays['TotalIncome']/1000.
    ValuesArray[4,:] = ProjArrays['TotalCash']/1000.
    ValuesArray[5,:] = ProjArrays['Expenses']/1000.
    ValuesArray[6,:] = ProjArrays['Taxes']/1000.
    ValuesArray[7,:] = ProjArrays['Penalties']/1000.
    ValuesArray[8,:] = ProjArrays['RMDtotal']/1000.

    PlotLabelArray = ['TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','TotalIncome',
                      'TotalCash','Expenses','Taxes','Penalties','RMDs'] #'SpecifiedIncome',
    PlotColorArray = ['r','b','g','c','m','y','limegreen','fuchsia','saddlebrown'] # 'k', #orangered, chocolate, peru, darkorange, gold, olive, slategrey

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'][:,0],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Yearly Values [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values vs Age',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyValuesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

# and plot without TotalCash
if YearlyValuesNoTotalCashVsAge:

    NumPlots = 8 #9
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['TotalStandardIncome'])))
    # ValuesArray[0,:] = ProjArrays['SpecifiedIncome']/1000.
    ValuesArray[0,:] = ProjArrays['TotalStandardIncome']/1000.
    ValuesArray[1,:] = ProjArrays['TotalLTcapGainsIncome']/1000.
    ValuesArray[2,:] = ProjArrays['TotalSSincome']/1000.
    ValuesArray[3,:] = ProjArrays['TotalIncome']/1000.
    ValuesArray[4,:] = ProjArrays['Expenses']/1000.
    ValuesArray[5,:] = ProjArrays['Taxes']/1000.
    ValuesArray[6,:] = ProjArrays['Penalties']/1000.
    ValuesArray[7,:] = ProjArrays['RMDtotal']/1000.

    PlotLabelArray = ['TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','TotalIncome',
                      'Expenses','Taxes','Penalties','RMDs'] #'SpecifiedIncome',
    PlotColorArray = ['r','b','g','c','y','limegreen','fuchsia','saddlebrown'] #'k',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'][:,0],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Yearly Values [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values vs Age',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyValuesNoTotalCashVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot asset diff plots - TPM vs Traditional

if TPMorTraditionalWithdrawal == 'Both' and AssetBalancesVsAgeTPMvsTraditionalDiff:

    NumPlots = 6 #7 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion #, CapGainsTotal
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = (ProjArrays['TotalAssets']-ProjArraysTraditional['TotalAssets'])/1.e6
    AssetsArray[1,:] = (ProjArrays['PostTaxTotal']-ProjArraysTraditional['PostTaxTotal'])/1.e6
    AssetsArray[2,:] = (ProjArrays['PreTaxTotal']-ProjArraysTraditional['PreTaxTotal'])/1.e6
    AssetsArray[3,:] = (ProjArrays['PreTax457bTotal']-ProjArraysTraditional['PreTax457bTotal'])/1.e6
    AssetsArray[4,:] = (ProjArrays['RothTotal']-ProjArraysTraditional['RothTotal'])/1.e6
    AssetsArray[5,:] = (ProjArrays['CashCushion']-ProjArraysTraditional['CashCushion'])/1.e6
    # AssetsArray[6,:] = (ProjArrays['CapGainsTotal']-ProjArraysTraditional['CapGainsTotal'])/1.e6

    PlotLabelArray = ['Total, Final $'+'{:.3f}M'.format((ProjArrays['TotalAssets'][-1]-
                                                         ProjArraysTraditional['TotalAssets'][-1])/1.e6),'PostTaxTotal',
                      'PreTax','PreTax457b','Roth','CashCushion']#,'CapGains']
    PlotColorArray = ['k','r','b','g','c','m'] #,'limegreen']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'][:,0],
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(AssetsArray)-0.1, 'ymax': np.max(AssetsArray)+0.1,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Asset Balance Difference [2022 $M]',
         'xlabel': 'Age',
         'TitleText': 'Asset Diffs (TPM - Traditional), Annual ROI 7%',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'lower left', #'upper right', #
         'SaveFile': OutDir+'AssetBalancesVsAgeDiffsTPMvsTraditional.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot yearly values diff plots - TPM vs Traditional

if TPMorTraditionalWithdrawal == 'Both' and YearlyValuesVsAgeTPMvsTraditionalDiff:

    # TotalIncome, Expenses, Taxes, Penalties # TotalCash, SpecifiedIncome, TotalStandardIncome, TotalLTcapGainsIncome, TotalSSincome,
    NumPlots = 4 #8 #9
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['SpecifiedIncome'])))
    # ValuesArray[0,:] = (ProjArrays['SpecifiedIncome']-ProjArraysTraditional['SpecifiedIncome'])/1000.
    # ValuesArray[1,:] = (ProjArrays['TotalStandardIncome']-ProjArraysTraditional['TotalStandardIncome'])/1000.
    # ValuesArray[2,:] = (ProjArrays['TotalLTcapGainsIncome']-ProjArraysTraditional['TotalLTcapGainsIncome'])/1000.
    # ValuesArray[3,:] = (ProjArrays['TotalSSincome']-ProjArraysTraditional['TotalSSincome'])/1000.
    ValuesArray[0,:] = (ProjArrays['TotalIncome']-ProjArraysTraditional['TotalIncome'])/1000.
    # ValuesArray[1,:] = (ProjArrays['Expenses']-ProjArraysTraditional['Expenses'])/1000.
    ValuesArray[1,:] = (ProjArrays['Taxes']-ProjArraysTraditional['Taxes'])/1000.
    ValuesArray[2,:] = (ProjArrays['Penalties']-ProjArraysTraditional['Penalties'])/1000.
    # ValuesArray[5,:] = (ProjArrays['TotalCash']-ProjArraysTraditional['TotalCash'])/1000.
    ValuesArray[3,:] = (ProjArrays['RMDtotal']-ProjArraysTraditional['RMDtotal'])/1000.


    PlotLabelArray = ['TotalIncome','Taxes','Penalties','RMDs'] #'TotalCash', 'SpecifiedIncome','TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','Expenses',
    PlotColorArray = ['c','limegreen','fuchsia','saddlebrown'] #'m', 'k','r','b','g','y',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'][:,0],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(ValuesArray)-1., 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Yearly Value Diffs [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values Diffs (TPM - Traditional) vs Age',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyValueDiffsVsAgeTPMvsTraditional.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
