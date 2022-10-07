# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawalOptimizationTemplate.py

import numpy as np
import copy
import os
# import matplotlib.pyplot as plt
# from scipy import optimize

from TaxRateInfoInput import TaxRateInfoInput
from SupportMethods import MultiPlot
from ProjFinalBalance import ProjFinalBalance
from ProjFinalBalanceTraditional import ProjFinalBalanceTraditional

# Compute optimal withdrawal method/sequence of assets to minimize taxes, maximize ACA subsidies, ensure sufficient
# funds always available, and maximize long term growth of assets

#############################################################################################################
# Inputs

# Bring in 2022 income tax bracket info, used for inputs (modify if beyond 2022)
TaxRateInfo = TaxRateInfoInput()

# Pre-tax assets initial value
PreTaxIV = 400000. # Scenario 1
# PreTaxIV = 500000. # Scenario 2
PreTax457bIV = 100000. # Scenario 1
# PreTax457bIV = 200000. # Scenario 2
# Every lot in post-tax account, to know what cap gains are on each
PostTaxIV = np.array([50000., 50000., 50000., 50000., 50000., 50000., 50000., 50000.], dtype=float) # Scenario 1
# PostTaxIV = np.array([25000., 25000., 25000., 25000., 25000., 25000., 25000., 25000.], dtype=float)  # Scenario 2
# current unrealized cap gains on each lot
CurrentUnrealizedCapGains = np.array([15000., 15000., 15000., 15000., 15000., 15000., 15000., 15000.], dtype=float) # Scenario 1
# CurrentUnrealizedCapGains = np.array([7500., 7500., 7500., 7500., 7500., 7500., 7500., 7500.], dtype=float) # Scenario 2
# NOTE: after the first year, withdrawal code will assume all cap gains are long term cap gains, to simplify the logic.
# If there ARE any lots purchased the first year of retirement (e.g. you did some tax loss harvesting and then decided
# to retire that same year), set relevant value in LotPurchasedFirstYear to True.
# Only a concern for first year of analysis loop, to avoid short term cap gains if possible
LotPurchasedFirstYear = np.array([False,False,False,False,False,False,False,True])

# Note: include HSA accounts in Roth category, since it also grows tax-free and can be used without paying taxes if
# spent on medical expenses (easy enough as you get older)
RothIV = 80000.
RothContributions = 40000.

CashCushion = 20000.

# Retirement Income
# Dividends
CurrentAnnualQualifiedDividends = 10000. # Scenario 1
# CurrentAnnualQualifiedDividends = 5000. # Scenario 2
CurrentAnnualNonQualifiedDividends = 100.
# Social security - taxed different, so don't place in OtherIncomeSources
SocialSecurityPayments = np.array([17000,17000], dtype=float)
AgeSSwillStart = np.array([67,67], dtype=float)
# Note: Once you've reached full retirement age (67 if born after 1960), you can earn as much as you want with no penalties.
# Before your full retirement age, you can earn up to $19,560 per year (as of 2022) without having your Social Security
# payments reduced. Bad news: If you earn over this limit, your benefits will be cut. Good news: When you reach full
# retirement age, any withheld benefits will be returned to you in the form of higher monthly payments.
# https://investor.vanguard.com/investor-resources-education/article/top-questions-about-social-security
# Other income
OtherIncomeSources = np.array([], dtype=float) # e.g. pension, in current dollars
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)  # using first person in CurrentAge array
# Maximum standard income to achieve (not LT cap gains)
MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction']
# Income need to achieve, e.g. for maximizing ACA subsidies
SpecifiedIncome = 50000.
# When enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap gains bracket
SpecifiedIncomeAfterACA = TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]

# Retirement Expenses - in current year dollars, as is everything else in this simulation
Exp = 40000. # Scenario 1
# Exp = 45000. # Scenario 2

# Future expense adjustments (e.g. a mortgage is paid off)
FutureExpenseAdjustments = np.array([-800.*12], dtype=float)
FutureExpenseAdjustmentsAge = np.array([66], dtype=float) # using first person in CurrentAge array


CurrentAge = np.array([40,38]) # array to allow for 2+ people (e.g. spouses), place oldest person first
NumYearsToProject = 32
FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Tax and Penalty Minimization (TPM) Withdrawal Method or Traditional Withdrawal Method
TPMorTraditionalWithdrawal = 'TPM' #'Traditional' #

# Plot flags
AssetBalancesVsAge = True
YearlyValuesVsAge = False
YearlyValuesNoTotalCashVsAge = False

#############################################################################################################

# Capturing inputs in relevant dictionaries

IVdict = {'PreTaxIV': PreTaxIV,
          'PreTax457bIV': PreTax457bIV,
          'PostTaxIV': PostTaxIV,
          'CurrentUnrealizedCapGains': CurrentUnrealizedCapGains,
          'LotPurchasedFirstYear': LotPurchasedFirstYear,
          'RothIV': RothIV,
          'RothContributions': RothContributions,
          'CashCushion': CashCushion}

