# Copyright (c) 2019 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/should-you-refinance-your-mortgage-consider-investment-returns/)

# MortgageRefinanceDecisionTemplate.py

import numpy as np

import matplotlib
matplotlib.use('TkAgg')
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Compute and plot liquid account balance over time for different mortgage refinance / non-refinance options
# Include investment return opportunity costs (especially for closing costs) in all options

# Formula for computing monthly payments for given interest and loan amount:
# From https://www.thebalance.com/loan-payment-calculations-315564 and http://www.oxfordmathcenter.com/drupal7/node/434:
# P = L * ( r*(1+r)^n ) / ( (1+r)^n - 1)
# P = monthly payment
# L = Loan amount
# r = monthly interest rate = annual interest rate / 12 (not actually correct, but every source I find says this)
# n = number of payments = number of years * 12 (360 for 30 year mortgage)

#############################################################################################################
# Inputs

# * Total closing cost
# * Mortgage rate
# * Size of the loan (at most 80% of the value of the house, so that can have tradition mortgage with 20% equity)
# * Assumed annual return for the market

# The initial liquid cash balance doesn't impact the difference in balances, so just use a reasonable number
# that is larger than the refi cost (otherwise it turns negative)
InitialLiquidBalance = 200000
# Original loan amount
OriginalLoanAmount = 189600
# Current mortgage rate
CurrentMortgageRate = 0.0475
# Number of months of current mortgage
NumMonths = 360 # 30 year mortgage
# Loan Origination Date 09/25/13, Original Maturity Date 10/2043
# Current month: Nov 2019
# So 11 months, plus 2020 to 2043
RemainingNumberOfMonthsOnCurrentLoan = 11+(2043-2020)*12

NewLoanAmount = 169455.74
NewInterestRate = 0.038 # Annual, for 30 year mortgage
ReFiCost = 4345 # https://www.valuepenguin.com/mortgages/average-cost-of-refinance
# Possibly more accurate: 235+480+0.01*NewLoanAmount+255+275+750+733+138+58
NumMonthsNewLoan = 360 # 30 year mortgage

# Assumed rate of return for investments in index funds
MarketReturnRate = 0.07 #0.04 #0.00 # annual

# Evaluating cash-out refinance, using the additional funds to invest in the market:
ShowCashOutRefi = True
# If house is worth ~350k, and you get a mortgage for 80% of that: 280k
NewLoanAmountV2 = 0.8*350000
NewLoanV2minusCurrentBalance = NewLoanAmountV2-NewLoanAmount

# Evaluating 15 year mortgage
Show15yearRefi = True
# NewLoanAmount same as 30 year refi
New15yearInterestRate = 0.032
# ReFiCost same as 30 year refi
NumMonthsNewLoan15year = 180 # 15 year mortgage
# MarketReturnRate as 30 year refi

# Output file
OutputFile = 'Output.txt'

#############################################################################################################
# Calculating different mortgage rates

# Testing monthly payment calculation with current mortgage:
MonthlyMortgageRate = CurrentMortgageRate/12
P = OriginalLoanAmount * (MonthlyMortgageRate*(1+MonthlyMortgageRate)**NumMonths) / \
    ((1+MonthlyMortgageRate)**NumMonths - 1)
print('Current Monthly Payment (confirm) = '+str(round(P,2)))
# TotalInterest = P*NumMonths - OriginalLoanAmount

# New loan payment for normal refi
NewMonthlyMortgageRate = NewInterestRate/12
Pnew = NewLoanAmount * (NewMonthlyMortgageRate*(1+NewMonthlyMortgageRate)**NumMonths) / \
       ((1+NewMonthlyMortgageRate)**NumMonths - 1)
print('New Monthly Payment = '+str(round(Pnew,2)))
# TotalInterestNew = Pnew*NumMonths - OriginalLoanAmount

# New loan payment for cash-out refi (V2)
if ShowCashOutRefi:
    PnewV2 = NewLoanAmountV2 * (NewMonthlyMortgageRate*(1+NewMonthlyMortgageRate)**NumMonths) / \
             ((1+NewMonthlyMortgageRate)**NumMonths - 1)
    print('New Monthly Payment for Cash-out Refi = '+str(round(PnewV2,2)))

# new loan payment for 15 year refi
if Show15yearRefi:
    NewMonthly15yearInterestRate = New15yearInterestRate/12
    Pnew15year = NewLoanAmount * (NewMonthly15yearInterestRate*(1+NewMonthly15yearInterestRate)**NumMonthsNewLoan15year) / \
                 ((1+NewMonthly15yearInterestRate)**NumMonthsNewLoan15year - 1)
    print('New Monthly Payment for 15 year Refi = '+str(round(Pnew15year,2)))

