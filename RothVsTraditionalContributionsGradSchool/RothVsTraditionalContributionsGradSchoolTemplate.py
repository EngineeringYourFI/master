# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular
# https://engineeringyourfi.com/roth-vs-traditional-ira-contributions-in-grad-school/)

# RothVsTraditionalContributionsGradSchoolTemplate.py

import numpy as np
import os
import copy

from Multiplot import *

# Consider making Roth vs Traditional IRA contributions while in grad school with a low marginal tax bracket

# Assumptions:
# 1. All input and output values, and assumed investment returns, in present-day dollars

#############################################################################################################
# User Inputs

# Grad School Dollar Contribution
OriginalContribution = 1000.
# Your age when you made the contribution
ContributionAge = 20

# Marginal tax bracket rate in grad school
OriginalTaxRate = 0.12
# using 12% top tax bracket because the standard deduction of $13,850 plus the top of the 10% bracket $11,000
# is just $24,850, and I think most grad students probably make more than that now, but not sure
# but 10% vs 12% is pretty minor, and I strongly suspect won’t make a difference

# After-inflation annual investment return
# https://www.thesimpledollar.com/investing/stocks/where-does-7-come-from-when-it-comes-to-long-term-stock-returns/?
# "For the period 1950 to 2009, if you adjust the S&P 500 for inflation and account for dividends, the average annual
# return comes out to exactly 7.0%."
# If 70% equities and 30% bonds (at real 1% ROI), 0.7*7 + 0.3*1 = 5.2%, so we'll just assume 5% ROI for the default
ROI = 0.05

# Number of years to simulate
NumYears = 70

# Output Directory
OutDir = './'

# Flags
CashOutComparisonNoTaxes = True
CashOutComparison12percentTaxes = True
CashOutComparison24percentTaxes = True
LongevityComparison12percentTaxes = True
RothLadderScenario = True

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Default plotting parameters, using dictionary (can modify if needed)
DefaultPlotDict = \
    {'FigWidth': 10.8, 'FigHeight': 10.8,
     'LineStyle': '-', 'LineWidth': 3,
     'MarkerSize': 10,
     'CopyrightX': 0.01, 'CopyrightY': 1-0.01, 'CopyrightText': 'EngineeringYourFI.com', 'CopyrightFontSize': 20,
     'CopyrightVertAlign': 'top',
     'ylabelFontSize': 30, 'xlabelFontSize': 30,
     'Title_yoffset': 0.99, #'Title_xoffset': 0.5,
     'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20, 'LegendOn': True,
     'PlotSecondaryLines': False,
     'AddTextBox':False,
     'TextBoxX': 0.02,
     'TextBoxY': 0.93,
     'TextBoxFontSize': 20}

#############################################################################################################

