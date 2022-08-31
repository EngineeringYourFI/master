# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-much-of-my-social-security-income-will-be-taxed/)

# TaxableSocSecIncomeTemplate.py

import numpy as np
import copy
import os

from SupportMethods import MultiPlot, ComputeTaxes

from TaxableSS import TaxableSS
from TaxableSSconsolidated import TaxableSSconsolidated

# Evaluate methods to compute taxable social security income

#############################################################################################################
# Inputs

# Non-SS income
NonSSincome = 20000.

# Total SS income
TotalSSincome = 36000. #18000 #

# Filing status - Married Filing Jointly ('Married') or Not (Single, head of household, qualifying widow(er), married
# filing seperately)
MarriedOrNot = 'Married' #'Not' #

# Output Directory
OutDir = './'
# Output file
# OutputFile = 'Output.txt'

# Flags
TaxableSSconsolidatedVerification = False
SpecificSituations = True

# Plot flags
TaxSSIvsNSSI_SingleSSI = False
TaxSSIvsSSI_SingleNSSI = False
TaxSSIvsNSSI_MultiSSI = False
TaxSSIvsSSI_MultiNSSI = False

#############################################################################################################

# 2022 income tax bracket info (also applies for nonqualified dividends)
# Note: can easily expand to also include Head of Household and Married Filing Seperately values in the future
Rates = np.array([0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37], dtype=float)
SingleIncomeBracketMins = np.array([0,10275,41775,89075,170050,215950,539900], dtype=float)
MarriedIncomeBracketMins = SingleIncomeBracketMins*2
MarriedIncomeBracketMins[-1] = 647850.

# 2022 standard deductions
SingleStandardDeduction = 12950.
MarriedStandardDeduction = SingleStandardDeduction*2

# 2022 long term cap gains tax bracket info (also applies for qualified dividends)
CapGainsRatesLT = np.array([0.0, 0.15, 0.2], dtype=float)
SingleIncomeBracketLTcapGainsMins = np.array([0,41675,459750], dtype=float)
MarriedIncomeBracketLTcapGainsMins = np.array([0,83350,517200], dtype=float)

#############################################################################################################

# Capturing inputs in relevant dictionaries
TaxRateInfo = {'Rates': Rates,
               'SingleIncomeBracketMins': SingleIncomeBracketMins,
               'MarriedIncomeBracketMins': MarriedIncomeBracketMins,
               'SingleStandardDeduction': SingleStandardDeduction,
               'MarriedStandardDeduction': MarriedStandardDeduction,
               'CapGainsRatesLT': CapGainsRatesLT,
               'SingleIncomeBracketLTcapGainsMins': SingleIncomeBracketLTcapGainsMins,
               'MarriedIncomeBracketLTcapGainsMins': MarriedIncomeBracketLTcapGainsMins}

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

# Verification of TaxableSSconsolidated method
if TaxableSSconsolidatedVerification:

    # Compute taxable amount of SS income
    TaxableSSincome1 = TaxableSS(NonSSincome,TotalSSincome,MarriedOrNot)
    TaxableSSincome2 = TaxableSSconsolidated(NonSSincome,TotalSSincome,MarriedOrNot)

    # test for a variety of NonSSincome - $100 increments from $0 to $100K
    NonSSincomeArray = np.arange(0.,100000.,100.)
    TaxableSSincome1array = np.zeros(len(NonSSincomeArray))
    TaxableSSincome2array = np.zeros(len(NonSSincomeArray))
    for ct in range(0,len(NonSSincomeArray)):
        TaxableSSincome1array[ct] = TaxableSS(NonSSincomeArray[ct],TotalSSincome,MarriedOrNot)
        TaxableSSincome2array[ct] = TaxableSSconsolidated(NonSSincomeArray[ct],TotalSSincome,MarriedOrNot)

    # compute the difference of the two arrays, look at any non-zero deltas between the two methods (if any)
    TaxableSSincome2minus1diffArray = TaxableSSincome2array - TaxableSSincome1array

    # Test for a variety of TotalSSincome - $1K increments from $0 to $50K
    # For each TotalSSincome, look at NonSSincome - $100 increments from $0 to $100K
    NonSSincomeArray = np.arange(0.,100000.,100.)
    TotalSSincomeArray = np.arange(0.,50000.,1000.)
    TaxableSSincome1array2D = np.zeros((len(NonSSincomeArray),len(TotalSSincomeArray)))
    TaxableSSincome2array2D = np.zeros((len(NonSSincomeArray),len(TotalSSincomeArray)))
    for ct1 in range(0,len(TotalSSincomeArray)): # looping over TotalSSincome levels
        for ct2 in range(0,len(NonSSincomeArray)): # looping over NonSSincome levels
            TaxableSSincome1array2D[ct2,ct1] = TaxableSS(NonSSincomeArray[ct2],TotalSSincomeArray[ct1],MarriedOrNot)
            TaxableSSincome2array2D[ct2,ct1] = TaxableSSconsolidated(NonSSincomeArray[ct2],TotalSSincomeArray[ct1],MarriedOrNot)

    # compute the difference of the two arrays, look at any non-zero deltas between the two methods (if any)
    TaxableSSincome2minus1diffArray2D = TaxableSSincome2array2D - TaxableSSincome1array2D
    TaxableSSincome2minus1diffArray2Dsum = np.sum(TaxableSSincome2minus1diffArray2D)

