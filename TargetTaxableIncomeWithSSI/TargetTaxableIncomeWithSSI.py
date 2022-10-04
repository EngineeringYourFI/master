# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-pay-no-taxes-on-social-security-income/)

# TargetTaxableIncomeWithSSI.py

import numpy as np
import copy
import os
from SupportMethods import MultiPlot, ComputeTaxes
from TaxableIncomeTargetMethodWithSSI import TaxableIncomeTargetMethodWithSSI
from TaxableSSconsolidated import TaxableSSconsolidated

# Target a particular total taxable income (standard and perhaps also LT cap gains) when you also have Social Security
# Income (SSI)

#############################################################################################################
# Inputs

# 2022 income tax bracket info (also applies for nonqualified dividends)
# Note: can easily expand to also include Head of Household and Married Filing Seperately values in the future
Rates = np.array([0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37], dtype=float)
SingleIncomeBracketMins = np.array([0,10275,41775,89075,170050,215950,539900], dtype=float)
MarriedIncomeBracketMins = SingleIncomeBracketMins*2
MarriedIncomeBracketMins[-1] = 647850.
# 2022 standard deductions
SingleStandardDeduction = 12950.
MarriedStandardDeduction = SingleStandardDeduction*2
# 2022 long term cap gains tax bracket info (also applies for qualified dividends)
CapGainsRatesLT = np.array([0.0, 0.15, 0.2], dtype=float)
SingleIncomeBracketLTcapGainsMins = np.array([0,41675,459750], dtype=float)
MarriedIncomeBracketLTcapGainsMins = np.array([0,83350,517200], dtype=float)

# Retirement Income
# Dividends
# CurrentAnnualQualifiedDividends = 10000. # Scenario 1
# # CurrentAnnualQualifiedDividends = 5000. # Scenario 2
# also include any other sources of income you can’t easily dial up and down (e.g. a pension)
CurrentAnnualNonQualifiedDividends = 0. #100.
# Social security - taxed different, so don't place in OtherIncomeSources
SocialSecurityPayments = np.array([20000], dtype=float) # other filing status #17000
# SocialSecurityPayments = np.array([20000,20000], dtype=float) # married filing jointly # 17000,17000

# Maximum possible SSI for plotting
MaxSSI = 50000. # other filing status
# MaxSSI = 100000. # married filing jointly

# Maximum standard income to achieve (not LT cap gains)
MaxStandardIncome = SingleStandardDeduction # other filing status
# MaxStandardIncome = MarriedStandardDeduction # married filing jointly
# Targeted Income - set equal to top of 0% LT cap gains bracket nominally (includes standard income + LT cap gains)
SpecifiedIncome = SingleIncomeBracketLTcapGainsMins[1] # other filing status
# SpecifiedIncome = MarriedIncomeBracketLTcapGainsMins[1] # married filing jointly

MarriedOrOther = 'Other' # other filing statuses
# MarriedOrOther = 'Married' # married filing jointly

# Non-SSI standard income and LT cap gains that ignore how SSI is taxed (and thus ignore this targeting algorithm)
# Note: only have married filing jointly or single so far for tax rate info, so sticking with those scenarios
# includes nonqualified dividends:
NonSSInoTargeting = SingleStandardDeduction # 2985.81 # single filing status
# NonSSInoTargeting = MarriedStandardDeduction #0. # married filing jointly
# includes qualified dividends:
LTcapGainsNoTargeting = SingleIncomeBracketLTcapGainsMins[1] - SingleStandardDeduction # 28725.00 #   # single filing status
# LTcapGainsNoTargeting = MarriedIncomeBracketLTcapGainsMins[1] - MarriedStandardDeduction #50294.12 # married filing jointly
# only have married filing jointly or single so far for tax rate info
FilingStatusNoTargeting = 'Single' # Single
# FilingStatusNoTargeting = 'Married' # Married

# Output Directory
OutDir = './'
# Output file
# OutputFile = 'Output.txt'

# Section/Plot flags
TargetWithInputSectionValues = True
ComputeTaxesWithNoTargeting = True
PlotIncomeValuesVsSSI = True
PlotIncomeValuesVsSSIyaxisBuffer = 4.

#############################################################################################################

# Capturing inputs in relevant dictionaries

