# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# SingleNonZeroAcctBalStep.py

import numpy as np

# If down to a single non-zero balance account, set step accordingly

def SingleNonZeroAcctBalStep(WithdrawalDeltaArray,PostTax,Roth,PreTax457b,PreTax,YearCt,RemainingCashNeeded,NumPeople):

    # Determine which account remains non-zero
    SoleRemainingAcctInd = np.nonzero(WithdrawalDeltaArray)[0][0]

    # if SoleRemainingAcctInd = 0, then it's PostTax
    if SoleRemainingAcctInd == 0:
        RemainingBal = np.sum(PostTax['Bal'][YearCt,:])
    # if one person:
    elif NumPeople == 1:
        if SoleRemainingAcctInd == 1:
            RemainingBal = Roth['Bal'][YearCt,0]
        if SoleRemainingAcctInd == 2:
            RemainingBal = PreTax457b['Bal'][YearCt,0]
        if SoleRemainingAcctInd == 3:
            RemainingBal = PreTax['Bal'][YearCt,0]
    else: # two people
        if SoleRemainingAcctInd == 1:
            RemainingBal = Roth['Bal'][YearCt,0]
        if SoleRemainingAcctInd == 2:
            RemainingBal = Roth['Bal'][YearCt,1]
        if SoleRemainingAcctInd == 3:
            RemainingBal = PreTax457b['Bal'][YearCt,0]
        if SoleRemainingAcctInd == 4:
            RemainingBal = PreTax457b['Bal'][YearCt,1]
        if SoleRemainingAcctInd == 5:
            RemainingBal = PreTax['Bal'][YearCt,0]
        if SoleRemainingAcctInd == 6:
            RemainingBal = PreTax['Bal'][YearCt,1]

    # Set step equal to smaller of RemainingCashNeeded or total remaining balance
    if RemainingCashNeeded > RemainingBal:
        Step = RemainingBal
    else:
        Step = RemainingCashNeeded

    return Step
