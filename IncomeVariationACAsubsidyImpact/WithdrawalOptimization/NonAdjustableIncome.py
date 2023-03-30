# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# NonAdjustableIncome.py

import numpy as np
from WithdrawalOptimization.ComputeRMD import *
import copy

# All "non-adjustable" income sources (i.e., we cannot modify the amounts, in the framework of this simulation),
# including dividends, "other income", RMDs, and social security

def NonAdjustableIncome(TotalCash,Income,PreTax,PreTax457b,RMD, PostTax,IncDict,Age,YearCt):

    # Unpack needed dictionary items - for easier access
    QualDivYield = IncDict['QualifiedDividendYield']
    NonQualDivYield = IncDict['NonQualifiedDividendYield']
    IncTotStd = Income['TotalStandard'][YearCt]
    IncTotLTcapGains = Income['TotalLTcapGains'][YearCt]
    IncTot = Income['Total'][YearCt]
    IncMaxStd = Income['MaxStandard'][YearCt]
    IncMaxTot = Income['MaxTotal'][YearCt]
    OtherIncomeSources = IncDict['OtherIncomeSources']
    AgeOtherIncomeSourcesWillStart = IncDict['AgeOtherIncomeSourcesWillStart']
    PreTaxBal = PreTax['Bal'][YearCt,:]
    PreTax457bBal = PreTax457b['Bal'][YearCt,:]
    RMDbal = RMD['Bal'][YearCt,:]
    RMDtot = RMD['Total'][YearCt]
    SocialSecurityPayments = IncDict['SocialSecurityPayments']
    AgeSSwillStart = IncDict['AgeSSwillStart']
    TotalSS = Income['TotalSS'][YearCt]

    # Dividends
    QualDiv = QualDivYield * np.sum(PostTax['Bal'][YearCt,:])
    NonQualDiv = NonQualDivYield * np.sum(PostTax['Bal'][YearCt,:])
    TotalCash[YearCt] += QualDiv + NonQualDiv
    IncTotStd += NonQualDiv
    IncTotLTcapGains += QualDiv
    IncTot += QualDiv + NonQualDiv

    # Other income
    for ct in range(len(OtherIncomeSources)):
        if Age[YearCt,0] >= AgeOtherIncomeSourcesWillStart[ct]:
            TotalCash[YearCt] += OtherIncomeSources[ct]
            # assuming all "other income sources" are taxed as standard income (vs LT cap gains, social security, etc.)
            IncTotStd += OtherIncomeSources[ct]
            IncTot += OtherIncomeSources[ct]

    # If after "other income" the Total Standard Income or Total Income exceeds the user set Max Standard Income or
    # Max Total Income, reset Max Standard Income and/or Max Total Income
    if IncTotStd > IncMaxStd:
        IncMaxStd = copy.deepcopy(IncTotStd)
    if IncTot > IncMaxTot:
        IncMaxTot = copy.deepcopy(IncTot)

    # Required Minimum Distributions (RMDs)
    for ct in range(len(PreTaxBal)):
        if Age[YearCt,ct] >= RMD['RMDstartAge'][ct]:
            # PreTax
            RMDpretax, WR = ComputeRMD(PreTaxBal[ct],Age[YearCt,ct])
            # 457b
            RMD457b, WR = ComputeRMD(PreTax457bBal[ct],Age[YearCt,ct])
            # Sum of all pretax accounts
            RMDbal[ct] = RMDpretax + RMD457b
            # add to cash and income totals
            TotalCash[YearCt] += RMDbal[ct]
            IncTotStd += RMDbal[ct]
            IncTot += RMDbal[ct]
            # remove from pretax accounts
            PreTaxBal[ct] -= RMDpretax
            PreTax457bBal[ct] -= RMD457b
    RMDtot = np.sum(RMDbal)

    # Social security
    for ct in range(len(SocialSecurityPayments)):
        if Age[YearCt,ct] >= AgeSSwillStart[ct]:
            TotalSS += SocialSecurityPayments[ct]
    TotalCash[YearCt] += TotalSS

    # Repack any modified immutable dictionary items (mutable items such as arrays will already be modified)
    Income['TotalStandard'][YearCt] = IncTotStd
    Income['TotalLTcapGains'][YearCt] = IncTotLTcapGains
    Income['Total'][YearCt] = IncTot
    Income['MaxStandard'][YearCt] = IncMaxStd
    Income['MaxTotal'][YearCt] = IncMaxTot
    RMD['Total'][YearCt] = RMDtot
    Income['TotalSS'][YearCt] = TotalSS
