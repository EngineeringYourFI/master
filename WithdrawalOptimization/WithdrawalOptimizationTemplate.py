# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawalOptimizationTemplate.py

import numpy as np
import copy
import os

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
# always put older person first
PreTaxIV = np.array([200000.,200000.], dtype=float) # Scenario 1
# PreTaxIV = 500000. # Scenario 2
# PreTaxIV = np.array([400000.], dtype=float) # Scenario 3, single person
# 457b can be withdrawn without 10% penalty before 59.5
PreTax457bIV = np.array([50000.,50000.], dtype=float)  # Scenario 1
# PreTax457bIV = 200000. # Scenario 2
# PreTax457bIV = np.array([100000.], dtype=float)  # Scenario 3, single person

# Every lot in post-tax account, to know what cap gains are on each
PostTaxIV = np.array([50000., 50000., 50000., 50000., 50000., 50000., 50000., 50000.], dtype=float) # Scenario 1 & 3
# PostTaxIV = np.array([25000., 25000., 25000., 25000., 25000., 25000., 25000., 25000.], dtype=float)  # Scenario 2
# current unrealized cap gains on each lot
CurrentUnrealizedCapGains = np.array([15000., 15000., 15000., 15000., 15000., 15000., 15000., 15000.], dtype=float) # Scenario 1 & 3
# CurrentUnrealizedCapGains = np.array([7500., 7500., 7500., 7500., 7500., 7500., 7500., 7500.], dtype=float) # Scenario 2
# NOTE: after the first year, withdrawal code will assume all cap gains are long term cap gains, to simplify the logic.
# If there ARE any lots purchased the first year of retirement (e.g. you did some tax loss harvesting and then decided
# to retire that same year), set relevant value in LotPurchasedFirstYear to True.
# Only a concern for first year of analysis loop, to avoid short term cap gains if possible
LotPurchasedFirstYear = np.array([False,False,False,False,False,False,False,True])

# Note: include HSA accounts in Roth category, since it also grows tax-free and can be used without paying taxes if
# spent on medical expenses (easy enough as you get older)
# always put older person first
RothIV = np.array([40000.,40000.], dtype=float) # Scenario 1
# RothIV = np.array([80000.], dtype=float) # Scenario 3, single person
RothContributions = np.array([20000.,20000.], dtype=float) # Scenario 1
# RothContributions = np.array([40000.], dtype=float) # Scenario 3, single person

CashCushion = 20000.

# Retirement Income
# Dividends
CurrentAnnualQualifiedDividends = 10000. # Scenario 1 & 3
# CurrentAnnualQualifiedDividends = 5000. # Scenario 2
CurrentAnnualNonQualifiedDividends = 100. # Scenario 1 & 3
# Social security - taxed different, so don't place in OtherIncomeSources
# always put older person first
SocialSecurityPayments = np.array([17000,17000], dtype=float) # Scenario 1 & 2
# SocialSecurityPayments = np.array([17000], dtype=float) # Scenario 3, single person
AgeSSwillStart = np.array([67,67], dtype=float) # Scenario 1 & 2
# AgeSSwillStart = np.array([67], dtype=float) # Scenario 3, single person
# Note: Once you've reached full retirement age (67 if born after 1960), you can earn as much as you want with no penalties.
# Before your full retirement age, you can earn up to $19,560 per year (as of 2022) without having your Social Security
# payments reduced. Bad news: If you earn over this limit, your benefits will be cut. Good news: When you reach full
# retirement age, any withheld benefits will be returned to you in the form of higher monthly payments.
# https://investor.vanguard.com/investor-resources-education/article/top-questions-about-social-security
# Other income
OtherIncomeSources = np.array([], dtype=float) # e.g. pension, in current dollars
AgeOtherIncomeSourcesWillStart = np.array([], dtype=float)  # using first person in CurrentAge array
# Maximum standard income to achieve (not LT cap gains)
MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction'] # Scenario 1 & 2
# MaxStandardIncome = TaxRateInfo['SingleStandardDeduction'] # Scenario 3, single person
# Income need to achieve, e.g. for maximizing ACA subsidies
SpecifiedIncome = 50000.
# When old enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap gains bracket
SpecifiedIncomeAfterACA = TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1] # Scenario 1 & 2
# SpecifiedIncomeAfterACA = TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1] # Scenario 3, single person

# Retirement Expenses - in current year dollars, as is everything else in this simulation
Exp = 40000. # Scenario 1
# Exp = 45000. # Scenario 2

# Future expense adjustments (e.g. a mortgage is paid off)
FutureExpenseAdjustments = np.array([-800.*12], dtype=float)
FutureExpenseAdjustmentsAge = np.array([66], dtype=float) # using first person in CurrentAge array

