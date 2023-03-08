# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# AppendVerboseOutput.py

import numpy as np

def AppendVerboseOutput(OutputFile,OutputDict,FilingStatus):

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



    file=open(OutputFile,'a')

    file.write('\n\n')
    file.write('*** Additional Details, Verbose Mode ***\n\n')

    file.write('Tax-advantaged Account Balances And Withdrawals:\n\n')

    if FilingStatus == 'MarriedFilingJointly': # two people

        file.write('PreTax (Traditional IRA, 401(k), 403(b)) Withdrawals\n')
        file.write('Person 1 Initial Balance: $'+'{:.2f}'.format(PreTaxIV[0])+'\n')
        file.write('Person 1 Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[0])+'\n')
        file.write('Person 1 Withdrawal: $'+'{:.2f}'.format(PreTaxWithdrawal[0])+'\n')
        file.write('Person 2 Initial Balance: $'+'{:.2f}'.format(PreTaxIV[1])+'\n')
        file.write('Person 2 Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[1])+'\n')
        file.write('Person 2 Withdrawal: $'+'{:.2f}'.format(PreTaxWithdrawal[1])+'\n')
        file.write('Total Withdrawal for Both People: $'+'{:.2f}'.format(PreTaxTotalWithdrawal)+'\n')

        if np.sum(PreTax457bIV) > 0.: # only output 457(b) if non-zero start (many people won't have 457(b))
            file.write('\n')
            file.write('457(b) Withdrawals\n')
            file.write('Person 1 Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[0])+'\n')
            file.write('Person 1 Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[0])+'\n')
            file.write('Person 1 Withdrawal: $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+'\n')
            file.write('Person 2 Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[1])+'\n')
            file.write('Person 2 Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[1])+'\n')
            file.write('Person 2 Withdrawal: $'+'{:.2f}'.format(PreTax457bWithdrawal[1])+'\n')
            file.write('Total Withdrawal for Both People: $'+'{:.2f}'.format(PreTax457bTotalWithdrawal)+'\n')

        file.write('\n')
        file.write('Roth IRA Withdrawals\n')
        file.write('Person 1 Initial Balance: $'+'{:.2f}'.format(RothIV[0])+'\n')
        file.write('Person 1 Final Balance: $'+'{:.2f}'.format(RothFinalBal[0])+'\n')
        file.write('Person 1 Withdrawal: $'+'{:.2f}'.format(RothWithdrawal[0])+'\n')
        file.write('Person 2 Initial Balance: $'+'{:.2f}'.format(RothIV[1])+'\n')
        file.write('Person 2 Final Balance: $'+'{:.2f}'.format(RothFinalBal[1])+'\n')
        file.write('Person 2 Withdrawal: $'+'{:.2f}'.format(RothWithdrawal[1])+'\n')
        file.write('Total Withdrawal for Both People: $'+'{:.2f}'.format(RothTotalWithdrawal)+'\n')

    else: # 1 person
        file.write('PreTax (Traditional IRA, 401(k), 403(b)) Withdrawals\n')
        file.write('Initial Balance: $'+'{:.2f}'.format(PreTaxIV[0])+'\n')
        file.write('Final Balance: $'+'{:.2f}'.format(PreTaxFinalBal[0])+'\n')
        file.write('Total Withdrawal: $'+'{:.2f}'.format(PreTaxTotalWithdrawal)+'\n')

        if np.sum(PreTax457bIV) > 0.: # only output 457(b) if non-zero start (many people won't have 457(b))
            file.write('\n')
            file.write('457(b) Withdrawals\n')
            file.write('Initial Balance: $'+'{:.2f}'.format(PreTax457bIV[0])+'\n')
            file.write('Final Balance: $'+'{:.2f}'.format(PreTax457bFinalBal[0])+'\n')
            file.write('Total Withdrawal: $'+'{:.2f}'.format(PreTax457bTotalWithdrawal)+'\n')

        file.write('\n')
        file.write('Roth IRA Withdrawals\n')
        file.write('Initial Balance: $'+'{:.2f}'.format(RothIV[0])+'\n')
        file.write('Final Balance: $'+'{:.2f}'.format(RothFinalBal[0])+'\n')
        file.write('Total Withdrawal: $'+'{:.2f}'.format(RothTotalWithdrawal)+'\n')


    file.write('\n')
    file.write('Cash Account Balances And Withdrawal\n')
    file.write('Initial Balance: $'+'{:.2f}'.format(CashIV)+'\n')
    file.write('Final Balance: $'+'{:.2f}'.format(CashFinalBal)+'\n')
    file.write('Withdrawal: $'+'{:.2f}'.format(CashWithdrawal)+'\n')

    file.write('\n')
    file.write('Taxable Account Balances And Withdrawals\n')
    file.write('Initial Balance For Each Lot:\n')
    for ct in range(len(PostTaxIV)):
        if ct == len(PostTaxIV)-1:
            file.write('{:>10}\n'.format('${:.2f}'.format(PostTaxIV[ct])))
        else:
            file.write('{:>10}, '.format('${:.2f}'.format(PostTaxIV[ct])))
    file.write('Final Balance For Each Lot:\n')
    for ct in range(len(PostTaxFinalBal)):
        if ct == len(PostTaxFinalBal)-1:
            file.write('{:>10}\n'.format('${:.2f}'.format(PostTaxFinalBal[ct])))
        else:
            file.write('{:>10}, '.format('${:.2f}'.format(PostTaxFinalBal[ct])))
    PostTaxIVtotalBal = np.sum(PostTaxIV)
    file.write('Initial Total Balance: $'+'{:.2f}'.format(PostTaxIVtotalBal)+'\n')
    PostTaxTotalBalanceAfterWithdrawal = np.sum(PostTaxFinalBal[0:len(PostTaxIV)])
    file.write('Total balance after withdrawal: $'+'{:.2f}'.format(PostTaxTotalBalanceAfterWithdrawal)+'\n')
    PostTaxTotalWithdrawal = PostTaxIVtotalBal - PostTaxTotalBalanceAfterWithdrawal
    file.write('Total Withdrawal: $'+'{:.2f}'.format(PostTaxTotalWithdrawal)+'\n')
    PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash = np.sum(PostTaxFinalBal[:])
    ExcessCashGenerated = PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash - PostTaxTotalBalanceAfterWithdrawal
    file.write('Excess Cash Generated: $'+'{:.2f}'.format(ExcessCashGenerated)+'\n')
    file.write('Final Total Balance (after investing excess cash): $'+'{:.2f}'.format(
        PostTaxTotalBalanceAfterWithdrawalAndInvestingExcessCash)+'\n')

    file.write('\n')
    file.write('Taxable Account Capital Gains\n')
    file.write('Initial Cap Gains For Each Lot:\n')
    for ct in range(len(PostTaxIVCG)):
        if ct == len(PostTaxIVCG)-1:
            file.write('{:>10}\n'.format('${:.2f}'.format(PostTaxIVCG[ct])))
        else:
            file.write('{:>10}, '.format('${:.2f}'.format(PostTaxIVCG[ct])))
    file.write('Final Cap Gains For Each Lot:\n')
    for ct in range(len(PostTaxFinalCG)):
        if ct == len(PostTaxFinalCG)-1:
            file.write('{:>10}\n'.format('${:.2f}'.format(PostTaxFinalCG[ct])))
        else:
            file.write('{:>10}, '.format('${:.2f}'.format(PostTaxFinalCG[ct])))
    PostTaxIVCGtotal = np.sum(PostTaxIVCG)
    file.write('Initial Total Cap Gains: $'+'{:.2f}'.format(PostTaxIVCGtotal)+'\n')
    file.write('Final Total Cap Gains: $'+'{:.2f}'.format(PostTaxFinalCGtotal)+'\n')
    file.write('Change in Total Cap Gains: $'+'{:.2f}'.format(PostTaxIVCGtotal - PostTaxFinalCGtotal)+'\n')
    file.write('Note: change in total cap gains can be smaller than total cap gain income (see above) due to qualified '
               'dividend income that counts as long term cap gains for taxation purposes.\n')

    file.write('\n')
    file.write('Total Asset Balances And Withdrawal\n')
    file.write('Initial Balance: $'+'{:.2f}'.format(TotalIV)+'\n')
    file.write('Final Balance: $'+'{:.2f}'.format(TotalFinalBal)+'\n')
    file.write('Change in Balance: $'+'{:.2f}'.format(TotalIV - TotalFinalBal)+'\n')
    file.write('Note: change in balance can be smaller than Total Cash Needed (see above) due to income sources such'+
               ' as dividends or other "non-adjustable" income streams.')

    file.close()