# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# DetermineIfMinCreditsObtained.py

# Determine if the minimum 40 credits have been achieved, and thus eligible for SocSec

# https://www.ssa.gov/benefits/retirement/planner/credits.html#h2
# "You need 40 credits to qualify for retirement."
# "you can earn up to a maximum of 4 credits per year"

# https://www.ssa.gov/oact/cola/QC.html
# "No matter how high your earnings may be, you can not earn more than 4 QC's in one year."
# "For years before 1978, an individual generally was credited with a quarter of coverage for each quarter in which
# wages of $50 or more were paid, or an individual was credited with 4 quarters of coverage for every taxable year in
# which $400 or more of self-employment income was earned. Beginning in 1978, employers generally report wages on an
# annual, instead of quarterly, basis. With this change to annual reporting, the law provided that a quarter of coverage
# be credited for each $250 of an individual's total wages and self-employment income for calendar year 1978 (up to a
# maximum of 4 quarters of coverage for the year). After 1978, the amount of earnings needed for a quarter of coverage
# changes automatically each year with changes in the national average wage index."
# "The law specifies that the quarter of coverage (QC) amount for 2023 is equal to the 1978 amount of $250 multiplied by
# the ratio of the national average wage index for 2021 to that for 1976, or, if larger, the 2022 amount of $1,510. If
# the amount so determined is not a multiple of $10, it shall be rounded to the nearest multiple of $10."
# But they also provide a table, so easy enough to just use that (can do this computation in the future if desired, but
# it'll still depend on the published average wage index, so can't fully automate for the future)

def DetermineIfMinCreditsObtained(Income):

    # Unpack needed dicts
    IncomeYears = Income['IncomeYears']
    IncomeArray = Income['IncomeArray']

    # Amounts needed to earn one quarter of coverage (one credit) for each year from 1978 to 2023:
    # Table provided at https://www.ssa.gov/oact/cola/QC.html
    YearsArray = list(range(1978, 2024))
    CreditCost = [250, 260, 290, 310, 340, 370, 390, 410, 440, 460, 470, 500, 520, 540, 570, 590, 620, 630, 640, 670,
                  700, 740, 780, 830, 870, 890, 900, 920, 970, 1000, 1050, 1090, 1120, 1120, 1130, 1160, 1200, 1220,
                  1260, 1300, 1320, 1360, 1410, 1470, 1510, 1640]

    # Initialize
    TotalCredits = 0

    # Loop over income years
    for ct in range(len(IncomeYears)):

        # Determine credit cost for this year
        Year = IncomeYears[ct]
        # If year is within YearsArray, grab corresponding index:
        if Year <= YearsArray[-1]:
            ind = YearsArray.index(Year)
        else: # use the credit cost for the final year listed
            ind = len(YearsArray) - 1
        CreditCostThisYear = CreditCost[ind]

        NumCreditsThisYear = int(IncomeArray[ct] / CreditCostThisYear)
        if NumCreditsThisYear > 4: # maximum number of credits each year is 4
            NumCreditsThisYear = 4

        TotalCredits += NumCreditsThisYear

    if TotalCredits >= 40:
        MinCreditsObtained = True
    else: MinCreditsObtained = False

    return MinCreditsObtained, TotalCredits