#############################################################################################################
# Compute result of not refinancing, over the next 30 years (360 months)
LiquidBalance = np.zeros(360+1)
LiquidBalance[0] = InitialLiquidBalance
for ct in range(0,360):
    if ct < RemainingNumberOfMonthsOnCurrentLoan:
        LiquidBalance[ct+1] = LiquidBalance[ct] - round(P,2)
        LiquidBalance[ct+1] = LiquidBalance[ct+1] * (1+MarketReturnRate/12) # simplification dividing by 12
    else:
        LiquidBalance[ct+1] = LiquidBalance[ct] * (1+MarketReturnRate/12)  # simplification dividing by 12


#############################################################################################################
# Result of refinancing, over the next 30 years (360 months)
LiquidBalanceRefi = np.zeros(360+1)
LiquidBalanceRefi[0] = InitialLiquidBalance - ReFiCost
for ct in range(0,360):
    if ct < NumMonthsNewLoan:
        LiquidBalanceRefi[ct+1] = LiquidBalanceRefi[ct] - round(Pnew,2)
        LiquidBalanceRefi[ct+1] = LiquidBalanceRefi[ct+1] * (1+MarketReturnRate/12) # simplification dividing by 12
    else:
        LiquidBalanceRefi[ct+1] = LiquidBalanceRefi[ct] * (1+MarketReturnRate/12)  # simplification dividing by 12

#############################################################################################################
# Result of refinancing at 80% current value, over the next 30 years (360 months)
if ShowCashOutRefi:
    LiquidBalanceRefiV2 = np.zeros(360+1)
    LiquidBalanceRefiV2[0] = InitialLiquidBalance - ReFiCost + NewLoanV2minusCurrentBalance
    for ct in range(0,360):
        if ct < NumMonthsNewLoan:
            LiquidBalanceRefiV2[ct+1] = LiquidBalanceRefiV2[ct] - round(PnewV2,2)
            LiquidBalanceRefiV2[ct+1] = LiquidBalanceRefiV2[ct+1] * (1+MarketReturnRate/12) # simplification dividing by 12
        else:
            LiquidBalanceRefiV2[ct+1] = LiquidBalanceRefiV2[ct] * (1+MarketReturnRate/12)  # simplification dividing by 12

#############################################################################################################
# Result of refinancing, over the next 15 years (180 months)
if Show15yearRefi:
    LiquidBalanceRefi15yearRefi = np.zeros(360+1)
    LiquidBalanceRefi15yearRefi[0] = InitialLiquidBalance - ReFiCost
    for ct in range(0,360):
        if ct < NumMonthsNewLoan15year:
            LiquidBalanceRefi15yearRefi[ct+1] = LiquidBalanceRefi15yearRefi[ct] - round(Pnew15year,2)
            LiquidBalanceRefi15yearRefi[ct+1] = LiquidBalanceRefi15yearRefi[ct+1] * (1+MarketReturnRate/12) # simplification dividing by 12
        else:
            LiquidBalanceRefi15yearRefi[ct+1] = LiquidBalanceRefi15yearRefi[ct] * (1+MarketReturnRate/12)  # simplification dividing by 12


#############################################################################################################
# Computing break even point, max savings, output to text file
# LiquidBalance/1000-LiquidBalanceRefi/1000 - find first positive value
BalanceDiff = LiquidBalanceRefi/1000 - LiquidBalance/1000
for ct in range(0,len(BalanceDiff)):
    if BalanceDiff[ct]>0.0:
        BreakEvenIndex = ct
        break

BreakEvenMonth = ct
BreakEvenYear = float(ct)/12.0

# Print to output file
file=open(OutputFile,'w')
file.write('Break Even Month = '+str(BreakEvenMonth)+'\n')
file.write('Break Even Year = '+str(round(BreakEvenYear,2))+'\n')
file.write('End Balance Diff (30 year Refi minus NoRefi) = $'+str(round(BalanceDiff[-1],2))+'K\n')
if ShowCashOutRefi:
    file.write('End Balance Diff (Cash-Out Refi minus NoRefi) = $'+str(round(LiquidBalanceRefiV2[-1]/1000 -
                                                                             LiquidBalance[-1]/1000,2))+'K\n')
if Show15yearRefi:
    file.write('End Balance Diff (15 year Refi minus NoRefi) = $'+str(round(LiquidBalanceRefi15yearRefi[-1]/1000 -
                                                                            LiquidBalance[-1]/1000,2))+'K\n')

file.close()


#############################################################################################################
# Plotting Results

# Plotting balances

