# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# SupportMethods.py

import numpy as np
import copy
import sys
# import os
import matplotlib.pyplot as plt
# from scipy import optimize

#############################################################################################################

# Compute total taxes due from both standard income and long term cap gains / qualified dividends
def ComputeTaxes(TaxRateInfo,FilingStatus,TotalStandardIncome,TotalLTcapGainsIncome):

    # Use appropriate standard deduction, tax brackets
    if FilingStatus=='Single':
        StandardDeduction = TaxRateInfo['SingleStandardDeduction']
        # tax bracket mins are mutable objects (numpy arrays) within TaxRateInfo, so must make copies to avoid changing
        # accidentally (which would change them outside this function)
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['SingleIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['SingleIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='MarriedFilingJointly' or FilingStatus=='QualifyingWidow(er)':
        StandardDeduction = TaxRateInfo['MarriedFilingJointlyStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['MarriedFilingJointlyIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['MarriedFilingJointlyIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='MarriedFilingSeparately':
        StandardDeduction = TaxRateInfo['MarriedFilingSeparatelyStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['MarriedFilingSeparatelyIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['MarriedFilingSeparatelyIncomeBracketLTcapGainsMins'])
    elif FilingStatus=='HeadOfHousehold':
        StandardDeduction = TaxRateInfo['HeadOfHouseholdStandardDeduction']
        IncomeBracketMins = copy.deepcopy(TaxRateInfo['HeadOfHouseholdIncomeBracketMins'])
        IncomeBracketLTcapGainsMins = copy.deepcopy(TaxRateInfo['HeadOfHouseholdIncomeBracketLTcapGainsMins'])
    else:
        print('Filing Status not recognized. Exiting.')
        sys.exit()

    # Remove standard deduction from standard income to get taxable standard income
    # (and from LT cap gains if needed - though hopefully it's never wasted that way)
    if TotalStandardIncome >= StandardDeduction:
        TaxableStandardIncome = TotalStandardIncome - StandardDeduction
        TaxableLTcapGains = TotalLTcapGainsIncome
    elif (TotalStandardIncome + TotalLTcapGainsIncome) >= StandardDeduction:
        TaxableStandardIncome = 0
        TaxableLTcapGains = TotalLTcapGainsIncome - (StandardDeduction - TotalStandardIncome)
    else:
        TaxableStandardIncome = 0
        TaxableLTcapGains = 0

    # Compute taxes on standard income
    # np.searchsorted returns the index of the Min value beyond TaxableStandardIncome (and +1 beyond the last index if
    # greater than the last value) i.e. the index of the max value of the top bracket
    ind = np.searchsorted(IncomeBracketMins,TaxableStandardIncome)
    TaxesOnStandardIncome = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            TaxesOnStandardIncome += TaxRateInfo['Rates'][ct]*(IncomeBracketMins[ct+1]-IncomeBracketMins[ct])
        else: # top bracket
            TaxesOnStandardIncome += TaxRateInfo['Rates'][ct]*(TaxableStandardIncome - IncomeBracketMins[ct])

    # Compute taxes on LT Cap Gains
    ind = np.searchsorted(IncomeBracketLTcapGainsMins,TaxableLTcapGains)
    TaxesOnLTcapGains = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            TaxesOnLTcapGains += TaxRateInfo['CapGainsRatesLT'][ct]*(IncomeBracketLTcapGainsMins[ct+1] -
                                                                     IncomeBracketLTcapGainsMins[ct])
        else: # top bracket
            TaxesOnLTcapGains += TaxRateInfo['CapGainsRatesLT'][ct]*(TaxableLTcapGains -
                                                                     IncomeBracketLTcapGainsMins[ct])

    return TaxesOnStandardIncome + TaxesOnLTcapGains

#############################################################################################################

# Compute for a given amount of money pulled from pre-tax, how much taxes will be paid, and thus resulting post-tax
# money you can spend
def PostTaxFromPreTax(Pulled,StandardDeduction,IncomeBracketMins,Rates):

    if Pulled > StandardDeduction:
        Taxable = Pulled - StandardDeduction
    else:
        Taxable = 0

    # np.searchsorted returns the index of the Min value beyond Taxable (and +1 beyond the last index if greater than
    # the last value) i.e. the index of the max value of the top bracket
    ind = np.searchsorted(IncomeBracketMins,Taxable)
    Taxes = 0 # init
    for ct in range(0,ind):
        # if it's before the top bracket
        if ct < (ind-1):
            Taxes += Rates[ct]*(IncomeBracketMins[ct+1]-IncomeBracketMins[ct])
        else: # top bracket
            Taxes += Rates[ct]*(Taxable - IncomeBracketMins[ct])

    PostTax = Pulled - Taxes

    return PostTax

#############################################################################################################

# Compute for a needed amount of post-tax money needed, how much money must be pulled from pre-tax account
def PreTaxFromPostTax(Needed,StandardDeduction,IncomeBracketMins,Rates):
    # Account for standard deduction
    if Needed > StandardDeduction:
        # The amount you need on TOP of standard deduction
        NeededSansSD = Needed - StandardDeduction
    else:
        # so if you need an amount equal or less than the standard deduction (though of course you'll always want to
        # pull at least the standard deduction to get the money tax free), you'll pay no taxes
        NeededSansSD = 0

    # Map NeededSansSD back to pre-tax dollars
    # To do this, must first compute post-tax bracket mins
    PostTaxBracketMins = np.zeros(len(IncomeBracketMins))
    for ct in range(len(PostTaxBracketMins)):
        if ct == 0:
            PostTaxBracketMins[ct] = 0
        else:
            PostTaxBracketMins[ct] = PostTaxBracketMins[ct-1] + (1-Rates[ct-1])*(IncomeBracketMins[ct]-IncomeBracketMins[ct-1])

    # np.searchsorted returns the index of the PostTaxBracketMins value beyond NeededSansSD (and +1 beyond the last index if
    # greater than the last value) i.e. the index of the max value of the top bracket
    ind = np.searchsorted(PostTaxBracketMins,NeededSansSD)

    if ind > 0:
        PreTax = (NeededSansSD - PostTaxBracketMins[ind-1])/(1-Rates[ind-1]) + IncomeBracketMins[ind-1] + \
                 StandardDeduction
    else:
        PreTax = Needed

    return PreTax

#############################################################################################################

# General multiplot method
def MultiPlot(PlotDict):

    # Properties for text boxes - these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

    fig = plt.figure(1,figsize=(PlotDict['FigWidth'],PlotDict['FigHeight']))

    # Loop over plots
    for ct in range(0,PlotDict['NumPlots']):
        if PlotDict['PlotSecondaryLines'] == False:
            if PlotDict['SemilogyFlag'] == False:
                plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'],
                         linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                         label=PlotDict['PlotLabelArray'][ct])
            else:
                plt.semilogy(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'],
                             linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                             label=PlotDict['PlotLabelArray'][ct])
        else:
            if PlotDict['SemilogyFlag'] == False:
                plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'][ct],
                         linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                         label=PlotDict['PlotLabelArray'][ct])
                plt.plot(PlotDict['IndepData'], PlotDict['DepData'][ct+PlotDict['NumPlots'],:],
                         PlotDict['LineStyle'][ct+PlotDict['NumPlots']],
                         linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                         label=PlotDict['PlotLabelArray'][ct+PlotDict['NumPlots']])
            else:
                plt.semilogy(PlotDict['IndepData'], PlotDict['DepData'][ct,:], PlotDict['LineStyle'][ct],
                         linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                         label=PlotDict['PlotLabelArray'][ct])
                plt.semilogy(PlotDict['IndepData'], PlotDict['DepData'][ct+PlotDict['NumPlots'],:],
                         PlotDict['LineStyle'][ct+PlotDict['NumPlots']],
                         linewidth=PlotDict['LineWidth'], color=PlotDict['PlotColorArray'][ct],
                         label=PlotDict['PlotLabelArray'][ct+PlotDict['NumPlots']])

    ax = plt.gca()
    plt.ylim(PlotDict['ymin'],PlotDict['ymax'])
    plt.xlim(PlotDict['xmin'],PlotDict['xmax'])

    ax.text(PlotDict['CopyrightX'], PlotDict['CopyrightY'], PlotDict['CopyrightText'], transform=ax.transAxes,
            fontsize=PlotDict['CopyrightFontSize'], verticalalignment=PlotDict['CopyrightVertAlign'])

    if PlotDict['SemilogyFlag'] == False:
        ax.ticklabel_format(useOffset=False)

    plt.ylabel(PlotDict['ylabel'], fontsize=PlotDict['ylabelFontSize'])
    plt.xlabel(PlotDict['xlabel'], fontsize=PlotDict['xlabelFontSize'])
    plt.title(PlotDict['TitleText'], y=PlotDict['Title_yoffset'], fontsize=PlotDict['TitleFontSize'])
    plt.gca().tick_params(axis='both', which='major', labelsize=30)
    plt.grid(color='gray',linestyle='--') # or just plt.grid(True)  color='lightgray'
    plt.legend(loc=PlotDict['LegendLoc'],fontsize=PlotDict['LegendFontSize'],numpoints=1)
    plt.tight_layout()
    plt.savefig(PlotDict['SaveFile'])
    plt.close()
