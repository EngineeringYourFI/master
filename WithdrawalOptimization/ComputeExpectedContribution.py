# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-compute-aca-obamacare-subsidies/)

# ComputeExpectedContribution.py

# Compute expected contribution to ACA health insurance premiums, given income relative to Federal Poverty Level (FPL)

# If you earn -- Your expected contribution is
# Up to 150% of FPL -- 0% of your income (ie, the benchmark plan will have no premium)
# 150%-200% of FPL -- 0%-2% of your income
# 200%-250% of FPL -- 2%-4% of your income
# 250%-300% of FPL -- 4%-6% of your income
# 300%-400% of FPL -- 6%-8.5% of your income
# 400% of FPL or higher -- 8.5% of your income

def ComputeExpectedContribution(FPLpercent,Income):

    if FPLpercent <= 150.:
        ExpectedContributionFraction = 0.
    elif FPLpercent > 150. and FPLpercent <= 200.:
        ExpectedContributionFraction = ((FPLpercent - 150.)/50)*0.02 + 0.
    elif FPLpercent > 200. and FPLpercent <= 250.:
        ExpectedContributionFraction = ((FPLpercent - 200.)/50)*0.02 + 0.02
    elif FPLpercent > 250. and FPLpercent <= 300.:
        ExpectedContributionFraction = ((FPLpercent - 250.)/50)*0.02 + 0.04
    elif FPLpercent > 300. and FPLpercent <= 400.:
        ExpectedContributionFraction = ((FPLpercent - 300.)/100)*0.025 + 0.06
    elif FPLpercent > 400.:
        ExpectedContributionFraction = 0.085

    ExpectedContribution = ExpectedContributionFraction*Income

    return ExpectedContribution