#############################################################################################################

# Specific situations
if SpecificSituations:
    # Single, which has a standard deduction of 12,950
    NonSSincomeA = 40000.
    TotalSSincome = 20000.
    MarriedOrNot = "Not"
    TaxableSSincomeA = TaxableSSconsolidated(NonSSincomeA,TotalSSincome,MarriedOrNot)
    # maxing out 401K, assuming over 50 (so can go up to $27K):
    NonSSincomeB = NonSSincomeA - 25000. #27000.
    TaxableSSincomeB = TaxableSSconsolidated(NonSSincomeB,TotalSSincome,MarriedOrNot)

    # taxes owed
    # Args: TaxRateInfo,SingleOrMarried,TotalStandardIncome,TotalLTcapGainsIncome
    TaxesOwedA = ComputeTaxes(TaxRateInfo,'Single',NonSSincomeA+TaxableSSincomeA,0.)
    TaxesOwedB = ComputeTaxes(TaxRateInfo,'Single',NonSSincomeB+TaxableSSincomeB,0.)

    # Married
    NonSSincomeC = 60000. #30K each #80000
    TotalSSincome = 40000.
    MarriedOrNot = "Married"
    TaxableSSincomeC = TaxableSSconsolidated(NonSSincomeC,TotalSSincome,MarriedOrNot)
    # maxing out 401K, assuming over 50 (so can go up to $27K per person):
    NonSSincomeD = NonSSincomeC - 24000.*2.
    TaxableSSincomeD = TaxableSSconsolidated(NonSSincomeD,TotalSSincome,MarriedOrNot)

    # taxes owed
    # Args: TaxRateInfo,SingleOrMarried,TotalStandardIncome,TotalLTcapGainsIncome
    TaxesOwedC = ComputeTaxes(TaxRateInfo,'Married',NonSSincomeC+TaxableSSincomeC,0.)
    TaxesOwedD = ComputeTaxes(TaxRateInfo,'Married',NonSSincomeD+TaxableSSincomeD,0.)

#############################################################################################################

