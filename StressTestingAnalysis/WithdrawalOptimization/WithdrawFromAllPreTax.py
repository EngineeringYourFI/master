# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromAllPreTax.py

import numpy as np
from WithdrawalOptimization.WithdrawFrom457b import WithdrawFrom457b
from WithdrawalOptimization.WithdrawFromPreTax import WithdrawFromPreTax

# Withdraw from PreTax accounts (PreTax and PreTax457b)

def WithdrawFromAllPreTax(PreTax,PreTax457b,Income,TotalCash,Roth, Age,YearCt):

    if PreTax457b['TPMwithdraw457bFirst']:
        # withdraw 457b if room
        # loop over all 457b accounts (one or two)
        for ct in range(np.shape(PreTax457b['Bal'])[1]):
            WithdrawFrom457b(Income,PreTax457b,TotalCash, YearCt,ct)
        PreTax457b['Total'][YearCt] = np.sum(PreTax457b['Bal'][YearCt,:])

    # withdraw PreTax if room, rollover to Roth if not 60 yet
    # loop over all PreTax accounts (one or two in general)
    for ct in range(np.shape(PreTax['Bal'])[1]):
        WithdrawFromPreTax(Income,PreTax,TotalCash,Roth, Age,YearCt,ct)
    PreTax['Total'][YearCt] = np.sum(PreTax['Bal'][YearCt,:])
    Roth['Total'][YearCt] = np.sum(Roth['Bal'][YearCt,:])

    if PreTax457b['TPMwithdraw457bFirst'] == False:
        # withdraw 457b if room
        # loop over all 457b accounts (one or two in general)
        for ct in range(np.shape(PreTax457b['Bal'])[1]):
            WithdrawFrom457b(Income,PreTax457b,TotalCash, YearCt,ct)
        PreTax457b['Total'][YearCt] = np.sum(PreTax457b['Bal'][YearCt,:])
