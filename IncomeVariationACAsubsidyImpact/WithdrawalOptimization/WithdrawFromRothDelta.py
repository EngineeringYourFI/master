# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# WithdrawFromRothDelta.py

import numpy as np

# Automatically assume 10% penalty applies, because this method is called in
# GetRemainingNeededCashWithTaxesAndOrPenalties - so assume age is under 60, because if over 60 the Roth account will be
# depleted in GetRemainingNeededCashNoTaxesOrPenalties method prior to calling
# GetRemainingNeededCashWithTaxesAndOrPenalties

# All original Roth contributions are fully depleted in GetRemainingNeededCashNoTaxesOrPenalties previously
# All Conversions 5 years or older will are fully depleted in GetRemainingNeededCashNoTaxesOrPenalties previously
# If withdrawing just from Conversions less than 5 years old, only 10% penalty applies
# If withdrawing from earnings, 10% penalties applies and the earnings count as standard income which can be taxed

def WithdrawFromRothDelta(Roth,Step,TotalCash,YearCt,PersonCt,Execute):

    # Unpack needed dictionary items - for easier access
    RothBal = Roth['Bal'][YearCt,PersonCt]
    RothConversionAmount = Roth['ConversionAmount']
    RothConversionPerson = Roth['ConversionPerson']

    RemainingStepNeeded = Step
    Penalty = 0.
    Withdrawal = 0.
    StdIncDeltaFromEarnings = 0.

    # First attempt to withdraw from any Conversions for this person
    # loop over all Conversions
    for ct in range(len(RothConversionAmount)):
        # if Conversion non-zero and corresponds to this person:
        if (RothConversionAmount[ct] > 0.) and (RothConversionPerson[ct] == PersonCt):
            # and to avoid a scenerio where Conversion is greater than balance (e.g. if ROI is negative), use
            # the min of Conversion vs bal
            MinVal = min(RothConversionAmount[ct],RothBal)
            # if MinVal covers entire remaining step needed:
            if MinVal > RemainingStepNeeded:
                if Execute:
                    TotalCash[YearCt] += RemainingStepNeeded
                    RothConversionAmount[ct] -= RemainingStepNeeded
                Withdrawal += RemainingStepNeeded
                RothBal -= RemainingStepNeeded
                Penalty += 0.1*RemainingStepNeeded
                RemainingStepNeeded = 0.
                break
            else:
                # then just withdraw MinVal
                if Execute:
                    TotalCash[YearCt] += MinVal
                    RothConversionAmount[ct] -= MinVal
                Withdrawal += MinVal
                RothBal -= MinVal
                Penalty += 0.1*MinVal
                RemainingStepNeeded -= MinVal

    # If still need withdrawal after attempting to pull from Conversions (just a 10% penalty), next pull from earnings
    if RemainingStepNeeded > 0.009 and RothBal > 0.009:

        if RothBal > RemainingStepNeeded:
            if Execute:
                TotalCash[YearCt] += RemainingStepNeeded
            Withdrawal += RemainingStepNeeded
            RothBal -= RemainingStepNeeded
            Penalty += 0.1*RemainingStepNeeded
            StdIncDeltaFromEarnings += RemainingStepNeeded
            RemainingStepNeeded = 0.
        else:
            if Execute:
                TotalCash[YearCt] += RothBal
            Withdrawal += RothBal
            Penalty += 0.1*RothBal
            StdIncDeltaFromEarnings += RothBal
            RemainingStepNeeded -= RothBal
            RothBal = 0.

    if Execute:
        # Repack any modified immutable dictionary items (mutable items such as arrays/lists will already be modified)
        Roth['Bal'][YearCt,PersonCt] = RothBal
        # Update Roth['Total']
        Roth['Total'][YearCt] = np.sum(Roth['Bal'][YearCt,:])
        # Roth['ConversionAmount'] is already updated because it's a mutable list and tied to RothConversionAmount

    return Withdrawal, Penalty, StdIncDeltaFromEarnings
