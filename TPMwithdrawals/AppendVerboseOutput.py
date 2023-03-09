# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# AppendVerboseOutput.py

import numpy as np
import sys

def AppendVerboseOutput(OutputFile,OutputDict,FilingStatus,OutputToScreen):

    # Unpack OutputDict
    PreTaxIV = OutputDict['PreTaxIV']
    PreTaxFinalBal = OutputDict['PreTaxFinalBal']
    PreTaxWithdrawal = OutputDict['PreTaxWithdrawal']
    PreTaxTotalWithdrawal = OutputDict['PreTaxTotalWithdrawal']

    PreTax457bIV = OutputDict['PreTax457bIV']
    PreTax457bFinalBal = OutputDict['PreTax457bFinalBal']
    PreTax457bWithdrawal = OutputDict['PreTax457bWithdrawal']
    PreTax457bTotalWithdrawal = OutputDict['PreTax457bTotalWithdrawal']

    ConversionOccurred = OutputDict['ConversionOccurred']
    ConversionAmount = OutputDict['ConversionAmount']

    RothIV = OutputDict['RothIV']
    RothFinalBal = OutputDict['RothFinalBal']
    RothWithdrawal = OutputDict['RothWithdrawal']
    RothTotalWithdrawal = OutputDict['RothTotalWithdrawal']

    CashIV = OutputDict['CashIV']
    CashFinalBal = OutputDict['CashFinalBal']
    CashWithdrawal = OutputDict['CashWithdrawal']

    PostTaxIV = OutputDict['PostTaxIV']
    PostTaxFinalBal = OutputDict['PostTaxFinalBal']
    PostTaxWithdrawal = OutputDict['PostTaxWithdrawal']
    PostTaxTotalWithdrawal = OutputDict['PostTaxTotalWithdrawal']

    PostTaxIVCG = OutputDict['PostTaxIVCG']
    PostTaxFinalCG = OutputDict['PostTaxFinalCG']
    PostTaxFinalCGtotal = OutputDict['PostTaxFinalCGtotal']

    TotalCash = OutputDict['TotalCash']
    TotalCashNeeded = OutputDict['TotalCashNeeded']
    ExcessCash = OutputDict['ExcessCash']

    StdIncomeGoal = OutputDict['StdIncomeGoal']
    StdIncomeAchieved = OutputDict['StdIncomeAchieved']
    LTCGincomeGoal = OutputDict['LTCGincomeGoal']
    LTCGincomeAchieved = OutputDict['LTCGincomeAchieved']
    TotalIncomeGoal = OutputDict['TotalIncomeGoal']
    TotalIncomeAchieved = OutputDict['TotalIncomeAchieved']

    Taxes = OutputDict['Taxes']
    Penalties = OutputDict['Penalties']

    Refund = OutputDict['Refund']
    TaxesStillOwed = OutputDict['TaxesStillOwed']
    EstimatedTaxesToPayThisYear = OutputDict['EstimatedTaxesToPayThisYear']

    TotalIV = OutputDict['TotalIV']
    TotalFinalBal = OutputDict['TotalFinalBal']
    TotalWithdrawalAcrossAllAccounts = OutputDict['TotalWithdrawalAcrossAllAccounts']

    RMD = OutputDict['RMD']

    # Saving the reference of the standard output
    original_stdout = sys.stdout

    file=open(OutputFile,'a')
    if OutputToScreen == False: # then output to file
        sys.stdout = file

    # Use print instead of file.write, and also remove one \n, since print includes a single line break after already

    print('\n')
    print('*** Additional Details, Verbose Mode ***\n')

    print('Tax-advantaged Account Balances And Withdrawals:\n')

    if FilingStatus == 'MarriedFilingJointly': # two people

        print('PreTax (Traditional IRA, 401(k), 403(b)) Withdrawals')
        print('Person 1 Initial Balance: $'+'{:.2f}'.format(PreTaxIV[0])+'')
        print('Person 1 Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[0])+'')
        print('Person 1 Withdrawal: $'+'{:.2f}'.format(PreTaxWithdrawal[0])+'')
        print('Person 2 Initial Balance: $'+'{:.2f}'.format(PreTaxIV[1])+'')
        print('Person 2 Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[1])+'')
        print('Person 2 Withdrawal: $'+'{:.2f}'.format(PreTaxWithdrawal[1])+'')
        print('Total Withdrawal for Both People: $'+'{:.2f}'.format(PreTaxTotalWithdrawal)+'')

        if np.sum(PreTax457bIV) > 0.: # only output 457(b) if non-zero start (many people won't have 457(b))
            print('')
            print('457(b) Withdrawals')
            print('Person 1 Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[0])+'')
            print('Person 1 Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[0])+'')
            print('Person 1 Withdrawal: $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+'')
            print('Person 2 Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[1])+'')
            print('Person 2 Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[1])+'')
            print('Person 2 Withdrawal: $'+'{:.2f}'.format(PreTax457bWithdrawal[1])+'')
            print('Total Withdrawal for Both People: $'+'{:.2f}'.format(PreTax457bTotalWithdrawal)+'')

        print('')
        print('Roth IRA Withdrawals')
        print('Person 1 Initial Balance: $'+'{:.2f}'.format(RothIV[0])+'')
        print('Person 1 Final Balance: $'+'{:.2f}'.format(RothFinalBal[0])+'')
        print('Person 1 Withdrawal: $'+'{:.2f}'.format(RothWithdrawal[0])+'')
        print('Person 2 Initial Balance: $'+'{:.2f}'.format(RothIV[1])+'')
        print('Person 2 Final Balance: $'+'{:.2f}'.format(RothFinalBal[1])+'')
        print('Person 2 Withdrawal: $'+'{:.2f}'.format(RothWithdrawal[1])+'')
        print('Total Withdrawal for Both People: $'+'{:.2f}'.format(RothTotalWithdrawal)+'')

    else: # 1 person
        print('PreTax (Traditional IRA, 401(k), 403(b)) Withdrawals')
        print('Initial Balance: $'+'{:.2f}'.format(PreTaxIV[0])+'')
        print('Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[0])+'')
        print('Total Withdrawal: $'+'{:.2f}'.format(PreTaxTotalWithdrawal)+'')

        if np.sum(PreTax457bIV) > 0.: # only output 457(b) if non-zero start (many people won't have 457(b))
            print('')
            print('457(b) Withdrawals')
            print('Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[0])+'')
            print('Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[0])+'')
            print('Total Withdrawal: $'+'{:.2f}'.format(PreTax457bTotalWithdrawal)+'')

        print('')
        print('Roth IRA Withdrawals')
        print('Initial Balance: $'+'{:.2f}'.format(RothIV[0])+'')
        print('Final Balance: $'+'{:.2f}'.format(RothFinalBal[0])+'')
        print('Total Withdrawal: $'+'{:.2f}'.format(RothTotalWithdrawal)+'')


    print('')
    print('Cash Account Balances And Withdrawal')
    print('Initial Balance: $'+'{:.2f}'.format(CashIV)+'')
    print('Final Balance: $'+'{:.2f}'.format(CashFinalBal)+'')
    print('Withdrawal: $'+'{:.2f}'.format(CashWithdrawal)+'')

    print('')
    print('Taxable Account Balances And Withdrawals')
    print('Initial Balance For Each Lot:')
    for ct in range(len(PostTaxIV)):
        if ct == len(PostTaxIV)-1:
            print('{:>10}'.format('${:.2f}'.format(PostTaxIV[ct])))
        else:
            print('{:>10}, '.format('${:.2f}'.format(PostTaxIV[ct])), end = '')
    print('Final Balance For Each Lot:')
    for ct in range(len(PostTaxFinalBal)):
        if ct == len(PostTaxFinalBal)-1:
            print('{:>10}'.format('${:.2f}'.format(PostTaxFinalBal[ct])))
        else:
            print('{:>10}, '.format('${:.2f}'.format(PostTaxFinalBal[ct])), end = '')
    PostTaxIVtotalBal = np.sum(PostTaxIV)
    print('Initial Total Balance: $'+'{:.2f}'.format(PostTaxIVtotalBal)+'')
    PostTaxTotalBalanceAfterWithdrawal = np.sum(PostTaxFinalBal[0:len(PostTaxIV)])
    print('Total balance after withdrawal: $'+'{:.2f}'.format(PostTaxTotalBalanceAfterWithdrawal)+'')
    PostTaxTotalWithdrawal = PostTaxIVtotalBal - PostTaxTotalBalanceAfterWithdrawal
    print('Total Withdrawal: $'+'{:.2f}'.format(PostTaxTotalWithdrawal)+'')
    PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash = np.sum(PostTaxFinalBal[:])
    ExcessCashGenerated = PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash - PostTaxTotalBalanceAfterWithdrawal
    print('Excess Cash Generated: $'+'{:.2f}'.format(ExcessCashGenerated)+'')
    print('Final Total Balance (after investing excess cash): $'+'{:.2f}'.format(
        PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash)+'')

    print('')
    print('Taxable Account Capital Gains')
    print('Initial Cap Gains For Each Lot:')
    for ct in range(len(PostTaxIVCG)):
        if ct == len(PostTaxIVCG)-1:
            print('{:>10}'.format('${:.2f}'.format(PostTaxIVCG[ct])))
        else:
            print('{:>10}, '.format('${:.2f}'.format(PostTaxIVCG[ct])), end = '')
    print('Final Cap Gains For Each Lot:')
    for ct in range(len(PostTaxFinalCG)):
        if ct == len(PostTaxFinalCG)-1:
            print('{:>10}'.format('${:.2f}'.format(PostTaxFinalCG[ct])))
        else:
            print('{:>10}, '.format('${:.2f}'.format(PostTaxFinalCG[ct])), end = '')
    PostTaxIVCGtotal = np.sum(PostTaxIVCG)
    print('Initial Total Cap Gains: $'+'{:.2f}'.format(PostTaxIVCGtotal)+'')
    print('Final Total Cap Gains: $'+'{:.2f}'.format(PostTaxFinalCGtotal)+'')
    print('Change in Total Cap Gains: $'+'{:.2f}'.format(PostTaxIVCGtotal - PostTaxFinalCGtotal)+'')
    print('Note: change in total cap gains can be smaller than total cap gain income (see above) due to qualified '
               'dividend income that counts as long term cap gains for taxation purposes.')

    print('')
    print('Total Asset Balances And Withdrawal')
    print('Initial Balance: $'+'{:.2f}'.format(TotalIV)+'')
    print('Final Balance: $'+'{:.2f}'.format(TotalFinalBal)+'')
    print('Change in Balance: $'+'{:.2f}'.format(TotalIV - TotalFinalBal)+'')
    print('Note: change in balance can be smaller than Total Cash Needed (see above) due to income sources such'+
               ' as dividends or other "non-adjustable" income streams.')

    file.close()
