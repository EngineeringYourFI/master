# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/the-irs-wont-wait-forever-required-minimum-distributions/)

# ReqMinDistTemplate.py

import numpy as np
import copy
import os
from TaxRateInfoInput import TaxRateInfoInput
from MultiPlot import MultiPlot
from ProjWithRMDs import ProjWithRMDs

# Driver for employing method to compute required minimum distribution for a given age and pretax asset value

#############################################################################################################
# Inputs

# Bring in 2022 income tax bracket info, used for inputs (modify if beyond 2022)
TaxRateInfo = TaxRateInfoInput()

# Pre-tax assets initial value
PreTaxIV = 1000000.0 #0.
PostTaxIV = 0. #1000000.

# Retirement Income
# Social security - taxed different, so don't place in OtherIncomeSources
SocialSecurityPayments = np.array([20000], dtype=float) #,20000

# Retirement Expenses - in current year dollars, as is everything else in this simulation
Exp = 40000.

NumYearsToProject = 20 # so from age 72 to 92
FilingStatus = 'Single' # 'MarriedFilingJointly' # 'HeadOfHousehold' # 'MarriedFilingSeparately' # 'QualifyingWidow(er)'

# Annual investment interest rate (i.e. expected investment return)
R = 0.07

# Output Directory
OutDir = './'
# Output file
OutputFile = 'Output.txt'

# Processing flags
ProjectWithRMDsingleRun = True
FinalBalanceVsFractionPretax = True

# Plot flags
PrintSingleRun = True # Only if ProjectWithRMDsingleRun = True
AssetBalancesVsAge = True # Only if ProjectWithRMDsingleRun = True
YearlyValuesVsAge = True # Only if ProjectWithRMDsingleRun = True
ReqWR = True # Only if ProjectWithRMDsingleRun = True
PlotFinalBalanceVsFractionPretax = True # Only if FinalBalanceVsFractionPretax = True
PlotTotalTaxesVsFractionPretax = True # Only if FinalBalanceVsFractionPretax = True
PlotTotalRMDsVsFractionPretax = True # Only if FinalBalanceVsFractionPretax = True

#############################################################################################################

# Capturing inputs in relevant dictionaries

IVdict = {'PreTaxIV': PreTaxIV,
          'PostTaxIV': PostTaxIV}

IncDict = {'SocialSecurityPayments': SocialSecurityPayments}

ExpDict = {'Exp': Exp}

#############################################################################################################

# Default plotting parameters, using dictionary (can modify if needed)
DefaultPlotDict = \
    {'FigWidth': 10.8, 'FigHeight': 10.8,
     'LineStyle': '-', 'LineWidth': 3,
     'MarkerSize': 10,
     'CopyrightX': 0.01, 'CopyrightY': 1-0.01, 'CopyrightText': 'EngineeringYourFI.com', 'CopyrightFontSize': 20,
     'CopyrightVertAlign': 'top',
     'ylabelFontSize': 30, 'xlabelFontSize': 30,
     'Title_yoffset': 1.04, 'TitleFontSize': 32,
     'LegendLoc': 'best', 'LegendFontSize': 20,
     'PlotSecondaryLines': False}

#############################################################################################################

# Check if directory (e.g. save directory) exists - if not, create. if so, output message and quit
if not os.path.exists(OutDir):
    os.makedirs(OutDir)

#############################################################################################################

# Project forward by NumYearsToProject with RMDs
if ProjectWithRMDsingleRun:
    ProjArrays = ProjWithRMDs(NumYearsToProject,IVdict,SocialSecurityPayments,TaxRateInfo,FilingStatus,Exp,R)

#############################################################################################################