# Compute future "cash out" values for Traditional vs Roth contribution from grad school, assuming no taxes
# (i.e. you're retired or taking a long enough sabbatical that you're income is low enough to be within the
# standard deduction)
if CashOutComparisonNoTaxes:

    TraditionalBalance = np.zeros(NumYears)
    RothBalance = np.zeros(NumYears)
    TraditionalCashOutBalance = np.zeros(NumYears)
    RothCashOutBalance = np.zeros(NumYears)

    OriginalTradContribution = OriginalContribution # immutable, so can do a direct = to copy
    OriginalRothContribution = OriginalContribution*(1-OriginalTaxRate)

    Age = range(ContributionAge,ContributionAge+NumYears)

    for ct in range(NumYears):
        TraditionalBalance[ct] = OriginalTradContribution * (1.+ROI)**float(ct)
        RothBalance[ct] = OriginalRothContribution * (1.+ROI)**float(ct)

        if ct == 0:
            # use np.nan for the first year of the cash-out balance, since doesn’t make sense to have a
            # cash-out value for that year that you make the contribution, especially if assuming a 12% tax
            # bracket on the year of the contribution and 0% of the year of the withdrawal
            TraditionalCashOutBalance[ct] = np.nan
            RothCashOutBalance[ct] = np.nan
            continue
        if Age[ct] < 60:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct]*0.9
            RothCashOutBalance[ct] = OriginalRothContribution + \
                                     (RothBalance[ct] - OriginalRothContribution)*0.9
        else:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct]
            RothCashOutBalance[ct] = RothBalance[ct]

    NumPlots = 4
    PlotLabelArray = ['Traditional Balance','Roth Balance','Traditional Cash Out','Roth Cash Out']
    PlotColorArray = ['r','b','g','c'] #,'m','k','limegreen','saddlebrown','orange'

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 0% (retired/sabbatical)'

    # DepData array must be 2D for MultiPlot
    BalanceArray2D = np.zeros((4,NumYears))
    BalanceArray2D[0,:] = TraditionalBalance
    BalanceArray2D[1,:] = RothBalance
    BalanceArray2D[2,:] = TraditionalCashOutBalance
    BalanceArray2D[3,:] = RothCashOutBalance

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Age,
         'DepData': BalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(BalanceArray2D/1000.)+1.5,
         'xmin': Age[0], 'xmax': Age[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Traditional And Roth Balances vs Age',
         'LegendLoc': 'center left', #'upper right', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'CashOutComparisonNoTaxes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


    # Plot diff of cash-out balances
    CashOutDiff = TraditionalCashOutBalance - RothCashOutBalance

    NumPlots = 1
    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 0% (retired/sabbatical)'

    # DepData array must be 2D for MultiPlot
    DiffBalanceArray2D = np.zeros((1,NumYears))
    DiffBalanceArray2D[0,:] = CashOutDiff

    # Update plot dict
    UpdateDict = \
        {'DepData': DiffBalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': 0., 'ymax': np.nanmax(DiffBalanceArray2D/1000.)+0.5,
         'ylabel': 'Balance Diff [$K]',
         'TitleText': 'Traditional Minus Roth Cash Out vs Age',
         'LegendOn': False,
         'SaveFile': OutDir+'CashOutComparisonNoTaxesDiff.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


#############################################################################################################

# Compute future "cash out" values for Traditional vs Roth contribution from grad school, assuming a 12% tax
# rate on the withdrawal (i.e. you're retired or taking a long enough sabbatical that you're income is low
# enough to be within the 12% marginal tax bracket)
if CashOutComparison12percentTaxes:

    TraditionalBalance = np.zeros(NumYears)
    RothBalance = np.zeros(NumYears)
    TraditionalCashOutBalance = np.zeros(NumYears)
    RothCashOutBalance = np.zeros(NumYears)

    OriginalTradContribution = OriginalContribution # immutable, so can do a direct = to copy
    OriginalRothContribution = OriginalContribution*(1-OriginalTaxRate)

    Age = range(ContributionAge,ContributionAge+NumYears)

    for ct in range(NumYears):
        TraditionalBalance[ct] = OriginalTradContribution * (1.+ROI)**float(ct)
        RothBalance[ct] = OriginalRothContribution * (1.+ROI)**float(ct)

        if ct == 0:
            # use np.nan for the first year of the cash-out balance
            TraditionalCashOutBalance[ct] = np.nan
            RothCashOutBalance[ct] = np.nan
            continue
        if Age[ct] < 60:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.1 - 0.12)
            RothCashOutBalance[ct] = OriginalRothContribution + \
                                     (RothBalance[ct] - OriginalRothContribution) * (1 - 0.1 - 0.12)
        else:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.12)
            RothCashOutBalance[ct] = RothBalance[ct]

    NumPlots = 4
    PlotLabelArray = ['Traditional Balance','Roth Balance','Traditional Cash Out','Roth Cash Out']
    PlotColorArray = ['r','b','g','c'] #,'m','k','limegreen','saddlebrown','orange'

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 12%'

    # DepData array must be 2D for MultiPlot
    BalanceArray2D = np.zeros((4,NumYears))
    BalanceArray2D[0,:] = TraditionalBalance
    BalanceArray2D[1,:] = RothBalance
    BalanceArray2D[2,:] = TraditionalCashOutBalance
    BalanceArray2D[3,:] = RothCashOutBalance

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Age,
         'DepData': BalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(BalanceArray2D/1000.)+1.5,
         'xmin': Age[0], 'xmax': Age[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Traditional And Roth Balances vs Age',
         'LegendLoc': 'center left', #'upper right', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'CashOutComparison12percentTaxes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


    # Plot diff of cash-out balances
    CashOutDiff = TraditionalCashOutBalance - RothCashOutBalance

    NumPlots = 1
    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 12%'

    # DepData array must be 2D for MultiPlot
    DiffBalanceArray2D = np.zeros((1,NumYears))
    DiffBalanceArray2D[0,:] = CashOutDiff

    # Update plot dict
    UpdateDict = \
        {'DepData': DiffBalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': np.nanmin(DiffBalanceArray2D/1000.)-0.1, 'ymax': np.nanmax(DiffBalanceArray2D/1000.)+0.1,
         'ylabel': 'Balance Diff [$K]',
         'TitleText': 'Traditional Minus Roth Cash Out vs Age',
         'LegendOn': False,
         'SaveFile': OutDir+'CashOutComparison12percentTaxesDiff.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute future "cash out" values for Traditional vs Roth contribution from grad school, assuming a 24% tax
# rate on the withdrawal (i.e. you're working full time and yet still really need that money so you're in a
# higher tax bracket unfortunately, or you're retired and your retirement income alone is enough to push you
# into a higher bracket)
if CashOutComparison24percentTaxes:

    TraditionalBalance = np.zeros(NumYears)
    RothBalance = np.zeros(NumYears)
    TraditionalCashOutBalance = np.zeros(NumYears)
    RothCashOutBalance = np.zeros(NumYears)

    OriginalTradContribution = OriginalContribution # immutable, so can do a direct = to copy
    OriginalRothContribution = OriginalContribution*(1-OriginalTaxRate)

    Age = range(ContributionAge,ContributionAge+NumYears)

    for ct in range(NumYears):
        TraditionalBalance[ct] = OriginalTradContribution * (1.+ROI)**float(ct)
        RothBalance[ct] = OriginalRothContribution * (1.+ROI)**float(ct)

        if ct == 0:
            # use np.nan for the first year of the cash-out balance
            TraditionalCashOutBalance[ct] = np.nan
            RothCashOutBalance[ct] = np.nan
            continue
        if Age[ct] < 60:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.1 - 0.24)
            RothCashOutBalance[ct] = OriginalRothContribution + \
                                     (RothBalance[ct] - OriginalRothContribution) * (1 - 0.1 - 0.24)
        else:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.24)
            RothCashOutBalance[ct] = RothBalance[ct]

    NumPlots = 4
    PlotLabelArray = ['Traditional Balance','Roth Balance','Traditional Cash Out','Roth Cash Out']
    PlotColorArray = ['r','b','g','c'] #,'m','k','limegreen','saddlebrown','orange'

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 24%'

    # DepData array must be 2D for MultiPlot
    BalanceArray2D = np.zeros((4,NumYears))
    BalanceArray2D[0,:] = TraditionalBalance
    BalanceArray2D[1,:] = RothBalance
    BalanceArray2D[2,:] = TraditionalCashOutBalance
    BalanceArray2D[3,:] = RothCashOutBalance

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Age,
         'DepData': BalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(BalanceArray2D/1000.)+1.5,
         'xmin': Age[0], 'xmax': Age[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Traditional And Roth Balances vs Age',
         'LegendLoc': 'center left', #'upper right', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'CashOutComparison24percentTaxes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


    # Plot diff of cash-out balances
    CashOutDiff = TraditionalCashOutBalance - RothCashOutBalance

    NumPlots = 1
    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 24%'

    # DepData array must be 2D for MultiPlot
    DiffBalanceArray2D = np.zeros((1,NumYears))
    DiffBalanceArray2D[0,:] = CashOutDiff

    # Update plot dict
    UpdateDict = \
        {'DepData': DiffBalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': np.nanmin(DiffBalanceArray2D/1000.)-0.1, 'ymax': np.nanmax(DiffBalanceArray2D/1000.)+0.5,
         'ylabel': 'Balance Diff [$K]',
         'TitleText': 'Traditional Minus Roth Cash Out vs Age',
         'LegendOn': False,
         'SaveFile': OutDir+'CashOutComparison24percentTaxesDiff.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)



#############################################################################################################

# For the withdrawal 12% tax rate scenario (the  Roth and Traditional exactly equal each other after age 60),
# start withdrawing $1K from each type of account at age 60, see how long each last.
if LongevityComparison12percentTaxes:

    # Annual cash needed from each account
    CashNeeded = 450.

    TraditionalBalance = np.zeros(NumYears-(60-ContributionAge))
    RothBalance = np.zeros(NumYears-(60-ContributionAge))

    OriginalTradContribution = OriginalContribution # immutable, so can do a direct = to copy
    OriginalRothContribution = OriginalContribution*(1-OriginalTaxRate)

    TraditionalBalance[0] = OriginalTradContribution * (1.+ROI)**float(60-ContributionAge)
    RothBalance[0] = OriginalRothContribution * (1.+ROI)**float(60-ContributionAge)

    Age = range(60,ContributionAge+NumYears)

    TraditionalBalanceDepleted = False
    RothBalanceDepleted = False

    for ct in range(NumYears-(60-ContributionAge)):

        if ct > 0:
            # Add growth
            TraditionalBalance[ct] = TraditionalBalance[ct-1] * (1.+ROI)
            RothBalance[ct] = RothBalance[ct-1] * (1.+ROI)

            # Then do withdrawal to get cash needed
            TraditionalBalance[ct] -= CashNeeded / (1 - 0.12)
            RothBalance[ct] -= CashNeeded

        if TraditionalBalance[ct] < 0. and TraditionalBalanceDepleted == False:
            TraditionalBalanceDepleted = True
            TraditionalBalanceDepletionAge = 60 + ct
        if RothBalance[ct] < 0. and RothBalanceDepleted == False:
            RothBalanceDepleted = True
            RothBalanceDepletionAge = 60 + ct

    NumPlots = 2
    PlotLabelArray = ['Traditional, Depleted at '+'{:d}'.format(TraditionalBalanceDepletionAge),
                      'Roth, Depleted at '+'{:d}'.format(RothBalanceDepletionAge)]
    PlotColorArray = ['r','b'] #,'g','c','m','k','limegreen','saddlebrown','orange'

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 12%\nWithdrawing $450/year'

    # DepData array must be 2D for MultiPlot
    BalanceArray2D = np.zeros((2,NumYears-(60-ContributionAge)))
    BalanceArray2D[0,:] = TraditionalBalance
    BalanceArray2D[1,:] = RothBalance

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Age,
         'DepData': BalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(BalanceArray2D/1000.)+1.5,
         'xmin': Age[0], 'xmax': Age[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Traditional & Roth Balances - Annual Withdrawal',
         'LegendLoc': 'upper right', #'center left', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'LongevityComparison12percentTaxes.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


#############################################################################################################

# Roth Ladder scenario: assuming 12% withdrawal tax to keep things "fair", assume you work until age 35/40 and
# then FIRE (since saving 50% or more will let you retire in 15 years or less). At that age you start a Roth
# ladder, are able to tap those funds at age 40/45+ without penalty (original contribution at least).
# * Scenario 1 is a traditional IRA until you FIRE, then a Roth (and you can access the rollover amount
# penalty free 5 years later)
# * Scenario 2 is Roth the entire time
# * Calculate the cash-out value of each scenario
if RothLadderScenario:

    RetirementAge = 35

    TraditionalBalance = np.zeros(NumYears)
    RothBalance = np.zeros(NumYears)
    RothRolloverBalance = np.zeros(NumYears)
    TraditionalCashOutBalance = np.zeros(NumYears)
    RothCashOutBalance = np.zeros(NumYears)
    RothRolloverCashOutBalance = np.zeros(NumYears)

    OriginalTradContribution = OriginalContribution # immutable, so can do a direct = to copy
    OriginalRothContribution = OriginalContribution*(1-OriginalTaxRate)

    TraditionalBalance[0] = OriginalTradContribution
    RothBalance[0] = OriginalRothContribution

    RolloverHappened = False

    Age = range(ContributionAge,ContributionAge+NumYears)

    for ct in range(len(Age)):

        if ct > 0:
            # Add growth
            TraditionalBalance[ct] = TraditionalBalance[ct-1] * (1.+ROI)
            RothBalance[ct] = RothBalance[ct-1] * (1.+ROI)
            RothRolloverBalance[ct] = RothRolloverBalance[ct-1] * (1.+ROI)

        # perform rollover at retirement age
        if Age[ct] == RetirementAge:
            RolloverHappened = True
            RothRolloverContribution = TraditionalBalance[ct] * (1 - 0.12)
            RothRolloverBalance[ct] = RothRolloverContribution
            TraditionalBalance[ct] = 0.

        # Compute cash-out value
        if ct == 0:
            # use np.nan for the first year of the cash-out balance
            TraditionalCashOutBalance[ct] = np.nan
            RothCashOutBalance[ct] = np.nan
            RothRolloverCashOutBalance[ct] = np.nan
            continue
        if Age[ct] < 60:
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.1 - 0.12)
            RothCashOutBalance[ct] = OriginalRothContribution + \
                                     (RothBalance[ct] - OriginalRothContribution) * (1 - 0.1 - 0.12)
            if RolloverHappened:
                if Age[ct] < (RetirementAge+5): # assuming retiring before age 55 and thus needing the Roth ladder
                    # If not yet five years since rollover, you'll pay a penalty on the rollover amount (but not
                    # taxes, since you already did that) and both a penalty and taxes on the growth
                    RothRolloverCashOutBalance[ct] = RothRolloverContribution * (1 - 0.1) + \
                                                     (RothRolloverBalance[ct] - RothRolloverContribution) * \
                                                     (1 - 0.1 - 0.12)
                else:
                    # After five years, you can withdraw the original rollover contribution penalty free, but
                    # you'll still pay both a penalty and taxes on the growth if under 59.5
                    RothRolloverCashOutBalance[ct] = RothRolloverContribution + \
                                                     (RothRolloverBalance[ct] - RothRolloverContribution) * \
                                                     (1 - 0.1 - 0.12)


        else: # over 59.5, so can withdraw penalty free
            TraditionalCashOutBalance[ct] = TraditionalBalance[ct] * (1 - 0.12)
            RothCashOutBalance[ct] = RothBalance[ct]
            RothRolloverCashOutBalance[ct] = RothRolloverBalance[ct]


    NumPlots = 6
    PlotLabelArray = ['Traditional Balance','Roth Balance','Rollover Roth','Traditional Cash Out',
                      'Roth Cash Out','Rollover Roth Cash Out']
    PlotColorArray = ['r','b','g','c','m','k'] #,'limegreen','saddlebrown','orange'

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 12%'

    # DepData array must be 2D for MultiPlot
    BalanceArray2D = np.zeros((6,NumYears))
    BalanceArray2D[0,:] = TraditionalBalance
    BalanceArray2D[1,:] = RothBalance
    BalanceArray2D[2,:] = RothRolloverBalance
    BalanceArray2D[3,:] = TraditionalCashOutBalance
    BalanceArray2D[4,:] = RothCashOutBalance
    BalanceArray2D[5,:] = RothRolloverCashOutBalance


    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Age,
         'DepData': BalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(BalanceArray2D/1000.)+1.5,
         'xmin': Age[0], 'xmax': Age[-1],
         'ylabel': 'Balance [$K]',
         'xlabel': 'Age',
         'TitleText': 'Traditional And Roth Balances vs Age',
         'LegendLoc': 'center left', #'upper right', #'center right', #'upper center', #
         'AddTextBox': True,
         'TextBoxStr': TextBoxString,
         'SaveFile': OutDir+'RothLadderScenario.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


    # Plot diff of cash-out balances
    CashOutDiff = np.zeros(NumYears)
    CashOutDiff[0:(RetirementAge-ContributionAge)] = TraditionalCashOutBalance[0:(RetirementAge-ContributionAge)] - \
                                                     RothCashOutBalance[0:(RetirementAge-ContributionAge)]
    CashOutDiff[(RetirementAge-ContributionAge):] = RothRolloverCashOutBalance[(RetirementAge-ContributionAge):] - \
                                                    RothCashOutBalance[(RetirementAge-ContributionAge):]

    NumPlots = 1
    PlotLabelArray = ['']
    PlotColorArray = ['k']

    # Text box string
    TextBoxString = 'Original Marginal Tax 12%\nWithdrawal Tax 12%'

    # DepData array must be 2D for MultiPlot
    DiffBalanceArray2D = np.zeros((1,NumYears))
    DiffBalanceArray2D[0,:] = CashOutDiff

    # Update plot dict
    UpdateDict = \
        {'DepData': DiffBalanceArray2D/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'ymin': np.nanmin(DiffBalanceArray2D/1000.)-0.1, 'ymax': np.nanmax(DiffBalanceArray2D/1000.)+0.1,
         'ylabel': 'Balance Diff [$K]',
         'TitleText': 'Traditional/Rollover Minus Roth Cash Out vs Age',
         'LegendOn': False,
         'SaveFile': OutDir+'RothLadderScenarioDiff.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

