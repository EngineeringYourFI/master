# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/choosing-your-dental-insurance-plan-with-math/)

# ChoosingDentalInsurance.py

import numpy as np
import os
import copy
from Multiplot import *

# Deciding which dental insurance plan to select - either directly from an insurance company or those provided via the
# Affordable Care Act (ACA) Health Insurance Marketplace (otherwise known as Obamacare).

# Assumptions:
# 1. All values in post-tax real dollars

#############################################################################################################
# User Inputs

# Plan names
PlanNames = ['MetLife',
             'UnitedHealthcare: Golden Rule', 'UnitedHealthcare: Smile Now Texas',
             'Guardian: Preventive Plus','Guardian: Basics','Guardian: Essentials']

# 'MetLife'
# https://www.metlifetakealongdental.com/Content/downloads/FullSOB_Low.pdf

# 'UnitedHealthcare: Golden Rule'
# https://www.uhone.com/api/supplysystem/?FileName=45585B-G202108.pdf
# 'UnitedHealthcare: Smile Now Texas':
# https://pd.solsticebenefits.com/2377_187027b9-83d3-44d0-a603-e1e77d30661b.pdf

# 'Guardian: Preventive Plus','Guardian: Basics','Guardian: Essentials'
# https://assets.ctfassets.net/jrhizl9l7csx/TNiwK3DaG9IF0XFgEgZhd/448ca983780718da3f7577e0aa32aaf6/TX_PPO_Preventive_Plus_Ben_Sum_2024.pdf
# https://assets.ctfassets.net/jrhizl9l7csx/zekTiCOJB3zXxUixwIJHE/3341acd3ff0cd7c79516ad90020f8186/TX_PPO_Basics_Ben_Sum_2024.pdf
# https://assets.ctfassets.net/jrhizl9l7csx/29sKx4GhuczgLqKeyKlHaD/acdc4a13e993235773e859bf5f7771e3/TX_PPO_Essentials_Ben_Sum_2024.pdf




# Cash discount rate - depends on the policy of your dentist
CashDiscount = 0.1
# The negotiated discount the insurance company will get from the dentist - typically around 20%
# (anecdotal, likely depends on specific insurance company, dentist, and perhaps even the specific service)
# This is important to have, because this dramatically impacts the max coverage amount
# Also assuming that if you hit max coverage, you'll continue to pay the negotiated rate beyond that
InsuranceNegotiatedDiscount = 0.2

# Expected cash price for preventive  - depends on the policy of your dentist - contact them to get these rates
# Adult: $172 + $201 (cash price of one cleaning+exam and one cleaning+exam+xrays)
# Kid 1: $146 + $201
# Kid 2: $146 + $201
# Total: 172 + 201 + 146 + 201 + 146 + 201 = $1067 (though with CashDiscount of 10%, it's actually $960.30)
CashPricePreventiveTotal = 172. + 201. + 146. + 201. + 146. + 201.
CashPricePreventiveKid = 146. + 201. # going to assume kid doing all preventive services for this analysis
CashPricePreventiveAdult = 172. + 201.

# Annual Premiums For Each Plan - annual
AnnualPremiums = [60.32*12.,
                  67.13*12., 72.31*12.,
                  67.78*12., 70.18*12., 73.35*12.]

# Is the deductible needed before paying 100% on preventive?
DeductibleNeededForPreventive = [False,
                                 False, True,
                                 True, True, True]

# Deductibles - only for non-preventive services, also assume the same deductible for each person
Deductibles_Kid = [75.,
                   50., 60.,
                   150., 150., 150.]
Deductibles_Adult = [75.,
                     50., 50.,
                     50., 50., 50.]

# Coinsurance - for Basic services (the only type considered here, beyond preventive)
# Here coinsurance is defined as the percentage that YOU will pay
# Thus the insurance company will pay (1 - this rate)
CoinsuranceRate_Kid = [0.5,
                       0.5, 0.4,
                       0.2, 0.2, 0.2]

CoinsuranceRate_Adult = [0.5,
                         0.5, 0.4,
                         0.5, 0.4, 0.5]

# Kids Max Out of Pocket - if ACA plan (2024: $400 for one child and $800 for more than one child)
KidIndividualMaxOOP = [np.nan,
                       np.nan, 400.,
                       400.,400.,400.]
KidFamilyMaxOOP = [np.nan,
                   np.nan, 800.,
                   800.,800.,800.]

# Max coverage per person - both kids and adults if non-ACA plan, just adults if ACA plan
MaxCoverage = [750.,
               1000., 1000.,
               1000., 1500., 1000.]

NumAdults = 1
NumKids = 2

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'
# Output to screen instead of file:
OutputToScreen = True

