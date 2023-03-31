# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeMaxAdjustableNonSSstandardIncome.py

import numpy as np
import copy
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy import optimize
from TaxableSSconsolidated import TaxableSSconsolidated

# Compute MaxAdjustableNonSSstandardIncome such that NonadjustableStandardIncome +
# TaxableSS(NonadjustableStandardIncome+NonadjustableLTcapGainsIncome+MaxAdjustableNonSSstandardIncome,TotalSS,
# FilingStatus) + MaxAdjustableNonSSstandardIncome = MaxStandardIncome

# Approach:
# MaxStandardIncome = NonadjustableStandardIncome + TaxableSS(NonadjustableStandardIncome+NonadjustableLTcapGainsIncome+
# MaxAdjustableNonSSstandardIncome,TotalSS,FilingStatus) + MaxAdjustableNonSSstandardIncome
# solve for MaxAdjustableNonSSstandardIncome
# setting equal to 0 to use numerical solver (Newton-Rhapson method):
# 0 = NonadjustableStandardIncome + TaxableSS(NonadjustableStandardIncome+NonadjustableLTcapGainsIncome+
# MaxAdjustableNonSSstandardIncome,TotalSS,FilingStatus) + MaxAdjustableNonSSstandardIncome - MaxStandardIncome

def ZeroFn(MaxAdjustableNonSSstandardIncome,NonadjustableStandardIncome,TotalSS,LTcapGains,MaxStandardIncome,
           FilingStatus):

    TaxableSSincome = TaxableSSconsolidated(NonadjustableStandardIncome+MaxAdjustableNonSSstandardIncome+LTcapGains,
                                            TotalSS,FilingStatus)

    return NonadjustableStandardIncome + MaxAdjustableNonSSstandardIncome + TaxableSSincome - MaxStandardIncome

def ComputeMaxAdjustableNonSSstandardIncome(NonadjustableStandardIncome,LTcapGains,TotalSS,MaxStandardIncome,
                                            FilingStatus):

    # initialize
    MaxAdjustableNonSSstandardIncomeIV = MaxStandardIncome - NonadjustableStandardIncome

    MaxAdjustableNonSSstandardIncome = optimize.newton(ZeroFn, x0=MaxAdjustableNonSSstandardIncomeIV,
                                                       args=(NonadjustableStandardIncome,TotalSS,LTcapGains,
                                                             MaxStandardIncome,FilingStatus))

    return MaxAdjustableNonSSstandardIncome
