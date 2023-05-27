# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/when-should-you-start-social-security/)

# WhenToStartSocialSecurityTemplate.py

import numpy as np
import os
import copy

from Multiplot import *
from SocialSecurityCalculation.ComputePIA import *
from SocialSecurityCalculation.EarlyLateAdjust import *

# Assess options for when to start taking Social Security Income, known as "Retirement Insurance Benefits" (RIB)

# Assumptions:
# 1. All input and output values, and assumed investment returns, in present-day dollars
# 2. Full retirement age = 67 (true for everyone born after 1960)
# 3. Min 40 credits obtained for eligibility
# 4. No earned income starting at age 62 (to have proper apples-to-apples comparison)
# 5. You turn 62 in 2023 or later (so will use the PIA bend points published for 2023)

# Future work may include loosening assumptions 2, 4, and 5 (allowing user to specify)

#############################################################################################################
# User Inputs

# Average inflation-adjusted monthly earnings over 35 highest earning years
# This is the "AIME" value in the RIB calculation
# Using 2022 median individual income, which is $1059 weekly, translated to monthly income
# https://www.bls.gov/cps/cpsaat39.htm
AIME = 1059.*52./12.

# After-inflation annual investment return
# https://www.thesimpledollar.com/investing/stocks/where-does-7-come-from-when-it-comes-to-long-term-stock-returns/?
# "For the period 1950 to 2009, if you adjust the S&P 500 for inflation and account for dividends, the average annual
# return comes out to exactly 7.0%."
ROI = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'
# Output to screen instead of file:
OutputToScreen = True

# Plot flags
TotalBalvsAge = True

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Assemble dicts
Income = {'AIME': AIME}

#############################################################################################################

# Compute balance over time for each starting age

# Can start social security at any age from 62 to 70
StartAges = range(62,71)
AllAges = range(62,101)

# Balance array
BalanceArray = np.zeros((len(StartAges),len(AllAges)))

# Loop over starting ages
for ct1 in range(len(StartAges)):

    # Compute RIB in present-day dollars for this starting age
    PIA = ComputePIA(Income,2023-62)
    RIBmonthly = np.floor(EarlyLateAdjust(67.,PIA,StartAges[ct1]))
    RIBannual = RIBmonthly*12.

    # Compute balance from age 62 to 100 for each starting age
    for ct2 in range(len(AllAges)):
        # if the current age is at or past the starting age
        if AllAges[ct2] >= StartAges[ct1]:
            # if past the first year (age 62), apply ROI
            if ct2 > 0:
                BalanceArray[ct1,ct2] = BalanceArray[ct1,ct2-1]*(1.+ROI) + RIBannual
            else: # don't apply ROI
                BalanceArray[ct1,ct2] = RIBannual
        else:
            BalanceArray[ct1,ct2] = 0.

#############################################################################################################

# Default plotting parameters, using dictionary (can modify if needed)
DefaultPlotDict = \
    {'FigWidth': 10.8, 'FigHeight': 10.8,
     'LineStyle': '-', 'LineWidth': 3,
     'MarkerSize': 10,
     'CopyrightX': 0.01, 'CopyrightY': 1-0.01, 'CopyrightText': 'EngineeringYourFI.com', 'CopyrightFontSize': 20,
     'CopyrightVertAlign': 'top',
     'ylabelFontSize': 30, 'xlabelFontSize': 30,
     'Title_yoffset': 0.99, #'Title_xoffset': 0.5,
     'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20, 'LegendOn': True,
     'PlotSecondaryLines': False}

#############################################################################################################

# Plot total balance vs starting ages
if TotalBalvsAge:

    NumPlots = 9 # number of starting ages
    PlotLabelArray = []
    for ct in range(len(StartAges)):
        PlotLabelArray.append('Start at '+'{:d}'.format(StartAges[ct]))

    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange'] #

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': AllAges,
         'DepData': BalanceArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(BalanceArray/1000.) + 100.,
         'xmin': AllAges[0], 'xmax': AllAges[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Balance vs Age, '+'{:d}'.format(int(ROI*100))+'% ROI',
         'LegendLoc': 'upper center', #'upper right',
         'SaveFile': OutDir+'TotalBalvsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Compute and plot diff from FRA = 67 balance
    BalanceArrayDiff = np.zeros((len(StartAges),len(AllAges)))
    for ct in range(BalanceArray.shape[0]):
        BalanceArrayDiff[ct,:] = BalanceArray[ct,:] - BalanceArray[5,:]

    UpdateDict = \
        {'DepData': BalanceArrayDiff/1000.,
         'ymin': np.min(BalanceArrayDiff/1000.)-10.,
         'ymax': np.max(BalanceArrayDiff/1000.)+10.,
         'ylabel': 'Balance Difference From FRA (67) Option [$K]',
         'TitleText': 'Balance Difference vs Age, '+'{:d}'.format(int(ROI*100))+'% ROI',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'TotalBalDiffvsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