# Flags
TotalCostWithIndividualExpenses_Kid = True
TotalCostWithIndividualExpenses_Adult = True

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

# Compute total base cost for each plan: cost of premiums plus cost of preventive services for all people

NumPlans = len(PlanNames)
NumPlansPlusCashOnly = NumPlans + 1

BaseCost = np.zeros(NumPlansPlusCashOnly)
for ct in range(NumPlans):
    BaseCost[ct] += AnnualPremiums[ct]
    if DeductibleNeededForPreventive[ct]:
        # Asssume preventive services easily exceed deductible, so base cost equal to the deductible
        BaseCost[ct] += NumKids * Deductibles_Kid[ct]
        BaseCost[ct] += NumAdults * Deductibles_Adult[ct]
# Base cost for cash-only is just the cash price of all the preventive services, with any cash discount
BaseCost[-1] = CashPricePreventiveTotal * (1. - CashDiscount)

#############################################################################################################

# Compute total cost of each plan across a wide range of Basic services expenses for a single kid

if TotalCostWithIndividualExpenses_Kid:

    BasicServiceExpenses = np.arange(0.,2500.,1.)

    # Initialize needed running totals - all for kid individual
    TotalPaidTowardDeductible = np.zeros((NumPlans,len(BasicServiceExpenses)))
    TotalPaidByInsurance = np.zeros((NumPlans,len(BasicServiceExpenses)))
    TotalPaidByYouBeyondPremiums = np.zeros((NumPlans,len(BasicServiceExpenses)))
    # Total cost overall for you, including premiums, preventive services for everyone, and Basic service
    # expenses for a single kid
    TotalCost = np.zeros((NumPlansPlusCashOnly,len(BasicServiceExpenses)))

    # Before considering basic services expenses, determine how preventive services impact the running totals
    # Loop over plans
    for ct in range(NumPlans):
        if DeductibleNeededForPreventive[ct]:
            TotalPaidTowardDeductible[ct,0] = Deductibles_Kid[ct]
            TotalPaidByInsurance[ct,0] = CashPricePreventiveKid * (1 - InsuranceNegotiatedDiscount) - \
                                         Deductibles_Kid[ct]
            TotalPaidByYouBeyondPremiums[ct,0] = Deductibles_Kid[ct]
            TotalCost[ct,0] = BaseCost[ct]
        else:
            TotalPaidTowardDeductible[ct,0] = 0. # not necessary, but clarifies
            TotalPaidByInsurance[ct,0] = CashPricePreventiveKid * (1 - InsuranceNegotiatedDiscount)
            TotalPaidByYouBeyondPremiums[ct,0] = 0. # not necessary, but clarifies
            TotalCost[ct,0] = BaseCost[ct]

    # Now update running totals for each additional dollar of basic service expenses at standard dental
    # office rates
    # For each dollar of basic service expenses at standard dental office rates, use "actual addition" for
    # each running total - the amount you and the insurance company will pay after the negotiated rate
    # discount (which will be different for the cash-only scenario below)
    ActualAddition = 1. * (1 - InsuranceNegotiatedDiscount)

    # Loop over plans
    for ct1 in range(NumPlans):
        # Loop over expense levels
        for ct2 in range(len(BasicServiceExpenses)):

            # if it's the first index for basic service expenses, they equal zero - running totals unaffected
            if ct2 == 0:
                continue

            # If deductible has not been met
            if TotalPaidTowardDeductible[ct1,ct2-1] < Deductibles_Kid[ct1]:
                # Then this dollar of expense goes into that deductible
                # Though you do get the insurance discounted rate (ActualAddition)
                TotalPaidTowardDeductible[ct1,ct2] = TotalPaidTowardDeductible[ct1,ct2-1] + ActualAddition
                # And insurance pays nothing
                TotalPaidByInsurance[ct1,ct2] = TotalPaidByInsurance[ct1,ct2-1] + 0.
                TotalPaidByYouBeyondPremiums[ct1,ct2] = TotalPaidByYouBeyondPremiums[ct1,ct2-1] + ActualAddition
                TotalCost[ct1,ct2] = TotalCost[ct1,ct2-1] + ActualAddition
            else: # the deductible has been met, move on to next stage
                # First add this expense to relevant totals

                # Done paying toward deductible, so just carry forward this total
                TotalPaidTowardDeductible[ct1,ct2] = TotalPaidTowardDeductible[ct1,ct2-1]

                # Compute how much the insurance company pays for the incremental expense
                TotalPaidByInsurance[ct1,ct2] = TotalPaidByInsurance[ct1,ct2-1] +\
                                                (1. - CoinsuranceRate_Kid[ct1]) * ActualAddition

                # Compute how much you pay for the incremental expense
                TotalPaidByYouBeyondPremiums[ct1,ct2] = TotalPaidByYouBeyondPremiums[ct1,ct2-1] + \
                                                        CoinsuranceRate_Kid[ct1] * ActualAddition

                # Total cost paid by you
                TotalCost[ct1,ct2] = TotalCost[ct1,ct2-1] + CoinsuranceRate_Kid[ct1] * ActualAddition

                # Then check against any constraints, such as max OOP or max coverage

                # If there is a max OOP, cut off at that point if TotalPaidByYouBeyondPremiums exceed it:
                if KidIndividualMaxOOP[ct1] is not np.nan:
                    if TotalPaidByYouBeyondPremiums[ct1,ct2] > KidIndividualMaxOOP[ct1]:
                        # Remove the excess and place it in the TotalPaidByInsurance[ct1,ct2] total
                        Excess = TotalPaidByYouBeyondPremiums[ct1,ct2] - KidIndividualMaxOOP[ct1]
                        TotalPaidByYouBeyondPremiums[ct1,ct2] -= Excess
                        TotalPaidByInsurance[ct1,ct2] += Excess
                        TotalCost[ct1,ct2] -= Excess

                else: # if there's not a max OOP, then assume there is a max coverage limit
                    if TotalPaidByInsurance[ct1,ct2] > MaxCoverage[ct1]:
                        # Remove the excess from what insurance pays and place it what you pay :-(
                        Excess = TotalPaidByInsurance[ct1,ct2] - MaxCoverage[ct1]
                        TotalPaidByInsurance[ct1,ct2] -= Excess
                        TotalPaidByYouBeyondPremiums[ct1,ct2] += Excess
                        TotalCost[ct1,ct2] += Excess

    # Loop over expense levels for cash-only
    TotalCost[-1,0] = BaseCost[-1]

    # For each dollar of basic service expenses at standard dental office rates, use "actual cash addition"
    # for each running total - the amount you will pay after the cash discount at the dentist
    ActualAddition = 1. * (1 - CashDiscount)
    # Loop over expense levels
    for ct in range(len(BasicServiceExpenses)):
        # if it's the first index for basic service expenses, they equal zero - running totals unaffected
        if ct == 0:
            continue
        TotalCost[-1,ct] = TotalCost[-1,ct-1] + ActualAddition


    NumPlots = NumPlansPlusCashOnly
    PlotLabelArray = copy.deepcopy(PlanNames)
    PlotLabelArray.append('Cash Only')
    PlotColorArray = ['r','b','g',  'k','limegreen','saddlebrown','orange'] # 'c','m',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': BasicServiceExpenses/1000.,
         'DepData': TotalCost/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0.5, 'ymax': 2.5,
         'xmin': BasicServiceExpenses[0]/1000., 'xmax': BasicServiceExpenses[-1]/1000.,
         'ylabel': 'Total Out of Pocket Cost [$K]',
         'xlabel': 'Basic Service Expenses [$K]',
         'TitleText': 'Total Out of Pocket Cost vs \nBasic Service Expenses for Individual Kid',
         'LegendLoc': 'upper right', #'center right', #'center left', #'upper center', #
         'AddTextBox': False,
         'SaveFile': OutDir+'TotalCostWithIndividualExpenses_Kid.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)



