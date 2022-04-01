# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/what-savings-rate-should-i-aim-for/)

# SavingsRate.py

import numpy as np

import matplotlib
# matplotlib.use('TkAgg')
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
matplotlib.rcParams.update({'font.size': 23})

import os

# Compute and plot time to FI given initial net worth and savings rate

# Derivation:
# Savings = Income - Expenses
# Expenses = Income - Savings
# Expenses = WithdrawalRate * FutureValue
# E = I - S = WR * FV
# Future value from initial value/balance
# FVA = IV * (1+R)^N
# IV = initial value, R = assumed annual interest rate (i.e. investment return rate), N = Number of Years
# Future value from ongoing payments (i.e. your savings from income)
# FVB = S * ((1+R)^N - 1)/R
# Both future value equations well established in literature, and shown here:
# https://en.wikipedia.org/wiki/Compound_interest#Investing:_monthly_deposits

# Pulling everything together and solving for N:
# I - S = WR * ( IV * (1+R)^N + S * ((1+R)^N - 1)/R)
# dividing by I on both sides:
# 1 - SR = WR * ( IV * (1/I) * (1+R)^N + SR * ((1+R)^N - 1)/R)
# Where SR = savings rate = S / I
# 1 - SR = (WR*IV)/I * (1+R)^N + (WR*SR)/R * (1+R)^2 - (WR*SR)/R

# 1 - SR + (WR*SR)/R = ( (WR*IV)/I + (WR*SR)/R ) * (1+R)^N
# (1 - SR + (WR*SR)/R) / ( (WR*IV)/I + (WR*SR)/R ) = (1+R)^N
# ln( (1 - SR + (WR*SR)/R) / ( (WR*IV)/I + (WR*SR)/R ) ) / ln(1+R) = N
# So N is a function of: SR, WR, R, IV, I

# If IV = 0
# ln( (1 - SR + (WR*SR)/R) / ( (WR*SR)/R ) ) / ln(1+R) = N
# ln( (1/(WR*SR)) * (R - R*SR) + 1 ) / ln(1+R) = N
# So N is a function of: SR, WR, R - no income or initial value

# To express N in terms of E and SR instead of I:
# SR = S / I = (I - E) / I = 1 - E / I
# E / I = 1 - SR
# I = E / (1 - SR)
# Plugging this expression for I into general expression for N:
# N = ln( (1 - SR + (WR*SR)/R) / ( (WR*IV)/(E / (1 - SR)) + (WR*SR)/R ) ) / ln(1+R)
# N = ln( (1 - SR + (WR*SR)/R) / ( (WR*IV*(1 - SR)) / E + (WR*SR)/R ) ) / ln(1+R)
# Thus for given IV, the lower E is, the lower N is. I.t. for any given initial amount of money you start with,
# the lower your expenses, the closer you are to FI.

#############################################################################################################
# Inputs

# Savings rate
SR = 0.5 #0.7 #
# Annual withdrawal rate
WR = 0.04
# Annual interest rate (i.e. expected investment return)
R = 0.05

# Annual income
I = 100000
# Initial net worth
IV = 0 # 50000 #

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Plotting
PlotMarkerSize = 10

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

# Compute number of years to FI with full expression
# N = ln( (1 - SR + (WR*SR)/R) / ( (WR*IV)/I + (WR*SR)/R ) ) / ln(1+R)
NumYearsWithIV = np.log( (1 - SR + (WR*SR)/R) / ( (WR*IV)/I + (WR*SR)/R ) ) / np.log(1+R)
print('NumYearsWithIV = ', str(NumYearsWithIV))

# Compute number of years to FI with IV assumed zero
# N = ln( (1/(WR*SR)) * (R - R*SR) + 1 ) / ln(1+R)
NumYearsWithoutIV = np.log( (1/(WR*SR)) * (R - R*SR) + 1 ) / np.log(1+R)
print('NumYearsWithoutIV = ', str(NumYearsWithoutIV))

#############################################################################################################

