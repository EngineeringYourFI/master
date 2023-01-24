# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/reducing-standard-income-increasing-long-term-cap-gains-to-generate-more-cash-not-worth-it/)

# ReducingStdIncomeIncreasingLTCG.py

import numpy as np
import copy
import os
import time

from WithdrawalOptimization.TaxRateInfoInput import TaxRateInfoInput
from WithdrawalOptimization.SupportMethods import MultiPlot
from WithdrawalOptimization.ProjFinalBalance import ProjFinalBalance
from WithdrawalOptimization.ProjFinalBalanceTraditional import ProjFinalBalanceTraditional
from WithdrawalOptimization.ComputeTaxes import ComputeTaxes

# Assess TryIncreasingPostTaxWithdrawalAndMaybeReducingStdInc method

#############################################################################################################
# Inputs

# Bring in 2022 income tax bracket info, used for inputs (modify if beyond 2022)
TaxRateInfo = TaxRateInfoInput()

# Scenario 1, MarriedFilingJointly
Scenario1 = False
if Scenario1:
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

    # When old enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap
    # gains bracket
    SpecifiedIncomeAfterACA = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] + \
                              TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]

    # always put older person first
    CurrentAge = np.array([40,38]) # Scenario 1, MarriedFilingJointly

    FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'


# Scenario 2, Single
Scenario2 = True
if Scenario2:
    PreTaxIV = np.array([400000.+100000.], dtype=float)
    PreTax457bIV = np.array([0.], dtype=float)
    RothIV = np.array([80000.+20000.], dtype=float)
    RothContributions = np.array([40000.+20000.], dtype=float)
    SocialSecurityPayments = np.array([17000], dtype=float)
    AgeSSwillStart = np.array([67], dtype=float)
    MaxStandardIncome = TaxRateInfo['SingleStandardDeduction']
    SpecifiedIncomeAfterACA = TaxRateInfo['SingleStandardDeduction']+TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1]
    CurrentAge = np.array([40])
    FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

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
QualifiedDividendYield = 0. #0.016 # based on 5-year average dividend yield of VTSAX
NonQualifiedDividendYield = 0.0 # assume negligible

# Other income
OtherIncomeSources = np.array([], dtype=float) # e.g. pension, in current dollars
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)  # using first person in CurrentAge array

# Change to MaxStandardIncome at any particular age / year
MaxStandardIncomeChange = np.array([], dtype=float) #10000
AgeMaxStandardIncomeChangeWillStart = np.array([], dtype=float)  # using first person in CurrentAge array #73

# Income need to achieve, e.g. for maximizing ACA subsidies
# (eventually include ACA subsidy model to further optimize)
SpecifiedIncome = 50000.

# Retirement Expenses - in current year dollars, as is everything else in this simulation
Exp = 69000. 
ExpRate = 0. # How much expenses (in current day dollars) change each year

# Future expense adjustments (e.g. a mortgage is paid off)
FutureExpenseAdjustments = np.array([-800.*12], dtype=float)
FutureExpenseAdjustmentsAge = np.array([66], dtype=float) # using first person in CurrentAge array

NumYearsToProject = 52 

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
# This method has not yet produces better results than not running the method - but it's available if desired
TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag = True

# TPM Method - Withdraw from 457b or Pretax first
TPMwithdraw457bFirst = True

# Plot flags
AssetDiffBalancesVsAge = True
YearlyDiffValuesVsAge = True

#############################################################################################################

# Capturing inputs in relevant dictionaries

IVdict = {'PreTaxIV': PreTaxIV,
          'PreTax457bIV': PreTax457bIV,
          'PostTaxIV': PostTaxIV,
          'CurrentUnrealizedCapGains': CurrentUnrealizedCapGains,
          'LotPurchasedFirstYear': LotPurchasedFirstYear,
          'RothIV': RothIV,
          'RothContributions': RothContributions,
          'CashCushion': CashCushion,
          'TaxesGenPrevYear': TaxesGenPrevYear,
          'TaxesPaidPrevYear': TaxesPaidPrevYear,
          'PenaltiesGenPrevYear': PenaltiesGenPrevYear,
          'PenaltiesPaidPrevYear': PenaltiesPaidPrevYear}

IncDict = {'QualifiedDividendYield': QualifiedDividendYield, #'CurrentAnnualQualifiedDividends': CurrentAnnualQualifiedDividends,
           'NonQualifiedDividendYield': NonQualifiedDividendYield, #'CurrentAnnualNonQualifiedDividends': CurrentAnnualNonQualifiedDividends,
           'SocialSecurityPayments': SocialSecurityPayments,
           'AgeSSwillStart': AgeSSwillStart,
           'OtherIncomeSources': OtherIncomeSources,
           'AgeOtherIncomeSourcesWillStart': AgeOtherIncomeSourcesWillStart,
           'MaxStandardIncome': MaxStandardIncome,
           'MaxStandardIncomeChange': MaxStandardIncomeChange,
           'AgeMaxStandardIncomeChangeWillStart': AgeMaxStandardIncomeChangeWillStart,
           'SpecifiedIncome': SpecifiedIncome,
           'SpecifiedIncomeAfterACA': SpecifiedIncomeAfterACA,
           'TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag': TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag}

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

