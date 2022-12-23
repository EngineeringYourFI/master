# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-method-stress-testing/)

# StressTestingAnalysis.py

import numpy as np
import copy
import os
import time

from WithdrawalOptimization.TaxRateInfoInput import TaxRateInfoInput
from WithdrawalOptimization.SupportMethods import MultiPlot
from WithdrawalOptimization.ProjFinalBalance import ProjFinalBalance
from WithdrawalOptimization.ProjFinalBalanceTraditional import ProjFinalBalanceTraditional

# Vary expenses and ROI to assess how the Traditional and TPM withdrawal methods fare

#############################################################################################################
# Inputs

# Bring in 2022 income tax bracket info, used for inputs (modify if beyond 2022)
TaxRateInfo = TaxRateInfoInput()

# Scenario 1, MarriedFilingJointly
Scenario1 = True
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
    # Note: Once you've reached full retirement age (67 if born after 1960), you can earn as much as you want with no penalties.
    # Before your full retirement age, you can earn up to $19,560 per year (as of 2022) without having your Social Security
    # payments reduced. Bad news: If you earn over this limit, your benefits will be cut. Good news: When you reach full
    # retirement age, any withheld benefits will be returned to you in the form of higher monthly payments.
    # https://investor.vanguard.com/investor-resources-education/article/top-questions-about-social-security

    # Maximum standard income to achieve (not LT cap gains)
    MaxStandardIncome = TaxRateInfo['MarriedFilingJointlyStandardDeduction']

    # When old enough to collect SS, no longer need to worry about ACA subsidies, so set equal to top of 0% LT cap gains bracket
    SpecifiedIncomeAfterACA = TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'][1]

    # always put older person first
    CurrentAge = np.array([40,38])

    FilingStatus = 'MarriedFilingJointly' # 'Single' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'


# Scenario 2, Single
Scenario2 = False
if Scenario2:
    PreTaxIV = np.array([400000.], dtype=float)
    PreTax457bIV = np.array([100000.], dtype=float)
    RothIV = np.array([80000.+20000.], dtype=float)
    RothContributions = np.array([40000.+20000.], dtype=float)
    SocialSecurityPayments = np.array([17000], dtype=float)
    AgeSSwillStart = np.array([67], dtype=float)
    MaxStandardIncome = TaxRateInfo['SingleStandardDeduction']
    SpecifiedIncomeAfterACA = TaxRateInfo['SingleIncomeBracketLTcapGainsMins'][1]
    CurrentAge = np.array([40])
    FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

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
CashCushion = 0. #20000. #

# TotalIV = PreTaxIV + PreTax457bIV + np.sum(PostTaxIV) + RothIV + CashCushion

# Retirement Income
# Dividends
QualifiedDividendYield = 0.016 # based on 5-year average dividend yield of VTSAX
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
Exp = 40000.

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
TPMorTraditionalWithdrawal = 'Both' #'TPM' #'Traditional' #

# TPM Method - Withdraw from 457b or Pretax first
TPMwithdraw457bFirst = True

# Analysis Flags
VaryExpensesAnalysis = True
VaryExpensesAnalysisFinalAssets = False
VaryExpensesAnalysisOutOfMoneyAges = True
VaryROIanalysis = False

