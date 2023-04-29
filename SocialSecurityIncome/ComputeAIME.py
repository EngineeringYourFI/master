# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

import numpy as np

# ComputeAIME.py

# Compute Average Indexed Monthly Earnings (AIME) - using highest 35 years of indexed (inflation-adjusted) earnings

def ComputeAIME(Income):

    # Unpack needed dicts
    AdjustedTaxableIncome = Income['AdjustedTaxableIncome']

    # If more than 35 years of earnings:
    if len(AdjustedTaxableIncome) > 35:
        ThirtyFiveHighestYearEarnings = np.array(sorted(AdjustedTaxableIncome,reverse=True)[:35])
    else:
        ThirtyFiveHighestYearEarnings = np.zeros(35)
        ThirtyFiveHighestYearEarnings[0:len(AdjustedTaxableIncome)] = AdjustedTaxableIncome

    AIME = np.sum(ThirtyFiveHighestYearEarnings)/420. # 420 = num of months in 35 years

    # Round down to next lower dollar amount
    # https://www.investopedia.com/terms/a/aime.asp:
    # "The amount is then rounded down to the next lower dollar amount."
    # https://www.ssa.gov/oact/cola/Benefits.html:
    # "We then round the resulting average amount down to the next lower dollar amount."
    # Confirmed they do this rounding down in the examples at
    # https://www.ssa.gov/oact/ProgData/retirebenefit1.html and https://www.ssa.gov/oact/ProgData/retirebenefit2.html

    AIME = np.trunc(AIME)

    return AIME