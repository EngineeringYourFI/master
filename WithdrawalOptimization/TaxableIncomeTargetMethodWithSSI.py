# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-pay-no-taxes-on-social-security-income/)

# TaxableIncomeTargetMethodWithSSI.py

import numpy as np
from TaxableSSconsolidated import TaxableSSconsolidated
from ComputeMaxNonSSstandardIncome import ComputeMaxNonSSstandardIncome
from ComputeMaxCapGains import ComputeMaxCapGains

def TaxableIncomeTargetMethodWithSSI(TotalStandardIncome,TotalSS,MaxStandardIncome,SpecifiedIncome,FilingStatus):

    # Determine how much room left in standard income
    RemainingStandardIncomeRoom = MaxStandardIncome - TotalStandardIncome

    # Solve for max non-SS standard income that will, when added to taxable SS income, equal RemainingStandardIncomeRoom
    MaxNonSSstandardIncome = np.round(ComputeMaxNonSSstandardIncome(TotalSS,SpecifiedIncome,RemainingStandardIncomeRoom,
                                                           FilingStatus),2)
    # determine how much of social security income will be taxable
    TaxableSSincome = RemainingStandardIncomeRoom - MaxNonSSstandardIncome
    # Should be the same, even if MaxNonSSstandardIncome is negative (see below):
    # TaxableSSincome = TaxableSSconsolidated(MaxNonSSstandardIncome + SpecifiedIncome-MaxStandardIncome,TotalSS,
    #                                         FilingStatus)

    # if MaxNonSSstandardIncome is negative, that means TaxableSSincome is GREATER than RemainingStandardIncomeRoom
    # (i.e. how much room left in standard deduction)
    if MaxNonSSstandardIncome < 0.:
        # first determine if it's possible to lower cap gains enough to get TaxableSSincome less than
        # RemainingStandardIncomeRoom:
        TaxableSSincomeNoOtherIncome = TaxableSSconsolidated(0.,TotalSS,FilingStatus)

        # if so, then determine what cap gains will result in TaxableSSincome = RemainingStandardIncomeRoom
        if TaxableSSincomeNoOtherIncome < RemainingStandardIncomeRoom:
            MaxCapGains = np.round(ComputeMaxCapGains(TotalSS,RemainingStandardIncomeRoom,FilingStatus),2)
            # TaxableSSincome should now equal RemainingStandardIncomeRoom
            TaxableSSincome = np.round(TaxableSSconsolidated(0.+MaxCapGains,TotalSS,FilingStatus),2)
            # Reset SpecifiedIncome to account for the lower cap gains
            SpecifiedIncome = np.round(TotalStandardIncome + TaxableSSincome + MaxCapGains,2) # sometimes requires np.round
            # change MaxNonSSstandardIncome to zero (instead of negative), since we're lowering our capital gains to
            # allow TaxableSSincome = RemainingStandardIncomeRoom, and have no room for additional NonSSstandardIncome
            MaxNonSSstandardIncome = 0.
        else:
            MaxCapGains = SpecifiedIncome - MaxStandardIncome
    else:
        MaxCapGains = SpecifiedIncome - MaxStandardIncome

    return TaxableSSincome, SpecifiedIncome, MaxNonSSstandardIncome, MaxCapGains