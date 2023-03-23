# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-compute-aca-obamacare-subsidies/)

# ACAsubsidiesTemplate.py

import numpy as np
import copy
import os

from ComputeSubsidy import *
from Multiplot import *
from TaxRateInfoInput import *
from ComputeTaxes import *

# Compute ACA subsidies, plot results

#############################################################################################################
# User Inputs

# Number of people in household
NumPeople = 4.

# Household income - Modified Adjusted Gross Income (MAGI) (after deductions like retirement account contributions and
# health insurance premiums, but before standard deduction)
Income = 63000.

# Annual cost of benchmark plan (second-cheapest Silver level plan in your area and for your situation)
BenchmarkPrice = 1458.76*12.

Residence = 'Contiguous' #'Alaska' #'Hawaii' #

# Output Directory
OutDir = './'

# Plot flags
SubsidiesVsIncome = False
ScaledSubsidiesVsIncome = False
ConsumerPaymentVsIncome = False
ScaledConsumerPaymentVsIncome = False

SubsidyLossRateVsIncome = True
FedIncomeTaxRateVsIncome = True
SubsidyLossRatePlusFedIncomeTaxRateVsIncome = True

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Single situation
AnnualSubsidy = ComputeSubsidy(Income,NumPeople,Residence,BenchmarkPrice)

print('Annual Subsidy: $'+'{:.2f}'.format(np.round(AnnualSubsidy,2)))
print('Monthly Subsidy: $'+'{:.2f}'.format(np.round(AnnualSubsidy/12.,2)))

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
     'PlotSecondaryLines': False}

#############################################################################################################

# Compute and Plot subsidies as function of income for variety of family sizes
if SubsidiesVsIncome:
    
    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.
    
    # Provide benchmark prices for each family size considered (1 through 5)
    BenchmarkPriceArray = np.array([454.,902.,1180.,1459.,1737.])*12.
    FamilySizeArray = np.array([1.,2.,3.,4.,5.])
    IncomeArray = np.arange(MinIncome,MaxIncome,1000.)
    AnnualSubsidyArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))

    # Loop over family sizes
    for ct1 in range(len(FamilySizeArray)):
        # Loop over income
        for ct2 in range(len(IncomeArray)):
            AnnualSubsidyArray[ct1,ct2] = ComputeSubsidy(IncomeArray[ct2],FamilySizeArray[ct1],Residence,BenchmarkPriceArray[ct1])

    NumPlots = 5 # number of family sizes

    PlotLabelArray = ['1 person, $'+'{:.1f}'.format(454.*12./1000.)+'K/yr Benchmark',
                      '2 people, $'+'{:.1f}'.format(902.*12./1000.)+'K/yr Benchmark',
                      '3 people, $'+'{:.1f}'.format(1180.*12./1000.)+'K/yr Benchmark',
                      '4 people, $'+'{:.1f}'.format(1459.*12./1000.)+'K/yr Benchmark',
                      '5 people, $'+'{:.1f}'.format(1737.*12./1000.)+'K/yr Benchmark']
    PlotColorArray = ['k','r','b','g','c'] #,'m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': AnnualSubsidyArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(AnnualSubsidyArray/1000.) + 1.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Annual Subsidy [$K]',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Subsidies vs Income, for 5 Family Sizes',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AnnualSubsidiesVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Monthly subsidies
    PlotLabelArray = ['1 person, $'+'{:.0f}'.format(454.)+'/mo Benchmark',
                      '2 people, $'+'{:.0f}'.format(902.)+'/mo Benchmark',
                      '3 people, $'+'{:.0f}'.format(1180.)+'/mo Benchmark',
                      '4 people, $'+'{:.0f}'.format(1459.)+'/mo Benchmark',
                      '5 people, $'+'{:.0f}'.format(1737.)+'/mo Benchmark']
    UpdateDict = \
        {'DepData': AnnualSubsidyArray/12.,
         'ymax': np.max(AnnualSubsidyArray/12.) + 100.,
         'ylabel': 'Monthly Subsidy [$]',
         'PlotLabelArray': PlotLabelArray,
         'SaveFile': OutDir+'MonthlySubsidiesVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and Plot subsidies scaled by benchmark price, as function of income for variety of family sizes
if ScaledSubsidiesVsIncome:

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.

    # Provide benchmark prices for each family size considered (1 through 5)
    BenchmarkPriceArray = np.array([454.,902.,1180.,1459.,1737.])*12.
    FamilySizeArray = np.array([1.,2.,3.,4.,5.])
    IncomeArray = np.arange(MinIncome,MaxIncome,1000.)
    AnnualScaledSubsidyArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))

    # Loop over family sizes
    for ct1 in range(len(FamilySizeArray)):
        # Loop over income
        for ct2 in range(len(IncomeArray)):
            AnnualScaledSubsidyArray[ct1,ct2] = ComputeSubsidy(IncomeArray[ct2], FamilySizeArray[ct1], Residence,
                                                               BenchmarkPriceArray[ct1]) / (BenchmarkPriceArray[ct1])

    NumPlots = 5 # number of family sizes
    PlotLabelArray = ['1 person','2 people','3 people','4 people','5 people']
    PlotColorArray = ['k','r','b','g','c'] #,'m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': AnnualScaledSubsidyArray*100.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 105.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Subsidy % Of Benchmark Rate',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Subsidy % Of Benchmark Rate vs Income',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'ScaledSubsidiesVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and Plot consumer payment after subsidies as function of income for variety of family sizes
