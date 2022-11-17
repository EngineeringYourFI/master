# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/is-it-worth-using-lower-tax-brackets-to-reduce-rmds-later)

# WorthPayingTaxesEarlyTemplate.py

import numpy as np
import copy
import os

from TaxRateInfoInput import TaxRateInfoInput
from SupportMethods import MultiPlot
from ProjFinalBalance import ProjFinalBalance

# Looking at reducing RMDs by withdrawing more than standard deduction from pre-tax accounts before RMDs start

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
RothIV = np.array([40000.+10000.,40000.+10000.], dtype=float) # Scenario 1 # [40000.,40000.]
# RothIV = np.array([80000.], dtype=float) # Scenario 3, single person
RothContributions = np.array([20000.+10000.,20000.+10000.], dtype=float) # Scenario 1 # [20000.,20000.]
# RothContributions = np.array([40000.], dtype=float) # Scenario 3, single person

# Moving cash to Roth (increasing balance and contributions, so can still easily pull from the account just like a cash
# account) to prevent complications with 0% interest on cash that can happen when some scenarios dip into the cash
# account vs those that don't
CashCushion = 0. # 20000.

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
# Change to MaxStanardIncome at any particular age / year
MaxStandardIncomeChange = np.array([], dtype=float) #10000
AgeMaxStandardIncomeChangeWillStart = np.array([], dtype=float)  # using first person in CurrentAge array #73

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
# Scenario 1 & 2
FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'
# Scenario 3, single person
# FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Withdraw from 457b or Pretax first
TPMwithdraw457bFirst = True

# Scenario and Plot Flags
ExtraStandardIncomeEntireSimulation = True
ExtraStandardIncomeLaterInSimulation = True
RunAndPlotDiffsSingleExtraIncome = True

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
           'MaxStandardIncomeChange': MaxStandardIncomeChange,
           'AgeMaxStandardIncomeChangeWillStart': AgeMaxStandardIncomeChangeWillStart,
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
     'LegendLoc': 'best', 'LegendFontSize': 20, 'LegendOn': True,
     'PlotSecondaryLines': False}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Nominal run with default Max Standard Income (e.g. standard deduction)
ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R, FilingStatus,
                              TPMwithdraw457bFirst)

#############################################################################################################

# Vary how much extra standard income is generated across entire simulation
if ExtraStandardIncomeEntireSimulation:
    DefaultMaxStandardIncome = IncDict['MaxStandardIncome']
    IncreaseAmounts = np.arange(0.,9500.,500.)
    FinalTotalDiff = np.zeros(len(IncreaseAmounts))
    BreakEvenAge = np.zeros(len(IncreaseAmounts))
    MinTotalDiff = np.zeros(len(IncreaseAmounts))

    for ct in range(0,len(IncreaseAmounts)):
        IncDict['MaxStandardIncome'] = DefaultMaxStandardIncome + IncreaseAmounts[ct]
        ProjArraysIncreasedStandardIncome = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,
                                                             NumYearsToProject, R, FilingStatus,TPMwithdraw457bFirst)

        TotalDiffArray = ProjArraysIncreasedStandardIncome['TotalAssets']-ProjArrays['TotalAssets']
        # Compute diff in final total
        FinalTotalDiff[ct] = TotalDiffArray[-1]

        # Compute "break even" Age
        if IncreaseAmounts[ct] > 0. and np.any(TotalDiffArray>0.):
            BreakEvenIndex = np.where(TotalDiffArray>0.)[0][0] # itemindex = numpy.where(array==item)[0][0]
            BreakEvenAge[ct] = ProjArrays['Age'][BreakEvenIndex,0]
        else:
            BreakEvenAge[ct] = np.nan

        # Compute diff minimum (max negative), and confirm it corresponds to when RMDs start (maybe)
        MinTotalDiff[ct] = np.min(TotalDiffArray)

    # Reset just in case
    IncDict['MaxStandardIncome'] = DefaultMaxStandardIncome

    # Plot diff in final total and diff minimum vs addition to max standard income
    NumPlots = 2 # FinalTotalDiff, MinTotalDiff
    DiffsArray = np.zeros((NumPlots,len(FinalTotalDiff)))
    DiffsArray[0,:] = FinalTotalDiff/1.e3
    DiffsArray[1,:] = MinTotalDiff/1.e3
    PlotLabelArray = ['Final Total Diff','Minimum Total Diff']
    PlotColorArray = ['k','r']
    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncreaseAmounts/1.e3,
         'DepData': DiffsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(DiffsArray)-5, 'ymax': np.max(DiffsArray)+20,
         'xmin': IncreaseAmounts[0]/1.e3, 'xmax': IncreaseAmounts[-1]/1.e3,
         'ylabel': 'Asset Balance Difference [2022 $K]',
         'xlabel': 'Max Standard Income Increase [2022 $K]',
         'TitleText': 'Asset Balance Diffs vs \n Increased Max Standard Income',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AssetDiffsVsIncreasedStandardIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Plot BreakEvenAge vs addition to max standard income
    NumPlots = 1 # BreakEvenAge
    AgeArray = np.zeros((NumPlots,len(BreakEvenAge)))
    AgeArray[0,:] = BreakEvenAge
    PlotLabelArray = ['']
    PlotColorArray = ['k']
    PlotDict = copy.deepcopy(DefaultPlotDict)
    UpdateDict = \
        {'IndepData': IncreaseAmounts/1.e3,
         'DepData': AgeArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 89, 'ymax': 92,
         # 'ymin': np.min(AgeArray)-1, 'ymax': np.max(AgeArray)+1,
         'xmin': IncreaseAmounts[0]/1.e3, 'xmax': IncreaseAmounts[-1]/1.e3,
         'ylabel': 'Break Even Age',
         'xlabel': 'Max Standard Income Increase [2022 $K]',
         'TitleText': 'Break Even Age vs \n Increased Max Standard Income',
         # 'LegendLoc': 'upper right',
         'LegendOn': False,
         'SaveFile': OutDir+'BreakEvenAgeVsIncreasedStandardIncome.png'}
    PlotDict.update(UpdateDict)
    MultiPlot(PlotDict)