def PlotNumYearsToFI(YearsArray,SaveFile):
    # Properties for text boxes
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    NumSteps = len(YearsArray)
    IndexArray = np.arange(0,NumSteps)/NumSteps*100

    fig = plt.figure(1,figsize=(13.16,10.0))
    plt.plot(IndexArray, YearsArray, '-', linewidth=3, color='r')

    ax = plt.gca()
    plt.ylim(0,100)
    plt.xlim(0,100)
    # Putting dots at 10% intervals, starting at 10% savings rate
    for ct in range(1,10):
        SRct = IndexArray[int(ct/10*NumSteps)]
        NumYearsCt = YearsArray[int(ct/10*NumSteps)-1]

        plt.plot(SRct, NumYearsCt, 'o', markersize=PlotMarkerSize, markeredgewidth=1, markeredgecolor='k', markerfacecolor='k')

        # place a text box for each point
        if NumYearsCt < 100 and NumYearsCt > 0:
            if ct == 1:
                ax.text(SRct/100+0.02, NumYearsCt/100+0.06, '{:0.1f}'.format(NumYearsCt)+' Years', transform=ax.transAxes,
                        fontsize=30, verticalalignment='top', bbox=props)
            else:
                ax.text(SRct/100+0.02, NumYearsCt/100+0.06, '{:0.1f}'.format(NumYearsCt), transform=ax.transAxes,
                        fontsize=30, verticalalignment='top', bbox=props)

    # add site name, bottom left
    ax.text(0.01, 0.04, 'EngineeringYourFI.com', transform=ax.transAxes, fontsize=20, verticalalignment='top') #, bbox=props)

    ax.ticklabel_format(useOffset=False)
    plt.ylabel('Number of Years to FI', fontsize=30) #,fontsize=20)
    plt.xlabel('Savings Rate %', fontsize=30) #,fontsize=20)
    plt.title('Years to FI vs Savings Rate, Starting with $0', y=1.04, fontsize=35) # fontsize=23,
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--') # or just plt.grid(True)  color='lightgray'
    # plt.legend(loc='best',fontsize=20,numpoints=1)
    plt.tight_layout()
    plt.savefig(SaveFile)
    plt.close()


# number of years to FI vs SR, IV = 0
NumSteps = 1000
NumYearsWithoutIVarray = np.zeros(NumSteps)
for ct in range(0, NumSteps):
    SR = (ct+1)/NumSteps
    NumYearsWithoutIVarray[ct] = np.log( (1/(WR*SR)) * (R - R*SR) + 1 ) / np.log(1+R)

PlotNumYearsToFI(NumYearsWithoutIVarray,OutDir+'NumYearsToFI_noIV.png')


#############################################################################################################

