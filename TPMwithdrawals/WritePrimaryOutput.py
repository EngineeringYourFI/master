# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)
import numpy as np
import sys

# WritePrimaryOutput.py

def WritePrimaryOutput(OutputFile,OutputDict,FilingStatus,OutputToScreen):

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

    # with open(OutputFile,'w') as file:
    #     sys.stdout = file

    file = open(OutputFile,'w')
    if OutputToScreen == False: # then output to file
        sys.stdout = file

    # file.write('TPMwithdrawals.py\n\n')
    # Use print instead of file.write, and also remove one \n, since print includes a single line break after already
    print('TPMwithdrawals.py\n')

    if TotalCash < TotalCashNeeded:
        print('*** BAD NEWS: You have run out of money ***\n')
        print('Unfortunately with the provided assets, income, and expenses for this year, you will run out of '+
                   'money and not be able to cover all your expenses.\n')
        print('Your total needed cash (living expenses + taxes owed from last year + penalties owed from last '+
                   'year + estimated tax payment this year) is $'+'{:.2f}'.format(TotalCashNeeded)+
                   ', and you will only be able to generate $'+'{:.2f}'.format(TotalCash)+
                   ' ('+'{:.2f}'.format(TotalCash/TotalCashNeeded*100.)+'%) of that needed cash. Which means you still'+
                   ' need $'+'{:.2f}'.format(TotalCashNeeded - TotalCash)+'.\n')
        print('So you will have to either cut your expenses or increase your income to avoid going into debt.\n')

    print('')
    print('*** Actions ***\n')

    print('This year, you should:\n')

    if FilingStatus == 'MarriedFilingJointly': # two people

        # PreTax Withdrawal - and which person

        if PreTaxWithdrawal[0] > 0.:
            if ConversionOccurred[0]:
                print('* Convert $'+'{:.2f}'.format(ConversionAmount[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth (Person 1)', end = '')
                if np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]) > 0.009:
                    print(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0])) +
                               ' from Pre-Tax that is NOT converted to Roth\n')
                else:
                    print('\n')
            else:
                print('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (Person 1) (no conversion to Roth)\n')

        if PreTaxWithdrawal[1] > 0.:
            if ConversionOccurred[1]:
                print('* Convert $'+'{:.2f}'.format(ConversionAmount[1])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth (Person 2)', end = '')
                if np.absolute(PreTaxWithdrawal[1]-ConversionAmount[1]) > 0.009:
                    print(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[1]-ConversionAmount[1]))+
                               ' from Pre-Tax that is NOT converted to Roth\n')
                else:
                    print('\n')
            else:
                print('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[1])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (Person 2) (no conversion to Roth)\n')

        # PreTax457b Withdrawal - and which person

        if PreTax457bWithdrawal[0] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+
                       ' from 457(b) account (Person 1) (no conversion to Roth, no early withdrawal penalty)\n')

        if PreTax457bWithdrawal[1] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[1])+
                       ' from 457(b) account (Person 2) (no conversion to Roth, no early withdrawal penalty)\n')

        # Roth Withdrawal - and which person

        if RothWithdrawal[0] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[0])+
                       ' from Roth account (Person 1) (after conversions, if any)\n')

        if RothWithdrawal[1] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[1])+
                       ' from Roth account (Person 2) (after conversions, if any)\n')

    else: # one person

        # PreTax Withdrawal
        if PreTaxWithdrawal[0] > 0.:
            if ConversionOccurred[0]:
                print('* Convert $'+'{:.2f}'.format(ConversionAmount[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) to Roth', end = '')
                if np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]) > 0.009:
                    print(',\n  and withdraw an additional $' +
                               '{:.2f}'.format(np.absolute(PreTaxWithdrawal[0]-ConversionAmount[0]))+
                               ' from Pre-Tax that is NOT converted to Roth\n')
                else:
                    print('\n')
            else:
                print('* Withdraw $'+'{:.2f}'.format(PreTaxWithdrawal[0])+
                           ' from Pre-Tax (Traditional IRA, 401(k), 403(b)) (no conversion to Roth)\n')

        # PreTax457b Withdrawal
        if PreTax457bWithdrawal[0] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(PreTax457bWithdrawal[0])+
                       ' from 457(b) account (no conversion to Roth, no early withdrawal penalty)\n')

        # Roth Withdrawal
        if RothWithdrawal[0] > 0.:
            print('* Withdraw $'+'{:.2f}'.format(RothWithdrawal[0])+
                       ' from Roth account (after conversions, if any)\n')

    # Cash Withdrawal - and which person
    if CashWithdrawal > 0.:
        print('* Withdraw $'+'{:.2f}'.format(CashWithdrawal)+' from Cash account\n')

    # Loop over all PostTax lots, specify how much of each to sell
    for ct in range(len(PostTaxWithdrawal)):
        if PostTaxWithdrawal[ct] > 0.:
            print('* Sell $'+'{:.2f}'.format(PostTaxWithdrawal[ct])+' from Taxable Lot #'+
                       '{:d}'.format(ct+1))
    print('')

    if ExcessCash > 0.:
        print('* Invest the $'+'{:.2f}'.format(ExcessCash)+
                   ' excess cash generated (based on values provided) in a new taxable lot\n')
    else:
        print('You should not have any excess cash to invest this year (based on values provided) - all cash '+
                   'generated is used\n')

    # Estimated tax payment
    print('* Pay $'+'{:.2f}'.format(EstimatedTaxesToPayThisYear)+' in estimated taxes to the IRS this year')
    print('Note: split total estimated taxes into the four required payments in April, June, Sept, and the' +
               ' following Jan')
    print('Note: any mandatory 20% withholding on 401(k)/403(b)/457(b) withdrawals counts towards estimated ' +
               'tax payment\n')
    if TaxesStillOwed > 0.:
        print('* Pay the IRS $'+'{:.2f}'.format(TaxesStillOwed)+' in owed taxes from last year when you file in ' +
                   'the spring\n')
    elif Refund > 0.:
        print('You should get a $'+'{:.2f}'.format(Refund)+' refund from the IRS when you file in the spring\n')
    else:
        print('You should not get a refund or owe the IRS anything when you file in the spring\n')


    print('')
    print('*** Withdrawal Info ***\n')

    # Total tax-deferred account withdrawals
    print('Total pre-tax (Traditional IRA, 401(k), 403(b), 457(b)) withdrawals (including Roth conversions): $' +
               '{:.2f}'.format(PreTaxTotalWithdrawal + PreTax457bTotalWithdrawal))

    if FilingStatus == 'MarriedFilingJointly': # two people
        # RMDs for each person
        if RMD[0,0] > 0. or RMD[0,1] > 0.:
            print('Which includes a required minimum distribution (RMD) of $' +
                   '{:.2f}'.format(RMD[0,0])+' for Person 1 and $' +
                   '{:.2f}'.format(RMD[0,1])+' for Person 2')
    else: # one person
        if RMD[0,0] > 0.:
            print('Which includes a required minimum distribution (RMD) of $' +
                   '{:.2f}'.format(RMD[0,0]))
    print('')

    # Total Roth account withdrawals
    print('Total Roth withdrawals: $' + '{:.2f}'.format(RothTotalWithdrawal)+'\n')

    # Total cash account withdrawals
    print('Total cash account withdrawals: $' + '{:.2f}'.format(CashWithdrawal)+'\n')

    # Total taxable account withdrawals
    print('Total taxable account withdrawals: $' + '{:.2f}'.format(PostTaxTotalWithdrawal)+'\n')

    # Total Withdrawals
    print('Total withdrawals across all accounts: $'+'{:.2f}'.format(TotalWithdrawalAcrossAllAccounts)+'\n')


    print('')
    print('*** Income and Cash Goals ***\n')

    print('Your standard income goal is $'+'{:.2f}'.format(StdIncomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(StdIncomeAchieved)+
               ' ('+'{:.2f}'.format(StdIncomeAchieved/StdIncomeGoal*100.)+'%) of that goal\n')
    print('Your long term capital gains income goal is $'+'{:.2f}'.format(LTCGincomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(LTCGincomeAchieved)+
               ' ('+'{:.2f}'.format(LTCGincomeAchieved/LTCGincomeGoal*100.)+'%) of that goal\n')
    print('Your total income goal is $'+'{:.2f}'.format(TotalIncomeGoal)+
               ', and the above actions achieve $'+'{:.2f}'.format(TotalIncomeAchieved)+
               ' ('+'{:.2f}'.format(TotalIncomeAchieved/TotalIncomeGoal*100.)+'%) of that goal\n')

    print('Your total needed cash (living expenses + taxes owed from last year + penalties owed from last year '+
               '+ estimated tax payment this year) is $'+'{:.2f}'.format(TotalCashNeeded)+
               ', and the above actions generate $'+'{:.2f}'.format(TotalCash)+
               ' ('+'{:.2f}'.format(TotalCash/TotalCashNeeded*100.)+'%) of that needed cash\n')


    print('')
    print('*** Taxes and Penalties ***\n')
    print('The above actions generate $'+'{:.2f}'.format(Taxes)+' in taxes and $'+'{:.2f}'.format(Penalties)+
               ' in penalties.')

    file.close()
