# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-compute-aca-obamacare-subsidies/)

# ComputeSubsidy.py

from WithdrawalOptimization.ComputeFPLpercent import *
from WithdrawalOptimization.ComputeExpectedContribution import *

# Compute ACA subsidy given income, family size, residence, benchmark price

def ComputeSubsidy(Income,NumPeople,Residence,BenchmarkPrice):
    
    # Compute Federal Poverty Level (FPL) percentage
    FPLpercent = ComputeFPLpercent(Income,NumPeople,Residence)
    
    # Compute expected contribution
    # Make sure to account for 100% FPL cutoff of subsidies
    if FPLpercent > 100.:
        ExpectedContribution = ComputeExpectedContribution(FPLpercent,Income)
        EligibleForSubsidy = True
    else:
        EligibleForSubsidy = False
    
    # Compute subsidy, if eligible
    if EligibleForSubsidy == True:
        if ExpectedContribution < BenchmarkPrice:
            AnnualSubsidy = BenchmarkPrice - ExpectedContribution
        else:
            AnnualSubsidy = 0.
    else:
        AnnualSubsidy = 0.

    return AnnualSubsidy