fig1 = plt.figure(1)
MonthArray = np.arange(0,361)
YearArray = MonthArray/12
plt.plot(YearArray,LiquidBalance/1000,'-b', label='No Refi') # markersize=5,
plt.plot(YearArray,LiquidBalanceRefi/1000,'-r', label='Refi') # markersize=5,
if ShowCashOutRefi:
    plt.plot(YearArray,LiquidBalanceRefiV2/1000,'-g', label='Refi at 80%') #markersize=10,
if Show15yearRefi:
    plt.plot(YearArray,LiquidBalanceRefi15yearRefi/1000,'-c', label='15 year Refi') #markersize=10,
# Add title
plt.title('Balance With and Without Refinancing',fontsize=18)
# x axis label
plt.xlabel('Years',fontsize=15)
# y axis label
plt.ylabel('Balance ($k)',fontsize=15)
plt.gca().tick_params(axis='both', which='major', labelsize=12)
# add x-axis and y-axis limits if needed
# Turn grid on
plt.grid()
# legend
plt.legend(fontsize=15)
# tight layout
plt.tight_layout()
# Save plot
plt.savefig('BalanceComparison.png')
# close plot
plt.close()


# Plotting balance difference: Refi Minus No Refi
fig1 = plt.figure(1)
MonthArray = np.arange(0,361)
YearArray = MonthArray/12
plt.plot(YearArray,LiquidBalanceRefi/1000 - LiquidBalance/1000,'-')
# Add title
plt.title('Balance: 30 Year Refi Minus No Refi',fontsize=16)
# x axis label
plt.xlabel('Years',fontsize=15)
# y axis label
plt.ylabel('Balance ($k)',fontsize=15)
plt.gca().tick_params(axis='both', which='major', labelsize=12)
# add x-axis and y-axis limits if needed
# Turn grid on
plt.grid()
# legend
# plt.legend(fontsize=15)
# tight layout
plt.tight_layout()
# Save plot
plt.savefig('BalanceDifference.png')
# close plot
plt.close()


# Plotting balance difference: Refi at 80% Home Value Minus No Refi
if ShowCashOutRefi:
    fig1 = plt.figure(1)
    MonthArray = np.arange(0,361)
    YearArray = MonthArray/12
    plt.plot(YearArray,(LiquidBalanceRefiV2 - LiquidBalance)/1000,'-')
    # Add title
    plt.title('Balance: Refi (80% Home Value) Minus No Refi',fontsize=16)
    # x axis label
    plt.xlabel('Years',fontsize=15)
    # y axis label
    plt.ylabel('Balance ($k)',fontsize=15)
    plt.gca().tick_params(axis='both', which='major', labelsize=12)
    # add x-axis and y-axis limits if needed
    # Turn grid on
    plt.grid()
    # legend
    # plt.legend(fontsize=15)
    # tight layout
    plt.tight_layout()
    # Save plot
    plt.savefig('BalanceDifferenceCashOutRefi.png')
    # close plot
    plt.close()


# Plotting balance difference: 15 year Refi Minus No Refi
if Show15yearRefi:
    fig1 = plt.figure(1)
    MonthArray = np.arange(0,361)
    YearArray = MonthArray/12
    plt.plot(YearArray,LiquidBalanceRefi15yearRefi/1000-LiquidBalance/1000,'-') #,label='No Refi Minus Refi')
    # Add title
    plt.title('Balance: 15 Year Refi Minus No Refi',fontsize=16)
    # x axis label
    plt.xlabel('Years',fontsize=15)
    # y axis label
    plt.ylabel('Balance ($k)',fontsize=15)
    plt.gca().tick_params(axis='both', which='major', labelsize=12)
    # add x-axis and y-axis limits if needed
    # Turn grid on
    plt.grid()
    # legend
    # plt.legend(fontsize=15)
    # tight layout
    plt.tight_layout()
    # Save plot
    plt.savefig('BalanceDifference15yearRefi.png')
    # close plot
    plt.close()

# Plotting balance difference: 30 year Refi Minus 15 year Refi
if Show15yearRefi:
    fig1 = plt.figure(1)
    MonthArray = np.arange(0,361)
    YearArray = MonthArray/12
    plt.plot(YearArray,LiquidBalanceRefi/1000-LiquidBalanceRefi15yearRefi/1000,'-') #,label='No Refi Minus Refi')
    # Add title
    plt.title('Balance: 30 year Refi Minus 15 Year Refi',fontsize=16)
    # x axis label
    plt.xlabel('Years',fontsize=15)
    # y axis label
    plt.ylabel('Balance ($k)',fontsize=15)
    plt.gca().tick_params(axis='both', which='major', labelsize=12)
    # add x-axis and y-axis limits if needed
    # Turn grid on
    plt.grid()
    # legend
    # plt.legend(fontsize=15)
    # tight layout
    plt.tight_layout()
    # Save plot
    plt.savefig('BalanceDifference30vs15yearRefi.png')
    # close plot
    plt.close()