TaxRateInfo = {'Rates': Rates,
               'SingleIncomeBracketMins': SingleIncomeBracketMins,
               'MarriedIncomeBracketMins': MarriedIncomeBracketMins,
               'SingleStandardDeduction': SingleStandardDeduction,
               'MarriedStandardDeduction': MarriedStandardDeduction,
               'CapGainsRatesLT': CapGainsRatesLT,
               'SingleIncomeBracketLTcapGainsMins': SingleIncomeBracketLTcapGainsMins,
               'MarriedIncomeBracketLTcapGainsMins': MarriedIncomeBracketLTcapGainsMins}

IncDict = {'CurrentAnnualNonQualifiedDividends': CurrentAnnualNonQualifiedDividends,
           'SocialSecurityPayments': SocialSecurityPayments,
           'MaxStandardIncome': MaxStandardIncome,
           'SpecifiedIncome': SpecifiedIncome}
            # 'CurrentAnnualQualifiedDividends': CurrentAnnualQualifiedDividends,

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

# Compute for income and filing status provided above in inputs section
if TargetWithInputSectionValues:
    # accounting for dividends first
    TotalInitialStandardIncome = copy.deepcopy(IncDict['CurrentAnnualNonQualifiedDividends'])

    # Total SSI
    TotalSS = np.sum(IncDict['SocialSecurityPayments'])

    # Run TaxableIncomeTargetMethodWithSSI
    TaxableSSincome, SpecifiedIncome, MaxNonSSstandardIncome, MaxCapGains = \
        TaxableIncomeTargetMethodWithSSI(TotalInitialStandardIncome,TotalSS,IncDict['MaxStandardIncome'],
                                         IncDict['SpecifiedIncome'],MarriedOrOther)

    # Print results
    print('Total Social Security Income (SSI): '+'{:0.2f}'.format(TotalSS)+'\n')
    print('Taxable SSI: '+'{:0.2f}'.format(TaxableSSincome)+'\n')
    print('Max Non-SSI standard income for keeping Non-SSI + Taxable SSI within standard deduction: ' +
          '{:0.2f}'.format(MaxNonSSstandardIncome)+'\n')
    print('Max LT Cap Gains (including qualified dividends), for keeping Non-SSI standard income + Taxable SSI within ' +
          'standard deduction and LT Cap Gains within 0% LT cap gains tax bracket: ' + '{:0.2f}'.format(MaxCapGains)+'\n')
    print('Max Total Taxable Income, for staying within standard deduction for standard income and 0% LT cap gains tax ' +
          'bracket (maximum LT Cap Gains + qualified dividends + maximum Non-SSI standard income + Taxable SSI): ' +
          '{:0.2f}'.format(SpecifiedIncome)+'\n\n')

#############################################################################################################

# compute the taxes paid if you ignore how SSI is taxed (and thus ignore this targeting algorithm)
if ComputeTaxesWithNoTargeting:

    TotalSS = np.sum(IncDict['SocialSecurityPayments'])

    TaxableSSincome = TaxableSSconsolidated(NonSSInoTargeting + LTcapGainsNoTargeting,TotalSS, MarriedOrOther)

    TotalStandardIncome = NonSSInoTargeting + TaxableSSincome

    Taxes = ComputeTaxes(TaxRateInfo,FilingStatusNoTargeting,TotalStandardIncome,LTcapGainsNoTargeting)

    # Print results
    print('If you ignore how SSI is taxed (and thus ignore this targeting algorithm): \n')
    print('Total Social Security Income (SSI): '+'{:0.2f}'.format(TotalSS)+'\n')
    print('Taxable SSI: '+'{:0.2f}'.format(TaxableSSincome)+'\n')
    print('Non-SSI standard income: '+'{:0.2f}'.format(NonSSInoTargeting)+'\n')
    print('Total Taxable Standard Income (including taxable SSI): '+'{:0.2f}'.format(TotalStandardIncome)+'\n')
    print('Long term capital gains (including qualified dividends): '+'{:0.2f}'.format(LTcapGainsNoTargeting)+'\n')
    print('Taxes Owed: '+'{:0.2f}'.format(Taxes)+'\n')

    debug = 1

#############################################################################################################

