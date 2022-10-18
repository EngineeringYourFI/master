# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/the-irs-wont-wait-forever-required-minimum-distributions/)

# ProjWithRMDs.py

from ComputeRMD import ComputeRMD
from ComputeTaxes import ComputeTaxes
from TaxableSSconsolidated import TaxableSSconsolidated

import numpy as np

def ProjWithRMDs(NumYearsToProject,IVdict,SocialSecurityPayments,TaxRateInfo,FilingStatus,Exp,R):

    # Project balances from age 72, accounting for RMDs

    # Initialize asset values
    PreTax = np.zeros(NumYearsToProject)
    PostTax = np.zeros(NumYearsToProject)
    TotalAssets = np.zeros(NumYearsToProject)
    PreTax[0] = IVdict['PreTaxIV']
    PostTax[0] = IVdict['PostTaxIV']
    TotalAssets[0] = PreTax[0] + PostTax[0]

    # Initialize Yearly values
    Age = np.zeros(NumYearsToProject)
    Age[0] = 72
    RMD = np.zeros(NumYearsToProject)
    WR = np.zeros(NumYearsToProject)
    TotalStandardIncome = np.zeros(NumYearsToProject)
    TotalCash = np.zeros(NumYearsToProject)
    TotalSS = np.zeros(NumYearsToProject)
    TaxableSSincome = np.zeros(NumYearsToProject)
    Taxes = np.zeros(NumYearsToProject)

    # loop over years
    for ct in range(0,NumYearsToProject):

        # apply investment growth to accounts if not at first year
        if ct > 0:
            Age[ct] = Age[ct-1] + 1
            PreTax[ct] = np.round(PreTax[ct-1]*(1+R),2)
            PostTax[ct] = np.round(PostTax[ct-1]*(1+R),2)

        # Compute RMD, withdrawal rate (for plotting / awareness)
        RMD[ct], WR[ct] = ComputeRMD(PreTax[ct],Age[ct])
        TotalStandardIncome[ct] = RMD[ct]
        TotalCash[ct] += RMD[ct]
        # Remove from pretax
        PreTax[ct] -= RMD[ct]

        # Social security
        TotalSS[ct] = np.sum(SocialSecurityPayments)
        TotalCash[ct] += TotalSS[ct]
        # Compute Taxable SSI
        TaxableSSincome[ct] = TaxableSSconsolidated(TotalStandardIncome[ct],TotalSS[ct],FilingStatus)
        # Add to TotalStandardIncome
        TotalStandardIncome[ct] += TaxableSSincome[ct]

        # Compute Taxes - assume $0 LT cap gains, because assuming SSI + RMD covering expenses, and/or other sources can
        # cover remaining expenses such as a Roth or cash account if cap gains push past 0% LT cap gain bracket
        Taxes[ct] = ComputeTaxes(TaxRateInfo,FilingStatus,TotalStandardIncome[ct],0.)

        # Subtract taxes from cash
        CashMinusTaxes = TotalCash[ct] - Taxes[ct]

        # Subtract expenses from CashMinusTaxes
        CashMinusTaxesMinusExpenses = CashMinusTaxes - Exp

        # add remaining cash to PostTax
        # or, if RMDs + SSI did not cover expenses, CashMinusTaxesMinusExpenses will be negative and thus PostTax[ct] will
        # shrink from pulling that amount from PostTax account (and assume any resulting LT cap gains taxed at 0%)
        PostTax[ct] += CashMinusTaxesMinusExpenses

        TotalAssets[ct] = PreTax[ct] + PostTax[ct]

    # assemble output dictionary
    ProjArrays = {'PreTax': PreTax,
                  'PostTax': PostTax,
                  'TotalAssets': TotalAssets,
                  'Age': Age,
                  'RMD': RMD,
                  'WR': WR,
                  'TotalStandardIncome': TotalStandardIncome,
                  'TotalCash': TotalCash,
                  'TotalSS': TotalSS,
                  'TaxableSSincome': TaxableSSincome,
                  'Expenses': Exp,
                  'Taxes': Taxes}

    return ProjArrays