if ConsumerPaymentVsIncome:

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.

    # Provide benchmark prices for each family size considered (1 through 5)
    BenchmarkPriceArray = np.array([454.,902.,1180.,1459.,1737.])*12.
    FamilySizeArray = np.array([1.,2.,3.,4.,5.])
    IncomeArray = np.arange(MinIncome,MaxIncome,1000.)
    AnnualSubsidyArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))
    ConsumerPaymentArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))

    # Loop over family sizes
    for ct1 in range(len(FamilySizeArray)):
        # Loop over income
        for ct2 in range(len(IncomeArray)):
            AnnualSubsidyArray[ct1,ct2] = ComputeSubsidy(IncomeArray[ct2], FamilySizeArray[ct1], Residence, 
                                                         BenchmarkPriceArray[ct1])
            ConsumerPaymentArray[ct1,ct2] = BenchmarkPriceArray[ct1] - AnnualSubsidyArray[ct1,ct2]

    NumPlots = 5 # number of family sizes

    PlotLabelArray = ['1 person, $'+'{:.1f}'.format(454.*12./1000.)+'K/yr Benchmark',
                      '2 people, $'+'{:.1f}'.format(902.*12./1000.)+'K/yr Benchmark',
                      '3 people, $'+'{:.1f}'.format(1180.*12./1000.)+'K/yr Benchmark',
                      '4 people, $'+'{:.1f}'.format(1459.*12./1000.)+'K/yr Benchmark',
                      '5 people, $'+'{:.1f}'.format(1737.*12./1000.)+'K/yr Benchmark']
    PlotColorArray = ['k','r','b','g','c'] #,'m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': ConsumerPaymentArray/1000.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(ConsumerPaymentArray/1000.) + 1.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Annual Consumer Payment After Subsidy [$K]',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Consumer Payment vs Income',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AnnualConsumerPaymentVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    # Monthly subsidies
    PlotLabelArray = ['1 person, $'+'{:.0f}'.format(454.)+'/mo Benchmark',
                      '2 people, $'+'{:.0f}'.format(902.)+'/mo Benchmark',
                      '3 people, $'+'{:.0f}'.format(1180.)+'/mo Benchmark',
                      '4 people, $'+'{:.0f}'.format(1459.)+'/mo Benchmark',
                      '5 people, $'+'{:.0f}'.format(1737.)+'/mo Benchmark']
    UpdateDict = \
        {'DepData': ConsumerPaymentArray/12.,
         'ymax': np.max(ConsumerPaymentArray/12.) + 100.,
         'ylabel': 'Monthly Consumer Payment After Subsidy [$]',
         'PlotLabelArray': PlotLabelArray,
         'SaveFile': OutDir+'MonthlyConsumerPaymentVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and Plot consumer payment after subsidies, scaled by benchmark price, as function of income for variety of family sizes
if ScaledConsumerPaymentVsIncome:

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.

    # Provide benchmark prices for each family size considered (1 through 5)
    BenchmarkPriceArray = np.array([454.,902.,1180.,1459.,1737.])*12.
    FamilySizeArray = np.array([1.,2.,3.,4.,5.])
    IncomeArray = np.arange(MinIncome,MaxIncome,1000.)
    AnnualSubsidyArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))
    ScaledConsumerPaymentArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))

    # Loop over family sizes
    for ct1 in range(len(FamilySizeArray)):
        # Loop over income
        for ct2 in range(len(IncomeArray)):
            AnnualSubsidyArray[ct1,ct2] = ComputeSubsidy(IncomeArray[ct2], FamilySizeArray[ct1], Residence,
                                                         BenchmarkPriceArray[ct1])
            ScaledConsumerPaymentArray[ct1,ct2] = (BenchmarkPriceArray[ct1] - AnnualSubsidyArray[ct1,ct2]) / \
                                                  BenchmarkPriceArray[ct1]

    NumPlots = 5 # number of family sizes

    PlotLabelArray = ['1 person','2 people','3 people','4 people','5 people']
    PlotColorArray = ['k','r','b','g','c'] #,'m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': ScaledConsumerPaymentArray*100.,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': 105.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Consumer Payment % Of Benchmark Rate',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Percent You Pay Of Benchmark Rate vs Income',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'ScaledConsumerPaymentVsIncome.png'}

    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


