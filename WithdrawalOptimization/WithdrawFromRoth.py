# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRoth.py

import numpy as np

def WithdrawFromRoth(Expenses,Age,Roth,TotalCash,RothContributions,Taxes,RothRolloverAmount,
                     RothRolloverAge,RothRolloverPerson,Person):

    # compute cash needed
    CashMinusTaxes = TotalCash - Taxes
    RemainingCashNeeded = Expenses - CashMinusTaxes

    if RemainingCashNeeded > 0.:
        # first determine if Age >= 60
        if Age >= 60.:
            # pull from entire balance without worrying about anything - no penalties or taxes
            # if Roth balance greater than remaining cash needed:
            if Roth > RemainingCashNeeded:
                TotalCash += RemainingCashNeeded
                Roth -= RemainingCashNeeded
            else: # withdraw the entire balance
                TotalCash += Roth
                Roth = 0.
        else: # haven't hit 60 (actually 59.5) yet, so need to avoid growth and rollovers less than 5 years old if possible
            # first try to pull from original contributions
            # if contributions cover entire remaining cash needed:
            if RothContributions > RemainingCashNeeded:
                TotalCash += RemainingCashNeeded
                RothContributions -= RemainingCashNeeded
                Roth -= RemainingCashNeeded
            else:
                # then just withdraw remaining contributions
                TotalCash += RothContributions
                Roth -= RothContributions
                RothContributions = 0.

                # Then recompute cash needed
                CashMinusTaxes = TotalCash - Taxes
                RemainingCashNeeded = Expenses - CashMinusTaxes

                # since original contributions not enough, next pull from rollovers if they were made at least 5
                # years ago
                # loop over all rollovers
                for ct in range(len(RothRolloverAmount)):
                    # if rollover non-zero, at least 5 years old, corresponds to this person, and still need cash:
                    if (RothRolloverAmount[ct] > 0.) and (Age >= RothRolloverAge[ct] + 5) and \
                            (RothRolloverPerson[ct] == Person) and (RemainingCashNeeded > 0.):
                        # if rollover covers entire remaining cash needed:
                        if RothRolloverAmount[ct] > RemainingCashNeeded:
                            TotalCash += RemainingCashNeeded
                            RothRolloverAmount[ct] -= RemainingCashNeeded
                            Roth -= RemainingCashNeeded
                            # Then recompute cash needed
                            CashMinusTaxes = TotalCash - Taxes
                            RemainingCashNeeded = Expenses - CashMinusTaxes
                        else:
                            # then just withdraw remaining rollover amount
                            TotalCash += RothRolloverAmount[ct]
                            Roth -= RothRolloverAmount[ct]
                            RothRolloverAmount[ct] = 0.
                            # Then recompute cash needed
                            CashMinusTaxes = TotalCash - Taxes
                            RemainingCashNeeded = Expenses - CashMinusTaxes

    return Roth, TotalCash, RothContributions, RothRolloverAmount
