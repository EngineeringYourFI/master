# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRothDelta.py

import numpy as np

# Automatically assume 10% penalty applies, because this method is called in
# GetRemainingNeededCashWithTaxesAndOrPenalties - so assume age is under 60, because if over 60 the Roth account will be
# depleted in GetRemainingNeededCashNoTaxesOrPenalties method prior to calling
# GetRemainingNeededCashWithTaxesAndOrPenalties

# Also assume that all original Roth contributions are fully depleted in GetRemainingNeededCashNoTaxesOrPenalties before

# But there can be rollovers from IRA accounts that are not yet 5 years old

def WithdrawFromRothDelta(Roth,Step,TotalCash,YearCt,PersonCt,Execute):

    # Unpack needed dictionary items - for easier access
    RothBal = Roth['Bal'][YearCt,PersonCt]
    if Execute:
        RothRollAmount = Roth['RolloverAmount']
        RothRollPerson = Roth['RolloverPerson']

    if RothBal > Step:
        Withdrawal = Step
        Penalty = 0.1*Step
    else:
        Withdrawal = RothBal
        Penalty = 0.1*RothBal

    if Execute:

        # Withdraw from the full Roth balance
        if RothBal > Step:
            TotalCash[YearCt] += Step
            RothBal -= Step
        else: # withdraw the entire balance
            TotalCash[YearCt] += RothBal
            RothBal = 0.

        # Compute the sum of all Roth rollovers for that person
        RothRollAmountTotal = 0.
        for ct in range(len(RothRollAmount)):
            if RothRollPerson[ct] == PersonCt:
                RothRollAmountTotal += RothRollAmount[ct]

        # If the sum of the roth rollovers is greater the new Roth balance (indicating all growth from original
        # contributions and the rollovers has been depleted)
        if RothBal < RothRollAmountTotal:

            RemainingRothWithdrawal = RothRollAmountTotal - RothBal

            # loop over the rollovers (for that person) from most recent to least recent and lower / deplete each
            # rollover until the sum of the roth rollovers is equal to the new Roth balance.
            # Deplete from most recent (end of list) to least recent (beginning of list) to maximize the odds of the
            # oldest rollovers maturing in subsequent years and getting that money penalty free. No idea how that
            # granularity is tracked by the IRS though.
            for ct in reversed(range(len(RothRollAmount))):
                if RothRollPerson[ct] == PersonCt:
                    if RothRollAmount[ct] > RemainingRothWithdrawal:
                        RothRollAmount[ct] -= RemainingRothWithdrawal
                        RemainingRothWithdrawal = 0. # not needed, but good for reference/understanding
                        break
                    else:
                        RemainingRothWithdrawal -= RothRollAmount[ct]
                        RothRollAmount[ct] = 0.

            # Recompute RothRollAmountTotal and confirm it equals RothBal now
            RothRollAmountTotal = 0.
            for ct in range(len(RothRollAmount)):
                if RothRollPerson[ct] == PersonCt:
                    RothRollAmountTotal += RothRollAmount[ct]
            if np.abs(RothBal - RothRollAmountTotal) >= 0.01:
                print('Roth Balance not equal to Roth Rollover total - something is wrong, investigate.')
                exit()

        # Repack any modified immutable dictionary items (mutable items such as arrays/lists will already be modified)
        Roth['Bal'][YearCt,PersonCt] = RothBal
        # Update Roth['Total']
        Roth['Total'][YearCt] = np.sum(Roth['Bal'][YearCt,:])
        # Roth['RolloverAmount'] is already updated because it's a mutable list and tied to RothRollAmount

    return Withdrawal, Penalty