# For a particular TotalSSincome (provided in user inputs), plot TaxableSSincome for a range of NonSSincome - $100
# increments from $0 to $100K
if TaxSSIvsNSSI_SingleSSI:
    NonSSincomeArray = np.arange(0.,100000.,100.)
    TaxableSSincomeArray = np.zeros(len(NonSSincomeArray))
    for ct in range(0,len(NonSSincomeArray)):
        TaxableSSincomeArray[ct] = TaxableSSconsolidated(NonSSincomeArray[ct],TotalSSincome,MarriedOrNot)

    NumPlots = 1
    TaxableSSincomeArray2D = np.zeros((NumPlots,len(TaxableSSincomeArray)))
    TaxableSSincomeArray2D[0,:] = TaxableSSincomeArray

    PlotLabelArray = ['SSI = $36K'] #18K
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': NonSSincomeArray/1000.,
         'DepData': TaxableSSincomeArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 1.1*np.max(TaxableSSincomeArray2D/1000.),
         'xmin': NonSSincomeArray[0]/1000., 'xmax': NonSSincomeArray[-1]/1000.+1,
         'ylabel': 'Taxable SSI [$K]',
         'xlabel': 'Non-SSI [$K]',
         'TitleText': 'Taxable Social Security Income (SSI)',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'TaxableSSIvsNonSSI_SSI36K.png'} #18K
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# For a particular NonSSincome = 36K #18K, plot TaxableSSincome for a range of TotalSSincome - $100 increments from $0
# to $100K #50K
if TaxSSIvsSSI_SingleNSSI:

    # Max individual SS income in 2022 is $4194 * 12 = $50328
    # Thus max married couple SS income in 2022 is $50328 * 2 = $100656

    NonSSincome = 36000. #18000 #

    TotalSSincomeArray = np.arange(0.,100000.,100.) #50000.
    TaxableSSincomeArray = np.zeros(len(TotalSSincomeArray))
    for ct in range(0,len(TaxableSSincomeArray)):
        TaxableSSincomeArray[ct] = TaxableSSconsolidated(NonSSincome,TotalSSincomeArray[ct],MarriedOrNot)

    NumPlots = 1
    TaxableSSincomeArray2D = np.zeros((NumPlots,len(TaxableSSincomeArray)))
    TaxableSSincomeArray2D[0,:] = TaxableSSincomeArray

    PlotLabelArray = ['Non-SSI = $36K'] #18K
    PlotColorArray = ['k']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': TotalSSincomeArray/1000.,
         'DepData': TaxableSSincomeArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 1.1*np.max(TaxableSSincomeArray2D/1000.),
         'xmin': TotalSSincomeArray[0]/1000., 'xmax': TotalSSincomeArray[-1]/1000.+1,
         'ylabel': 'Taxable SSI [$K]',
         'xlabel': 'SSI [$K]',
         'TitleText': 'Taxable Social Security Income (SSI)',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'TaxableSSIvsSSI_NonSSI36K.png'} #18K
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot TaxableSSincome for a range of NonSSincome - $100 increments from $0 to $100K
# Create 5 lines (each different color), for multiple TotalSSincome: $20K, $40K, $60K, $80K, $100K  #$10K, $20K, $30K, $40K, $50K
if TaxSSIvsNSSI_MultiSSI:

    # Max individual SS income in 2022 is $4194 * 12 = $50328
    # Thus max married couple SS income in 2022 is $50328 * 2 = $100656

    NonSSincomeArray = np.arange(0.,100000.,100.)
    # TotalSSincomeArray = np.array([10000,20000,30000,40000,50000], dtype=float)
    TotalSSincomeArray = np.array([20000,40000,60000,80000,100000], dtype=float)

    NumPlots = len(TotalSSincomeArray)
    TaxableSSincomeArray2D = np.zeros((NumPlots,len(NonSSincomeArray)))

    for ct1 in range(0,NumPlots):
        for ct2 in range(0,len(NonSSincomeArray)):
            TaxableSSincomeArray2D[ct1,ct2] = TaxableSSconsolidated(NonSSincomeArray[ct2],TotalSSincomeArray[ct1],
                                                                    MarriedOrNot)

    # PlotLabelArray = ['SSI $10K','SSI $20K','SSI $30K','SSI $40K','SSI $50K']
    PlotLabelArray = ['SSI $20K','SSI $40K','SSI $60K','SSI $80K','SSI $100K']
    PlotColorArray = ['k','r','b','g','m']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': NonSSincomeArray/1000.,
         'DepData': TaxableSSincomeArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 1.1*np.max(TaxableSSincomeArray2D/1000.),
         'xmin': NonSSincomeArray[0]/1000., 'xmax': NonSSincomeArray[-1]/1000.+1,
         'ylabel': 'Taxable SSI [$K]',
         'xlabel': 'Non-SSI [$K]',
         'TitleText': 'Taxable Social Security Income (SSI)',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'TaxableSSIvsNonSSI_SSI20_40_60_80_100K.png'} #10_20_30_40_50K
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot TaxableSSincome for a range of TotalSSincome - $100 increments from $0 to $100K #50K
# Create 5 lines (each different color), for multiple NonSSincome: $20K, $40K, $60K, $80K, $100K
if TaxSSIvsSSI_MultiNSSI:

    # Max individual SS income in 2022 is $4194 * 12 = $50328
    # Thus max married couple SS income in 2022 is $50328 * 2 = $100656

    TotalSSincomeArray = np.arange(0.,100000.,100.) #50000
    NonSSincomeArray = np.array([20000,40000,60000,80000,100000], dtype=float)

    NumPlots = len(NonSSincomeArray)
    TaxableSSincomeArray2D = np.zeros((NumPlots,len(TotalSSincomeArray)))

    for ct1 in range(0,NumPlots):
        for ct2 in range(0,len(TotalSSincomeArray)):
            TaxableSSincomeArray2D[ct1,ct2] = TaxableSSconsolidated(NonSSincomeArray[ct1],TotalSSincomeArray[ct2],
                                                                    MarriedOrNot)

    PlotLabelArray = ['Non-SSI $20K','Non-SSI $40K','Non-SSI $60K','Non-SSI $80K','Non-SSI $100K']
    PlotColorArray = ['k','r','b','g','m']

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': TotalSSincomeArray/1000.,
         'DepData': TaxableSSincomeArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 1.1*np.max(TaxableSSincomeArray2D/1000.),
         'xmin': TotalSSincomeArray[0]/1000., 'xmax': TotalSSincomeArray[-1]/1000.+1,
         'ylabel': 'Taxable SSI [$K]',
         'xlabel': 'SSI [$K]',
         'TitleText': 'Taxable Social Security Income (SSI)',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'TaxableSSIvsSSI_NonSSI20_40_60_80_100K.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
