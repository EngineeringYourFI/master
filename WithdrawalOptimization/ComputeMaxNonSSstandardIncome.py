# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeMaxNonSSstandardIncome.py

import numpy as np
import copy
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy import optimize
from TaxableSSconsolidated import TaxableSSconsolidated

# Approach:
# MaxStandardIncome = MaxNonSSstandardIncome + TaxableSSincome
#                   = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome+LTcapGains,TotalSSincome,FilingStatus)
# solve for MaxNonSSstandardIncome
# setting equal to 0 to use numerical solver (Newton-Rhapson method):
# 0 = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome+LTcapGains,TotalSSincome,FilingStatus) - MaxStandardIncome

def ZeroFn(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,MaxStandardIncome,FilingStatus):

    TaxableSSincome = TaxableSSconsolidated(MaxNonSSstandardIncome+LTcapGains,TotalSSincome,FilingStatus)

    return MaxNonSSstandardIncome + TaxableSSincome - MaxStandardIncome

def ComputeMaxNonSSstandardIncome(TotalSSincome,SpecifiedIncome,MaxStandardIncome,FilingStatus):

    # initialize
    MaxNonSSstandardIncomeIV = MaxStandardIncome
    LTcapGains = SpecifiedIncome - MaxStandardIncome

    MaxNonSSstandardIncome = optimize.newton(ZeroFn, x0=MaxNonSSstandardIncomeIV,
                                             args=(TotalSSincome,LTcapGains,MaxStandardIncome,FilingStatus))

    return MaxNonSSstandardIncome
