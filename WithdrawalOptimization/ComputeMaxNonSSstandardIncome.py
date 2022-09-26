# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/??????????????????/)

# ComputeMaxNonSSstandardIncome.py

import numpy as np
import copy
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy import optimize
from TaxableSS import TaxableSS

# Approach:
# MaxStandardIncome = MaxNonSSstandardIncome + TaxableSSincome
#                   = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,SingleOrMarried)
# solve for MaxNonSSstandardIncome
# setting equal to 0 to use numerical solver (Newton-Rhapson method):
# 0 = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,SingleOrMarried) - MaxStandardIncome

def ZeroFn(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,MaxStandardIncome,SingleOrMarried):

    debug = 1

    TaxableSSincome = TaxableSS(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,SingleOrMarried)

    return MaxNonSSstandardIncome + TaxableSSincome - MaxStandardIncome

def ComputeMaxNonSSstandardIncome(TotalSSincome,SpecifiedIncome,MaxStandardIncome,SingleOrMarried):

    # initialize
    MaxNonSSstandardIncomeIV = MaxStandardIncome
    LTcapGains = SpecifiedIncome - MaxStandardIncome

    MaxNonSSstandardIncome = optimize.newton(ZeroFn, x0=MaxNonSSstandardIncomeIV,
                                             args=(TotalSSincome,LTcapGains,MaxStandardIncome,SingleOrMarried))
    debug = 1

    return MaxNonSSstandardIncome