#############################################################################################################

# Vary how much extra standard income is generated shortly before RMDs start
if ExtraStandardIncomeLaterInSimulation:
    IncreaseAmounts = np.arange(0.,9500.,500.)
    FinalTotalDiff = np.zeros(len(IncreaseAmounts))
    BreakEvenAge = np.zeros(len(IncreaseAmounts))
    MinTotalDiff = np.zeros(len(IncreaseAmounts))
    IncDict['AgeMaxStandardIncomeChangeWillStart'] = np.array([64], dtype=float)  # using first person in CurrentAge array

    for ct in range(0,len(IncreaseAmounts)):
        IncDict['MaxStandardIncomeChange'] = np.array([IncreaseAmounts[ct]], dtype=float)
        ProjArraysIncreasedStandardIncome = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,
                                                             NumYearsToProject, R, FilingStatus,TPMwithdraw457bFirst)

        TotalDiffArray = ProjArraysIncreasedStandardIncome['TotalAssets']-ProjArrays['TotalAssets']
        # Compute diff in final total
        FinalTotalDiff[ct] = TotalDiffArray[-1]

        # Compute "break even" Age
        if IncreaseAmounts[ct] > 0. and np.any(TotalDiffArray>0.):
            BreakEvenIndex = np.where(TotalDiffArray>0.)[0][0]
            BreakEvenAge[ct] = ProjArrays['Age'][BreakEvenIndex,0]
        else:
            BreakEvenAge[ct] = np.nan

        # Compute diff minimum (max negative)
        MinTotalDiff[ct] = np.min(TotalDiffArray)

    # Reset just in case
    IncDict['AgeMaxStandardIncomeChangeWillStart'] = np.array([], dtype=float)
    IncDict['MaxStandardIncomeChange'] = np.array([], dtype=float)

    # Plot diff in final total and diff minimum vs addition to max standard income
    NumPlots = 2 # FinalTotalDiff, MinTotalDiff
    DiffsArray = np.zeros((NumPlots,len(FinalTotalDiff)))
    DiffsArray[0,:] = FinalTotalDiff/1.e3
    DiffsArray[1,:] = MinTotalDiff/1.e3
    PlotLabelArray = ['Final Total Diff','Minimum Total Diff']
    PlotColorArray = ['k','r']
    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncreaseAmounts/1.e3,
         'DepData': DiffsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(DiffsArray)-1, 'ymax': np.max(DiffsArray)+20,
         'xmin': IncreaseAmounts[0]/1.e3, 'xmax': IncreaseAmounts[-1]/1.e3,
         'ylabel': 'Asset Balance Difference [2022 $K]',
         'xlabel': 'Max Standard Income Increase [2022 $K]',
         'TitleText': 'Asset Balance Diffs vs Extra Standard \n Income 34 Years Before RMDs',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AssetDiffsVsExtraStandardIncomeLater.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Plot BreakEvenAge vs addition to max standard income
    NumPlots = 1 # BreakEvenAge
    AgeArray = np.zeros((NumPlots,len(BreakEvenAge)))
    AgeArray[0,:] = BreakEvenAge
    PlotLabelArray = ['']
    PlotColorArray = ['k']
    PlotDict = copy.deepcopy(DefaultPlotDict)
    UpdateDict = \
        {'IndepData': IncreaseAmounts/1.e3,
         'DepData': AgeArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 89, 'ymax': 92,
         # 'ymin': np.min(AgeArray)-1, 'ymax': np.max(AgeArray)+1,
         'xmin': IncreaseAmounts[0]/1.e3, 'xmax': IncreaseAmounts[-1]/1.e3,
         'ylabel': 'Break Even Age',
         'xlabel': 'Max Standard Income Increase [2022 $K]',
         'TitleText': 'Break Even Age vs \n Extra Standard Income Later In Life',
         # 'LegendLoc': 'upper right',
         'LegendOn': False,
         'SaveFile': OutDir+'BreakEvenAgeVsExtraStandardIncomeLater.png'}
    PlotDict.update(UpdateDict)
    MultiPlot(PlotDict)

