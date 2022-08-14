# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TaxableSS.py

# import numpy as np
# import copy
# import os
# import matplotlib.pyplot as plt
# from scipy import optimize

# Compute how much of SS income is taxable

def TaxableSS(NonSSstandardIncome,TotalSSincome,LTcapGains,SingleOrMarried):

    # IRS worksheet that computes the amount of income from SS to include as taxable income:
    # https://www.irs.gov/pub/irs-pdf/p915.pdf#page=16.

    # 1. Enter the total amount from box 5 of ALL your Forms SSA-1099 and RRB-1099. = TotalSSincome
    # 2. Multiply line 1 by 50% (0.50)
    HalfTotalSSincome = TotalSSincome*0.5

    # 3. Combine the amounts from: Form 1040 or 1040-SR, lines 1, 2b, 3b, 4b, 5b, 7, and 8
    # i.e. all other income: wages, dividends, cap gains, IRA distributions, etc.
    NonSSincome = NonSSstandardIncome + LTcapGains

    # 4. Enter the amount, if any, from Form 1040 or 1040-SR, line 2a . - uncommon
    # 5. Enter the total of any exclusions/adjustments for: - uncommon
    # 6. Combine lines 2, 3, 4, and 5
    HalfTotalSSincomePlusNonSSincome = HalfTotalSSincome + NonSSincome

    # 7. Enter the total of the amounts from Schedule 1 (Form 1040), lines 11 through 20, and 23 and 25 - uncommon
    # 8. Is the amount on line 7 less than the amount on line 6?
    # No: STOP. None of your social security benefits are taxable.
    # Yes: Subtract line 7 from line 6
    # = HalfTotalSSincomePlusNonSSincome
    # 9. If you are:
    # Married filing jointly, enter $32,000
    # Single, head of household, qualifying widow(er), or married filing separately and you lived apart from your spouse
    # for all of 2021, enter $25,000
    if SingleOrMarried=='Single':
        MinOtherIncomeForSStoBeTaxed = 25000.
    else:
        MinOtherIncomeForSStoBeTaxed = 32000.

    # 10. Is the amount on line 9 less than the amount on line 8?
    # No: STOP. None of your benefits are taxable.
    # Yes. Subtract line 9 from line 8
    # Or another (I believe more intuitive) way to state this:
    # Is the amount on line 9 greater than the amount on line 8?
    # Yes: STOP. None of your benefits are taxable.
    # No: Subtract line 9 from line 8
    # Examples on https://www.irs.gov/pub/irs-pdf/p915.pdf
    if MinOtherIncomeForSStoBeTaxed > HalfTotalSSincomePlusNonSSincome:
        TaxableSSincome = 0.
        return TaxableSSincome
    else:
        IncomeOverMinOtherIncome = HalfTotalSSincomePlusNonSSincome - MinOtherIncomeForSStoBeTaxed

    # 11. Enter $12,000 if married filing jointly; $9,000 if single, head of household, qualifying widow(er), or married
    # filing separately and you lived apart from your spouse for all of 2021
    if SingleOrMarried=='Single':
        DeltaToTopOf50percentTaxableBracket = 9000.
    else:
        DeltaToTopOf50percentTaxableBracket = 12000.

    # 12. Subtract line 11 from line 10. If zero or less, enter -0-
    if IncomeOverMinOtherIncome > DeltaToTopOf50percentTaxableBracket:
        IncomeOver50percentTaxableBracket = IncomeOverMinOtherIncome - DeltaToTopOf50percentTaxableBracket
    else:
        IncomeOver50percentTaxableBracket = 0.

    # 13. Enter the smaller of line 10 or line 11
    if IncomeOverMinOtherIncome > DeltaToTopOf50percentTaxableBracket:
        Line13 = DeltaToTopOf50percentTaxableBracket
    else:
        Line13 = IncomeOverMinOtherIncome

    # 14. Multiply line 13 by 50% (0.50)
    Line14 = Line13*0.5

    # 15. Enter the smaller of line 2 or line 14
    if HalfTotalSSincome > Line14:
        TaxableIncomeIn50percentBracket = Line14
    else:
        TaxableIncomeIn50percentBracket = HalfTotalSSincome

    # 16. Multiply line 12 by 85% (0.85). If line 12 is zero, enter -0
    TaxableIncomeIn85percentBracket = IncomeOver50percentTaxableBracket*0.85

    # 17. Add lines 15 and 16
    TaxableIncomeFrom50percentAnd85percentBrackets = TaxableIncomeIn50percentBracket + TaxableIncomeIn85percentBracket

    # 18. Multiply line 1 by 85% (0.85)
    MaxTaxableSSincome = TotalSSincome*0.85

    # 19. Taxable benefits. Enter the smaller of line 17 or line 18.
    if MaxTaxableSSincome > TaxableIncomeFrom50percentAnd85percentBrackets:
        TaxableSSincome = TaxableIncomeFrom50percentAnd85percentBrackets
    else:
        TaxableSSincome = MaxTaxableSSincome

    return TaxableSSincome