# Print relevant numbers to output file (e.g. final asset values, etc.)
if PrintSingleRun:
    file=open(OutputFile,'w')
    file.write('ReqMinDist.py\n\n')

    file.write('PreTax Initial: $'+'{:.2f}'.format(IVdict['PreTaxIV'])+'\n')
    file.write('PostTax Initial: $'+'{:.2f}'.format(IVdict['PostTaxIV'])+'\n')
    file.write('Total Initial: $'+'{:.2f}'.format(IVdict['PreTaxIV']+IVdict['PostTaxIV'])+'\n\n')

    file.write('PreTax Final: $'+'{:.2f}'.format(ProjArrays['PreTax'][-1])+'\n')
    file.write('PostTax Final: $'+'{:.2f}'.format(ProjArrays['PostTax'][-1])+'\n')
    file.write('Total Final: $'+'{:.2f}'.format(ProjArrays['TotalAssets'][-1])+'\n\n')

    file.write('Taxes Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Taxes']))+'\n')

    file.close()

#############################################################################################################

# Plot nominal run results
if AssetBalancesVsAge:

    NumPlots = 3 # PreTax,PostTax,TotalAssets
    AssetsArray = np.zeros((NumPlots,len(ProjArrays['TotalAssets'])))
    AssetsArray[0,:] = ProjArrays['PreTax']/1.e6
    AssetsArray[1,:] = ProjArrays['PostTax']/1.e6
    AssetsArray[2,:] = ProjArrays['TotalAssets']/1.e6

    PlotLabelArray = ['PreTax','PostTax','Total, Final $'+'{:.3f}M'.format(ProjArrays['TotalAssets'][-1]/1.e6)]
    PlotColorArray = ['b','r','k'] #,'g','c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'],
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ProjArrays['TotalAssets']/1.e6)+1.,
         'xmin': ProjArrays['Age'][0], 'xmax': ProjArrays['Age'][-1],
         'ylabel': 'Asset Balance [2022 $M]',
         'xlabel': 'Age',
         'TitleText': 'Asset Balances vs Age with RMDs',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'AssetBalancesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot yearly results
if YearlyValuesVsAge:

    # RMD, TotalSS, TaxableSSincome, TotalStandardIncome, TotalCash, Expenses, Taxes

    NumPlots = 7
    ValuesArray = np.zeros((NumPlots,NumYearsToProject))
    ValuesArray[0,:] = ProjArrays['RMD']/1000.
    ValuesArray[1,:] = ProjArrays['TotalSS']/1000.
    ValuesArray[2,:] = ProjArrays['TaxableSSincome']/1000.
    ValuesArray[3,:] = ProjArrays['TotalStandardIncome']/1000.
    ValuesArray[4,:] = ProjArrays['TotalCash']/1000.
    ValuesArray[5,:] = Exp*np.ones(NumYearsToProject)/1000.
    ValuesArray[6,:] = ProjArrays['Taxes']/1000.

    PlotLabelArray = ['RMDs','Total SSI','Taxable SSI','TotalStandardIncome','TotalCash','Expenses','Taxes']
    PlotColorArray = ['k','r','b','g','c','m','y'] #,'limegreen','fuchsia'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArrays['Age'][0], 'xmax': ProjArrays['Age'][-1],
         'ylabel': 'Yearly Values [2022 $K]',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values vs Age',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'YearlyValuesVsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Plot required withdrawal rates
if ReqWR:

    NumPlots = 1
    ValuesArray = np.zeros((NumPlots,NumYearsToProject))
    ValuesArray[0,:] = ProjArrays['WR']

    PlotLabelArray = ['Required Withdrawal Rate']
    PlotColorArray = ['k'] #,'r','b','g','c','m','y','limegreen','fuchsia'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': ProjArrays['Age'],
         'DepData': ValuesArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(ValuesArray)+1.,
         'xmin': ProjArrays['Age'][0], 'xmax': ProjArrays['Age'][-1],
         'ylabel': 'Required Withdrawal Rate (%)',
         'xlabel': 'Age',
         'TitleText': 'Yearly Values vs Age',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'WRvsAge.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Varying the pretax vs posttax amounts by $1K increments from $1M and $0 to $0 and $1M

