# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# ComputePIA.py

# Compute Primary Insurance Amount (PIA)

import numpy as np

def ComputePIA(Income,BirthYear):

    # Unpack needed dicts
    AIME = Income['AIME']

    # PIA rates
    Rates = [0.9,0.32,0.15]

    # Determine year you turn 62
    YearYouTurn62 = BirthYear + 62

    # Determine bend points for the year you turned 62 (even if not starting RIB at age 62)
    # Bend points = Dollar amounts in PIA formula
    # Table provided at https://www.ssa.gov/oact/COLA/bendpoints.html
    # These bend points are determined using Bend Points for 1979 (180 and 1085), mapped forward in time using AWI:
    # https://www.ssa.gov/oact/COLA/piaformula.html

    BendPointYears = list(range(1979, 2024))
    BendPoint1array = [180, 194, 211, 230, 254, 267, 280, 297, 310, 319, 339, 356, 370, 387, 401, 422, 426, 437, 455,
                       477, 505, 531, 561, 592, 606, 612, 627, 656, 680, 711, 744, 761, 749, 767, 791, 816, 826, 856,
                       885, 895, 926, 960, 996, 1024, 1115]
    BendPoint2array = [1085, 1171, 1274, 1388, 1528, 1612, 1691, 1790, 1866, 1922, 2044, 2145, 2230, 2333, 2420, 2545,
                       2567, 2635, 2741, 2875, 3043, 3202, 3381, 3567, 3653, 3689, 3779, 3955, 4100, 4288, 4483, 4586,
                       4517, 4624, 4768, 4917, 4980, 5157, 5336, 5397, 5583, 5785, 6002, 6172, 6721]

    # Determine appropriate bend points: values for the year you turn 62
    # (or latest bend points if turning 62 after final value in BendPointYears array, assuming all future estimates in
    # current day dollars)
    if YearYouTurn62 <= BendPointYears[-1]:
        BendPointInd = BendPointYears.index(YearYouTurn62)
    else:
        BendPointInd = len(BendPointYears)-1
    BendPoint1 = BendPoint1array[BendPointInd]
    BendPoint2 = BendPoint2array[BendPointInd]
    BendPointList = [BendPoint1,BendPoint2]

    # Compute PIA using bend points - using same methodology as computing taxes in progressive tax brackets

    # Compute top bracket index for AIME
    # np.searchsorted returns the index of the Min value beyond AIME (and +1 beyond the last index if
    # greater than the last value) i.e. the index of the max value of the top bracket
    AIMEtopPIAbracketInd = np.searchsorted(BendPointList,AIME)
    # PIA = 0. # init
    if AIMEtopPIAbracketInd == 0: # before the first bend point
        PIA = Rates[0] * AIME
    elif AIMEtopPIAbracketInd == 1: # between the first bend point and second bend point
        PIA = Rates[0] * BendPointList[0] + Rates[1]*(AIME - BendPointList[0])
    elif AIMEtopPIAbracketInd == 2: # after the second bend point
        PIA = Rates[0] * BendPointList[0] + Rates[1] * (BendPointList[1] - BendPointList[0]) + \
              Rates[2]*(AIME - BendPointList[1])

    # truncate to the next lower dime
    # for some ridiculous reason np.floor doesn't allow you to specify decimals like round does
    PIA = np.floor(PIA*10.)/10.

    return PIA