#############################################################################################################

# Compute and Plot instantaneous and cumulative subsidy loss rate vs income
if SubsidyLossRateVsIncome:

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000. 

    # Provide benchmark prices for each family size considered (1 through 5)
    BenchmarkPriceArray = np.array([454.,902.,1180.,1459.,1737.])*12.
    FamilySizeArray = np.array([1.,2.,3.,4.,5.])
    IncomeArray = np.arange(MinIncome,MaxIncome,100.)
    AnnualSubsidyArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))
    ConsumerPaymentArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))
    InstantaneousSubsidyLossRateArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))
    CumulativeSubsidyLossRateArray = np.zeros((len(FamilySizeArray),len(IncomeArray)))

    # Loop over family sizes
    for ct1 in range(len(FamilySizeArray)):
        # Starting flag and index for cumulative rate
        CumulativeStartFlag = np.zeros(len(FamilySizeArray),dtype=bool)
        StartingInd = np.zeros(len(FamilySizeArray),dtype=int)
        # Loop over income
        for ct2 in range(len(IncomeArray)):

            AnnualSubsidyArray[ct1,ct2] = ComputeSubsidy(IncomeArray[ct2],FamilySizeArray[ct1],Residence,
                                                         BenchmarkPriceArray[ct1])
            ConsumerPaymentArray[ct1,ct2] = BenchmarkPriceArray[ct1] - AnnualSubsidyArray[ct1,ct2]
            if ct2 > 0:
                InstantaneousSubsidyLossRateArray[ct1,ct2] = (ConsumerPaymentArray[ct1,ct2] -
                                                              ConsumerPaymentArray[ct1,ct2-1]) / \
                                                             (IncomeArray[ct2] - IncomeArray[ct2-1])*100.

                # Determine when to start cumulative calculation - start when 100% FPL reached and subsidies kick in
                if ConsumerPaymentArray[ct1,ct2-1] == 0 and CumulativeStartFlag[ct1] == False:
                    CumulativeStartFlag[ct1] = True
                    StartingInd[ct1] = ct2-1
                if CumulativeStartFlag[ct1] == True:
                    CumulativeSubsidyLossRateArray[ct1,ct2] = (ConsumerPaymentArray[ct1,ct2] -
                                                               ConsumerPaymentArray[ct1,StartingInd[ct1]]) / \
                                                              (IncomeArray[ct2] - IncomeArray[StartingInd[ct1]])*100.

    NumPlots = 5 # number of family sizes

    PlotLabelArray = ['1 person, $'+'{:.0f}'.format(454.)+'/mo Benchmark',
                      '2 people, $'+'{:.0f}'.format(902.)+'/mo Benchmark',
                      '3 people, $'+'{:.0f}'.format(1180.)+'/mo Benchmark',
                      '4 people, $'+'{:.0f}'.format(1459.)+'/mo Benchmark',
                      '5 people, $'+'{:.0f}'.format(1737.)+'/mo Benchmark']

    PlotColorArray = ['k','r','b','g','c'] #,'m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': InstantaneousSubsidyLossRateArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(InstantaneousSubsidyLossRateArray) + 1.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000., #'xmin': IncomeArray[0]/1000.
         'ylabel': 'Instantaneous ACA Subsidy Loss Rate [%]',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Instantaneous ACA Subsidy Loss Rate vs Income',
         'LegendLoc': 'lower right', #'upper right',
         'SaveFile': OutDir+'InstantaneousSubsidyLossRateVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

    UpdateDict = \
        {'DepData': CumulativeSubsidyLossRateArray,
         'ymin': 0., 'ymax': np.max(CumulativeSubsidyLossRateArray) + 1.,
         'ylabel': 'Cumulative ACA Subsidy Loss Rate [%]',
         'TitleText': 'Cumulative ACA Subsidy Loss Rate vs Income',
         'SaveFile': OutDir+'CumulativeSubsidyLossRateVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and Plot federal income tax rate for each filing status vs income
if FedIncomeTaxRateVsIncome:

    # Bring in 2023 income tax bracket info, used for inputs (modify if beyond 2023)
    TaxRateInfo = TaxRateInfoInput()

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.
    
    # Filing status options
    FilingStatusOptions = ['Single','HeadOfHousehold','MarriedFilingJointly']
    # Married Filing Separately is identical to Single until an income of $346,875 - well past the edge of this plot

    # Initialize arrays
    IncomeArray = np.arange(MinIncome,MaxIncome,100.)
    FedIncomeTaxRateArray = np.zeros((len(FilingStatusOptions),len(IncomeArray)))

    # Loop over filing status options
    for ct1 in range(len(FilingStatusOptions)):
        # Loop over income
        for ct2 in range(len(IncomeArray)):
            # Compute Taxes
            # assume only standard income, no LTCG, for simplicity
            TaxesDict = ComputeTaxes(TaxRateInfo,FilingStatusOptions[ct1],IncomeArray[ct2],0.)
            FedIncomeTaxRateArray[ct1,ct2] = TaxesDict['StdIncTopTaxBracketRate']*100.

    NumPlots = 3 # number of filing status options

    PlotLabelArray = ['Single','Head Of Household','Married Filing Jointly']

    PlotColorArray = ['r','g','b'] #,'m','limegreen','c' 'k',

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': FedIncomeTaxRateArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(FedIncomeTaxRateArray) + 1.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Top Federal Income Tax Rate [%]',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Top Federal Income Tax Rate vs Income',
         'LegendLoc': 'upper right', #'lower right', #
         'SaveFile': OutDir+'FedIncomeTaxRateVsIncome.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Compute and plot the SUM of subsidy loss rate and federal income tax rate for single and married scenarios vs income
if SubsidyLossRatePlusFedIncomeTaxRateVsIncome:

    # Bring in 2023 income tax bracket info, used for inputs (modify if beyond 2023)
    TaxRateInfo = TaxRateInfoInput()

    MinIncome = 13590. # FPL for single person in contiguous US - lowest possible income to get subsidies
    MaxIncome = 200000.
    # IncomeArray = np.arange(MinIncome,MaxIncome,1000.)
    IncomeArray = np.arange(MinIncome,MaxIncome,100.)

    # Single scenario: Filing status = 'Single', Family size for ACA = 1
    FamilySize = 1.
    BenchmarkPrice = 454.*12.

    # Initialize arrays
    FedIncomeTaxRateArray = np.zeros(len(IncomeArray))
    AnnualSubsidyArray = np.zeros(len(IncomeArray))
    ConsumerPaymentArray = np.zeros(len(IncomeArray))
    InstantaneousSubsidyLossRateArray = np.zeros(len(IncomeArray))

    # Loop over income
    for ct in range(len(IncomeArray)):
        # Compute federal income taxes
        # assume only standard income, no LTCG, for simplicity
        TaxesDict = ComputeTaxes(TaxRateInfo,'Single',IncomeArray[ct],0.)
        FedIncomeTaxRateArray[ct] = TaxesDict['StdIncTopTaxBracketRate']*100.

        # Compute subsidy loss rate
        AnnualSubsidyArray[ct] = ComputeSubsidy(IncomeArray[ct],FamilySize,Residence,BenchmarkPrice)
        ConsumerPaymentArray[ct] = BenchmarkPrice - AnnualSubsidyArray[ct]
        if ct > 0:
            InstantaneousSubsidyLossRateArray[ct] = (ConsumerPaymentArray[ct] - ConsumerPaymentArray[ct-1]) / \
                                                    (IncomeArray[ct] - IncomeArray[ct-1])*100.

    TotalRateArray = FedIncomeTaxRateArray + InstantaneousSubsidyLossRateArray

    NumPlots = 3
    DepDataArray = np.zeros((NumPlots,len(FedIncomeTaxRateArray)))
    DepDataArray[0,:] = FedIncomeTaxRateArray
    DepDataArray[1,:] = InstantaneousSubsidyLossRateArray
    DepDataArray[2,:] = TotalRateArray

    PlotLabelArray = ['Marginal Federal Income Tax Rate','Instantaneous ACA Subsidy Loss Rate','Total "Tax" Rate']
    PlotColorArray = ['m','limegreen','k'] #, 'r','g','b','c'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': IncomeArray/1000.,
         'DepData': DepDataArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(DepDataArray) + 1.,
         'xmin': 0., 'xmax': IncomeArray[-1]/1000.,
         'ylabel': 'Tax/Loss Rates [%]',
         'xlabel': 'Annual Income [$K]',
         'TitleText': 'Tax/Loss Rates vs Income - Single Person',
         'LegendLoc': 'center right', #'upper right', #'lower right', #
         'SaveFile': OutDir+'SubsidyLossRatePlusFedIncomeTaxRateVsIncomeSingle.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


    # Married scenario: Filing status = 'MarriedFilingJointly', Family size for ACA = 4
    FamilySize = 4.
    BenchmarkPrice = 1459.*12.

    # Initialize arrays
    FedIncomeTaxRateArray = np.zeros(len(IncomeArray))
    AnnualSubsidyArray = np.zeros(len(IncomeArray))
    ConsumerPaymentArray = np.zeros(len(IncomeArray))
    InstantaneousSubsidyLossRateArray = np.zeros(len(IncomeArray))

    # Loop over income
    for ct in range(len(IncomeArray)):
        # Compute federal income taxes
        # assume only standard income, no LTCG, for simplicity
        TaxesDict = ComputeTaxes(TaxRateInfo,'MarriedFilingJointly',IncomeArray[ct],0.)
        FedIncomeTaxRateArray[ct] = TaxesDict['StdIncTopTaxBracketRate']*100.

        # Compute subsidy loss rate
        AnnualSubsidyArray[ct] = ComputeSubsidy(IncomeArray[ct],FamilySize,Residence,BenchmarkPrice)
        ConsumerPaymentArray[ct] = BenchmarkPrice - AnnualSubsidyArray[ct]
        if ct > 0:
            InstantaneousSubsidyLossRateArray[ct] = (ConsumerPaymentArray[ct] - ConsumerPaymentArray[ct-1]) / \
                                                    (IncomeArray[ct] - IncomeArray[ct-1])*100.

    TotalRateArray = FedIncomeTaxRateArray + InstantaneousSubsidyLossRateArray

    DepDataArray = np.zeros((NumPlots,len(FedIncomeTaxRateArray)))
    DepDataArray[0,:] = FedIncomeTaxRateArray
    DepDataArray[1,:] = InstantaneousSubsidyLossRateArray
    DepDataArray[2,:] = TotalRateArray

    # Specify unique plot values
    UpdateDict = \
        {'DepData': DepDataArray,
         'ymax': np.max(DepDataArray) + 1.,
         'TitleText': 'Tax/Loss Rates vs Income - Family of 4',
         'LegendLoc': 'lower right', #'center right', #'upper right', #
         'SaveFile': OutDir+'SubsidyLossRatePlusFedIncomeTaxRateVsIncomeFamilyOf4.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)