if FinalBalanceVsFractionPretax:

    PreTaxIVarray = np.arange(0.,1000000.,1000.)
    PostTaxIVarray = 1000000. - PreTaxIVarray
    TotalAssetsArray = np.zeros(len(PreTaxIVarray))
    TotalTaxesArray = np.zeros(len(PreTaxIVarray))
    TotalRMDarray = np.zeros(len(PreTaxIVarray))
    PreTaxIVpercentage = np.zeros(len(PreTaxIVarray))

    for ct in range(0,len(PreTaxIVarray)):

        IVdict['PreTaxIV'] = PreTaxIVarray[ct]
        IVdict['PostTaxIV'] = PostTaxIVarray[ct]
        PreTaxIVpercentage[ct] = np.round(PreTaxIVarray[ct]/PreTaxIVarray[-1]*100,2)

        ProjArrays = ProjWithRMDs(NumYearsToProject,IVdict,SocialSecurityPayments,TaxRateInfo,FilingStatus,Exp,R)

        TotalAssetsArray[ct] = ProjArrays['TotalAssets'][-1]
        TotalTaxesArray[ct] = np.sum(ProjArrays['Taxes'])
        TotalRMDarray[ct] = np.sum(ProjArrays['RMD'])

# Plot the total final balance for each increment
if PlotFinalBalanceVsFractionPretax:

    NumPlots = 1 # TotalAssetsArray
    AssetsArray = np.zeros((NumPlots,len(TotalAssetsArray)))
    AssetsArray[0,:] = TotalAssetsArray/1.e6

    PlotLabelArray = ['Total Assets']
    PlotColorArray = ['k'] #'b','r',,'g','c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': PreTaxIVpercentage,
         'DepData': AssetsArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': np.min(TotalAssetsArray/1.e6)-0.05, 'ymax': np.max(TotalAssetsArray/1.e6)+0.05,
         'xmin': PreTaxIVpercentage[0], 'xmax': PreTaxIVpercentage[-1],
         'ylabel': 'Asset Balance [2022 $M]',
         'xlabel': '% Of Initial $1M Portfolio as Pre-Tax',
         'TitleText': 'Final Total Asset Balance vs \n Initial % as Pre-Tax, with RMDs',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'FinalTotalAssetBalanceVsPreTaxIVpercent.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

# Plot the total taxes for each increment
if PlotTotalTaxesVsFractionPretax:

    NumPlots = 1 # TotalAssetsArray
    TaxesPlotArray = np.zeros((NumPlots,len(TotalTaxesArray)))
    TaxesPlotArray[0,:] = TotalTaxesArray/1.e3

    PlotLabelArray = ['Total Taxes']
    PlotColorArray = ['k'] #'b','r',,'g','c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': PreTaxIVpercentage,
         'DepData': TaxesPlotArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(TotalTaxesArray/1.e3)+1,
         'xmin': PreTaxIVpercentage[0], 'xmax': PreTaxIVpercentage[-1],
         'ylabel': 'Total Taxes [2022 $K]',
         'xlabel': '% Of Initial $1M Portfolio as Pre-Tax',
         'TitleText': 'Total Taxes Paid vs \n Initial % as Pre-Tax, with RMDs',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'FinalTotalTaxesVsPreTaxIVpercent.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

# Plot the total RMDs for each increment
if PlotTotalRMDsVsFractionPretax:

    NumPlots = 1 # TotalAssetsArray
    RMDplotArray = np.zeros((NumPlots,len(TotalRMDarray)))
    RMDplotArray[0,:] = TotalRMDarray/1.e3

    PlotLabelArray = ['Total RMDs']
    PlotColorArray = ['k'] #'b','r',,'g','c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': PreTaxIVpercentage,
         'DepData': RMDplotArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0., 'ymax': np.max(TotalRMDarray/1.e3)+1,
         'xmin': PreTaxIVpercentage[0], 'xmax': PreTaxIVpercentage[-1],
         'ylabel': 'Total RMDs [2022 $K]',
         'xlabel': '% Of Initial $1M Portfolio as Pre-Tax',
         'TitleText': 'Total RMDs vs \n Initial % as Pre-Tax, with RMDs',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'FinalTotalRMDsVsPreTaxIVpercent.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)
