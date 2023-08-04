# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/is-it-worth-letting-your-warehouse-club-membership-expire/)

# MinimizeWarehouseMembershipFees.py

import numpy as np
import os
import copy
# import time

from Multiplot import *
from ProjBalance import *

# Determine how long to wait between purchasing annual memberships at warehouse clubs such as Costco, Sam's Club, BJ's

#############################################################################################################
# User Inputs

# Costco annual membership: $60/year
# BJ’s annual membership: $55/year
# Sam’s club annual membership: $50/year
AnnualMembershipFee = 55.

# How much you spend at the warehouse
MonthlySpendAtWarehouse = 250.

# Discount on products purchased, vs other stores (e.g., 20% = 0.2)
# So prices at other stores would be 1/(1-Discount) higher (e.g. 1/(1-0.2) = 1.25, so 25% higher prices)
Discount = 0.2

# Annual Investment ROI (e.g., 5% = 0.05)
# If 70/30 stocks bonds allocation, 7% ROI for stocks and 1% for Bonds, 0.7 * 7% + 0.3 * 1% = 5.2% ROI
AnnualROI = 0.05

# Initial balance - just for showing single scenarios, for comparisons it won't matter
InitBal = 50000.

# Number of years to simulate
NumYears = 20

# Number of months to wait before rejoining after membership expires
NumMonthsToWait = 15

# Stock up in your last month
StockUp = True
# Pay higher prices during the membership gap
PayHigherPrices = False
# Note: if StockUp = False and PayHigherPrices = False, that means you're just going without your normal purchases at
# all during the membership gap, which may or may not be realistic depending on your purchases
# Also make sure not to have both these flags True, that would be buying double what you need!

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'
# Output to screen instead of file:
OutputToScreen = True

# Projection and Plotting flags
TotalBalvsTime = False
TotalBalvsTimeMultipleWaitPeriods = True

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Assemble dicts
ProjDict = {'AnnualMembershipFee': AnnualMembershipFee,
            'MonthlySpendAtWarehouse': MonthlySpendAtWarehouse,
            'Discount': Discount,
            'AnnualROI': AnnualROI,
            'InitBal': InitBal,
            'NumYears': NumYears,
            'NumMonthsToWait': NumMonthsToWait,
            'StockUp': StockUp,
            'PayHigherPrices': PayHigherPrices}

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

# Project and plot total balance vs time for a single set of inputs
if TotalBalvsTime:

    # Compute balance over time for each month
    BalanceArray, MonthArray = ProjBalance(ProjDict)

    NumPlots = 1 #9 # number of distinct lines plotted
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Final Balance: $'+'{:.3f}'.format(BalanceArray[ct,-1]/1000.)+'K')

    # PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange'] #
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': MonthArray,
         'DepData': BalanceArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(BalanceArray/1000.) - 1., 'ymax': np.max(BalanceArray/1000.) + 1.,
         'xmin': MonthArray[0], 'xmax': MonthArray[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Months',
         'TitleText': 'Balance vs Time',
         # 'LegendLoc': 'upper center', #'upper right',
         # 'LegendOn': False,
         'SaveFile': OutDir+'TotalBalvsTime.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Project and plot total balance vs time for multiple wait periods
if TotalBalvsTimeMultipleWaitPeriods:

    NumWaitPeriods = 10
    NumMonths = NumYears*12
    BalanceArray = np.zeros((NumWaitPeriods,NumMonths))

    # Loop over each wait period
    for ct in range(NumWaitPeriods):
        ProjDict['NumMonthsToWait'] = ct
        BalanceArray[ct,:], MonthArray = ProjBalance(ProjDict)

    NumPlots = NumWaitPeriods # number of distinct lines plotted
    PlotLabelArray = []
    for ct in range(NumPlots):
        PlotLabelArray.append('Wait '+'{:d}'.format(ct)+' Months')

    PlotColorArray = ['r','b','g','c','m','k','limegreen','saddlebrown','orange','cornflowerblue'] #

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': MonthArray,
         'DepData': BalanceArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(BalanceArray/1000.) - 1., 'ymax': np.max(BalanceArray/1000.) + 1.,
         'xmin': MonthArray[0], 'xmax': MonthArray[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Months',
         'TitleText': 'Balance vs Time',
         # 'LegendLoc': 'upper center', #'upper right',
         # 'LegendOn': False,
         'SaveFile': OutDir+'TotalBalvsTimeMultipleWaitPeriods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Compute and plot balance diff from Wait Period = 0, use $ instead of $K
    BalanceArrayDiff = np.zeros((NumWaitPeriods,NumMonths))
    for ct in range(BalanceArray.shape[0]):
        BalanceArrayDiff[ct,:] = BalanceArray[ct,:] - BalanceArray[0,:]

    UpdateDict = \
        {'DepData': BalanceArrayDiff,
         'ymin': np.min(BalanceArrayDiff)-100.,
         'ymax': np.max(BalanceArrayDiff)+100,
         'ylabel': 'Balance Difference [$]',
         'TitleText': 'Balance Difference vs Time',
         'LegendLoc': 'lower right',
         'SaveFile': OutDir+'TotalBalDiffvsTimeMultipleWaitPeriods.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Zoom in closer to zero-axis
    UpdateDict = \
        {'DepData': BalanceArrayDiff,
         'ymin': -300.,
         'ymax': 300.,
         'SaveFile': OutDir+'TotalBalDiffvsTimeMultipleWaitPeriodsZoom.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)