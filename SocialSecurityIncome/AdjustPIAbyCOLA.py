# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# AdjustPIAbyCOLA.py

# Adjust PIA with any relevant Cost of Living Adjustments (COLA)

# https://www.fool.com/retirement/social-security/benefits-formula/
# "Every year the government administers a cost-of-living adjustment (COLA) to help seniors' Social Security checks
# keep up with inflation. But it doesn't add the COLA to your take-home check. It ***adds it to your PIA***. If you
# want to calculate the size of your checks for next year, ***look at your PIA for the current year and add the
# COLA***. For example, the 2023 COLA is 8.7%, so you'd take your 2022 PIA and multiply it by 1.087 to get your
# 2023 PIA. ***Then you proceed with Steps 5 to 7 above to determine your new take-home benefit for the next year***."
# SO, apply the COLA to PIA (before adjusting RIB if not taking at FRA)

# https://www.ssa.gov/oact/ProgData/retirebenefit2.html
# "The worker in case B is first eligible in 2019 (the year case B reached age 62). Thus the case-B PIA is the case B
# amount computed above truncated to the next lower dime and increased by cost-of-living adjustments, or COLAs, for 2019
# through 2022. These COLAs are 1.6 percent, 1.3 percent, 5.9 percent, 8.7 percent, respectively. The resulting PIA is
# $3,627.10."

import numpy as np

def AdjustPIAbyCOLA(PIA,BirthYear):

    # Determine year you turn 62
    YearYouTurn62 = BirthYear + 62

    # Determine COLA from the year you turned 62 to the current year

    # Table of all COLA from 1975 to 2022
    # https://www.ssa.gov/oact/COLA/colaseries.html
    COLAyears = list(range(1975, 2023))
    COLAarray = np.array([8, 6.4, 5.9, 6.5, 9.9, 14.3, 11.2, 7.4, 3.5, 3.5, 3.1, 1.3, 4.2, 4, 4.7, 5.4, 3.7, 3, 2.6,
                          2.8, 2.6, 2.9, 2.1, 1.3, 2.5, 3.5, 2.6, 1.4, 2.1, 2.7, 4.1, 3.3, 2.3, 5.8, 0, 0, 3.6, 1.7,
                          1.5, 1.7, 0, 0.3, 2, 2.8, 1.6, 1.3, 5.9, 8.7])/100.

    # Determine index for year you turned 62
    if YearYouTurn62 <= COLAyears[-1]:
        # Then the year you turned 62 is in the published COLA table, so use that
        YearYouTurn62ind = COLAyears.index(YearYouTurn62)
        ApplyCOLA = True
    else:
        # Then you turned 62 after the end of the published COLA table (which includes values through the actual
        # previous year) - so don't do any COLA
        ApplyCOLA = False

    # If you turned 62 before the current year, loop from the year you turn 62 to the current year (assumed the year
    # after the final year listed in COLAyears), applying COLA for each year
    if ApplyCOLA:
        for ct in range(YearYouTurn62ind,len(COLAyears)):
            PIA = PIA * (1.+COLAarray[ct])
            # truncate down to the next lower dime
            PIA = np.floor(PIA*10.)/10.

    return PIA