#############################################################################################################

# Compute total cost of each plan across a wide range of Basic services expenses for a single adult

if TotalCostWithIndividualExpenses_Adult:

    BasicServiceExpenses = np.arange(0.,3000.,1.)

    # Initialize needed running totals - all for adult individual
    TotalPaidTowardDeductible = np.zeros((NumPlans,len(BasicServiceExpenses)))
    TotalPaidByInsurance = np.zeros((NumPlans,len(BasicServiceExpenses)))
    TotalPaidByYouBeyondPremiums = np.zeros((NumPlans,len(BasicServiceExpenses)))
    # Total cost overall for you, including premiums, preventive services for everyone, and Basic service
    # expenses for a single adult
    TotalCost = np.zeros((NumPlansPlusCashOnly,len(BasicServiceExpenses)))

    # Before considering basic services expenses, determine how preventive services impact the running totals
    # Loop over plans
    for ct in range(NumPlans):
        if DeductibleNeededForPreventive[ct]:
            TotalPaidTowardDeductible[ct,0] = Deductibles_Adult[ct]
            TotalPaidByInsurance[ct,0] = CashPricePreventiveAdult * (1 - InsuranceNegotiatedDiscount) - \
                                         Deductibles_Adult[ct]
            TotalPaidByYouBeyondPremiums[ct,0] = Deductibles_Adult[ct]
            TotalCost[ct,0] = BaseCost[ct]
        else:
            TotalPaidTowardDeductible[ct,0] = 0. # not necessary, but clarifies
            TotalPaidByInsurance[ct,0] = CashPricePreventiveAdult * (1 - InsuranceNegotiatedDiscount)
            TotalPaidByYouBeyondPremiums[ct,0] = 0. # not necessary, but clarifies
            TotalCost[ct,0] = BaseCost[ct]

    # Now update running totals for each additional dollar of basic service expenses at standard dental
    # office rates
    # For each dollar of basic service expenses at standard dental office rates, use "actual addition" for
    # each running total - the amount you and the insurance company will pay after the negotiated rate
    # discount (which will be different for the cash-only scenario below)
    ActualAddition = 1. * (1 - InsuranceNegotiatedDiscount)

    # Loop over plans
    for ct1 in range(NumPlans):
        # Loop over expense levels
        for ct2 in range(len(BasicServiceExpenses)):

            # if it's the first index for basic service expenses, they equal zero - running totals unaffected
            if ct2 == 0:
                continue

            # If deductible has not been met
            if TotalPaidTowardDeductible[ct1,ct2-1] < Deductibles_Adult[ct1]:
                # Then this dollar of expense goes into that deductible
                # Though you do get the insurance discounted rate (ActualAddition)
                TotalPaidTowardDeductible[ct1,ct2] = TotalPaidTowardDeductible[ct1,ct2-1] + ActualAddition
                # And insurance pays nothing
                TotalPaidByInsurance[ct1,ct2] = TotalPaidByInsurance[ct1,ct2-1] + 0.
                TotalPaidByYouBeyondPremiums[ct1,ct2] = TotalPaidByYouBeyondPremiums[ct1,ct2-1] + ActualAddition
                TotalCost[ct1,ct2] = TotalCost[ct1,ct2-1] + ActualAddition
            else: # the deductible has been met, move on to next stage
                # First add this expense to relevant totals

                # Done paying toward deductible, so just carry forward this total
                TotalPaidTowardDeductible[ct1,ct2] = TotalPaidTowardDeductible[ct1,ct2-1]

                # Compute how much the insurance company pays for the incremental expense
                TotalPaidByInsurance[ct1,ct2] = TotalPaidByInsurance[ct1,ct2-1] +\
                                                (1. - CoinsuranceRate_Adult[ct1]) * ActualAddition

                # Compute how much you pay for the incremental expense
                TotalPaidByYouBeyondPremiums[ct1,ct2] = TotalPaidByYouBeyondPremiums[ct1,ct2-1] + \
                                                        CoinsuranceRate_Adult[ct1] * ActualAddition

                # Total cost paid by you
                TotalCost[ct1,ct2] = TotalCost[ct1,ct2-1] + CoinsuranceRate_Adult[ct1] * ActualAddition

                # Then check against max coverage constraint

                if TotalPaidByInsurance[ct1,ct2] > MaxCoverage[ct1]:
                    # Remove the excess from what insurance pays and place it what you pay :-(
                    Excess = TotalPaidByInsurance[ct1,ct2] - MaxCoverage[ct1]
                    TotalPaidByInsurance[ct1,ct2] -= Excess
                    TotalPaidByYouBeyondPremiums[ct1,ct2] += Excess
                    TotalCost[ct1,ct2] += Excess

    # Loop over expense levels for cash-only
    TotalCost[-1,0] = BaseCost[-1]

    # For each dollar of basic service expenses at standard dental office rates, use "actual cash addition"
    # for each running total - the amount you will pay after the cash discount at the dentist
    ActualAddition = 1. * (1 - CashDiscount)
    # Loop over expense levels
    for ct in range(len(BasicServiceExpenses)):
        # if it's the first index for basic service expenses, they equal zero - running totals unaffected
        if ct == 0:
            continue
        TotalCost[-1,ct] = TotalCost[-1,ct-1] + ActualAddition


    NumPlots = NumPlansPlusCashOnly
    PlotLabelArray = copy.deepcopy(PlanNames)
    PlotLabelArray.append('Cash Only')
    PlotColorArray = ['r','b','g',  'k','limegreen','saddlebrown','orange'] # 'c','m',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': BasicServiceExpenses/1000.,
         'DepData': TotalCost/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0.5, 'ymax': 4.0,
         'xmin': BasicServiceExpenses[0]/1000., 'xmax': BasicServiceExpenses[-1]/1000.,
         'ylabel': 'Total Out of Pocket Cost [$K]',
         'xlabel': 'Basic Service Expenses [$K]',
         'TitleText': 'Total Out of Pocket Cost vs \nBasic Service Expenses for Individual Adult',
         'LegendLoc': 'upper right', #'center right', #'center left', #'upper center', #
         'AddTextBox': False,
         'SaveFile': OutDir+'TotalCostWithIndividualExpenses_Adult.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)