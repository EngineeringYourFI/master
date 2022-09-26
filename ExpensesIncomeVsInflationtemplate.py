# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/time-to-fi-what-about-inflation/)

# ExpensesIncomeVsInflation.py

import numpy as np
import copy
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy import optimize

# Compute and plot time to FI, accounting for expenses and/or income growing slower or faster than inflation
# Derivation: see https://engineeringyourfi.com/MathSpecs/ExpensesIncomeVsInflationDerivation.pdf

#############################################################################################################
# Inputs

# Savings info
# Savings rate - most important factor!
SR = 0.5 #0.7 #
# Annual income
Inc = 75000 #50000 #100000 #
# Income growth rate relative to inflation
RI = 0.0 #0.087 #
# Annual expenses - next most important factor
Exp = (1 - SR) * Inc
# E = 40000
# Expense growth rate relative to inflation
RE = -0.04 #-0.044 #0.0 #-0.01 #

# Initial net worth
IV = 0 #7000

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Annual withdrawal rate for FI
WR = 0.04

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Plot flags
NumYearsToFIvsExpGrowthRate = True
NumYearsToFIvsIncGrowthRate = True
NumYearsToFIvsExpGrowthRateForMultipleIncGrowthRates = True

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

# Compute number of years to FI from $0, accounting for expenses and/or income growing slower or faster than inflation

# Compute number of years to FI assuming expenses and income grow at exactly inflation, as initial value
NumYearsWithIV = np.log( (1 - SR + (WR*SR)/R) / ( (WR*IV)/Inc + (WR*SR)/R ) ) / np.log(1+R)

a = Exp - WR * Exp * ((1+RE)/(R-RE))
b = WR * (IV + Inc*((1+RI)/(R-RI)) - Exp*((1+RE)/(R-RE)))
c = (1+R)/(1+RE)
d = WR * Inc * (1+RI)/(R-RI)
e = (1+RI)/(1+RE)

# Max number of iterations
maxiter = 50

# # Direct implementation of Newton Rhapson method:
# # Initialize
# xm = copy.deepcopy(NumYearsWithIV)
# iterct = 0
#
# fx = b*c**xm - d*e**xm - a
# fpx = np.log(c)*b*c**xm - np.log(e)*d*e**xm
# xmp1 = xm - fx/fpx
# # Loop until converged
# while abs(xmp1 - xm) > 0.001 and iterct <= maxiter:
#     # set xm equal to previous iteration xmp1
#     xm = copy.deepcopy(xmp1)
#     fx = b*c**xm - d*e**xm - a
#     fpx = np.log(c)*b*c**xm - np.log(e)*d*e**xm
#     xmp1 = xm - fx/fpx
#     iterct = iterct+1
#
# NumYearsWithIVandVariableExpenseOrIncomeRate = copy.deepcopy(xmp1)

# # Using scipy.optimize.newton instead:
# def fx(xm):
#     return (b*c**xm - d*e**xm - a)
#
# def fpx(xm):
#     return (np.log(c)*b*c**xm - np.log(e)*d*e**xm)
#
# NumYearsWithIVandVariableExpenseOrIncomeRate = optimize.newton(fx, NumYearsWithIV, fprime=fpx)

# Using scipy.optimize.newton with lambda methods instead
# fx = lambda xm: b*c**xm - d*e**xm - a
# fpx = lambda xm: np.log(c)*b*c**xm - np.log(e)*d*e**xm
# NumYearsWithIVandVariableExpenseOrIncomeRate = optimize.newton(fx, NumYearsWithIV, fprime=fpx)

# Using scipy.optimize.newton with lambda methods and additional arguments to ensure correct values used:
fx = lambda xm, a, b, c, d, e: b*c**xm - d*e**xm - a
fpx = lambda xm, a, b, c, d, e: np.log(c)*b*c**xm - np.log(e)*d*e**xm
NumYearsWithIVandVariableExpenseOrIncomeRate = optimize.newton(fx, NumYearsWithIV, fprime=fpx, args=(a,b,c,d,e))
print('NumYearsWithIVandVariableExpenseOrIncomeRate = ', str(NumYearsWithIVandVariableExpenseOrIncomeRate))

