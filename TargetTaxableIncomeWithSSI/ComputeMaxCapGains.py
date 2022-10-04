# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeMaxCapGains.py

import numpy as np
# import copy
# import os
# import matplotlib.pyplot as plt
from scipy import optimize
from TaxableSSconsolidated import TaxableSSconsolidated

# Approach:
# MaxStandardIncome = TaxableSSincome  (NonSSstandardIncome = 0, due to size of TaxableSSincome)
#                   = f(LTcapGains,TotalSSincome,MarriedOrOther)
# solve for LTcapGains
# setting equal to 0 to use numerical solver (Newton-Rhapson method):
# 0 = f(LTcapGains,TotalSSincome,MarriedOrOther) - MaxStandardIncome

def ZeroFn(LTcapGains,TotalSS,MaxStandardIncome,MarriedOrOther):

    TaxableSSincome = TaxableSSconsolidated(0.+LTcapGains,TotalSS,MarriedOrOther)

    return TaxableSSincome - MaxStandardIncome

def ComputeMaxCapGains(TotalSS,MaxStandardIncome,MarriedOrOther):

    # initialize
    # loop through cap gains values from $0 to $100K, determine what gives TaxableSSincome the closest to the
    # MaxStandardIncome, then use that as a first guess.
    CapGainOptions = np.arange(0.,100000.,1000.)
    Delta = np.zeros(len(CapGainOptions))
    for ct in range(len(CapGainOptions)):

        TaxableSSincome = TaxableSSconsolidated(0.+CapGainOptions[ct],TotalSS,MarriedOrOther)
        # if the taxable SSI reaches the maximum value of 0.85*TotalSS, then it will no longer change at all for higher
        # capital gain values, which means a completely flat line from that point on - which is very bad for the
        # optimizer. So by setting to nan, the np.argmin will select the lowest delta that doesn't correspond to that
        # completely flat portion of the curve, and allow the optimizer to find the zero point
        if TaxableSSincome == 0.85*TotalSS:
            Delta[ct] = np.nan
        else:
            Delta[ct] = np.abs(MaxStandardIncome - TaxableSSincome)

    CapGainIV = CapGainOptions[np.nanargmin(Delta)]

    MaxCapGains = optimize.newton(ZeroFn, x0=CapGainIV, args=(TotalSS,MaxStandardIncome,MarriedOrOther))

    return MaxCapGains