#############################################################################################################

# Plot diffs for single increase amount vs default
if RunAndPlotDiffsSingleExtraIncome:
    DefaultMaxStandardIncome = IncDict['MaxStandardIncome']
    IncDict['MaxStandardIncome'] = DefaultMaxStandardIncome + 8000.
    ProjArraysIncreasedStandardIncome = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,
                                                         NumYearsToProject, R, FilingStatus,TPMwithdraw457bFirst)
    NumPlots = 6 # TotalAssets, PostTaxTotal, PreTax, PreTax457b, Roth, CashCushion
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = (ProjArraysIncreasedStandardIncome['TotalAssets']-ProjArrays['TotalAssets'])/1.e6
    AssetsArray[1,:] = (ProjArraysIncreasedStandardIncome['PostTaxTotal']-ProjArrays['PostTaxTotal'])/1.e6
    AssetsArray[2,:] = (ProjArraysIncreasedStandardIncome['PreTaxTotal']-ProjArrays['PreTaxTotal'])/1.e6
    AssetsArray[3,:] = (ProjArraysIncreasedStandardIncome['PreTax457bTotal']-ProjArrays['PreTax457bTotal'])/1.e6
    AssetsArray[4,:] = (ProjArraysIncreasedStandardIncome['RothTotal']-ProjArrays['RothTotal'])/1.e6
    AssetsArray[5,:] = (ProjArraysIncreasedStandardIncome['CashCushion']-ProjArrays['CashCushion'])/1.e6

    PlotLabelArray = ['Total, Final $'+'{:.3f}M'.format((ProjArraysIncreasedStandardIncome['TotalAssets'][-1]-
                                                         ProjArrays['TotalAssets'][-1])/1.e6),'PostTaxTotal','PreTax',
                      'PreTax457b','Roth','CashCushion','CapGains']
    PlotColorArray = ['k','r','b','g','c','m']

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
         #'ymin': np.min(AssetsArray)-0.1, 'ymax': np.max(AssetsArray)+0.1,
         'ymin': -2., 'ymax': 3.,
         'xmin': ProjArrays['Age'][0,0], 'xmax': ProjArrays['Age'][-1,0],
         'ylabel': 'Asset Balance Difference [2022 $M]',
         'xlabel': 'Age',
         'TitleText': 'Asset Balance Diffs vs Age, Annual ROI 7%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AssetBalancesVsAgeDiffs8000.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

############################################################################################################

# # Print relevant numbers to output file (e.g. final asset values, etc.)
#
# file=open(OutputFile,'w')
# file.write('WithdrawalOptimization.py\n\n')
#
# file.write('Total Final: $'+'{:.2f}'.format(ProjArrays['TotalAssets'][-1])+'\n')
# file.write('PostTaxTotal Final: $'+'{:.2f}'.format(ProjArrays['PostTaxTotal'][-1])+'\n')
# file.write('PreTax Final: $'+'{:.2f}'.format(ProjArrays['PreTaxTotal'][-1])+'\n')
# file.write('PreTax457b Final: $'+'{:.2f}'.format(ProjArrays['PreTax457bTotal'][-1])+'\n')
# file.write('Roth Final: $'+'{:.2f}'.format(ProjArrays['RothTotal'][-1])+'\n')
# file.write('CashCushion Final: $'+'{:.2f}'.format(ProjArrays['CashCushion'][-1])+'\n')
# file.write('CapGainsTotal Final: $'+'{:.2f}'.format(ProjArrays['CapGainsTotal'][-1])+'\n')
# file.write('Taxes Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Taxes']))+'\n')
# file.write('Penalties Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Penalties']))+'\n')
# file.write('RMDs Total: $'+'{:.2f}'.format(np.sum(ProjArrays['RMDtotal']))+'\n')
#
# file.close()

#############################################################################################################
