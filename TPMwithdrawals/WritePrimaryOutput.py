# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)
import numpy as np


# WritePrimaryOutput.py

def WritePrimaryOutput(OutputFile,OutputDict,FilingStatus):

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


    file=open(OutputFile,'w')
    file.write('TPMwithdrawals.py\n\n')

    if TotalCash < TotalCashNeeded:
        file.write('*** BAD NEWS: You have run out of money ***\n\n')
        file.write('Unfortunately with the provided assets, income, and expenses for this year, you will run out of '+
                   'money and not be able to cover all your expenses.\n\n')
        file.write('Your total needed cash (living expenses + taxes owed from last year + penalties owed from last '+
                   'year + estimated tax payment this year) is $'+'{:.2f}'.format(TotalCashNeeded)+
                   ', and you will only be able to generate $'+'{:.2f}'.format(TotalCash)+
                   ' ('+'{:.2f}'.format(TotalCash/TotalCashNeeded*100.)+'%) of that needed cash. Which means you still'+
                   ' need $'+'{:.2f}'.format(TotalCashNeeded - TotalCash)+'.\n\n')
        file.write('So you will have to either cut your expenses or increase your income to avoid going into debt.\n\n')

    file.write('\n')
    file.write('*** Actions ***\n\n')

    file.write('This year, you should:\n\n')

    if FilingStatus == 'MarriedFilingJointly': # two people

        # PreTax Withdrawal - and which person

        if PreTaxWithdrawal[0] > 0.:
            if ConversionOccurred[0]:
                file.write('* Convert $'+'{:.2f}'.format(ConversionAmount[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth (Person 1)')
                if np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]) > 0.009:
                    file.write(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0])) +
                               ' from Pre-Tax that is NOT converted to Roth\n\n')
                else:
                    file.write('\n\n')
            else:
                file.write('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (Person 1) (no conversion to Roth)\n\n')

        if PreTaxWithdrawal[1] > 0.:
            if ConversionOccurred[1]:
                file.write('* Convert $'+'{:.2f}'.format(ConversionAmount[1])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth (Person 2)')
                if np.absolute(PreTaxWithdrawal[1]-ConversionAmount[1]) > 0.009:
                    file.write(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[1]-ConversionAmount[1]))+
                               ' from Pre-Tax that is NOT converted to Roth\n\n')
                else:
                    file.write('\n\n')
            else:
                file.write('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[1])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (Person 2) (no conversion to Roth)\n\n')

        # PreTax457b Withdrawal - and which person

        if PreTax457bWithdrawal[0] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+
                       ' from 457(b) account (Person 1) (no conversion to Roth, no early withdrawal penalty)\n\n')

        if PreTax457bWithdrawal[1] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[1])+
                       ' from 457(b) account (Person 2) (no conversion to Roth, no early withdrawal penalty)\n\n')

        # Roth Withdrawal - and which person

        if RothWithdrawal[0] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[0])+
                       ' from Roth account (Person 1) (after conversions, if any)\n\n')

        if RothWithdrawal[1] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[1])+
                       ' from Roth account (Person 2) (after conversions, if any)\n\n')

    else: # one person

        # PreTax Withdrawal
        if PreTaxWithdrawal[0] > 0.:
            if ConversionOccurred[0]:
                file.write('* Convert $'+'{:.2f}'.format(ConversionAmount[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth')
                if np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]) > 0.009:
                    file.write(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]))+
                               ' from Pre-Tax that is NOT converted to Roth\n\n')
                else:
                    file.write('\n\n')
            else:
                file.write('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (no conversion to Roth)\n\n')

        # PreTax457b Withdrawal
        if PreTax457bWithdrawal[0] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+
                       ' from 457(b) account (no conversion to Roth, no early withdrawal penalty)\n\n')

        # Roth Withdrawal
        if RothWithdrawal[0] > 0.:
            file.write('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[0])+
                       ' from Roth account (after conversions, if any)\n\n')

    # Cash Withdrawal - and which person
    if CashWithdrawal > 0.:
        file.write('* Withdraw $'+'{:.2f}'.format(CashWithdrawal)+' from Cash account\n\n')

    # Loop over all PostTax lots, specify how much of each to sell
    for ct in range(len(PostTaxWithdrawal)):
        if PostTaxWithdrawal[ct] > 0.:
            file.write('* Sell $'+'{:.2f}'.format(PostTaxWithdrawal[ct])+' from Taxable Lot #'+
                       '{:d}'.format(ct+1)+'\n')
    file.write('\n')

    if ExcessCash > 0.:
        file.write('* Invest the $'+'{:.2f}'.format(ExcessCash)+
                   ' excess cash generated (based on values provided) in a new taxable lot\n\n')
    else:
        file.write('You should not have any excess cash to invest this year (based on values provided) - all cash '+
                   'generated is used\n\n')

    # Estimated tax payment
    file.write('* Pay $'+'{:.2f}'.format(EstimatedTaxesToPayThisYear)+' in estimated taxes to the IRS this year\n')
    file.write('Note: split total estimated taxes into the four required payments in April, June, Sept, and the' +
               ' following Jan\n')
    file.write('Note: any mandatory 20% withholding on 401(k)/403(b)/457(b) withdrawals counts towards estimated ' +
               'tax payment\n\n')
    if TaxesStillOwed > 0.:
        file.write('* Pay the IRS $'+'{:.2f}'.format(TaxesStillOwed)+' in owed taxes from last year when you file in ' +
                   'the spring\n\n')
    elif Refund > 0.:
        file.write('You should get a $'+'{:.2f}'.format(Refund)+' refund from the IRS when you file in the spring\n\n')
    else:
        file.write('You should not get a refund or owe the IRS anything when you file in the spring\n\n')


    file.write('\n')
    file.write('*** Withdrawal Info ***\n\n')

    # Total tax-deferred account withdrawals
    file.write('Total pre-tax (Traditional IRA, 401(k), 403(b), 457(b)) withdrawals (including Roth conversions): $' +
               '{:.2f}'.format(PreTaxTotalWithdrawal + PreTax457bTotalWithdrawal)+'\n')

    if FilingStatus == 'MarriedFilingJointly': # two people
        # RMDs for each person
        if RMD[0,0] > 0. or RMD[0,1] > 0.:
            file.write('Which includes a required minimum distribution (RMD) of $' +
                   '{:.2f}'.format(RMD[0,0])+' for Person 1 and $' +
                   '{:.2f}'.format(RMD[0,1])+' for Person 2\n')
    else: # one person
        if RMD[0,0] > 0.:
            file.write('Which includes a required minimum distribution (RMD) of $' +
                   '{:.2f}'.format(RMD[0,0])+'\n')
    file.write('\n')

    # Total Roth account withdrawals
    file.write('Total Roth withdrawals: $' + '{:.2f}'.format(RothTotalWithdrawal)+'\n\n')

    # Total cash account withdrawals
    file.write('Total cash account withdrawals: $' + '{:.2f}'.format(CashWithdrawal)+'\n\n')

    # Total taxable account withdrawals
    file.write('Total taxable account withdrawals: $' + '{:.2f}'.format(PostTaxTotalWithdrawal)+'\n\n')

    # Total Withdrawals
    file.write('Total withdrawals across all accounts: $'+'{:.2f}'.format(TotalWithdrawalAcrossAllAccounts)+'\n\n')


    file.write('\n')
    file.write('*** Income and Cash Goals ***\n\n')

    file.write('Your standard income goal is $'+'{:.2f}'.format(StdIncomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(StdIncomeAchieved)+
               ' ('+'{:.2f}'.format(StdIncomeAchieved/StdIncomeGoal*100.)+'%) of that goal\n\n')
    file.write('Your long term capital gains income goal is $'+'{:.2f}'.format(LTCGincomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(LTCGincomeAchieved)+
               ' ('+'{:.2f}'.format(LTCGincomeAchieved/LTCGincomeGoal*100.)+'%) of that goal\n\n')
    file.write('Your total income goal is $'+'{:.2f}'.format(TotalIncomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(TotalIncomeAchieved)+
               ' ('+'{:.2f}'.format(TotalIncomeAchieved/TotalIncomeGoal*100.)+'%) of that goal\n\n')

    file.write('Your total needed cash (living expenses + taxes owed from last year + penalties owed from last year '+
               '+ estimated tax payment this year) is $'+'{:.2f}'.format(TotalCashNeeded)+
               ', and the above actions generate $'+'{:.2f}'.format(TotalCash)+
               ' ('+'{:.2f}'.format(TotalCash/TotalCashNeeded*100.)+'%) of that needed cash\n\n')


    file.write('\n')
    file.write('*** Taxes and Penalties ***\n\n')
    file.write('The above actions generate $'+'{:.2f}'.format(Taxes)+' in taxes and $'+'{:.2f}'.format(Penalties)+
               ' in penalties.\n')

    file.close()
