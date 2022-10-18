# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# MultiPlot.py

# import numpy as np
import matplotlib.pyplot as plt

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