# Plot flags
# if VaryExpensesAnalysis:
FinalTotalAssetBalanceVsExpensesBothMethods = False # if VaryExpensesAnalysisFinalAssets
FinalTotalAssetBalanceVsExpensesDiffMethods = False # if VaryExpensesAnalysisFinalAssets
OutOfMoneyAgeVsExpensesBothMethods = True # if VaryExpensesAnalysisOutOfMoneyAges
OutOfMoneyAgeVsExpensesDiffMethods = True # if VaryExpensesAnalysisOutOfMoneyAges
# VaryROIanalysis
FinalTotalAssetBalanceVsROIbothMethods = False
FinalTotalAssetBalanceVsROIdiffMethods = False
OutOfMoneyAgeVsROIbothMethods = False
OutOfMoneyAgeVsROIdiffMethods = False

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
# Run simulation for variety of expense levels
if VaryExpensesAnalysis:
    if VaryExpensesAnalysisFinalAssets:
        MinExpense = 30000.
        MaxExpense = 80000.
    if VaryExpensesAnalysisOutOfMoneyAges:
        MinExpense = 60000.
        MaxExpense = 120000.
    ExpenseDelta = 1000.
    ExpenseRange = np.arange(MinExpense,MaxExpense,ExpenseDelta)
    FinalBalance = np.zeros(len(ExpenseRange))
    FinalBalanceTPM = np.zeros(len(ExpenseRange))
    FinalBalanceTraditional = np.zeros(len(ExpenseRange))
    OutOfMoneyAge = np.zeros(len(ExpenseRange))
    OutOfMoneyAgeTPM = np.zeros(len(ExpenseRange))
    OutOfMoneyAgeTraditional = np.zeros(len(ExpenseRange))

    t0 = time.time()

    for ct in range(len(ExpenseRange)):
        ExpDict['Exp'] = ExpenseRange[ct]
        print('Expenses = $',ExpenseRange[ct])

        if TPMorTraditionalWithdrawal == 'TPM':
            ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                          FilingStatus,TPMwithdraw457bFirst)
            FinalBalance[ct] = ProjArrays['TotalAssets'][-1]
            OutOfMoneyAge[ct] = ProjArrays['OutOfMoneyAge']
        elif TPMorTraditionalWithdrawal == 'Traditional':
            ProjArrays = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                                     FilingStatus)
            FinalBalance[ct] = ProjArrays['TotalAssets'][-1]
            OutOfMoneyAge[ct] = ProjArrays['OutOfMoneyAge']
        elif TPMorTraditionalWithdrawal == 'Both':
            ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                          FilingStatus,TPMwithdraw457bFirst)
            ProjArraysTraditional = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,
                                                                NumYearsToProject, R,FilingStatus)
            FinalBalanceTPM[ct] = ProjArrays['TotalAssets'][-1]
            FinalBalanceTraditional[ct] = ProjArraysTraditional['TotalAssets'][-1]
            OutOfMoneyAgeTPM[ct] = ProjArrays['OutOfMoneyAge']
            OutOfMoneyAgeTraditional[ct] = ProjArraysTraditional['OutOfMoneyAge']

    t1 = time.time()
    SimTime = t1-t0
    print('Projection Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################
# Run simulation for variety of assumed average ROI levels
if VaryROIanalysis:
    MinROI = -0.07 # 7%/year loss (after inflation) - hopefully wildly pessimistic
    MaxROI = 0.14 # 14%/year gain (after inflation) - likely wildly optimistic
    ROIdelta = 0.01
    ROIrange = np.arange(MinROI,MaxROI,ROIdelta)
    FinalBalance = np.zeros(len(ROIrange))
    FinalBalanceTPM = np.zeros(len(ROIrange))
    FinalBalanceTraditional = np.zeros(len(ROIrange))
    OutOfMoneyAge = np.zeros(len(ROIrange))
    OutOfMoneyAgeTPM = np.zeros(len(ROIrange))
    OutOfMoneyAgeTraditional = np.zeros(len(ROIrange))

    t0 = time.time()

    for ct in range(len(ROIrange)):
        R = ROIrange[ct]
        print('ROI = ',ROIrange[ct])

        if TPMorTraditionalWithdrawal == 'TPM':
            ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                          FilingStatus,TPMwithdraw457bFirst)
            FinalBalance[ct] = ProjArrays['TotalAssets'][-1]
            OutOfMoneyAge[ct] = ProjArrays['OutOfMoneyAge']
        elif TPMorTraditionalWithdrawal == 'Traditional':
            ProjArrays = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                                     FilingStatus)
            FinalBalance[ct] = ProjArrays['TotalAssets'][-1]
            OutOfMoneyAge[ct] = ProjArrays['OutOfMoneyAge']
        elif TPMorTraditionalWithdrawal == 'Both':
            ProjArrays = ProjFinalBalance(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,NumYearsToProject, R,
                                          FilingStatus,TPMwithdraw457bFirst)
            ProjArraysTraditional = ProjFinalBalanceTraditional(TaxRateInfo,IVdict,IncDict,ExpDict,CurrentAge,
                                                                NumYearsToProject, R,FilingStatus)
            FinalBalanceTPM[ct] = ProjArrays['TotalAssets'][-1]
            FinalBalanceTraditional[ct] = ProjArraysTraditional['TotalAssets'][-1]
            OutOfMoneyAgeTPM[ct] = ProjArrays['OutOfMoneyAge']
            OutOfMoneyAgeTraditional[ct] = ProjArraysTraditional['OutOfMoneyAge']

    t1 = time.time()
    SimTime = t1-t0
    print('Projection Time: '+'{:.2f}'.format(SimTime)+' seconds')