def PlotNumYearsToFIMulti(YearsArray1,YearsArray2,SecondLineType,SecondLineColor,LegendLine1,LegendLine2,
                          TextBoxLine1xOff,TextBoxLine1yOff,TextBoxLine2xOff,TextBoxLine2yOff,YearsLabelLine,SaveFile):
    # Properties for text boxes
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    NumSteps = len(YearsArray1)
    IndexArray = np.arange(0,NumSteps)/NumSteps*100

    fig = plt.figure(1,figsize=(13.16,10.0))
    plt.plot(IndexArray, YearsArray1, '-', linewidth=3, color='r', label=LegendLine1)
    plt.plot(IndexArray, YearsArray2, SecondLineType, linewidth=3, color=SecondLineColor, label=LegendLine2)

    ax = plt.gca()
    plt.ylim(0,100)
    plt.xlim(0,100)
    # Putting dots at 10% intervals, starting at 10% savings rate
    for ct in range(1,10):
        SRct = IndexArray[int(ct/10*NumSteps)]
        NumYearsCt1 = YearsArray1[int(ct/10*NumSteps)-1]
        NumYearsCt2 = YearsArray2[int(ct/10*NumSteps)-1]
        plt.plot(SRct, NumYearsCt1, 'o', markersize=PlotMarkerSize, markeredgewidth=1, markeredgecolor='k', markerfacecolor='k')
        plt.plot(SRct, NumYearsCt2, 'o', markersize=PlotMarkerSize, markeredgewidth=1, markeredgecolor='k', markerfacecolor='k')
        # place a text box for each point
        if NumYearsCt1 < 100 and NumYearsCt1 > 0:
            if ct == 1 and YearsLabelLine == 1:
                ax.text(SRct/100+TextBoxLine1xOff, NumYearsCt1/100+TextBoxLine1yOff, '{:0.1f}'.format(NumYearsCt1)+' Years',
                        transform=ax.transAxes, fontsize=30, verticalalignment='top', bbox=props)
            else:
                ax.text(SRct/100+TextBoxLine1xOff, NumYearsCt1/100+TextBoxLine1yOff, '{:0.1f}'.format(NumYearsCt1),
                        transform=ax.transAxes, fontsize=30, verticalalignment='top', bbox=props)
        if NumYearsCt2 < 100 and NumYearsCt2 > 0:
            if ct == 1 and YearsLabelLine == 2:
                ax.text(SRct/100+TextBoxLine2xOff, NumYearsCt2/100+TextBoxLine2yOff, '{:0.1f}'.format(NumYearsCt2)+' Years',
                            transform=ax.transAxes, fontsize=30, verticalalignment='top', bbox=props)
            else:
                ax.text(SRct/100+TextBoxLine2xOff, NumYearsCt2/100+TextBoxLine2yOff, '{:0.1f}'.format(NumYearsCt2),
                            transform=ax.transAxes, fontsize=30, verticalalignment='top', bbox=props)

    # add site name, bottom left
    ax.text(0.01, 0.04, 'EngineeringYourFI.com', transform=ax.transAxes, fontsize=20, verticalalignment='top') #, bbox=props)

    ax.ticklabel_format(useOffset=False)
    plt.ylabel('Number of Years to FI', fontsize=30) #,fontsize=20)
    plt.xlabel('Savings Rate %', fontsize=30) #,fontsize=20)
    plt.title('Years to FI vs Savings Rate, Starting with $0', y=1.04, fontsize=35) # fontsize=23,
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--') # or just plt.grid(True)  color='lightgray'
    plt.legend(loc='best',fontsize=30,numpoints=1)
    plt.tight_layout()
    plt.savefig(SaveFile)
    plt.close()


# Higher Annual interest rate (i.e. expected investment return)
R_75 = 0.075
SR = 0.5
NumYearsWithoutIV_R_75 = np.log( (1/(WR*SR)) * (R_75 - R_75*SR) + 1 ) / np.log(1+R_75)
print('NumYearsWithoutIVhigherROIof7.5 = ', str(NumYearsWithoutIV_R_75))

NumYearsWithoutIVarrayR_75 = np.zeros(NumSteps)
for ct in range(0, NumSteps):
    SR = (ct+1)/NumSteps
    NumYearsWithoutIVarrayR_75[ct] = np.log( (1/(WR*SR)) * (R_75 - R_75*SR) + 1 ) / np.log(1+R_75)

PlotNumYearsToFIMulti(NumYearsWithoutIVarray,NumYearsWithoutIVarrayR_75,'--','b','Annual Investment Interest = 5%',
                      'Annual Investment Interest = 7.5%',0.02,0.06,-0.08,-0.03,1,OutDir+'NumYearsToFI_noIV_R7.5.png')


# Lower safe withdrawal rate
SR = 0.5
WR_35 = 0.035
NumYearsWithoutIV_WR_35 = np.log( (1/(WR_35*SR)) * (R - R*SR) + 1 ) / np.log(1+R)
print('NumYearsWithoutIVlowerSWRof3.5 = ', str(NumYearsWithoutIV_WR_35))

NumYearsWithoutIVarrayWR_35 = np.zeros(NumSteps)
for ct in range(0, NumSteps):
    SR = (ct+1)/NumSteps
    NumYearsWithoutIVarrayWR_35[ct] = np.log( (1/(WR_35*SR)) * (R - R*SR) + 1 ) / np.log(1+R)

PlotNumYearsToFIMulti(NumYearsWithoutIVarray,NumYearsWithoutIVarrayWR_35,'--','g','Withdrawal Rate = 4%',
                      'Withdrawal Rate = 3.5%',-0.08,-0.03,0.02,0.06,2,OutDir+'NumYearsToFI_noIV_WR_3.5.png')