# Plot TaxableSSincome, MaxNonSSstandardIncome, MaxCapGains, Total Taxable Income
# versus range of SSI from $0 to MaxSSI
if PlotIncomeValuesVsSSI:

    # SSIarray = np.arange(0.,SpecifiedIncome,100.)
    SSIarray = np.arange(0.,MaxSSI,100.)
    TaxableSSIarray = np.zeros(len(SSIarray))
    SpecifiedIncomeArray = np.zeros(len(SSIarray))
    MaxNonSSstandardIncomeArray = np.zeros(len(SSIarray))
    MaxCapGainsArray = np.zeros(len(SSIarray))

    # to simplify this scenario (assume no non-qualified dividends)
    TotalInitialStandardIncome = 0.

    for ct in range(0,len(SSIarray)):
        # print('ct =',ct, ', % =',round(ct/len(SSIarray)*100,2),', SSIarray =',SSIarray[ct])
        # if ct == 305:
        #     debug = 1
        # if SSIarray[ct] == 10000.: #5000.:
        #     debug = 1

        TaxableSSIarray[ct], SpecifiedIncomeArray[ct], MaxNonSSstandardIncomeArray[ct], MaxCapGainsArray[ct] = \
        TaxableIncomeTargetMethodWithSSI(TotalInitialStandardIncome,SSIarray[ct],IncDict['MaxStandardIncome'],
                                         IncDict['SpecifiedIncome'],MarriedOrOther)

    NumPlots = 4 # TaxableSSI, SpecifiedIncome, MaxNonSSstandardIncome, MaxCapGains
    IncomeArray = np.zeros((NumPlots,len(SSIarray)))
    IncomeArray[0,:] = TaxableSSIarray/1.e3
    IncomeArray[1,:] = MaxNonSSstandardIncomeArray/1.e3
    IncomeArray[2,:] = MaxCapGainsArray/1.e3
    IncomeArray[3,:] = SpecifiedIncomeArray/1.e3

    PlotLabelArray = ['Taxable SSI','Max Non-SSI Standard Income','Max LT Capital Gains','Max Total Taxable Income']
    PlotColorArray = ['r','b','g','k'] #,'c','m','limegreen'

    # Initialize plot dict using default dict
    PlotDict = copy.deepcopy(DefaultPlotDict)
    # Specify unique plot values
    UpdateDict = \
        {'IndepData': SSIarray/1.e3,
         'DepData': IncomeArray,
         'NumPlots': NumPlots,
         'PlotColorArray': PlotColorArray,
         'PlotLabelArray': PlotLabelArray,
         'SemilogyFlag': False,
         'ymin': 0, 'ymax': np.max(IncomeArray)+PlotIncomeValuesVsSSIyaxisBuffer,
         'xmin': SSIarray[0]/1.e3, 'xmax': SSIarray[-1]/1.e3+0.1,
         'ylabel': 'Income Levels [2022 $K]',
         'xlabel': 'Social Security Income [2022 $K]',
         'TitleText': 'Income Types vs Social Security Income (SSI)  ',
         'LegendLoc': 'upper right',
         'SaveFile': OutDir+'IncomeValuesVsSSI.png'}
    # Update dict to have plot specific values
    PlotDict.update(UpdateDict)
    # Create plot
    MultiPlot(PlotDict)

#############################################################################################################

# Print relevant numbers to output file (e.g. final asset values, etc.)

# file=open(OutputFile,'w')
# file.write('WithdrawalOptimization.py\n\n')
#
# file.write('Total Final: $'+'{:.2f}'.format(ProjArrays['TotalAssets'][-1])+'\n')
# file.write('PostTaxTotal Final: $'+'{:.2f}'.format(ProjArrays['PostTaxTotal'][-1])+'\n')
# file.write('PreTax Final: $'+'{:.2f}'.format(ProjArrays['PreTax'][-1])+'\n')
# file.write('PreTax457b Final: $'+'{:.2f}'.format(ProjArrays['PreTax457b'][-1])+'\n')
# file.write('Roth Final: $'+'{:.2f}'.format(ProjArrays['Roth'][-1])+'\n')
# file.write('CashCushion Final: $'+'{:.2f}'.format(ProjArrays['CashCushion'][-1])+'\n')
# file.write('CapGainsTotal Final: $'+'{:.2f}'.format(ProjArrays['CapGainsTotal'][-1])+'\n')
# file.write('Taxes Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Taxes']))+'\n')
# file.write('Penalties Total: $'+'{:.2f}'.format(np.sum(ProjArrays['Penalties']))+'\n')
#
# file.close()