# special functions for when R = RE
fxReqRE = lambda xm, a, b, c, d: b*c**xm - d*xm - a
fpxReqRE = lambda xm, a, b, c, d: np.log(c)*b*c**xm - d

# special functions for when R = RI
fxReqRI = lambda xm, a, b, c, d: (b + c*xm)*d**xm - a
fpxReqRI = lambda xm, a, b, c, d: c*d**xm + np.log(d)*(b + c*xm)*d**xm

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
    plt.grid(color='gray',linestyle='--')
    plt.legend(loc=PlotDict['LegendLoc'],fontsize=PlotDict['LegendFontSize'],numpoints=1)
    plt.tight_layout()
    plt.savefig(PlotDict['SaveFile'])
    plt.close()

#############################################################################################################

# Plot time to FI vs Expense Growth Rate (relative to inflation) for multiple (initial) savings rate,
# same income (kept in current year dollars, i.e. adjusted exactly by inflation each year)
if NumYearsToFIvsExpGrowthRate:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    ExpGrowthRateArray = np.arange(-0.1,0.1,0.2/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']

    Inc = 75000
    RI = 0.0
    IV = 0.0

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):

        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% Initial SR'

        # initial value, with RI and RE equal zero (assuming expenses and income grow at exactly inflation)
        NumYearsWithIV = np.log( (1 - SavingsRateArray[ct1] + (WR*SavingsRateArray[ct1])/R) /
                                 ( (WR*IV)/Inc + (WR*SavingsRateArray[ct1])/R ) ) / np.log(1+R)
        Exp = (1 - SavingsRateArray[ct1]) * Inc

        # initialize convergence flag
        StillConverging = True

        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            if StillConverging:
                # Avoid singularity when R = RE
                if abs(R - ExpGrowthRateArray[ct2]) < 0.0001:
                    a = Exp - WR*IV - WR*Inc*((1+RI)/(R-RI))
                    b = -WR*Inc*((1+RI)/(R-RI))
                    c = (1+RI)/(1+R)
                    d = WR * Exp
                    NumYearsArray[ct1,ct2], rootresults = optimize.newton(fxReqRE, NumYearsWithIV, fprime=fpxReqRE,
                                                                          args=(a,b,c,d), full_output=True, disp=False)
                    if rootresults.converged == False: # just in case it still doesn't converge
                        NumYearsArray[ct1,ct2] = float("nan")
                    continue

                a = Exp - WR * Exp * ((1+ExpGrowthRateArray[ct2])/(R-ExpGrowthRateArray[ct2]))
                b = WR * (IV + Inc*((1+RI)/(R-RI)) - Exp*((1+ExpGrowthRateArray[ct2])/(R-ExpGrowthRateArray[ct2])))
                c = (1+R)/(1+ExpGrowthRateArray[ct2])
                d = WR * Inc * (1+RI)/(R-RI)
                e = (1+RI)/(1+ExpGrowthRateArray[ct2])
                NumYearsArray[ct1,ct2], rootresults = optimize.newton(fx, NumYearsWithIV, fprime=fpx, args=(a,b,c,d,e),
                                                                      full_output=True, disp=False)
                # if the NR method didn't converge
                if rootresults.converged == False:
                    # set to 1000, so that it always shoots off the plot to look better / really represent what’s going
                    # on (the number of years asymptotically approaching infinity)
                    NumYearsArray[ct1,ct2] = 1000
                    StillConverging = False
            else:
                # specify as NaN so it's not plotted
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpGrowthRateArray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 50,
         'xmin': ExpGrowthRateArray[0]*100, 'xmax': ExpGrowthRateArray[-1]*100+0.02,
         'ylabel': 'Number of Years to FI',
         'xlabel': 'Expense Growth Rate Relative To Inflation (%)',
         'TitleText': 'Years to FI vs Expense Growth Rate, \n Income $75K',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIvsExpGrowthRate.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot time to FI vs Income Growth Rate (relative to inflation) for multiple (initial) savings rate,
