# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/impact-of-fire-on-social-security-income/)

# ImpactOfFIREonSocSecTemplate.py

import numpy as np
import os
import copy
# import time

from Multiplot import *
from SocialSecurityCalculation.ComputePIA import *

# Assess the impact of retiring early in life on Social Security payments

# Assumptions:
# 1. All input and output values, and assumed investment returns, in present-day dollars
# 2. Full retirement age = 67 (true for everyone born after 1960)
# 3. You've earned 4 credits for every year you've worked ($1640*4 = $6560/year in 2023 dollars), which means you must
# work at least 10 years to receive SocSec at all (40 credit minimum)
# 4. You turn 62 in 2023 or later (so will use the PIA bend points published for 2023)

#############################################################################################################
# User Inputs

# Average inflation-adjusted annual earnings over your entire career (no matter how short)
# Using 2022 median individual income, which is $1059 weekly, translated to yearly income
# https://www.bls.gov/cps/cpsaat39.htm
AverageAnnualEarnings = 1059.*52.

# Number of years you worked
NumYearsWorked = 40.-22.

# After-inflation annual investment return
# https://www.thesimpledollar.com/investing/stocks/where-does-7-come-from-when-it-comes-to-long-term-stock-returns/?
# "For the period 1950 to 2009, if you adjust the S&P 500 for inflation and account for dividends, the average annual
# return comes out to exactly 7.0%."
# If 70% equities and 30% bonds (at real 1% ROI), 0.7*7 + 0.3*1 = 5.2%, so we'll just assume 5% ROI for the default
ROI = 0.05

# Output Directory
OutDir = './'

# Flags
SingleScenario = True
SocSecVsRetirementAge = False
SocSecVsRetirementAgeAndIncomes = False
AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncomes = False
AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncomes = False

AnnualIncomeIncreaseRate = 0.01
SocSecVsRetirementAgeAndIncreasingIncomes = False
AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes = False
AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes = False

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Default plotting parameters, using dictionary (can modify if needed)
DefaultPlotDict = \
    {'FigWidth': 10.8, 'FigHeight': 10.8,
     'LineStyle': '-', 'LineWidth': 3,
     'MarkerSize': 10,
     'CopyrightX': 0.01, 'CopyrightY': 1-0.01, 'CopyrightText': 'EngineeringYourFI.com', 'CopyrightFontSize': 20,
     'CopyrightVertAlign': 'top',
     'ylabelFontSize': 30, 'xlabelFontSize': 30,
     'Title_yoffset': 0.99,
     'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20, 'LegendOn': True,
     'PlotSecondaryLines': False,
     'AddTextBox':False,
     'TextBoxX': 0.02,
     'TextBoxY': 0.93,
     'TextBoxFontSize': 20}

#############################################################################################################

# Compute SocSec for single scenario
if SingleScenario:

    # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years (just 35 years
    # here, since assuming you make the same in inflation adjusted terms each year for simplicity)
    if NumYearsWorked > 35.:
        AIME = AverageAnnualEarnings * 35. / 35. / 12.
    else:
        AIME = AverageAnnualEarnings * NumYearsWorked / 35. / 12.
    # Create needed dictionary
    Income = {'AIME': AIME}

    # Compute Primary Insurance Amount (PIA) in present-day dollars
    PIA = ComputePIA(Income,2023-62)
    if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
        PIA = 0.

    AnnualPIA = PIA * 12.

    print("Annual SocSec Income at Full Retirement Age: $",np.round(PIA*12.,2))

    # Compute PIA if you retired at age 67
    Income = {'AIME': AverageAnnualEarnings * 35. / 35. / 12.}
    PIAifRetireAt67 = ComputePIA(Income,2023-62)
    AnnualPIAifRetireAt67 = PIAifRetireAt67 * 12.

    StartingAge = 22
    RetirementAge = StartingAge + NumYearsWorked
    AnnualPIAdiff = AnnualPIAifRetireAt67 - AnnualPIA
    AdditionalSavingsNeededAt67 = AnnualPIAdiff * 25. # Using 4% rule, can make more conservative if desired
    AdditionalSavingsNeededAtRetirementAge = AdditionalSavingsNeededAt67 / (1.+ROI)**(67 - RetirementAge)

    print("Additional Savings Need to Offset Lost SocSec Income at Full Retirement Age: $",np.round(AdditionalSavingsNeededAtRetirementAge,2))

