# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeMaxNonSSstandardIncome.py

# import numpy as np
# import copy
# import os
# import matplotlib
# import matplotlib.pyplot as plt
from scipy import optimize
from TaxableSSconsolidated import TaxableSSconsolidated

# Approach:
# MaxStandardIncome = MaxNonSSstandardIncome + TaxableSSincome
#                   = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,MarriedOrOther)
# solve for MaxNonSSstandardIncome
# setting equal to 0 to use numerical solver (Newton-Rhapson method):
# 0 = MaxNonSSstandardIncome + f(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,MarriedOrOther) - MaxStandardIncome

def ZeroFn(MaxNonSSstandardIncome,TotalSSincome,LTcapGains,MaxStandardIncome,MarriedOrOther):

    TaxableSSincome = TaxableSSconsolidated(MaxNonSSstandardIncome+LTcapGains,TotalSSincome,MarriedOrOther)

    return MaxNonSSstandardIncome + TaxableSSincome - MaxStandardIncome

def ComputeMaxNonSSstandardIncome(TotalSSincome,SpecifiedIncome,MaxStandardIncome,MarriedOrOther):

    # initialize
    MaxNonSSstandardIncomeIV = MaxStandardIncome
    LTcapGains = SpecifiedIncome - MaxStandardIncome

    MaxNonSSstandardIncome = optimize.newton(ZeroFn, x0=MaxNonSSstandardIncomeIV,
                                             args=(TotalSSincome,LTcapGains,MaxStandardIncome,MarriedOrOther))

    return MaxNonSSstandardIncome
