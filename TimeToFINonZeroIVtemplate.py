# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/time-to-fi-starting-above-0/)

# TimeToFINonZeroIVtemplate.py

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
matplotlib.rcParams.update({'font.size': 23})

import os

# Compute and plot time to FI

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
SR = 0.5
# Annual withdrawal rate
WR = 0.04
# Annual interest rate (i.e. expected investment return)
R = 0.05

# Annual income
I = 80000
# Initial net worth
IV = 100000 # 50000 #

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

#############################################################################################################

# Plot time to FI vs starting balance
def PlotNumYearsToFIvsIV(YearsArray,IVarray,SaveFile):

    # Properties for text boxes
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    fig = plt.figure(1,figsize=(13.16,10.0))
    plt.plot(IVarray/1000, YearsArray, '-', linewidth=3, color='r')

    ax = plt.gca()
    plt.ylim(0,np.round(YearsArray[0])+1)
    plt.xlim(0,IVarray[-1]/1000+1)

    # add site name, bottom left
    ax.text(0.01, 0.04, 'EngineeringYourFI.com', transform=ax.transAxes, fontsize=20, verticalalignment='top') #, bbox=props)

    ax.ticklabel_format(useOffset=False)
    plt.ylabel('Number of Years to FI', fontsize=30)
    plt.xlabel('Initial Portfolio Balance ($K)', fontsize=30)
    plt.title('Years to FI vs Initial Balance, Saving 50%', y=1.04, fontsize=35)
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--')
    plt.tight_layout()
    plt.savefig(SaveFile)
    plt.close()

# number of years to FI vs starting balance
NumSteps = 1000
NumYearsArray = np.zeros(NumSteps)
IVarray = np.zeros(NumSteps)
# Compute expenses from income and savings rate, then your FI number from your expenses and withdrawal rate
Expenses = I * SR
FInum = Expenses / WR

# Generate arrays of initial portfolio values and corresponding number of years to FI
for ct in range(0, NumSteps):
    IVarray[ct] = FInum / NumSteps * ct
    NumYearsArray[ct] = np.log( (1 - SR + (WR*SR)/R) / ( (WR*IVarray[ct])/I + (WR*SR)/R ) ) / np.log(1+R)

PlotNumYearsToFIvsIV(NumYearsArray,IVarray,OutDir+'NumYearsToFIvsIV.png')

#############################################################################################################

# Plot time to FI vs starting balance for multiple savings rates, same FI number (and thus same expenses, so different
# incomes)
def PlotNumYearsToFIvsIVmulti(YearsArray,IVarray,SavingsRateArray,PlotColorsArray,SaveFile):

    # Properties for text boxes
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    fig = plt.figure(1,figsize=(13.16,10.0))

    # Loop over savings rates, plot Years to FI values for each vs initial value
    for ct in range(0,len(SavingsRateArray)):
        plt.plot(IVarray/1000, YearsArray[ct,:], '-', linewidth=3, color=PlotColorsArray[ct],
                 label=str(int(SavingsRateArray[ct]*100))+'% SR')

    ax = plt.gca()
    plt.ylim(0,np.round(YearsArray[0,0])+1)
    plt.xlim(0,IVarray[-1]/1000+1)

    # add site name, top left
    ax.text(0.01, 1-0.01, 'EngineeringYourFI.com', transform=ax.transAxes, fontsize=20, verticalalignment='top')

    ax.ticklabel_format(useOffset=False)
    plt.ylabel('Number of Years to FI', fontsize=30)
    plt.xlabel('Initial Portfolio Balance ($K)', fontsize=30)
    plt.title('Years to FI vs Initial Balance, Expenses $40K', y=1.04, fontsize=35)
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--')
    plt.legend(loc='best',fontsize=20,numpoints=1)
    plt.tight_layout()
    plt.savefig(SaveFile)
    plt.close()

# To have a consistent x axis, expenses need to always be 40K so the FI number is always 1M
# e.g. for a FI number of 1M, expenses always need to be 40K
# So need to modify income each time savings rate modified

SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
IncomeArray = np.zeros(len(SavingsRateArray))
PlotColorsArray = ['r','b','g','c','m']

# Loop over savings rates
for ct1 in range(0, len(SavingsRateArray)):

    # Determine income from savings rate and constant expenses
    # SR = (I - E) / I
    #    = 1 - E/I
    # E / I = 1 - SR
    # I = E / (1 - SR)
    IncomeArray[ct1] = Expenses / (1 - SavingsRateArray[ct1])

    # Generate array of number of years to FI for this savings rate
    for ct2 in range(0, NumSteps):
        NumYearsArray[ct1,ct2] = np.log( (1 - SavingsRateArray[ct1] + (WR*SavingsRateArray[ct1])/R) /
                                         ( (WR*IVarray[ct2])/IncomeArray[ct1] + (WR*SavingsRateArray[ct1])/R ) ) / \
                                 np.log(1+R)

PlotNumYearsToFIvsIVmulti(NumYearsArray,IVarray,SavingsRateArray,PlotColorsArray,OutDir+'NumYearsToFIvsIVmultipleSR.png')

#############################################################################################################

# Plot time to FI vs expenses for multiple savings rates

def PlotNumYearsToFIvsExpensesMulti(YearsArray,ExpensesArray,SavingsRateArray,PlotColorsArray,SaveFile):

    # Properties for text boxes
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    fig = plt.figure(1,figsize=(13.16,10.0))

    # Loop over savings rates, plot Years to FI values for each vs initial value
    for ct in range(0,len(SavingsRateArray)):
        plt.plot(ExpensesArray/1000, YearsArray[ct,:], '-', linewidth=3, color=PlotColorsArray[ct],
                 label=str(int(SavingsRateArray[ct]*100))+'% SR')

    ax = plt.gca()
    plt.ylim(0,np.round(YearsArray[0,-1])+1)
    plt.xlim(0,ExpensesArray[-1]/1000+0.1)

    # add site name, bottom right
    ax.text(1-0.29, 0.04, 'EngineeringYourFI.com', transform=ax.transAxes, fontsize=20, verticalalignment='top')

    ax.ticklabel_format(useOffset=False)
    plt.ylabel('Number of Years to FI', fontsize=30)
    plt.xlabel('Annual Expenses ($K)', fontsize=30)
    plt.title('Years to FI vs Expenses, Initial Balance $200K', y=1.04, fontsize=35)
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--')
    plt.legend(loc='best',fontsize=20,numpoints=1)
    plt.tight_layout()
    plt.savefig(SaveFile)
    plt.close()

# Resetting just in case
SavingsRateArray = np.array([0.1,0.3,0.5,0.7,0.9])
NumYearsArray = np.zeros((len(SavingsRateArray),NumSteps))
ExpensesArray = np.zeros(NumSteps)
PlotColorsArray = ['r','b','g','c','m']

# Assuming $200K initial portfolio value, and max expenses of 100K (beyond which expenses are just ridiculous)
IV = 200000
MaxExpenses = 100000
MinExpenses = IV * WR

# Loop over savings rates
for ct1 in range(0, len(SavingsRateArray)):

    # Loop over expenses
    for ct2 in range(0, NumSteps):

        ExpensesArray[ct2] = (MaxExpenses-MinExpenses) / NumSteps * ct2 + MinExpenses

        # Determine income from savings rate and expenses
        # SR = (I - E) / I
        #    = 1 - E/I
        # E / I = 1 - SR
        # I = E / (1 - SR)
        Income = ExpensesArray[ct2] / (1 - SavingsRateArray[ct1])

        NumYearsArray[ct1,ct2] = np.log( (1 - SavingsRateArray[ct1] + (WR*SavingsRateArray[ct1])/R) /
                                         ( (WR*IV)/Income + (WR*SavingsRateArray[ct1])/R ) ) / np.log(1+R)

PlotNumYearsToFIvsExpensesMulti(NumYearsArray,ExpensesArray,SavingsRateArray,PlotColorsArray,
                                OutDir+'NumYearsToFIvsExpensesMultipleSR.png')

