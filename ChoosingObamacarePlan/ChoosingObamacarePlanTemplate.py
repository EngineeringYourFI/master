# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/choosing-your-obamacare-plan-with-math/)

# ChoosingObamacarePlanTemplate.py

import numpy as np
import os
import copy

from Multiplot import *

# Deciding which health insurance plan to select on the Affordable Care Act (ACA) Health Insurance
# Marketplace (otherwise known as Obamacare)

# Assumptions:
# 1. All values in post-tax real dollars

#############################################################################################################
# User Inputs

# Plan names
PlanNames = ['Aetna Gold 3', 'Aetna Gold S', 'Aetna Gold 4']

# Monthly Premiums For Each Plan
Premiums = [100.71, 104.21, 115.88]

# Copays
# Primary care physician (PCP)
PCPcopays = [15., 30., 0.]
# Specialist
SpecialistCopays = [35., 60., 10.]
# Urgent care
UrgentCareCopays = [25., 45., 10.]
# Outpatient Mental Health
MentalHealthCopays = [15., 30., 0.]

# Generic drugs price
GenericRx = [15., 15., 0.]

# X-rays and diagnostic imaging - copays
ImagingCopay = [35., np.nan, 10.]
# X-rays and diagnostic imaging - coinsurance rates
ImagingCoinsuranceRates = [np.nan, 0.25, np.nan]
# X-rays and diagnostic imaging - average cash price - if no set fee as part of the plan
ImagingCashPrice = 279. # https://www.mdsave.com/procedures/x-ray/d781f4cb/texas

# Labs
LabCopays = [20., np.nan, 0.]
LabCoinsuranceRates = [np.nan, 0.25, np.nan]
LabCashPrice = 100. # https://www.talktomira.com/post/how-much-do-lab-test-cost-without-insurance

# Other Medical Services
# Assuming Emergency room, Outpatient, and Inpatient (like a hospital stay) all have the same rates
# If not, can define and evaluate each one independently
CoinsuranceRates = [0.5, 0.25, 0.25]
# # Emergency room
# ERcoinsuranceRates = [0.5, 0.25, 0.25]
# # Outpatient
# OutpatientCoinsuranceRates = [0.5, 0.25, 0.25]
# # Inpatient (like a hospital stay)
# InpatientCoinsuranceRates = [0.5, 0.25, 0.25]

# Deductibles
IndividualDeductibles = [795., 1500., 3500.]
FamilyDeductibles = [1590., 3000., 7000.]

# Max Out of Pocket
IndividualMaxOOP = [9195., 8700., 9000.]
FamilyMaxOOP = [18390., 17400., 18000.]


# Average number of medical visits per year
PCPavgNumVisits = 12
SpecialistAvgNumVisits = 4
UrgentCareAvgNumVisits = 1
MentalHealthAvgNumVisits = 12

# Average number of prescriptions per year
NumRx = 12
# Average number of X-rays and diagnostic imaging per year
NumImaging = 0
# Average number of labs per year
NumLabs = 4

# Output Directory
OutDir = './'

# Flags
TotalCostWithIndividualExpenses = True
TotalCostWithFamilyExpenses = True

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

# Compute total cost of medical visit copays, Rx, imaging, labs using average numbers per year
# Note: if a plan has a "coinsurance rate after deductible" instead of a set fee, the cost for that item will
# be computed below when computing overall medical costs (since it will depend on total medical spend and
# whether deductible has been met or not)

NumPlans = len(PlanNames)

TotalCostCopaysRxImagingLabs = np.zeros(NumPlans)

for ct in range(NumPlans):
    TotalCostCopaysRxImagingLabs[ct] += PCPavgNumVisits * PCPcopays[ct]
    TotalCostCopaysRxImagingLabs[ct] += SpecialistAvgNumVisits * SpecialistCopays[ct]
    TotalCostCopaysRxImagingLabs[ct] += UrgentCareAvgNumVisits * UrgentCareCopays[ct]
    TotalCostCopaysRxImagingLabs[ct] += MentalHealthAvgNumVisits * MentalHealthCopays[ct]

    TotalCostCopaysRxImagingLabs[ct] += NumRx * GenericRx[ct]
    if ImagingCopay[ct] is not np.nan:
        TotalCostCopaysRxImagingLabs[ct] += NumImaging * ImagingCopay[ct]
    if LabCopays[ct] is not np.nan:
        TotalCostCopaysRxImagingLabs[ct] += NumLabs * LabCopays[ct]

#############################################################################################################

