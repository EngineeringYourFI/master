# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/time-to-fi-starting-below-0/)

# TimeToFIbelow0template.py

import numpy as np
import copy
import os
import matplotlib.pyplot as plt

# Compute and plot time to FI, starting with debt (i.e. having a net worth less than $0)
# Derivation: see https://engineeringyourfi.com/MathSpecs/TimeToFIbelow0Derivation.pdf

#############################################################################################################
# Inputs

# Savings info
# Savings rate - most important factor!
SR = 0.5
# Annual income
Income = 75000
# Annual expenses - next most important factor
E = (1 - SR) * Income
# E = 40000

# Loan info
# Initial loan balance
# "According to Experian, in 2019 the average American household carried $6,194 in credit card debt"
# average student balance is $32,731, with most b/n $25K and $50K https://www.valuepenguin.com/average-student-loan-debt
P0 = 510000 #32731 #6194 #
# Loan annual interest rate (APR)
# "according to The Balance's June 2020 Average Credit Card Interest report, the average credit card interest rate
# stood at 20.09%"
# 5.8% is the average student loan rate https://educationdata.org/average-student-loan-interest-rate
Rl = 0.058 #0.20 #

# Investment info (after paying off loan)
# Annual interest rate (i.e. expected investment return)
R = 0.07

# FI info
# Annual withdrawal rate for FI
WR = 0.04

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Plot flags
NumYearsTo0DebtvsP0multiSRconstExp = False
NumYearsTo0DebtvsP0multiSRconstInc = False
NumYearsTo0DebtvsP0multiSRloanRate58 = False
NumYearsToFIvsP0multiSRconstInc = False
NumYearsToFIvsP0multiSRloanRate58 = False
NumYearsToFIand0debtvsP0multiSRloanRate20 = False
NumYearsToFIand0debtvsP0multiSRloanRate58 = False
NumYearsTo0DebtvsRlmultiSRconstInc = False
NumYearsTo0DebtvsRlmultiSRinitLoan32731 = False
NumYearsToFIand0debtvsRlmultiSRinitLoan32731 = False

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

# Compute number of years to zero debt, FI from $0, and total time
# First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
if P0*Rl < E*(1/(1-SR) - 1):
    # Compute number of years to zero debt
    NumYearsToZeroDebt = -np.log(1 - P0*Rl / (E*(1/(1-SR) - 1))) / (12*np.log(1+Rl/12))
    NumMonthsToZeroDebt = NumYearsToZeroDebt*12
    print('NumYearsToZeroDebt = ', str(NumYearsToZeroDebt))
    print('NumMonthsToZeroDebt = ', str(NumMonthsToZeroDebt))

    # Compute number of years to FI from $0
    # N = ln( (1/(WR*SR)) * (R - R*SR) + 1 ) / ln(1+R)
    NumYearsToFIfromZero = np.log( (1/(WR*SR)) * (R - R*SR) + 1 ) / np.log(1+R)
    print('NumYearsToFIfrom0 = ', str(NumYearsToFIfromZero))

    # Total number of years to FI, including time to pay off debt
    TotalNumYearsToFI = NumYearsToZeroDebt + NumYearsToFIfromZero
    print('TotalNumYearsToFI = ', str(TotalNumYearsToFI))
else:
    print('NumYearsToZeroDebt = Infinity! Payment less than (or equal to) interest on loan.')

#############################################################################################################