# always put older person first
CurrentAge = np.array([40,38]) # Scenario 1 & 2
# CurrentAge = np.array([40]) # Scenario 3, single person
NumYearsToProject = 52
FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Tax and Penalty Minimization (TPM) Withdrawal Method or Traditional Withdrawal Method
TPMorTraditionalWithdrawal = 'TPM' #'Both' #'Traditional' #

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
     'Title_xoffset': 0.5, 'Title_yoffset': 1.04,
     'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20,
     'PlotSecondaryLines': False}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Single run of ProjFinalBalance

if TPMorTraditionalWithdrawal == 'TPM':
    ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                                  TPMwithdraw457bFirst)
elif TPMorTraditionalWithdrawal == 'Traditional':
    ProjArrays = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                             FilingStatus)
else:
    ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                                  TPMwithdraw457bFirst)
    ProjArraysTraditional = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                             FilingStatus)

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

#############################################################################################################

# Plot asset diff plots - TPM vs Traditional

if TPMorTraditionalWithdrawal == 'Both' and AssetBalancesVsAgeTPMvsTraditionalDiff:

    NumPlots = 6 #7 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion #, CapGainsTotal
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = (ProjArraysTraditional['TotalAssets']-ProjArrays['TotalAssets'])/1.e6
    AssetsArray[1,:] = (ProjArraysTraditional['PostTaxTotal']-ProjArrays['PostTaxTotal'])/1.e6
    AssetsArray[2,:] = (ProjArraysTraditional['PreTaxTotal']-ProjArrays['PreTaxTotal'])/1.e6
    AssetsArray[3,:] = (ProjArraysTraditional['PreTax457bTotal']-ProjArrays['PreTax457bTotal'])/1.e6
    AssetsArray[4,:] = (ProjArraysTraditional['RothTotal']-ProjArrays['RothTotal'])/1.e6
    AssetsArray[5,:] = (ProjArraysTraditional['CashCushion']-ProjArrays['CashCushion'])/1.e6
    # AssetsArray[6,:] = (ProjArraysTraditional['CapGainsTotal']-ProjArrays['CapGainsTotal'])/1.e6

    PlotLabelArray = ['Total, Final $'+'{:.3f}M'.format((ProjArraysTraditional['TotalAssets'][-1]-
                                                         ProjArrays['TotalAssets'][-1])/1.e6),'PostTaxTotal','PreTax',
                      'PreTax457b','Roth','CashCushion']#,'CapGains']
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
         'TitleText': 'Asset Diffs (Traditional - TPM), Annual ROI 7%',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'lower left', #'upper right',
         'SaveFile': OutDir+'AssetBalancesVsAgeDiffsTPMvsTraditional.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot yearly values diff plots - TPM vs Traditional

if TPMorTraditionalWithdrawal == 'Both' and YearlyValuesVsAgeTPMvsTraditionalDiff:

    # TotalIncome, Expenses, Taxes, Penalties # TotalCash, SpecifiedIncome, TotalStandardIncome, TotalLTcapGainsIncome, TotalSSincome,
    NumPlots = 3 #8 #9
    ValuesArray = np.zeros((NumPlots,len(ProjArrays['SpecifiedIncome'])))
    # ValuesArray[0,:] = (ProjArraysTraditional['SpecifiedIncome']-ProjArrays['SpecifiedIncome'])/1000.
    # ValuesArray[1,:] = (ProjArraysTraditional['TotalStandardIncome']-ProjArrays['TotalStandardIncome'])/1000.
    # ValuesArray[2,:] = (ProjArraysTraditional['TotalLTcapGainsIncome']-ProjArrays['TotalLTcapGainsIncome'])/1000.
    # ValuesArray[3,:] = (ProjArraysTraditional['TotalSSincome']-ProjArrays['TotalSSincome'])/1000.
    ValuesArray[0,:] = (ProjArraysTraditional['TotalIncome']-ProjArrays['TotalIncome'])/1000.
    # ValuesArray[1,:] = (ProjArraysTraditional['Expenses']-ProjArrays['Expenses'])/1000.
    ValuesArray[1,:] = (ProjArraysTraditional['Taxes']-ProjArrays['Taxes'])/1000.
    ValuesArray[2,:] = (ProjArraysTraditional['Penalties']-ProjArrays['Penalties'])/1000.
    # ValuesArray[5,:] = (ProjArraysTraditional['TotalCash']-ProjArrays['TotalCash'])/1000.

    PlotLabelArray = ['TotalIncome','Taxes','Penalties'] #'TotalCash', 'SpecifiedIncome','TotalStandardIncome','TotalLTcapGainsIncome','TotalSSincome','Expenses',
    PlotColorArray = ['c','limegreen','fuchsia'] #'m', 'k','r','b','g','y',

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
         'ylabel': 'Yearly Value Diffs [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values Diffs (Traditional - TPM) vs Age',
         'Title_xoffset': 0.44, # shift a bit to the left (0.5 is default)
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyValueDiffsVsAgeTPMvsTraditional.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
