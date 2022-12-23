# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ExecuteDeltaWithdrawal.py

import numpy as np
from WithdrawalOptimization.WithdrawFromPostTaxDelta import *
from WithdrawalOptimization.TaxableSSconsolidated import *
from WithdrawalOptimization.ComputeTaxes import *
from WithdrawalOptimization.WithdrawFromRothDelta import *
from WithdrawalOptimization.WithdrawFrom457bDelta import *
from WithdrawalOptimization.WithdrawFromPreTaxDelta import *

# Withdraw from the lowest tax+penalty delta percentage account, even if it doesn't provide full Step

def ExecuteDeltaWithdrawal(PostTax,Roth,PreTax457b,PreTax,Taxes,Income,TotalCash,Penalties, NumPeople,Step,
                           IVdict,YearCt,TotalSS,TaxableSS,IncTotStd,IncTotLTcapGains,FilingStatus,TaxRateInfo,
                           Age,DeltaPercentArray,PreTax457bIndices,PreTaxIndices,PostTaxIndex,RothIndices):

    # Determine which delta is smallest, go with that account (even if it doesn't provide full Step)
    # For some reason, np.nanargmin only returns the first
    DeltaPercentMinIndices = np.where(DeltaPercentArray==np.nanmin(DeltaPercentArray))[0]

    # If multiple accounts have the same tax+penalty percentage, select the account to withdraw from in this order:
    # 1. PreTax457b (good for reducing RMDs)
    # 2. PreTax (good for reducing RMDs)
    # 3. PostTax
    # 4. Roth (best for estate, so try to tap last)

    ##################################################################################################################
    # 457b
    ##################################################################################################################

    if any(np.isin(DeltaPercentMinIndices,PreTax457bIndices)):
        # Withdraw from whichever PreTax457b index is lower (corresponding to the first/older person)
        # Loop over all PreTax457bIndices, starting with lowest
        for ct in range(NumPeople):
            if PreTax457bIndices[ct] in DeltaPercentMinIndices:
                AcctToDrawFrom = ct
                break

        Withdrawal = WithdrawFrom457bDelta(PreTax457b,Income,TotalCash,Step,YearCt,AcctToDrawFrom,True)
        IncTotStd = Income['TotalStandard'][YearCt] # updating, for use here & next iteration of while loop
        # If SSI, recompute taxable SSI for higher income, then update total standard income
        if TotalSS > 0.:
            NonSSstandardIncome = IncTotStd - TaxableSS
            TaxableSS = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains, TotalSS, FilingStatus)
            Income['TaxableSS'][YearCt] = TaxableSS # updating
            IncTotStd = NonSSstandardIncome + TaxableSS
            Income['TotalStandard'][YearCt] = IncTotStd # updating
            Income['Total'][YearCt] = IncTotStd + IncTotLTcapGains # updating
        # Update Taxes
        NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStd,IncTotLTcapGains)
        Taxes[YearCt] = NewTaxes['Total']

    ##################################################################################################################
    # PreTax
    ##################################################################################################################

    elif any(np.isin(DeltaPercentMinIndices,PreTaxIndices)):
        # Withdraw from whichever PreTax index is lower (corresponding to the first/older person)
        # Loop over all PreTaxIndices, starting with lowest
        for ct in range(NumPeople):
            if PreTaxIndices[ct] in DeltaPercentMinIndices:
                AcctToDrawFrom = ct
                break

        Withdrawal, Penalty = WithdrawFromPreTaxDelta(PreTax,Income,TotalCash,Step,Age,YearCt,AcctToDrawFrom,True)
        Penalties[YearCt] += Penalty
        IncTotStd = Income['TotalStandard'][YearCt] # updating, for use here & next iteration of while loop
        # If SSI, recompute taxable SSI for higher income, then update total standard income
        if TotalSS > 0.:
            NonSSstandardIncome = IncTotStd - TaxableSS
            TaxableSS = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains, TotalSS, FilingStatus)
            Income['TaxableSS'][YearCt] = TaxableSS # updating
            IncTotStd = NonSSstandardIncome + TaxableSS
            Income['TotalStandard'][YearCt] = IncTotStd # updating
            Income['Total'][YearCt] = IncTotStd + IncTotLTcapGains # updating
        # Update Taxes
        NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStd,IncTotLTcapGains)
        Taxes[YearCt] = NewTaxes['Total']

    ##################################################################################################################
    # PostTax
    ##################################################################################################################

    elif PostTaxIndex in DeltaPercentMinIndices:
        # Then withdraw from PostTax
        Withdrawal, LTCGdelta = WithdrawFromPostTaxDelta(PostTax,Step,TotalCash,Income,IVdict,YearCt,True)
        IncTotLTcapGains = Income['TotalLTcapGains'][YearCt] # updating, for use here & next iteration of while loop
        # If SSI, recompute taxable SSI for higher income, then update total standard income
        if TotalSS > 0.:
            NonSSstandardIncome = IncTotStd - TaxableSS
            TaxableSS = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains, TotalSS, FilingStatus)
            Income['TaxableSS'][YearCt] = TaxableSS # updating
            IncTotStd = NonSSstandardIncome + TaxableSS
            Income['TotalStandard'][YearCt] = IncTotStd # updating
            Income['Total'][YearCt] = IncTotStd + IncTotLTcapGains # updating
        # Update Taxes
        NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStd,IncTotLTcapGains)
        Taxes[YearCt] = NewTaxes['Total']

    ##################################################################################################################
    # Roth
    ##################################################################################################################

    elif any(np.isin(DeltaPercentMinIndices,RothIndices)): # if any Roth index is in DeltaPercentMinIndices
        # Withdraw from whichever Roth index is lower (corresponding to the first/older person)
        # Loop over all RothIndices, starting with lowest
        for ct in range(NumPeople): #len(RothIndices)
            if RothIndices[ct] in DeltaPercentMinIndices:
                AcctToDrawFrom = ct
                break

        Withdrawal, Penalty = WithdrawFromRothDelta(Roth,Step,TotalCash,YearCt,AcctToDrawFrom,True)
        Penalties[YearCt] += Penalty
    else:
        print('Delta percent min indices not corresponding to specific account - investigate.')
        exit()

    return IncTotStd, TaxableSS, IncTotLTcapGains