# Compute total cost of each plan across a range of medical spending beyond medical visit copays, Rx,
# imaging, labs - for an individual within the family
if TotalCostWithIndividualExpenses:

    BaseCost = np.zeros(NumPlans)
    for ct in range(NumPlans):
        BaseCost[ct] = Premiums[ct] * 12. + TotalCostCopaysRxImagingLabs[ct]

    # Fortunately the remaining medical services like ER, outpatient, and inpatient have the same coinsurance
    # rates in this scenario, but if they are different, will need to differentiate with multiple plots somehow
    # CoinsuranceRates = copy.deepcopy(OutpatientCoinsuranceRates)

    Expense = np.arange(0.,30000.,10.)
    TotalCost = np.zeros((NumPlans,len(Expense)))

    for ct1 in range(NumPlans):
        for ct2 in range(0,len(Expense)):

            # Initialize
            TotalCost[ct1,ct2] = BaseCost[ct1]
            ExpenseAugmented = Expense[ct2]

            # if imaging / labs based on deductible instead of set fees, add to medical expense value here
            # Assumes the coinsurance rate for imaging and labs is the same as the other major medical expenses
            # (otherwise gets complicated - which expense counts towards the deductible first?)
            if ImagingCoinsuranceRates[ct1] is not np.nan:
                ExpenseAugmented += ImagingCashPrice * NumImaging
            if LabCoinsuranceRates[ct1] is not np.nan:
                ExpenseAugmented += LabCashPrice * NumLabs

            # If below deductible - full cost of medical expense must be paid
            if ExpenseAugmented < IndividualDeductibles[ct1]:
                TotalCost[ct1,ct2] += ExpenseAugmented
            else:
                # You've reached deductible, so pay coinsurance rate on subsequent expenses
                TotalCost[ct1,ct2] += IndividualDeductibles[ct1]

                AmountOverDeductible = ExpenseAugmented - IndividualDeductibles[ct1]
                Coinsurance = CoinsuranceRates[ct1] * AmountOverDeductible
                TotalCost[ct1,ct2] += Coinsurance

                # and cut off if at max OOP
                # while copays & other set fees do not count toward deductible, they do count towards max OOP
                if ((TotalCostCopaysRxImagingLabs[ct1] + IndividualDeductibles[ct1] + Coinsurance) >=
                        IndividualMaxOOP[ct1]):
                    TotalCost[ct1,ct2] = Premiums[ct1] * 12. + IndividualMaxOOP[ct1]

    NumPlots = 3
    PlotLabelArray = copy.deepcopy(PlanNames)
    PlotColorArray = ['r','b','g'] #,'c','m','k','limegreen','saddlebrown','orange'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Expense/1000.,
         'DepData': TotalCost/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(TotalCost/1000.)+1.5,
         'xmin': Expense[0]/1000., 'xmax': Expense[-1]/1000.,
         'ylabel': 'Total Out of Pocket Cost [$K]',
         'xlabel': 'Medical Expenses (E.g., Hospital Stays) \nBeyond Set Fee Services (E.g., Copays) [$K]',
         'TitleText': 'Total Out of Pocket Cost vs \nMedical Expenses for Individual',
         'LegendLoc': 'center right', #'upper right', #'center left', #'upper center', #
         'AddTextBox': False,
         'SaveFile': OutDir+'TotalCostWithIndividualExpenses.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute total cost of each plan across a range of medical spending beyond medical visit copays, Rx,
# imaging, labs - for the entire family
if TotalCostWithFamilyExpenses:

    BaseCost = np.zeros(NumPlans)
    for ct in range(NumPlans):
        BaseCost[ct] = Premiums[ct] * 12. + TotalCostCopaysRxImagingLabs[ct]

    # Fortunately the remaining medical services like ER, outpatient, and inpatient have the same coinsurance
    # rates in this scenario, but if they are different, will need to differentiate with multiple plots somehow
    # CoinsuranceRates = copy.deepcopy(OutpatientCoinsuranceRates)

    Expense = np.arange(0.,60000.,10.)
    TotalCost = np.zeros((NumPlans,len(Expense)))

    for ct1 in range(NumPlans):
        for ct2 in range(0,len(Expense)):

            # Initialize
            TotalCost[ct1,ct2] = BaseCost[ct1]
            ExpenseAugmented = Expense[ct2]

            # if imaging / labs based on deductible instead of set fees, add to medical expense value here
            # Assumes the coinsurance rate for imaging and labs is the same as the other major medical expenses
            # (otherwise gets complicated - which expense counts towards the deductible first?)
            if ImagingCoinsuranceRates[ct1] is not np.nan:
                ExpenseAugmented += ImagingCashPrice * NumImaging
            if LabCoinsuranceRates[ct1] is not np.nan:
                ExpenseAugmented += LabCashPrice * NumLabs

            # If below deductible - full cost of medical expense must be paid
            if ExpenseAugmented < FamilyDeductibles[ct1]:
                TotalCost[ct1,ct2] += ExpenseAugmented
            else:
                # You've reached deductible, so pay coinsurance rate on subsequent expenses
                TotalCost[ct1,ct2] += FamilyDeductibles[ct1]

                AmountOverDeductible = ExpenseAugmented - FamilyDeductibles[ct1]
                Coinsurance = CoinsuranceRates[ct1] * AmountOverDeductible
                TotalCost[ct1,ct2] += Coinsurance

                # and cut off if at max OOP
                # while copays & other set fees do not count toward deductible, they do count towards max OOP
                if ((TotalCostCopaysRxImagingLabs[ct1] + FamilyDeductibles[ct1] + Coinsurance) >=
                        FamilyMaxOOP[ct1]):
                    TotalCost[ct1,ct2] = Premiums[ct1] * 12. + FamilyMaxOOP[ct1]

    NumPlots = 3
    PlotLabelArray = copy.deepcopy(PlanNames)
    PlotColorArray = ['r','b','g'] #,'c','m','k','limegreen','saddlebrown','orange'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': Expense/1000.,
         'DepData': TotalCost/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.nanmax(TotalCost/1000.)+1.5,
         'xmin': Expense[0]/1000., 'xmax': Expense[-1]/1000.,
         'ylabel': 'Total Out of Pocket Cost [$K]',
         'xlabel': 'Medical Expenses (E.g., Hospital Stays) \nBeyond Set Fee Services (E.g., Copays) [$K]',
         'TitleText': 'Total Out of Pocket Cost vs \nMedical Expenses for Family',
         'LegendLoc': 'center right', #'upper right', #'center left', #'upper center', #
         'AddTextBox': False,
         'SaveFile': OutDir+'TotalCostWithFamilyExpenses.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################