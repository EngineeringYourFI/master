# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/is-it-worth-letting-your-warehouse-club-membership-expire/)

# ProjBalance.py

import numpy as np

def ProjBalance(ProjDict):

    # Unpack dict
    AnnualMembershipFee = ProjDict['AnnualMembershipFee']
    MonthlySpendAtWarehouse = ProjDict['MonthlySpendAtWarehouse']
    Discount = ProjDict['Discount']
    AnnualROI = ProjDict['AnnualROI']
    InitBal = ProjDict['InitBal']
    NumYears = ProjDict['NumYears']
    NumMonthsToWait = ProjDict['NumMonthsToWait']
    StockUp = ProjDict['StockUp']
    PayHigherPrices = ProjDict['PayHigherPrices']


    NumMonths = NumYears*12
    MonthlyROI = AnnualROI/12. # yes, this is just an approximation

    # Initialize balance array - must be 2D for plotting, with each row a distinct plotted line
    BalanceArray = np.zeros((1,NumMonths))
    BalanceArray[0,0] = InitBal
    MonthArray = range(0,NumMonths)

    MembershipMonthCt = 0
    InMembership = False
    WaitPeriodMonthCt = 0
    InWaitPeriod = False

    for ct in range(0,NumMonths):

        # Assume we start first month with joining warehouse club
        if ct == 0:
            InMembership = True
        else:
            # Bring balance forward, with appropriate ROI
            BalanceArray[0,ct] = np.round(BalanceArray[0,ct-1]*(1+MonthlyROI),2)

        if InMembership:
            # If the first month of the membership (zero-based indexing), subtract membership fee
            if MembershipMonthCt == 0:
                BalanceArray[0,ct] -= AnnualMembershipFee

            # If prior to final month of the membership (zero-based indexing)
            if MembershipMonthCt < 11:
                BalanceArray[0,ct] -= MonthlySpendAtWarehouse # just a standard monthly expense
                # Iterate MembershipMonthCt
                MembershipMonthCt += 1
            else: # then in final month
                if StockUp:
                    # buy for this month plus stock up for wait period months
                    BalanceArray[0,ct] -= MonthlySpendAtWarehouse * (1+NumMonthsToWait)
                else: # just buy for this month
                    BalanceArray[0,ct] -= MonthlySpendAtWarehouse
                # Reset MembershipMonthCt
                MembershipMonthCt = 0

                # If wait period at least one month, turn off membership and turn on wait period
                if NumMonthsToWait > 0:
                    InMembership = False
                    InWaitPeriod = True
                    continue

        if InWaitPeriod:

            if PayHigherPrices:
                # Then pay higher prices for your items
                BalanceArray[0,ct] -= MonthlySpendAtWarehouse * (1/(1-Discount))

            # if prior to the final month of the wait period
            if (WaitPeriodMonthCt + 1) < NumMonthsToWait:
                WaitPeriodMonthCt += 1

            else: # at the final month of the wait period
                # so turn off InWaitPeriod and turn on InMembership
                InWaitPeriod = False
                InMembership = True
                # Reset WaitPeriodMonthCt
                WaitPeriodMonthCt = 0
                # continue

    return BalanceArray, MonthArray