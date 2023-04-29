# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# AdjustIncomeForInflation.py

# Adjust taxable income (for social security) for inflation

# https://www.fool.com/retirement/social-security/benefits-formula/
# "The government uses the Average Wage Index (AWI) to adjust your wages for inflation so it can accurately pick out the
# years you've earned the most."
# "The AWI you use to adjust your wages is the one that was in effect in the year you turned 60. You divide this AWI by
# the AWI for the year you're adjusting wages for. The result is your index factor. Multiply this by your income as
# reported in your earnings record for that year to get your index-adjusted wages."

# https://www.ssa.gov/oact/cola/AWI.html
# AWI values from 1951

# https://www.ssa.gov/oact/ProgData/retirebenefit1.html
# "A factor will always equal one for the year in which the person attains age 60 and all later years."

import numpy as np

def AdjustIncomeForInflation(Income,Years):

    # Unpack needed dicts
    BirthYear = Years['BirthYear']
    IncomeYears = Income['IncomeYears']
    TaxableIncome = Income['TaxableIncome']

    # Determine year you turned 60
    YearYouTurn60 = BirthYear + 60

    # National average wage indexing series, 1951-2021
    # Table provided at https://www.ssa.gov/oact/cola/AWI.html
    AWIyears = list(range(1951, 2022))
    AWIarray = [2799.16, 2973.32, 3139.44, 3155.64, 3301.44, 3532.36, 3641.72, 3673.8, 3855.8, 4007.12, 4086.76, 4291.4,
                4396.64, 4576.32, 4658.72, 4938.36, 5213.44, 5571.76, 5893.76, 6186.24, 6497.08, 7133.8, 7580.16,
                8030.76, 8630.92, 9226.48, 9779.44, 10556.03, 11479.46, 12513.46, 13773.1, 14531.34, 15239.24, 16135.07,
                16822.51, 17321.82, 18426.51, 19334.04, 20099.55, 21027.98, 21811.6, 22935.42, 23132.67, 23753.53,
                24705.66, 25913.9, 27426, 28861.44, 30469.84, 32154.82, 32921.92, 33252.09, 34064.95, 35648.55,
                36952.94, 38651.41, 40405.48, 41334.97, 40711.61, 41673.83, 42979.61, 44321.67, 44888.16, 46481.52,
                48098.63, 48642.15, 50321.89, 52145.8, 54099.99, 55628.6, 60575.07]

    # Determine AWI base: AWI for the year you turn 60
    # (or latest AWI if turning 60 after final value in YearsArray, assuming all future estimates in current day dollars)
    if YearYouTurn60 <= AWIyears[-1]:
        AWIbaseInd = AWIyears.index(YearYouTurn60)
    else:
        AWIbaseInd = len(AWIyears)-1
    AWIbase = AWIarray[AWIbaseInd]

    # Initialize
    AdjustedTaxableIncome = np.zeros(len(TaxableIncome))

    # Loop over each year of earnings, and adjust using AWI from that year and the AWI base
    for ct in range(len(TaxableIncome)):
        Year = IncomeYears[ct]
        if Year in AWIyears:
            # if year is prior to AWI year:
            if Year < YearYouTurn60:
                ind = AWIyears.index(Year)
            else:
                # the inflation factor "will always equal one for the year in which the person attains age 60 and all
                # later years"
                ind = AWIbaseInd
            AWIthisYear = AWIarray[ind]
            # https://www.ssa.gov/cgi-bin/awiFactors.cgi provides 7 digits after the decimal, so use that
            IndexFactor = np.round(AWIbase / AWIthisYear,7)
        else: # that year's earnings are beyond the table of AWI values, so just specify the Index Factor as 1
            IndexFactor = 1.

        # https://sgp.fas.org/crs/misc/IF11747.pdf:
        # "Wage-indexed earnings are rounded to the nearest cent."
        AdjustedTaxableIncome[ct] = np.round(IndexFactor * TaxableIncome[ct],2)

    return AdjustedTaxableIncome