# General multiplot method
def MultiPlot(PlotDict):

    # Properties for text boxes - these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    fig = plt.figure(1,figsize=(PlotDict['FigWidth'],PlotDict['FigHeight']))

    # Loop over savings rates, plot Years to Zero Debt values for each vs initial loan value
    for ct in range(0,len(PlotDict['MultiPlotProperties'])):
        if PlotDict['PlotSecondaryLines'] == False:
            plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'],
                     linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                     label=PlotDict['PlotLabelArray'][ct])
        else:
            plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'][ct],
                     linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                     label=PlotDict['PlotLabelArray'][ct])
            plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct+len(PlotDict['MultiPlotProperties']),:],
                     PlotDict['LineStyle'][ct+len(PlotDict['MultiPlotProperties'])],
                     linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                     label=PlotDict['PlotLabelArray'][ct+len(PlotDict['MultiPlotProperties'])])

    ax = plt.gca()
    plt.ylim(PlotDict['ymin'],PlotDict['ymax'])
    plt.xlim(PlotDict['xmin'],PlotDict['xmax'])

    ax.text(PlotDict['CopyrightX'], PlotDict['CopyrightY'], PlotDict['CopyrightText'], transform=ax.transAxes,
            fontsize=PlotDict['CopyrightFontSize'], verticalalignment=PlotDict['CopyrightVertAlign'])

    ax.ticklabel_format(useOffset=False)
    plt.ylabel(PlotDict['ylabel'], fontsize=PlotDict['ylabelFontSize'])
    plt.xlabel(PlotDict['xlabel'], fontsize=PlotDict['xlabelFontSize'])
    plt.title(PlotDict['TitleText'], y=PlotDict['Title_yoffset'], fontsize=PlotDict['TitleFontSize'])
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--') # or just plt.grid(True)  color='lightgray'
    plt.legend(loc=PlotDict['LegendLoc'],fontsize=PlotDict['LegendFontSize'],numpoints=1)
    plt.tight_layout()
    plt.savefig(PlotDict['SaveFile'])
    plt.close()

#############################################################################################################

# Plot time to zero debt vs initial debt balance for multiple savings rates, same expenses and loan interest rate
if NumYearsTo0DebtvsP0multiSRconstExp:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray) #np.zeros(len(SavingsRateArray))
    PlotColorArray = ['r','b','g','c','m']
    E = 40000
    Rl = 0.2

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < E*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToZeroDebt
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (E*(1/(1-SavingsRateArray[ct1]) - 1))) / (12*np.log(1+Rl/12))
            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsTo0DebtvsP0multiSRconstExpDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsTo0DebtvsP0multiSRconstExpUpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 50,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to Zero Debt',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to Zero Debt vs Initial Loan Balance, \n Expenses $40K, Loan Rate 20%',
         'LegendLoc': 'upper center',
         'SaveFile': OutDir+'NumYearsToZeroDebtvsP0multiSRconstExp.png'}
    # Update dict to have plot specific values
    NumYearsTo0DebtvsP0multiSRconstExpDict.update(NumYearsTo0DebtvsP0multiSRconstExpUpdateDict)
    # Create plot
    MultiPlot(NumYearsTo0DebtvsP0multiSRconstExpDict)

#############################################################################################################

# Plot time to zero debt vs initial debt balance for multiple savings rates, same $75K income (so expenses modified each
# time) and loan interest rate (average CC interest rate)
if NumYearsTo0DebtvsP0multiSRconstInc:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.20

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToZeroDebt
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12))
            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsTo0DebtvsP0multiSRconstIncDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsTo0DebtvsP0multiSRconstIncUpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 30,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to Zero Debt',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to Zero Debt vs Initial Loan Balance, \n Income $75K, Loan Rate 20%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToZeroDebtvsP0multiSRconstInc.png'}
    # Update dict to have plot specific values
    NumYearsTo0DebtvsP0multiSRconstIncDict.update(NumYearsTo0DebtvsP0multiSRconstIncUpdateDict)
    # Create plot
    MultiPlot(NumYearsTo0DebtvsP0multiSRconstIncDict)

#############################################################################################################

# Plot time to zero debt vs initial debt balance for multiple savings rates, same $75K income (so expenses modified each
# time) and loan interest rate = 5.8% (average student loan debt rate, https://educationdata.org/average-student-loan-interest-rate)
# Average student loan balance = $32,731, with most b/n $25K and $50K, https://www.valuepenguin.com/average-student-loan-debt
if NumYearsTo0DebtvsP0multiSRloanRate58:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.058

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToZeroDebt
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12))
            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsTo0DebtvsP0multiSRloanRate58Dict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsTo0DebtvsP0multiSRloanRate58UpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 30,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to Zero Debt',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to Zero Debt vs Initial Loan Balance, \n Income $75K, Loan Rate 5.8%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToZeroDebtvsP0multiSRloanRate58.png'}
    # Update dict to have plot specific values
    NumYearsTo0DebtvsP0multiSRloanRate58Dict.update(NumYearsTo0DebtvsP0multiSRloanRate58UpdateDict)
    # Create plot
    MultiPlot(NumYearsTo0DebtvsP0multiSRloanRate58Dict)

#############################################################################################################