IncDict = {'CurrentAnnualQualifiedDividends': CurrentAnnualQualifiedDividends,
           'CurrentAnnualNonQualifiedDividends': CurrentAnnualNonQualifiedDividends,
           'SocialSecurityPayments': SocialSecurityPayments,
           'AgeSSwillStart': AgeSSwillStart,
           'OtherIncomeSources': OtherIncomeSources,
           'AgeOtherIncomeSourcesWillStart': AgeOtherIncomeSourcesWillStart,
           'MaxStandardIncome': MaxStandardIncome,
           'SpecifiedIncome': SpecifiedIncome,
           'SpecifiedIncomeAfterACA': SpecifiedIncomeAfterACA}

ExpDict = {'Exp': Exp,
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
     'Title_yoffset': 1.04, 'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20,
     'PlotSecondaryLines': False}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Single run of ProjFinalBalance

if TPMorTraditionalWithdrawal == 'TPM':
    ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus)
else:
    ProjArrays = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                             FilingStatus)

#############################################################################################################

# Print relevant numbers to output file (e.g. final asset values, etc.)

file=open(OutputFile,'w')
file.write('WithdrawalOptimization.py\n\n')

file.write('Total Final: $'+'{:.2f}'.format(ProjArrays['TotalAssets'][-1])+'\n')
file.write('PostTaxTotal Final: $'+'{:.2f}'.format(ProjArrays['PostTaxTotal'][-1])+'\n')
file.write('PreTax Final: $'+'{:.2f}'.format(ProjArrays['PreTax'][-1])+'\n')
file.write('PreTax457b Final: $'+'{:.2f}'.format(ProjArrays['PreTax457b'][-1])+'\n')
file.write('Roth Final: $'+'{:.2f}'.format(ProjArrays['Roth'][-1])+'\n')
file.write('CashCushion Final: $'+'{:.2f}'.format(ProjArrays['CashCushion'][-1])+'\n')
file.write('CapGainsTotal Final: $'+'{:.2f}'.format(ProjArrays['CapGainsTotal'][-1])+'\n')
file.write('Taxes Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Taxes']))+'\n')
file.write('Penalties Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Penalties']))+'\n')

file.close()

#############################################################################################################

# Plot nominal run results
if AssetBalancesVsAge:

    NumPlots = 7 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion, CapGainsTotal
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = ProjArrays['TotalAssets']/1.e6
    AssetsArray[1,:] = ProjArrays['PostTaxTotal']/1.e6
    AssetsArray[2,:] = ProjArrays['PreTax']/1.e6
    AssetsArray[3,:] = ProjArrays['PreTax457b']/1.e6
    AssetsArray[4,:] = ProjArrays['Roth']/1.e6
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

    # SpecifiedIncome, TotalStandardIncome, TotalLTcapGainsIncome, TotalSSincome, TotalIncome, TotalCash, Expenses, Taxes
    NumPlots = 9
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['SpecifiedIncome'])))
    ValuesArray[0,:] = ProjArrays['SpecifiedIncome']/1000.
    ValuesArray[1,:] = ProjArrays['TotalStandardIncome']/1000.
    ValuesArray[2,:] = ProjArrays['TotalLTcapGainsIncome']/1000.
    ValuesArray[3,:] = ProjArrays['TotalSSincome']/1000.
    ValuesArray[4,:] = ProjArrays['TotalIncome']/1000.
    ValuesArray[5,:] = ProjArrays['TotalCash']/1000.
    ValuesArray[6,:] = ProjArrays['Expenses']/1000.
    ValuesArray[7,:] = ProjArrays['Taxes']/1000.
    ValuesArray[8,:] = ProjArrays['Penalties']/1000.

    PlotLabelArray = ['SpecifiedIncome','TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','TotalIncome',
                      'TotalCash','Expenses','Taxes','Penalties']
    PlotColorArray = ['k','r','b','g','c','m','y','limegreen','fuchsia']

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

    NumPlots = 8
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['SpecifiedIncome'])))
    ValuesArray[0,:] = ProjArrays['SpecifiedIncome']/1000.
    ValuesArray[1,:] = ProjArrays['TotalStandardIncome']/1000.
    ValuesArray[2,:] = ProjArrays['TotalLTcapGainsIncome']/1000.
    ValuesArray[3,:] = ProjArrays['TotalSSincome']/1000.
    ValuesArray[4,:] = ProjArrays['TotalIncome']/1000.
    ValuesArray[5,:] = ProjArrays['Expenses']/1000.
    ValuesArray[6,:] = ProjArrays['Taxes']/1000.
    ValuesArray[7,:] = ProjArrays['Penalties']/1000.

    PlotLabelArray = ['SpecifiedIncome','TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','TotalIncome',
                      'Expenses','Taxes','Penalties']
    PlotColorArray = ['k','r','b','g','c','y','limegreen','fuchsia']

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