#############################################################################################################
# Varying expenses plots
#############################################################################################################
# Plot Final Total Asset Balance Vs Expenses results for both TPM and Traditional methods
if TPMorTraditionalWithdrawal == 'Both' and FinalTotalAssetBalanceVsExpensesBothMethods and VaryExpensesAnalysis:

    NumPlots = 2
    AssetsArray = np.zeros((NumPlots,len(FinalBalanceTPM)))
    AssetsArray[0,:] = FinalBalanceTPM/1.e6
    AssetsArray[1,:] = FinalBalanceTraditional/1.e6

    PlotLabelArray = ['TPM','Traditional']
    PlotColorArray = ['r','b'] #,'k','g','c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpenseRange/1.e3,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': 30.,
         'xmin': ExpenseRange[0]/1.e3, 'xmax': ExpenseRange[-1]/1.e3,
         'ylabel': 'Final Asset Balance [2022 $M]',
         'xlabel': 'Expenses [2022 $K]',
         'TitleText': 'Final Total Balance Vs Expenses',
         'LegendLoc': 'upper right',
         'LegendOn': True,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'FinalTotalAssetBalanceVsExpensesBothMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot asset diffs Vs Expenses: TPM - Traditional
if TPMorTraditionalWithdrawal == 'Both' and FinalTotalAssetBalanceVsExpensesDiffMethods and VaryExpensesAnalysis:

    NumPlots = 1
    AssetsArray = np.zeros((NumPlots,len(FinalBalanceTPM)))
    AssetsArray[0,:] = (FinalBalanceTPM-FinalBalanceTraditional)/1.e6

    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpenseRange/1.e3,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': 6.,
         'xmin': ExpenseRange[0]/1.e3, 'xmax': ExpenseRange[-1]/1.e3,
         'ylabel': 'Final Asset Balance Diff [2022 $M]',
         'xlabel': 'Expenses [2022 $K]',
         'TitleText': 'Final Total Balance Difference \n (TPM - Traditional) Vs Expenses',
         'LegendLoc': 'upper right',
         'LegendOn': False,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'FinalTotalAssetBalanceVsExpensesDiffMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot Out Of Money Age Vs Expenses results for both TPM and Traditional methods
if TPMorTraditionalWithdrawal == 'Both' and OutOfMoneyAgeVsExpensesBothMethods and VaryExpensesAnalysis:

    NumPlots = 2
    AssetsArray = np.zeros((NumPlots,len(OutOfMoneyAgeTPM)))
    AssetsArray[0,:] = OutOfMoneyAgeTPM
    AssetsArray[1,:] = OutOfMoneyAgeTraditional

    PlotLabelArray = ['TPM','Traditional']
    PlotColorArray = ['r','b']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpenseRange/1.e3,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 30., 'ymax': 90.,
         'xmin': ExpenseRange[0]/1.e3, 'xmax': ExpenseRange[-1]/1.e3,
         'ylabel': 'Out of Money Age (First Person Age) [Years]',
         'xlabel': 'Expenses [2022 $K]',
         'TitleText': 'Out of Money Age Vs Expenses',
         'LegendLoc': 'upper right',
         'LegendOn': True,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'OutOfMoneyAgeVsExpensesBothMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot Out Of Money Age Vs Expenses diffs: TPM - Traditional
if TPMorTraditionalWithdrawal == 'Both' and OutOfMoneyAgeVsExpensesDiffMethods and VaryExpensesAnalysis:

    NumPlots = 1
    AssetsArray = np.zeros((NumPlots,len(OutOfMoneyAgeTPM)))
    AssetsArray[0,:] = OutOfMoneyAgeTPM - OutOfMoneyAgeTraditional

    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpenseRange/1.e3,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 15.,
         'xmin': ExpenseRange[0]/1.e3, 'xmax': ExpenseRange[-1]/1.e3,
         'ylabel': 'Out of Money Age Diff (First Person Age) [Years]',
         'xlabel': 'Expenses [2022 $K]',
         'TitleText': 'Out of Money Age Difference \n (TPM - Traditional) Vs Expenses',
         'LegendLoc': 'upper right',
         'LegendOn': False,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'OutOfMoneyAgeVsExpensesDiffMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################