# Plot time to FI vs initial debt balance for multiple savings rates, same $75K income (so expenses modified each
# time) and loan interest rate (average CC interest rate)
if NumYearsToFIvsP0multiSRconstInc:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.2

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToFI
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12)) + \
                                         np.log( (1/(WR*SavingsRateArray[ct1])) * (R - R*SavingsRateArray[ct1]) + 1 ) / \
                                         np.log(1+R)

            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsToFIvsP0multiSRconstIncDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsToFIvsP0multiSRconstIncUpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 70,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to FI',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to FI vs Initial Loan Balance, \n Income $75K, Loan Rate 20%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIvsP0multiSRconstInc.png'}
    # Update dict to have plot specific values
    NumYearsToFIvsP0multiSRconstIncDict.update(NumYearsToFIvsP0multiSRconstIncUpdateDict)
    # Create plot
    MultiPlot(NumYearsToFIvsP0multiSRconstIncDict)

#############################################################################################################

# Plot time to FI vs initial debt balance for multiple savings rates, same $75K income (so expenses modified each
# time) and loan interest rate = 5.8% (average student loan debt rate)
if NumYearsToFIvsP0multiSRloanRate58:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.058

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToFI
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12)) + \
                                         np.log( (1/(WR*SavingsRateArray[ct1])) * (R - R*SavingsRateArray[ct1]) + 1 ) / \
                                         np.log(1+R)

            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsToFIvsP0multiSRloanRate58Dict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsToFIvsP0multiSRloanRate58UpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 70,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to FI',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to FI vs Initial Loan Balance, \n Income $75K, Loan Rate 5.8%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIvsP0multiSRloanRate58.png'}
    # Update dict to have plot specific values
    NumYearsToFIvsP0multiSRloanRate58Dict.update(NumYearsToFIvsP0multiSRloanRate58UpdateDict)
    # Create plot
    MultiPlot(NumYearsToFIvsP0multiSRloanRate58Dict)

#############################################################################################################

# Plot time to FI AND zero debt vs initial debt balance for multiple savings rates, same $75K income (so expenses
# modified each time) and loan interest rate (average 20% CC interest rate)
if NumYearsToFIand0debtvsP0multiSRloanRate20:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    # double the size of NumYearsArray, to store times to 0 debt
    NumYearsArray = np.zeros((len(SavingsRateArray)*2,NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    # double the size of PlotLabelArray, to label plots for time to 0 debt
    PlotLabelArray = [''] * len(SavingsRateArray)*2
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.2

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR, Total Time To FI'
        PlotLabelArray[ct1+len(SavingsRateArray)] = str(int(SavingsRateArray[ct1]*100))+'% SR, Debt Payoff Time'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToFI
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12)) + \
                                         np.log( (1/(WR*SavingsRateArray[ct1])) * (R - R*SavingsRateArray[ct1]) + 1 ) / \
                                         np.log(1+R)
                # NumYearsToZeroDebt
                NumYearsArray[ct1+len(SavingsRateArray),ct2] = \
                    -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                    (12*np.log(1+Rl/12))

            else:
                NumYearsArray[ct1,ct2] = float("nan")
                NumYearsArray[ct1+len(SavingsRateArray),ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsToFIand0debtvsP0multiSRloanRate20Dict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsToFIand0debtvsP0multiSRloanRate20UpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 70,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to Zero Debt and FI',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to FI vs Initial Loan Balance, \n Income $75K, Loan Rate 20%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIand0debtvsP0multiSRloanRate20.png',
         'PlotSecondaryLines': True,
         'LineStyle': ['-']*5+['--']*5}
    # Update dict to have plot specific values
    NumYearsToFIand0debtvsP0multiSRloanRate20Dict.update(NumYearsToFIand0debtvsP0multiSRloanRate20UpdateDict)
    # Create plot
    MultiPlot(NumYearsToFIand0debtvsP0multiSRloanRate20Dict)

#############################################################################################################

