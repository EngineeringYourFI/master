# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# TaxableIncomeTargetMethodWithSSI.py

# Note: any references to "SSI" stand for normal social security income (RIB), not Supplemental Security Income (a
# different program that is also provided by the Social Security Administration).

import numpy as np
from TaxableSSconsolidated import TaxableSSconsolidated
from ComputeMaxAdjustableNonSSstandardIncome import ComputeMaxAdjustableNonSSstandardIncome

def TaxableIncomeTargetMethodWithSSI(NonadjustableStandardIncome,NonadjustableLTcapGainsIncome,TotalSS,
                                     MaxStandardIncome,MaxTotalIncome,FilingStatus):

    # Start by adjusting MaxStandardIncome and MaxTotalIncome if needed
    MinTaxableSS = np.round(TaxableSSconsolidated(NonadjustableStandardIncome+NonadjustableLTcapGainsIncome,TotalSS,
                                                  FilingStatus),2)
    MinStandardIncome = NonadjustableStandardIncome + MinTaxableSS
    if MinStandardIncome > MaxStandardIncome:
        MaxStandardIncome = MinStandardIncome

    MinTotalIncome = NonadjustableStandardIncome + NonadjustableLTcapGainsIncome + MinTaxableSS
    if MinTotalIncome > MaxTotalIncome:
        MaxTotalIncome = MinTotalIncome

    # Compute MaxAdjustableNonSSstandardIncome if any room
    if MinStandardIncome < MaxStandardIncome:

        # Solve for MaxAdjustableNonSSstandardIncome such that
        # NonadjustableStandardIncome + TaxableSS(NonadjustableStandardIncome,NonadjustableLTcapGainsIncome,TotalSS,
        # MaxAdjustableNonSSstandardIncome,0) + MaxAdjustableNonSSstandardIncome = MaxStandardIncome
        # Where MaxAdjustableLTcapGainsIncome set equal to zero.

        MaxAdjustableNonSSstandardIncome = \
            np.round(ComputeMaxAdjustableNonSSstandardIncome(NonadjustableStandardIncome,NonadjustableLTcapGainsIncome,
                                                             TotalSS,MaxStandardIncome,FilingStatus),2)

        # Compute how much of social security income will be taxable
        TaxableSS = MaxStandardIncome - NonadjustableStandardIncome - MaxAdjustableNonSSstandardIncome
        # # To verify, should be the same:
        # LTcapGains = NonadjustableLTcapGainsIncome
        # TaxableSS = np.round(TaxableSSconsolidated(NonadjustableStandardIncome+MaxAdjustableNonSSstandardIncome+
        #                                            LTcapGains,TotalSS,FilingStatus),2)
    else:
        # MaxAdjustableNonSSstandardIncome = 0.
        TaxableSS = MinTaxableSS

    # if TaxableSS < 0.85*TotalSS, need to set MaxAdjustableNonSSstandardIncome as zero (as any increase in LT cap
    # gains will increase TaxableSS, and thus push standard income beyond MaxStandardIncome, or even further beyond
    # MaxStandardIncome), which means changing output MaxTotalIncome to MaxStandardIncome + NonadjustableLTcapGainsIncome
    if TaxableSS <= (0.85*TotalSS - 0.01):
        MaxTotalIncome = MaxStandardIncome + NonadjustableLTcapGainsIncome

        # if MinTotalIncome > MaxTotalIncome: # in case this ever happens
        if (MinTotalIncome - MaxTotalIncome) >= 0.01: # in case this ever happens
            print('MinTotalIncome > MaxTotalIncome: Figure out what to do in this situation (if ever encountered).')

    # If TaxableSS = 0.85*Total, then it's already maximized and additional LT cap gains won't increase TaxableSS,
    # so we can leave MaxTotalIncome as-is, indicating that MaxAdjustableLTcapGainsIncome can be increased until
    # total income reaches MaxTotalIncome.
    # Could also directly compute MaxAdjustableLTcapGainsIncome = MaxTotalIncome - (NonadjustableStandardIncome +
    # NonadjustableLTcapGainsIncome + TaxableSS + MaxAdjustableNonSSstandardIncome)
    # But not needed, since just outputting MaxTotalIncome.

    return TaxableSS, MaxStandardIncome, MaxTotalIncome
