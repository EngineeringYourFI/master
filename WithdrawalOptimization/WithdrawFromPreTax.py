# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromPreTax.py

import numpy as np

def WithdrawFromPreTax(MaxStandardIncome,TotalStandardIncome,PreTax,TotalCash,TotalIncome,Age,Roth,RothRolloverAmount,
                       RothRolloverAge,RothRolloverPerson,Person):

    # withdraw PreTax if room, rollover to Roth if not 60 yet
    RemainingStandardIncomeRoom = MaxStandardIncome - TotalStandardIncome
    if RemainingStandardIncomeRoom > 0. and PreTax > 0.:
        # if enough funds in PreTax to cover the entire remainder
        if PreTax > RemainingStandardIncomeRoom:
            PreTax -= RemainingStandardIncomeRoom

            if Age < 60.: # Rollover to roth
                Roth += RemainingStandardIncomeRoom
                # capture rollover amount with age, to ensure not spent in less than 5 years
                RothRolloverAmount = np.append(RothRolloverAmount,RemainingStandardIncomeRoom)
                RothRolloverAge = np.append(RothRolloverAge,Age)
                RothRolloverPerson = np.append(RothRolloverPerson,Person)
            else: # use the cash - no penalties
                TotalCash += RemainingStandardIncomeRoom

            TotalStandardIncome += RemainingStandardIncomeRoom
            TotalIncome += RemainingStandardIncomeRoom
        else: # withdraw remaining balance
            if Age < 60.: # Rollover to roth
                Roth += PreTax
                # capture rollover amount with age, to ensure not spent in less than 5 years
                RothRolloverAmount = np.append(RothRolloverAmount,PreTax)
                RothRolloverAge = np.append(RothRolloverAge,Age)
                RothRolloverPerson = np.append(RothRolloverPerson,Person)
            else: # use the cash - no penalties
                TotalCash += PreTax

            TotalStandardIncome += PreTax
            TotalIncome += PreTax
            PreTax = 0.

    return PreTax,TotalCash,TotalStandardIncome,TotalIncome,Roth,RothRolloverAmount,RothRolloverAge,RothRolloverPerson