# Plot time to FI AND zero debt vs initial debt balance for multiple savings rates, same $75K income (so expenses
# modified each time) and loan interest rate = 5.8% (average student loan debt rate)
if NumYearsToFIand0debtvsP0multiSRloanRate58:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    # double the size of NumYearsArray, to store times to 0 debt
    NumYearsArray = np.zeros((len(SavingsRateArray)*2,NumSteps))
    P0array = np.arange(0,100000,100000/NumSteps)
    # double the size of PlotLabelArray, to label plots for time to 0 debt
    PlotLabelArray = [''] * len(SavingsRateArray)*2
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    Rl = 0.058

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR, Total Time To FI'
        PlotLabelArray[ct1+len(SavingsRateArray)] = str(int(SavingsRateArray[ct1]*100))+'% SR, Debt Payoff Time'
        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0array[ct2]*Rl < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # NumYearsToFI
                NumYearsArray[ct1,ct2] = -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1])
                                                                                            - 1))) / (12*np.log(1+Rl/12)) + \
                                         np.log( (1/(WR*SavingsRateArray[ct1])) * (R - R*SavingsRateArray[ct1]) + 1 ) / \
                                         np.log(1+R)
                # NumYearsToZeroDebt
                NumYearsArray[ct1+len(SavingsRateArray),ct2] = \
                    -np.log(1 - P0array[ct2]*Rl / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                    (12*np.log(1+Rl/12))

            else:
                NumYearsArray[ct1,ct2] = float("nan")
                NumYearsArray[ct1+len(SavingsRateArray),ct2] = float("nan")

    # Initialize plot dict using default dict
    NumYearsToFIand0debtvsP0multiSRloanRate58Dict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    NumYearsToFIand0debtvsP0multiSRloanRate58UpdateDict = \
        {'IndepData': P0array/1000,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 70,
         'xmin': 0, 'xmax': P0array[-1]/1000+0.1,
         'ylabel': 'Number of Years to Zero Debt and FI',
         'xlabel': 'Initial Loan Balance ($K)',
         'TitleText': 'Years to FI vs Initial Loan Balance, \n Income $75K, Loan Rate 5.8%',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIand0debtvsP0multiSRloanRate58.png',
         'PlotSecondaryLines': True,
         'LineStyle': ['-']*5+['--']*5}
    # Update dict to have plot specific values
    NumYearsToFIand0debtvsP0multiSRloanRate58Dict.update(NumYearsToFIand0debtvsP0multiSRloanRate58UpdateDict)
    # Create plot
    MultiPlot(NumYearsToFIand0debtvsP0multiSRloanRate58Dict)

#############################################################################################################

# Plot time to zero debt vs debt rate for multiple savings rates, same $75K income (so expenses modified each
# time) and initial loan balance = 6194 (average CC balance)
if NumYearsTo0DebtvsRlmultiSRconstInc:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    Rlarray = np.arange(0,0.35,0.35/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    P0 = 6194

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        # Loop over debt rates
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0*Rlarray[ct2] < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # Confirm interest rate > 0%:
                if Rlarray[ct2] > 0:
                    # NumYearsToZeroDebt
                    NumYearsArray[ct1,ct2] = \
                        -np.log(1 - P0*Rlarray[ct2] / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                        (12*np.log(1+Rlarray[ct2]/12))
                else:
                    # If interest rate = 0%, compute differently - divide principle by annual payment
                    NumYearsArray[ct1,ct2] = P0 / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))
            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    PlotUpdateDict = \
        {'IndepData': Rlarray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 1,
         'xmin': 0, 'xmax': Rlarray[-1]*100,
         'ylabel': 'Number of Years to Zero Debt',
         'xlabel': 'Loan Interest Rate (%)',
         'TitleText': 'Years to Zero Debt vs Loan Rate, \n Income \$75K, Initial Balance \$6,194',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToZeroDebtvsRlmultiSRconstInc.png'}
    # Update dict to have plot specific values
    PlotDict.update(PlotUpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot time to zero debt vs debt rate for multiple savings rates, same $75K income (so expenses modified each
# time) and initial loan balance = 32731 (average student loan balance)
if NumYearsTo0DebtvsRlmultiSRinitLoan32731:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    Rlarray = np.arange(0,0.15,0.15/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    P0 = 32731

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR'
        # Generate array of number of years to FI for this savings rate
        # Loop over debt rates
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0*Rlarray[ct2] < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # Confirm interest rate > 0%:
                if Rlarray[ct2] > 0:
                    # NumYearsToZeroDebt
                    NumYearsArray[ct1,ct2] = \
                        -np.log(1 - P0*Rlarray[ct2] / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                        (12*np.log(1+Rlarray[ct2]/12))
                else:
                    # If interest rate = 0%, compute differently - divide principle by annual payment
                    NumYearsArray[ct1,ct2] = P0 / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))
            else:
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    PlotUpdateDict = \
        {'IndepData': Rlarray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 10,
         'xmin': 0, 'xmax': np.round(Rlarray[-1]*100),
         'ylabel': 'Number of Years to Zero Debt',
         'xlabel': 'Loan Interest Rate (%)',
         'TitleText': 'Years to Zero Debt vs Loan Rate, \n Income \$75K, Initial Balance \$32,731',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToZeroDebtvsRlmultiSRinitLoan32731.png'}
    # Update dict to have plot specific values
    PlotDict.update(PlotUpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot time to FI AND zero debt vs debt rate for multiple savings rates, same $75K income (so expenses
# modified each time) and initial loan balance = 32731 (average student loan balance)
if NumYearsToFIand0debtvsRlmultiSRinitLoan32731:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    # double the size of NumYearsArray, to store times to 0 debt
    NumYearsArray = np.zeros((len(SavingsRateArray)*2,NumSteps))
    Rlarray = np.arange(0,0.15,0.15/NumSteps)
    # double the size of PlotLabelArray, to label plots for time to 0 debt
    PlotLabelArray = [''] * len(SavingsRateArray)*2
    PlotColorArray = ['r','b','g','c','m']
    Income = 75000
    P0 = 32731

    # Determine expenses from savings rate and constant income
    # SR = (I - E) / I = 1 - E/I
    # E / I = 1 - SR
    # E = (1 - SR) * I
    ExpensesArray = (1 - SavingsRateArray) * Income

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):
        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% SR, Total Time To FI'
        PlotLabelArray[ct1+len(SavingsRateArray)] = str(int(SavingsRateArray[ct1]*100))+'% SR, Debt Payoff Time'
        # Generate array of number of years to FI for this savings rate
        # Loop over debt rates
        for ct2 in range(0, NumSteps):
            # First need to verify the payment is greater than the interest - otherwise you'll never pay it off!
            if P0*Rlarray[ct2] < ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1):
                # Confirm interest rate > 0%:
                if Rlarray[ct2] > 0:
                    # NumYearsToFI
                    NumYearsArray[ct1,ct2] = \
                        -np.log(1 - P0*Rlarray[ct2] / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                        (12*np.log(1+Rlarray[ct2]/12)) + np.log( (1/(WR*SavingsRateArray[ct1])) *
                                                                 (R - R*SavingsRateArray[ct1]) + 1 ) / np.log(1+R)
                    # NumYearsToZeroDebt
                    NumYearsArray[ct1+len(SavingsRateArray),ct2] = \
                        -np.log(1 - P0*Rlarray[ct2] / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))) / \
                        (12*np.log(1+Rlarray[ct2]/12))
                else:
                    # If interest rate = 0%, compute differently - divide principle by annual payment
                    # NumYearsToZeroDebt
                    NumYearsArray[ct1+len(SavingsRateArray),ct2] = P0 / (ExpensesArray[ct1]*(1/(1-SavingsRateArray[ct1]) - 1))
                    # NumYearsToFI
                    NumYearsArray[ct1,ct2] = NumYearsArray[ct1+len(SavingsRateArray),ct2] + np.log( (1/(WR*SavingsRateArray[ct1])) *
                                                                 (R - R*SavingsRateArray[ct1]) + 1 ) / np.log(1+R)
            else:
                NumYearsArray[ct1,ct2] = float("nan")
                NumYearsArray[ct1+len(SavingsRateArray),ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    PlotUpdateDict = \
        {'IndepData': Rlarray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 50,
         'xmin': 0, 'xmax': np.round(Rlarray[-1]*100),
         'ylabel': 'Number of Years to Zero Debt and FI',
         'xlabel': 'Loan Interest Rate (%)',
         'TitleText': 'Years to FI vs Loan Interest Rate, \n Income $75K, Initial Balance \$32,731',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIand0debtvsRlmultiSRinitLoan32731.png',
         'PlotSecondaryLines': True,
         'LineStyle': ['-']*5+['--']*5}
    # Update dict to have plot specific values
    PlotDict.update(PlotUpdateDict)
    # Create plot
    MultiPlot(PlotDict)
