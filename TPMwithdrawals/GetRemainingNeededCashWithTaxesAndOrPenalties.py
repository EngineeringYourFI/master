# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)
import copy

# GetRemainingNeededCashWithTaxesAndOrPenalties.py

import numpy as np
from ComputeDeltaPercent import *
from ExecuteDeltaWithdrawal import *
from SingleNonZeroAcctBalStep import *

# If unable to obtain enough cash without additional taxes or penalties, proceed with sources that WILL generate
# additional taxes and/or penalties

# Employing numerical approach:
# Attempt to withdraw $100 (or another value depending on computation expense, TBD) from each account
# Compute total taxes and penalties delta from this withdrawal for each account, compute delta percentage of withdrawal
# Withdraw from lowest delta percentage account (i.e. lowest tax+penalty percentage)
# Repeat until less than $100 from TotalCashNeeded, then attempt to withdraw remaining amount for each account

def GetRemainingNeededCashWithTaxesAndOrPenalties(PreTax,PreTax457b,PostTax,Roth,Income,TotalCash,Taxes,Penalties,
                                                  IVdict,TaxRateInfo,FilingStatus,TotalCashNeeded,Age,YearCt):

    # Unpack needed dictionary items - for easier access
    TotalSS = Income['TotalSS'][YearCt]
    TaxableSS = Income['TaxableSS'][YearCt]
    IncTotStd = Income['TotalStandard'][YearCt]
    IncTotLTcapGains = Income['TotalLTcapGains'][YearCt]
    RothBal = Roth['Bal'][YearCt,:]

    NumPeople = len(RothBal)
    if NumPeople == 1: # one person: 1. PostTax, 2. Roth, 3. 457b, 4. PreTax
        NumAccounts = 4
    else: # two people: # one PostTax account, one of each tax-advantaged accounts
        NumAccounts = 7

    PostTaxIndex = np.array([0])
    if NumPeople == 1:
        RothIndices = np.array([1])
        PreTax457bIndices = np.array([2])
        PreTaxIndices = np.array([3])
    else:
        RothIndices = np.array([1,2])
        PreTax457bIndices = np.array([3,4])
        PreTaxIndices = np.array([5,6])

    # Numerical targeting increment
    TargetingIncrement = 100.

    while TotalCashNeeded - TotalCash[YearCt] >= 0.01:

        # Recompute for each step through the loop
        RemainingCashNeeded = TotalCashNeeded - TotalCash[YearCt]

        # Determine what step to take
        if RemainingCashNeeded > TargetingIncrement:
            Step = TargetingIncrement
        else:
            Step = RemainingCashNeeded

        # Compute total taxes and penalties delta for Step withdrawal for each account, compute delta % of withdrawal
        WithdrawalDeltaArray, DeltaPercentArray = ComputeDeltaPercent(PostTax,Roth,PreTax457b,PreTax,NumAccounts,
                                                                      NumPeople,Step,IVdict,YearCt,TotalSS,TaxableSS,
                                                                      IncTotStd,IncTotLTcapGains,FilingStatus,
                                                                      TaxRateInfo,Taxes,Age)

        # exit while loop if out of money - if entire WithdrawalDeltaArray is zero
        if np.sum(WithdrawalDeltaArray) == 0.:
            break

        # Determine if down to a single non-zero balance account, set step accordingly
        if np.size(np.nonzero(WithdrawalDeltaArray)) == 1:
            Step = SingleNonZeroAcctBalStep(WithdrawalDeltaArray,PostTax,Roth,PreTax457b,PreTax,YearCt,
                                            RemainingCashNeeded,NumPeople)

        # Withdraw from the lowest tax+penalty delta percentage account, even if it doesn't provide full Step
        IncTotStd, TaxableSS, IncTotLTcapGains = \
            ExecuteDeltaWithdrawal(PostTax,Roth,PreTax457b,PreTax,Taxes,Income,TotalCash,Penalties, NumPeople,Step,
                                   IVdict,YearCt,TotalSS,TaxableSS,IncTotStd,IncTotLTcapGains,FilingStatus,TaxRateInfo,
                                   Age,DeltaPercentArray,PreTax457bIndices,PreTaxIndices,PostTaxIndex,RothIndices)


    # Update "Total" values for PreTax and PreTax457b
    PreTax['Total'][YearCt] = np.sum(PreTax['Bal'][YearCt,:])
    PreTax457b['Total'][YearCt] = np.sum(PreTax457b['Bal'][YearCt,:])
    # Not needed for PostTax, since that Total value is computed at the end of ProjFinalBalance (after purchasing
    # any new PostTax lots with excess cash).

    # Also update total max and standard max if they are now lower than total and total standard, because they had
    # to increase to generate enough cash
    if Income['Total'][YearCt] > Income['MaxTotal'][YearCt]:
        Income['MaxTotal'][YearCt] = copy.deepcopy(Income['Total'][YearCt])
    if Income['TotalStandard'][YearCt] > Income['MaxStandard'][YearCt]:
        Income['MaxStandard'][YearCt] = copy.deepcopy(Income['TotalStandard'][YearCt])