# Varying ROI plots
#############################################################################################################
# Plot Final Total Asset Balance Vs ROI results for both TPM and Traditional methods
if TPMorTraditionalWithdrawal == 'Both' and FinalTotalAssetBalanceVsROIbothMethods and VaryROIanalysis:

    NumPlots = 2
    AssetsArray = np.zeros((NumPlots,len(FinalBalanceTPM)))
    AssetsArray[0,:] = FinalBalanceTPM/1.e6
    AssetsArray[1,:] = FinalBalanceTraditional/1.e6

    PlotLabelArray = ['TPM','Traditional']
    PlotColorArray = ['r','b']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ROIrange*100,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': 50.,
         'xmin': ROIrange[0]*100, 'xmax': ROIrange[-1]*100,
         'ylabel': 'Final Asset Balance [2022 $M]',
         'xlabel': 'Assumed Average Annual ROI [%]',
         'TitleText': 'Final Total Balance Vs ROI',
         'LegendLoc': 'upper right',
         'LegendOn': True,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'FinalTotalAssetBalanceVsROIbothMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot Final Total Asset Balance Vs ROI results for both TPM and Traditional methods
if TPMorTraditionalWithdrawal == 'Both' and FinalTotalAssetBalanceVsROIdiffMethods and VaryROIanalysis:
    NumPlots = 1
    AssetsArray = np.zeros((NumPlots,len(FinalBalanceTPM)))
    AssetsArray[0,:] = (FinalBalanceTPM-FinalBalanceTraditional)/1.e6

    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ROIrange*100,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': 5.,
         'xmin': ROIrange[0]*100, 'xmax': ROIrange[-1]*100,
         'ylabel': 'Final Asset Balance Diff [2022 $M]',
         'xlabel': 'Assumed Average Annual ROI [%]',
         'TitleText': 'Final Total Balance Difference \n (TPM - Traditional) Vs ROI',
         'LegendLoc': 'upper right',
         'LegendOn': False,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'FinalTotalAssetBalanceVsROIdiffMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot Out Of Money Age Vs ROI results for both TPM and Traditional methods
if TPMorTraditionalWithdrawal == 'Both' and OutOfMoneyAgeVsROIbothMethods and VaryROIanalysis:

    NumPlots = 2
    AssetsArray = np.zeros((NumPlots,len(OutOfMoneyAgeTPM)))
    AssetsArray[0,:] = OutOfMoneyAgeTPM
    AssetsArray[1,:] = OutOfMoneyAgeTraditional

    PlotLabelArray = ['TPM','Traditional']
    PlotColorArray = ['r','b']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ROIrange*100.,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 40., 'ymax': 80.,
         'xmin': ROIrange[0]*100., 'xmax': ROIrange[-1]*100.,
         'ylabel': 'Out of Money Age (First Person Age) [Years]',
         'xlabel': 'Assumed Average Annual ROI [%]',
         'TitleText': 'Out of Money Age Vs ROI',
         'LegendLoc': 'upper right',
         'LegendOn': True,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'OutOfMoneyAgeVsROIbothMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
#############################################################################################################
# Plot Out Of Money Age Vs ROI diffs: TPM - Traditional
if TPMorTraditionalWithdrawal == 'Both' and OutOfMoneyAgeVsROIdiffMethods and VaryROIanalysis:

    NumPlots = 1
    AssetsArray = np.zeros((NumPlots,len(OutOfMoneyAgeTPM)))
    AssetsArray[0,:] = OutOfMoneyAgeTPM - OutOfMoneyAgeTraditional

    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ROIrange*100.,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 6.,
         'xmin': ROIrange[0]*100., 'xmax': ROIrange[-1]*100.,
         'ylabel': 'Out of Money Age Diff (First Person Age) [Years]',
         'xlabel': 'Assumed Average Annual ROI [%]',
         'TitleText': 'Out of Money Age Difference \n (TPM - Traditional) Vs Expenses',
         'LegendLoc': 'upper right',
         'LegendOn': False,
         'Title_yoffset': 1.01,
         'SaveFile': OutDir+'OutOfMoneyAgeVsROIdiffMethods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