# Run ProjFinalBalance with and without TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag on

t0 = time.time()

IncDict['TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag'] = True
ProjArraysFlagOn = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                              TPMwithdraw457bFirst)
IncDict['TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag'] = False
ProjArraysFlagOff = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                              TPMwithdraw457bFirst)

t1 = time.time()
SimTime = t1-t0
print('Sim Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################

# Plot asset diff plots - TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag On vs Off

if AssetDiffBalancesVsAge:

    NumPlots = 6 #7 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion #, CapGainsTotal
    AssetsArray = np.zeros((NumPlots,len(ProjArraysFlagOn['TotalAssets'])))
    AssetsArray[0,:] = (ProjArraysFlagOn['TotalAssets']-ProjArraysFlagOff['TotalAssets'])/1.e3
    AssetsArray[1,:] = (ProjArraysFlagOn['PostTaxTotal']-ProjArraysFlagOff['PostTaxTotal'])/1.e3
    AssetsArray[2,:] = (ProjArraysFlagOn['PreTaxTotal']-ProjArraysFlagOff['PreTaxTotal'])/1.e3
    AssetsArray[3,:] = (ProjArraysFlagOn['PreTax457bTotal']-ProjArraysFlagOff['PreTax457bTotal'])/1.e3
    AssetsArray[4,:] = (ProjArraysFlagOn['RothTotal']-ProjArraysFlagOff['RothTotal'])/1.e3
    AssetsArray[5,:] = (ProjArraysFlagOn['CashCushion']-ProjArraysFlagOff['CashCushion'])/1.e3
    # AssetsArray[6,:] = (ProjArrays['CapGainsTotal']-ProjArraysTraditional['CapGainsTotal'])/1.e3

    PlotLabelArray = ['Total, Final $'+'{:.3f}K'.format((ProjArraysFlagOn['TotalAssets'][-1]-
                                                         ProjArraysFlagOff['TotalAssets'][-1])/1.e3),'PostTaxTotal',
                      'PreTax','PreTax457b','Roth','CashCushion']#,'CapGains']
    PlotColorArray = ['k','r','b','g','c','m'] #,'limegreen']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArraysFlagOn['Age'][:,0],
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(AssetsArray)-0.1, 'ymax': np.max(AssetsArray)+0.1,
         'xmin': ProjArraysFlagOn['Age'][0,0], 'xmax': ProjArraysFlagOn['Age'][-1,0],
         'ylabel': 'Asset Balance Difference [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Asset Diffs (On - Off), Annual ROI 7%',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'upper right', #'lower left', #
         'SaveFile': OutDir+'AssetDiffBalancesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot yearly values diff plots - TryIncreasingPostTaxWithdrawalAndMaybeReducingStdIncFlag On vs Off

if YearlyDiffValuesVsAge:

    # TotalStandardIncome, TotalLTcapGainsIncome, TotalSSincome, TotalIncome, Taxes, Penalties, RMDs # TotalCash, SpecifiedIncome, Expenses,
    NumPlots = 7
    ValuesArray = np.zeros((NumPlots,len(ProjArraysFlagOn['SpecifiedIncome'])))
    # ValuesArray[0,:] = (ProjArraysFlagOn['SpecifiedIncome']-ProjArraysFlagOff['SpecifiedIncome'])/1000.
    ValuesArray[0,:] = (ProjArraysFlagOn['TotalStandardIncome']-ProjArraysFlagOff['TotalStandardIncome'])/1000.
    ValuesArray[1,:] = (ProjArraysFlagOn['TotalLTcapGainsIncome']-ProjArraysFlagOff['TotalLTcapGainsIncome'])/1000.
    ValuesArray[2,:] = (ProjArraysFlagOn['TotalSSincome']-ProjArraysFlagOff['TotalSSincome'])/1000.
    ValuesArray[3,:] = (ProjArraysFlagOn['TotalIncome']-ProjArraysFlagOff['TotalIncome'])/1000.
    # ValuesArray[1,:] = (ProjArraysFlagOn['Expenses']-ProjArraysFlagOff['Expenses'])/1000.
    ValuesArray[4,:] = (ProjArraysFlagOn['Taxes']-ProjArraysFlagOff['Taxes'])/1000.
    ValuesArray[5,:] = (ProjArraysFlagOn['Penalties']-ProjArraysFlagOff['Penalties'])/1000.
    # ValuesArray[5,:] = (ProjArraysFlagOn['TotalCash']-ProjArraysFlagOff['TotalCash'])/1000.
    ValuesArray[6,:] = (ProjArraysFlagOn['RMDtotal']-ProjArraysFlagOff['RMDtotal'])/1000.

    PlotLabelArray = ['TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','TotalIncome','Taxes','Penalties','RMDs'] #'TotalCash', 'SpecifiedIncome','Expenses',
    PlotColorArray = ['r','b','g','c','limegreen','fuchsia','saddlebrown'] #'m', 'k','y',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArraysFlagOn['Age'][:,0],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(ValuesArray)-1., 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArraysFlagOn['Age'][0,0], 'xmax': ProjArraysFlagOn['Age'][-1,0],
         'ylabel': 'Yearly Value Diffs [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values Diffs (On - Off) vs Age',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyDiffValuesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