# same initial income and same expenses (kept in current year dollars, i.e. adjusted exactly by inflation each year)
if NumYearsToFIvsIncGrowthRate:

    NumSteps = 1000
    SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
    NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
    IncGrowthRateArray = np.arange(0.1,-0.1,-0.2/NumSteps)
    PlotLabelArray = [''] * len(SavingsRateArray)
    PlotColorArray = ['r','b','g','c','m']

    Inc = 75000
    RE = 0.0
    IV = 0.0

    # Loop over savings rates
    for ct1 in range(0, len(SavingsRateArray)):

        # labels for plots
        PlotLabelArray[ct1] = str(int(SavingsRateArray[ct1]*100))+'% Initial SR'

        # initial value, with RI and RE equal zero (assuming expenses and income grow at exactly inflation)
        NumYearsWithIV = np.log( (1 - SavingsRateArray[ct1] + (WR*SavingsRateArray[ct1])/R) /
                                 ( (WR*IV)/Inc + (WR*SavingsRateArray[ct1])/R ) ) / np.log(1+R)
        # Expenses which will grow by exactly inflation each year
        Exp = (1 - SavingsRateArray[ct1]) * Inc

        # initialize convergence flag
        StillConverging = True

        # Generate array of number of years to FI for this savings rate
        for ct2 in range(0, NumSteps):
            if StillConverging:
                # Avoid singularity when R = RE
                if abs(R - IncGrowthRateArray[ct2]) < 0.0001:
                    a = Exp - WR * Exp * ((1+RE)/(R-RE))
                    b = WR * (IV - Exp*((1+RE)/(R-RE)))
                    c = WR * Inc
                    d = (1+R)/(1+RE)
                    NumYearsArray[ct1,ct2], rootresults = optimize.newton(fxReqRI, NumYearsWithIV, fprime=fpxReqRI,
                                                                          args=(a,b,c,d), full_output=True, disp=False)
                    if rootresults.converged == False: # just in case it still doesn't converge
                        NumYearsArray[ct1,ct2] = float("nan")
                    continue

                a = Exp - WR * Exp * ((1+RE)/(R-RE))
                b = WR * (IV + Inc*((1+IncGrowthRateArray[ct2])/(R-IncGrowthRateArray[ct2])) - Exp*((1+RE)/(R-RE)))
                c = (1+R)/(1+RE)
                d = WR * Inc * (1+IncGrowthRateArray[ct2])/(R-IncGrowthRateArray[ct2])
                e = (1+IncGrowthRateArray[ct2])/(1+RE)
                NumYearsArray[ct1,ct2], rootresults = optimize.newton(fx, NumYearsWithIV, fprime=fpx, args=(a,b,c,d,e),
                                                                      full_output=True, disp=False)
                # if the NR method didn't converge
                if rootresults.converged == False:
                    # set to 1000, so that it always shoots off the plot to look better / really represent what’s going
                    # on (the number of years asymptotically approaching infinity)
                    NumYearsArray[ct1,ct2] = 1000
                    StillConverging = False

                # if the number of years exceeds 100, then can safely stop the loop over income growth rates (and
                # prevents errors from popping up that are unnecessary to see)
                if NumYearsArray[ct1,ct2] > 100.:
                    StillConverging = False

            else:
                # specify as NaN so it's not plotted
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncGrowthRateArray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': SavingsRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 50,
         'xmin': IncGrowthRateArray[-1]*100-0.02, 'xmax': IncGrowthRateArray[0]*100+0.02,
         'ylabel': 'Number of Years to FI',
         'xlabel': 'Income Growth Rate Relative To Inflation (%)',
         'TitleText': 'Years to FI vs Income Growth Rate, \n Initial Income $75K',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIvsIncGrowthRate.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


