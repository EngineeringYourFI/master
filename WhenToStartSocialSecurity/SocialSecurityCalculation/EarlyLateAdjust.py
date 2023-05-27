# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# EarlyLateAdjust.py

# Early / late retirement adjustment (if taking RIB before or after FRA)

# https://www.ssa.gov/oact/quickcalc/early_late.html
# "In the case of early retirement, a benefit is reduced 5/9 of one percent for each month before normal retirement age,
# up to 36 months. If the number of months exceeds 36, then the benefit is further reduced 5/12 of one percent per
# month."
# "Delayed retirement credits increase a retiree's benefits. The table below shows the delayed retirement credit by year
# of birth."
# 1943 and later: Credit per year = 8% (so 8/12% per month)
# https://www.ssa.gov/oact/ProgData/ar_drc.html - confirms the % increase after FRA

# https://www.fool.com/retirement/social-security/benefits-formula/
# "If you claim Social Security early, the government reduces your checks by:
# 5/9 of 1% per month up to 36 months
# 5/12 of 1% for each additional month if you claim more than 36 months early"
# "You add 2/3 of 1% per month for every month you delay past your FRA. However, this only continues until you turn 70."

# If you begin claiming at 62, you'll get only 70% of your standard benefit if your FRA is 67 or 75% if your FRA is
# 66. Every month you delay benefits increases your checks slightly until you reach the maximum benefit at 70. This
# is 124% of your standard benefit if your FRA is 67 or 132% if your FRA is 66.

import numpy as np

def EarlyLateAdjust(FRA,PIA,StartingAge):

    # if StartingAge = FRA (full retirement age), then RIB = PIA
    if abs(StartingAge - FRA) < 0.01:
        RIB = PIA
    else: # must adjust for early/late retirement
        # for early retirement, if FRA > StartingAge
        if FRA - StartingAge > 0.01:
            HowManyMonthsEarly = np.round((FRA - StartingAge)*12.)
            if HowManyMonthsEarly <= 36.:
                RIB = PIA * (1 - (5/9)*0.01*HowManyMonthsEarly)
            else:
                RIB = PIA * (1 - 0.2 - (5/12)*0.01*(HowManyMonthsEarly-36.))

        # for late retirement, if StartingAge > FRA:
        if StartingAge - FRA > 0.01:
            HowManyMonthsLate = np.round((StartingAge - FRA)*12.)
            RIB = PIA * (1 + (2/3)*0.01*HowManyMonthsLate)

    return RIB