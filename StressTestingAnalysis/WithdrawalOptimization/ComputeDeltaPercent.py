# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeDeltaPercent.py

import numpy as np
from WithdrawalOptimization.WithdrawFromPostTaxDelta import *
from WithdrawalOptimization.TaxableSSconsolidated import *
from WithdrawalOptimization.ComputeTaxes import *
from WithdrawalOptimization.WithdrawFromRothDelta import *
from WithdrawalOptimization.WithdrawFrom457bDelta import *
from WithdrawalOptimization.WithdrawFromPreTaxDelta import *

# Compute total taxes and penalties delta for Step withdrawal for each account, compute delta percentage of withdrawal

def ComputeDeltaPercent(PostTax,Roth,PreTax457b,PreTax,NumAccounts,NumPeople,Step,IVdict,YearCt,TotalSS,TaxableSS,
                        IncTotStd,IncTotLTcapGains,FilingStatus,TaxRateInfo,Taxes,Age):

    # The percentage of taxes+penalties generated from withdrawals of each account type, recomputed for each increment
    DeltaPercentArray = np.zeros(NumAccounts)
    # Total withdrawal for each account (in case the lowest percentage accounts do not provide enough cash to meet Step)
    WithdrawalDeltaArray = np.zeros(NumAccounts)

    ##################################################################################################################
    # PostTax
    ##################################################################################################################

    # Pull Step from PostTax, compute LT cap gains
    # Sort the lots from lowest to highest percentage LT cap gain and sell them in that order to minimize taxes
    WithdrawalDeltaArray[0], LTCGdelta = WithdrawFromPostTaxDelta(PostTax,Step,0,0,IVdict,YearCt,False)
    if WithdrawalDeltaArray[0] > 0.: # if PostTax still has non-zero balance
        # if SSI, recompute taxable SSI for higher income, then update total standard income
        if TotalSS > 0.:
            NonSSstandardIncome = IncTotStd - TaxableSS
            TaxableSSdelta = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains + LTCGdelta, TotalSS,
                                                   FilingStatus)
            IncTotStdDelta = NonSSstandardIncome + TaxableSSdelta
        else: IncTotStdDelta = IncTotStd
        # Determine Delta % in taxes
        NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStdDelta,IncTotLTcapGains + LTCGdelta)
        Delta = NewTaxes['Total'] - Taxes[YearCt]
        DeltaPercentArray[0] = Delta / WithdrawalDeltaArray[0]
    else:
        DeltaPercentArray[0] = np.nan

    ##################################################################################################################
    # Roth
    ##################################################################################################################

    # Pull Step from Roth - for each person
    for ct in range(NumPeople):
        WithdrawalDeltaArray[1+ct], Penalty = WithdrawFromRothDelta(Roth,Step,0,YearCt,ct,False)
        if WithdrawalDeltaArray[1+ct] > 0.: # if Roth still has non-zero balance
            # Determine Delta % in penalties (Roth will only be non-zero at this point if under 60, because if over
            # 60 it will be depleted in GetRemainingNeededCashNoTaxesOrPenalties method)
            DeltaPercentArray[1+ct] = Penalty / WithdrawalDeltaArray[1+ct]
        else:
            DeltaPercentArray[1+ct] = np.nan

    ##################################################################################################################
    # 457b
    ##################################################################################################################

    # Pull Step from PreTax475b - for each person
    StartInd = 2 if NumPeople == 1 else 3
    for ct in range(NumPeople):
        WithdrawalDeltaArray[StartInd+ct] = WithdrawFrom457bDelta(PreTax457b,0,0,Step,YearCt,ct,False)
        if WithdrawalDeltaArray[StartInd+ct] > 0.: # if PreTax457b still has non-zero balance
            # if SSI, recompute taxable SSI for higher income, then update total standard income
            if TotalSS > 0.:
                NonSSstandardIncome = IncTotStd - TaxableSS
                TaxableSSdelta = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains +
                                                       WithdrawalDeltaArray[StartInd+ct], TotalSS, FilingStatus)
                IncTotStdDelta = NonSSstandardIncome + TaxableSSdelta
            else:
                IncTotStdDelta = IncTotStd
            # Determine Delta % in taxes
            NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStdDelta+WithdrawalDeltaArray[StartInd+ct],
                                    IncTotLTcapGains)
            Delta = NewTaxes['Total'] - Taxes[YearCt]
            DeltaPercentArray[StartInd+ct] = Delta / WithdrawalDeltaArray[StartInd+ct]
        else:
            DeltaPercentArray[StartInd+ct] = np.nan

    ##################################################################################################################
    # PreTax
    ##################################################################################################################

    # Pull Step from PreTax - for each person
    StartInd = 3 if NumPeople == 1 else 5
    for ct in range(NumPeople):
        WithdrawalDeltaArray[StartInd+ct], Penalty = WithdrawFromPreTaxDelta(PreTax,0,0,Step,Age,YearCt,ct,False)
        if WithdrawalDeltaArray[StartInd+ct] > 0.: # if PreTax still has non-zero balance
            # if SSI, recompute taxable SSI for higher income, then update total standard income
            if TotalSS > 0.:
                NonSSstandardIncome = IncTotStd - TaxableSS
                TaxableSSdelta = TaxableSSconsolidated(NonSSstandardIncome + IncTotLTcapGains +
                                                       WithdrawalDeltaArray[StartInd+ct], TotalSS, FilingStatus)
                IncTotStdDelta = NonSSstandardIncome + TaxableSSdelta
            else:
                IncTotStdDelta = IncTotStd
            # Determine Delta % in taxes
            NewTaxes = ComputeTaxes(TaxRateInfo,FilingStatus,IncTotStdDelta+WithdrawalDeltaArray[StartInd+ct],
                                    IncTotLTcapGains)
            Delta = NewTaxes['Total'] - Taxes[YearCt]
            DeltaPercentArray[StartInd+ct] = (Delta+Penalty) / WithdrawalDeltaArray[StartInd+ct]
        else:
            DeltaPercentArray[StartInd+ct] = np.nan

    return WithdrawalDeltaArray, DeltaPercentArray