# Plot time to FI vs Expense Growth Rate (relative to inflation) for multiple income growth rate,
# same income (kept in current year dollars, i.e. adjusted exactly by inflation each year) and initial savings rate (50%)
if NumYearsToFIvsExpGrowthRateForMultipleIncGrowthRates:

    NumSteps = 1000
    IncGrowthRateArray = np.array([-0.06,-0.03,0.0,0.03,0.06])
    NumYearsArray = np.zeros((len(IncGrowthRateArray),NumSteps))
    ExpGrowthRateArray = np.arange(-0.1,0.1,0.2/NumSteps)
    PlotLabelArray = [''] * len(IncGrowthRateArray)
    PlotColorArray = ['r','b','g','c','m']

    Inc = 75000
    Exp = (1 - 0.5) * Inc
    IV = 0.0

    # Loop over income growth rates
    for ct1 in range(0, len(IncGrowthRateArray)):

        # labels for plots
        PlotLabelArray[ct1] = str(int(IncGrowthRateArray[ct1]*100))+'% Income Growth Rate'

        # initial value, with RI and RE equal zero (assuming expenses and income grow at exactly inflation)
        NumYearsWithIV = np.log( (1 - 0.5 + (WR*0.5)/R) / ( (WR*IV)/Inc + (WR*0.5)/R ) ) / np.log(1+R)

        # initialize convergence flag
        StillConverging = True

        # Generate array of number of years to FI for this income growth rate
        for ct2 in range(0, NumSteps):
            if StillConverging:
                # Avoid singularity when R = RE
                if abs(R - ExpGrowthRateArray[ct2]) < 0.0001:
                    a = Exp - WR*IV - WR*Inc*((1+IncGrowthRateArray[ct1])/(R-IncGrowthRateArray[ct1]))
                    b = -WR*Inc*((1+IncGrowthRateArray[ct1])/(R-IncGrowthRateArray[ct1]))
                    c = (1+IncGrowthRateArray[ct1])/(1+R)
                    d = WR * Exp
                    NumYearsArray[ct1,ct2], rootresults = optimize.newton(fxReqRE, NumYearsWithIV, fprime=fpxReqRE,
                                                                          args=(a,b,c,d), full_output=True, disp=False)
                    if rootresults.converged == False: # just in case it still doesn't converge
                        NumYearsArray[ct1,ct2] = float("nan")
                    continue

                a = Exp - WR * Exp * ((1+ExpGrowthRateArray[ct2])/(R-ExpGrowthRateArray[ct2]))
                b = WR * (IV + Inc*((1+IncGrowthRateArray[ct1])/(R-IncGrowthRateArray[ct1])) -
                          Exp*((1+ExpGrowthRateArray[ct2])/(R-ExpGrowthRateArray[ct2])))
                c = (1+R)/(1+ExpGrowthRateArray[ct2])
                d = WR * Inc * (1+IncGrowthRateArray[ct1])/(R-IncGrowthRateArray[ct1])
                e = (1+IncGrowthRateArray[ct1])/(1+ExpGrowthRateArray[ct2])
                NumYearsArray[ct1,ct2], rootresults = optimize.newton(fx, NumYearsWithIV, fprime=fpx, args=(a,b,c,d,e),
                                                                      full_output=True, disp=False)
                # if the NR method didn't converge
                if rootresults.converged == False:
                    # set to 1000, so that it always shoots off the plot to look better / really represent what’s going
                    # on (the number of years asymptotically approaching infinity)
                    NumYearsArray[ct1,ct2] = 1000
                    StillConverging = False
            else:
                # specify as NaN so it's not plotted
                NumYearsArray[ct1,ct2] = float("nan")

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ExpGrowthRateArray*100,
         'DepData': NumYearsArray,
         'MultiPlotProperties': IncGrowthRateArray,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0, 'ymax': 50,
         'xmin': ExpGrowthRateArray[0]*100, 'xmax': ExpGrowthRateArray[-1]*100+0.02,
         'ylabel': 'Number of Years to FI',
         'xlabel': 'Expense Growth Rate Relative To Inflation (%)',
         'TitleText': 'Years to FI vs Expense Growth Rate, \n Initial Income \$75K and Expenses \$37.5K',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'NumYearsToFIvsExpGrowthRateForMultipleIncGrowthRates.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