#############################################################################################################

# Compute and plot SocSec income for range of working years durations
if SocSecVsRetirementAge:

    StartingAge = 22
    RetirementAges = range(30,67)
    SocSecArray = np.zeros(len(RetirementAges))

    # Loop over retirement ages
    for ct in range(0,len(RetirementAges)):

        NumYearsWorked = RetirementAges[ct] - StartingAge

        # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years (just 35 years
        # here, since assuming you make the same in inflation adjusted terms each year for simplicity)
        if NumYearsWorked > 35.:
            AIME = AverageAnnualEarnings * 35. / 35. / 12.
        else:
            AIME = AverageAnnualEarnings * NumYearsWorked / 35. / 12.
        # Create needed dictionary
        Income = {'AIME': AIME}

        # Compute Primary Insurance Amount (PIA) in present-day dollars
        PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
        if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
            PIA = 0.

        # Yearly SocSec Income
        SocSecArray[ct] = PIA*12.

    # Plot SocSec Income vs retirement ages

    NumPlots = 1
    PlotLabelArray = ['Average Annual Working \n Income = $'+'{:.2f}'.format(AverageAnnualEarnings)]
    PlotColorArray = ['k']

    # Text box string
    TextBoxString = 'Starting Work Age = '+'{:d}'.format(StartingAge)

    # DepData array must be 2D for MultiPlot
    SocSecArray2D = np.zeros((1,len(SocSecArray)))
    SocSecArray2D[0,:] = SocSecArray

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': SocSecArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(SocSecArray/1000.)+1.5,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Social Security Income [$K/year]',
         'xlabel': 'Retirement Age',
         'TitleText': 'SocSec Income vs Retirement Age',
         'LegendLoc': 'center right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'SocSecVsRetirementAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot SocSec income for range of working years durations and range of incomes
if SocSecVsRetirementAgeAndIncomes:

    StartingAge = 22
    RetirementAges = range(30,67)
    IncomeArray = np.arange(40000.,130000.,10000.)
    SocSecArray = np.zeros((len(IncomeArray),len(RetirementAges)))

    # Loop over incomes
    for ct1 in range(len(IncomeArray)):

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            NumYearsWorked = RetirementAges[ct2] - StartingAge

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years (just 35 years
            # here, since assuming you make the same in inflation adjusted terms each year for simplicity)
            if NumYearsWorked > 35.:
                AIME = IncomeArray[ct1] * 35. / 35. / 12.
            else:
                AIME = IncomeArray[ct1] * NumYearsWorked / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            # Yearly SocSec Income
            SocSecArray[ct1,ct2] = PIA*12.

    # Plot SocSec Income vs retirement ages

    NumPlots = SocSecArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Avg Income $'+'{:.0f}'.format(IncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange']

    # Text box string
    TextBoxString = 'Starting Work Age = '+'{:d}'.format(StartingAge)

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': SocSecArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(SocSecArray/1000.)+1.5,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Social Security Income [$K/year]',
         'xlabel': 'Retirement Age',
         'TitleText': 'SocSec Income vs Retirement Age And Income',
         'LegendLoc': 'lower right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'SocSecVsRetirementAgeAndIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot how much additional savings need you need at each retirement age to make up for the lost
# SocSec (as compared to working until standard full retirement age 67), for different income levels
if AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncomes:

    StartingAge = 22
    RetirementAges = range(30,67)
    IncomeArray = np.arange(40000.,130000.,10000.)
    AdditionalSavingsArray = np.zeros((len(IncomeArray),len(RetirementAges)))

    # Loop over incomes
    for ct1 in range(len(IncomeArray)):

        # Compute PIA if you retired at age 67
        Income = {'AIME': IncomeArray[ct1] * 35. / 35. / 12.}
        PIAifRetireAt67 = ComputePIA(Income,2023-62)
        AnnualPIAifRetireAt67 = PIAifRetireAt67 * 12.

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            NumYearsWorked = RetirementAges[ct2] - StartingAge

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years (just 35 years
            # here, since assuming you make the same in inflation adjusted terms each year for simplicity)
            if NumYearsWorked > 35.:
                AIME = IncomeArray[ct1] * 35. / 35. / 12.
            else:
                AIME = IncomeArray[ct1] * NumYearsWorked / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            AnnualPIA = PIA * 12.

            AnnualPIAdiff = AnnualPIAifRetireAt67 - AnnualPIA
            AdditionalSavingsNeededAt67 = AnnualPIAdiff * 25. # Using 4% rule, can make more conservative if desired
            AdditionalSavingsNeededAtRetirementAge = AdditionalSavingsNeededAt67 / (1.+ROI)**(67 - RetirementAges[ct2])

            # Additional savings array
            AdditionalSavingsArray[ct1,ct2] = AdditionalSavingsNeededAtRetirementAge

    # Generate Plot

    NumPlots = AdditionalSavingsArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Avg Income $'+'{:.0f}'.format(IncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange']

    # Text box string
    TextBoxString = 'Starting Work Age = '+'{:d}'.format(StartingAge)

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': AdditionalSavingsArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(AdditionalSavingsArray/1000.)+1.5,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Additional Savings Needed [$K]',
         'xlabel': 'Retirement Age',
         'TitleText': 'Additional Savings To Offset Lost SocSec',
         'LegendLoc': 'upper right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Zoomed plot
    UpdateDict = \
        {'ymin': 0., 'ymax': 100.,
         'TextBoxX': 0.2,
         'TextBoxY': 0.93,
         'SaveFile': OutDir+'AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncomesZoom.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot how much additional work time is needed at each retirement age to generate the additional
# savings needed to make up for the lost SocSec (as compared to working until standard full retirement age
# 67), for different income levels.
if AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncomes:

    StartingAge = 22
    SavingsRate = 0.5 # at retirement age, might be higher or lower before that
    RetirementAges = range(30,67)
    IncomeArray = np.arange(40000.,130000.,10000.)
    FIassetsArray = IncomeArray*(1.-SavingsRate)*25.
    AdditionalSavingsTimeArray = np.zeros((len(IncomeArray),len(RetirementAges)))

    # Loop over incomes
    for ct1 in range(len(IncomeArray)):

        # Compute PIA if you retired at age 67
        Income = {'AIME': IncomeArray[ct1] * 35. / 35. / 12.}
        PIAifRetireAt67 = ComputePIA(Income,2023-62)
        AnnualPIAifRetireAt67 = PIAifRetireAt67 * 12.

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            NumYearsWorked = RetirementAges[ct2] - StartingAge

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years (just 35 years
            # here, since assuming you make the same in inflation adjusted terms each year for simplicity)
            if NumYearsWorked > 35.:
                AIME = IncomeArray[ct1] * 35. / 35. / 12.
            else:
                AIME = IncomeArray[ct1] * NumYearsWorked / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            AnnualPIA = PIA * 12.

            AnnualPIAdiff = AnnualPIAifRetireAt67 - AnnualPIA
            AdditionalSavingsNeededAt67 = AnnualPIAdiff * 25. # Using 4% rule, can make more conservative if desired
            AdditionalSavingsNeededAtRetirementAge = AdditionalSavingsNeededAt67 / (1.+ROI)**(67 - RetirementAges[ct2])

            # Compute how long to acheive that additional savings at retirement age
            AssetIncreasePerYear = FIassetsArray[ct1]*ROI + IncomeArray[ct1]*SavingsRate # assuming 50% savings
            AdditionalSavingsTimeArray[ct1,ct2] = AdditionalSavingsNeededAtRetirementAge / AssetIncreasePerYear # years

    # Generate Plot

    NumPlots = AdditionalSavingsTimeArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Avg Income $'+'{:.0f}'.format(IncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange']

    # Text box string
    TextBoxString = 'Starting Work Age = '+'{:d}'.format(StartingAge)

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': AdditionalSavingsTimeArray*12.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(AdditionalSavingsTimeArray*12.)+0.05*12.,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Additional Time Needed [Months]',
         'xlabel': 'Retirement Age',
         'TitleText': 'Additional Work Time Needed To Offset Lost SocSec',
         'TitleFontSize': 29,
         'LegendLoc': 'upper right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Zoomed plot
    UpdateDict = \
        {'ymin': 0., 'ymax': 12.,
         'TextBoxX': 0.2,
         'TextBoxY': 0.93,
         'SaveFile': OutDir+'AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncomesZoom.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot SocSec income for range of working years durations and range of INCREASING incomes
if SocSecVsRetirementAgeAndIncreasingIncomes:

    StartingAge = 22
    RetirementAges = range(30,67)
    StartingIncomeArray = np.arange(40000.,130000.,10000.)
    SocSecArray = np.zeros((len(StartingIncomeArray),len(RetirementAges)))

    # Loop over starting incomes
    for ct1 in range(len(StartingIncomeArray)):

        # Create initial set of incomes, leading up to initial retirement age, will append with each
        # subsequent iteration of retirement age loop
        IncomeHistory = []
        for ct2 in range(RetirementAges[0]-StartingAge):
            IncomeHistory.append(round(StartingIncomeArray[ct1]*(1+AnnualIncomeIncreaseRate)**(ct2),2))

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            # compute number of years worked, not including current retirement year
            NumYearsWorked = (RetirementAges[ct2]-1) - (StartingAge-1)

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years
            # (assumed to be the most recent 35 years, assuming increase of income each year)
            if NumYearsWorked > 35.:
                AIME = np.sum(IncomeHistory[-35:]) / 35. / 12.
            else:
                AIME = np.sum(IncomeHistory) / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            # Yearly SocSec Income
            SocSecArray[ct1,ct2] = PIA*12.

            # Now compute the income for this year if you hadn't retired
            CurrentIncome = round(StartingIncomeArray[ct1] * (1+AnnualIncomeIncreaseRate)**(NumYearsWorked),2)
            if CurrentIncome > 160200.: # max taxable income for SocSec
                CurrentIncome = 160200.
            IncomeHistory.append(CurrentIncome)

    # Plot SocSec Income vs retirement ages

    NumPlots = SocSecArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Starting Income $'+'{:.0f}'.format(StartingIncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange']

    # Text box string
    TextBoxString = ('Starting Work Age = '+'{:d}'.format(StartingAge)+'\n'+'{:.0f}'.format(AnnualIncomeIncreaseRate*100) +
                     '% Annual Real Salary Increase')

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': SocSecArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(SocSecArray/1000.)+1.5,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Social Security Income [$K/year]',
         'xlabel': 'Retirement Age',
         'TitleText': 'SocSec Income vs Retirement Age And Income',
         'LegendLoc': 'lower right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'SocSecVsRetirementAgeAndIncreasingIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot how much additional savings need you need at each retirement age to make up for the lost
# SocSec (as compared to working until standard full retirement age 67), for different INCREASING income levels
if AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes:

    StartingAge = 22
    RetirementAges = range(30,67)
    StartingIncomeArray = np.arange(40000.,130000.,10000.)
    AdditionalSavingsArray = np.zeros((len(StartingIncomeArray),len(RetirementAges)))

    # Loop over starting incomes
    for ct1 in range(len(StartingIncomeArray)):

        # Create initial set of incomes, leading up to initial retirement age, will append with each
        # subsequent iteration of retirement age loop
        IncomeHistory = []
        for ct2 in range(RetirementAges[0]-StartingAge):
            IncomeHistory.append(round(StartingIncomeArray[ct1]*(1+AnnualIncomeIncreaseRate)**(ct2),2))

        # Compute PIA if you retired at age 67
        # First generate income history to FRA (age 67)
        IncomeHistoryToFRA = []
        for ct2 in range(67-StartingAge):
            CurrentIncome = round(StartingIncomeArray[ct1] * (1+AnnualIncomeIncreaseRate)**(ct2),2)
            if CurrentIncome > 160200.: # max taxable income for SocSec
                CurrentIncome = 160200.
            IncomeHistoryToFRA.append(CurrentIncome)
        # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years
        # (assumed to be the most recent 35 years, assuming increase of income each year)
        Income = {'AIME': np.sum(IncomeHistoryToFRA[-35:]) / 35. / 12.}
        PIAifRetireAt67 = ComputePIA(Income,2023-62)
        AnnualPIAifRetireAt67 = PIAifRetireAt67 * 12.

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            # compute number of years worked, not including current retirement year
            NumYearsWorked = (RetirementAges[ct2]-1) - (StartingAge-1)

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years
            if NumYearsWorked > 35.:
                AIME = np.sum(IncomeHistory[-35:]) / 35. / 12.
            else:
                AIME = np.sum(IncomeHistory) / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            AnnualPIA = PIA * 12.

            AnnualPIAdiff = AnnualPIAifRetireAt67 - AnnualPIA
            AdditionalSavingsNeededAt67 = AnnualPIAdiff * 25. # Using 4% rule, can make more conservative if desired
            AdditionalSavingsNeededAtRetirementAge = AdditionalSavingsNeededAt67 / (1.+ROI)**(67 - RetirementAges[ct2])

            # Additional savings array
            AdditionalSavingsArray[ct1,ct2] = AdditionalSavingsNeededAtRetirementAge

            # Now compute the income for this year if you hadn't retired
            CurrentIncome = round(StartingIncomeArray[ct1] * (1+AnnualIncomeIncreaseRate)**(NumYearsWorked),2)
            if CurrentIncome > 160200.: # max taxable income for SocSec
                CurrentIncome = 160200.
            IncomeHistory.append(CurrentIncome)

    # Generate Plot

    NumPlots = AdditionalSavingsArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Starting Income $'+'{:.0f}'.format(StartingIncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange']

    # Text box string
    TextBoxString = ('Starting Work Age = '+'{:d}'.format(StartingAge)+'\n'+'{:.0f}'.format(AnnualIncomeIncreaseRate*100) +
                     '% Annual Real Salary Increase')

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': AdditionalSavingsArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(AdditionalSavingsArray/1000.)+1.5,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Additional Savings Needed [$K]',
         'xlabel': 'Retirement Age',
         'TitleText': 'Additional Savings To Offset Lost SocSec',
         'LegendLoc': 'upper right',
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Zoomed plot
    UpdateDict = \
        {'ymin': 0., 'ymax': 125.,
         'TextBoxX': 0.02,
         'TextBoxY': 0.40,
         'SaveFile': OutDir+'AdditionalSavingsNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomesZoom.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot how much additional work time is needed at each retirement age to generate the additional
# savings needed to make up for the lost SocSec (as compared to working until standard full retirement age
# 67), for different INCREASING income levels.
if AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes:

    StartingAge = 22
    SavingsRate = 0.5 # at retirement age, might be higher or lower before that
    RetirementAges = range(30,67)
    StartingIncomeArray = np.arange(40000.,130000.,10000.)
    AdditionalSavingsTimeArray = np.zeros((len(StartingIncomeArray),len(RetirementAges)))

    # Loop over incomes
    for ct1 in range(len(StartingIncomeArray)):

        # Create initial set of incomes, leading up to initial retirement age, will append with each
        # subsequent iteration of retirement age loop
        IncomeHistory = []
        for ct2 in range(RetirementAges[0]-StartingAge):
            IncomeHistory.append(round(StartingIncomeArray[ct1]*(1+AnnualIncomeIncreaseRate)**(ct2),2))

        # Compute PIA if you retired at age 67
        # First generate income history to FRA (age 67)
        IncomeHistoryToFRA = []
        for ct2 in range(67-StartingAge):
            CurrentIncome = round(StartingIncomeArray[ct1] * (1+AnnualIncomeIncreaseRate)**(ct2),2)
            if CurrentIncome > 160200.: # max taxable income for SocSec
                CurrentIncome = 160200.
            IncomeHistoryToFRA.append(CurrentIncome)
        # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years
        # (assumed to be the most recent 35 years, assuming increase of income each year)
        Income = {'AIME': np.sum(IncomeHistoryToFRA[-35:]) / 35. / 12.}
        PIAifRetireAt67 = ComputePIA(Income,2023-62)
        AnnualPIAifRetireAt67 = PIAifRetireAt67 * 12.

        # Loop over retirement ages
        for ct2 in range(len(RetirementAges)):

            # compute number of years worked, not including current retirement year
            NumYearsWorked = (RetirementAges[ct2]-1) - (StartingAge-1)

            # Compute Average inflation-adjusted monthly earnings (AIME) over 35 highest earning years
            if NumYearsWorked > 35.:
                AIME = np.sum(IncomeHistory[-35:]) / 35. / 12.
            else:
                AIME = np.sum(IncomeHistory) / 35. / 12.
            # Create needed dictionary
            Income = {'AIME': AIME}

            # Compute Primary Insurance Amount (PIA) in present-day dollars
            PIA = ComputePIA(Income,2023-62) # assume turn 62 in 2023 or later
            if NumYearsWorked < 10: # must have at least 40 credits, and you can earn at most 4 per year
                PIA = 0.

            AnnualPIA = PIA * 12.

            AnnualPIAdiff = AnnualPIAifRetireAt67 - AnnualPIA
            AdditionalSavingsNeededAt67 = AnnualPIAdiff * 25. # Using 4% rule, can make more conservative if desired
            AdditionalSavingsNeededAtRetirementAge = AdditionalSavingsNeededAt67 / (1.+ROI)**(67 - RetirementAges[ct2])

            # Compute FI assets at retirement: Final income at retirement * (1.-SavingsRate) * 25
            FIassets = IncomeHistory[-1] * (1.-SavingsRate)*25.

            # Compute how long to achieve that additional savings at retirement age
            AssetIncreasePerYear = FIassets*ROI + IncomeHistory[-1]*SavingsRate # assuming 50% savings
            AdditionalSavingsTimeArray[ct1,ct2] = AdditionalSavingsNeededAtRetirementAge / AssetIncreasePerYear # years

            # Now compute the income for this year if you hadn't retired
            CurrentIncome = round(StartingIncomeArray[ct1] * (1+AnnualIncomeIncreaseRate)**(NumYearsWorked),2)
            if CurrentIncome > 160200.: # max taxable income for SocSec
                CurrentIncome = 160200.
            IncomeHistory.append(CurrentIncome)

    # Generate Plot

    NumPlots = AdditionalSavingsTimeArray.shape[0]
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Starting Income $'+'{:.0f}'.format(StartingIncomeArray[ct]/1000.)+'K')
    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange'] 

    # Text box string
    TextBoxString = ('Starting Work Age = '+'{:d}'.format(StartingAge)+'\n'+'{:.0f}'.format(AnnualIncomeIncreaseRate*100) +
                     '% Annual Real Salary Increase')

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': RetirementAges,
         'DepData': AdditionalSavingsTimeArray*12.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(AdditionalSavingsTimeArray*12.)+0.05*12.,
         'xmin': RetirementAges[0], 'xmax': RetirementAges[-1],
         'ylabel': 'Additional Time Needed [Months]',
         'xlabel': 'Retirement Age',
         'TitleText': 'Additional Work Time Needed To Offset Lost SocSec',
         'TitleFontSize': 29,
         'LegendLoc': 'upper right', #'lower right', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Zoomed plot
    UpdateDict = \
        {'ymin': 0., 'ymax': 15.,
         'TextBoxX': 0.02,
         'TextBoxY': 0.30,
         'SaveFile': OutDir+'AdditionalTimeNeededToOffsetLostSocSecVsRetirementAgeAndIncreasingIncomesZoom.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)