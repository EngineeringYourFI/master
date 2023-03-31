# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/fire-withdrawal-strategy-algorithms/)

# ComputeOutputs.py

import numpy as np

def ComputeOutputs(ProjArrays,IVdict,FilingStatus,IncDict):

    # number of people (1 or 2)
    NumPeople = np.size(IVdict['PreTaxIV'])

    # Compute PreTax withdrawal
    PreTaxIV = IVdict['PreTaxIV']
    PreTaxFinalBal = ProjArrays['PreTax'][0,:]
    PreTaxWithdrawal = PreTaxIV - PreTaxFinalBal
    PreTaxTotalWithdrawal = np.sum(PreTaxWithdrawal)

    # Compute PreTax457b withdrawal
    PreTax457bIV = IVdict['PreTax457bIV']
    PreTax457bFinalBal = ProjArrays['PreTax457b'][0,:]
    PreTax457bWithdrawal = PreTax457bIV - PreTax457bFinalBal
    PreTax457bTotalWithdrawal = np.sum(PreTax457bWithdrawal)

    ConversionOccurred = np.zeros(NumPeople,dtype=bool)
    ConversionAmount = np.zeros(NumPeople)
    for ct in range(0,len(ProjArrays['RothConversionAmount'])):
        if ProjArrays['RothConversionAmount'][ct] > 0:
            if ProjArrays['RothConversionPerson'][ct] == 0 and ProjArrays['RothConversionAge'][ct] == ProjArrays['Age'][0,0]:
                ConversionOccurred[0] = True
                ConversionAmount[0] = ProjArrays['RothConversionAmount'][ct]
            if ProjArrays['RothConversionPerson'][ct] == 1 and ProjArrays['RothConversionAge'][ct] == ProjArrays['Age'][0,1]:
                ConversionOccurred[1] = True
                ConversionAmount[1] = ProjArrays['RothConversionAmount'][ct]

    # Compute Roth withdrawal
    RothIV = IVdict['RothIV']
    RothFinalBal = ProjArrays['Roth'][0,:]
    RothDelta = RothIV - RothFinalBal
    # Derivation of RothWithdrawal:
    # RothFinalBal = RothIV + ConversionAmount - RothWithdrawal
    # RothWithdrawal = RothIV + ConversionAmount - RothFinalBal
    # RothWithdrawal = RothIV - RothFinalBal + ConversionAmount
    # RothWithdrawal = RothDelta + ConversionAmount
    RothWithdrawal = RothDelta + ConversionAmount
    RothTotalWithdrawal = np.sum(RothWithdrawal)

    # Compute cash account withdrawal
    CashIV = IVdict['CashCushion']
    CashFinalBal = ProjArrays['CashCushion'][0]
    CashWithdrawal = CashIV - CashFinalBal

    # Compute PostTax withdrawals
    PostTaxIV = IVdict['PostTaxIV']
    PostTaxFinalBal = ProjArrays['PostTax'][0,:]
    PostTaxWithdrawal = PostTaxIV - PostTaxFinalBal[0:len(PostTaxIV)]
    PostTaxTotalWithdrawal = np.sum(PostTaxWithdrawal)

    # PostTax cap gains
    PostTaxIVCG = IVdict['CurrentUnrealizedCapGains']
    PostTaxFinalCG = ProjArrays['PostTaxCG'][0,:]
    PostTaxFinalCGtotal = ProjArrays['CapGainsTotal'][0]

    # Compute ExcessCash invested in new lot
    if len(PostTaxFinalBal) > len(PostTaxIV):
        ExcessCash = PostTaxFinalBal[-1]
    else:
        ExcessCash = 0.

    # Income goals and results, as well as cash
    StdIncomeGoal = IncDict['MaxStandardIncome']
    StdIncomeAchieved = ProjArrays['TotalStandardIncome'][0]
    LTCGincomeGoal = IncDict['SpecifiedIncome'] - IncDict['MaxStandardIncome']
    LTCGincomeAchieved = ProjArrays['TotalLTcapGainsIncome'][0]
    TotalIncomeGoal = IncDict['SpecifiedIncome']
    TotalIncomeAchieved = ProjArrays['TotalIncome'][0]

    TotalCash = ProjArrays['TotalCash'][0]
    TotalCashNeeded = ProjArrays['TotalCashNeeded'][0]

    # Taxes and Penalties
    Taxes = ProjArrays['Taxes'][0]
    Penalties = ProjArrays['Penalties'][0]

    TaxesPaidPrevYear = IVdict['TaxesPaidPrevYear']
    TaxesGenPrevYear = IVdict['TaxesGenPrevYear']
    EstimatedTaxesToPayThisYear = IVdict['TaxesGenPrevYear']

    # If taxes paid last year exceed what was owed, collect refund
    if TaxesPaidPrevYear - TaxesGenPrevYear > 0.:
        Refund = TaxesPaidPrevYear - TaxesGenPrevYear
        TaxesStillOwed = 0.
    else:
        Refund = 0.
        TaxesStillOwed = TaxesGenPrevYear - TaxesPaidPrevYear

    SubsidyDelta = ProjArrays['SubsidyDelta']

    TotalIV = np.sum(PreTaxIV) + np.sum(PreTax457bIV) + np.sum(RothIV) + np.sum(CashIV) + np.sum(PostTaxIV)
    TotalFinalBal = np.sum(PreTaxFinalBal) + np.sum(PreTax457bFinalBal) + np.sum(RothFinalBal) + \
                    np.sum(CashFinalBal) + np.sum(PostTaxFinalBal)
    TotalWithdrawalAcrossAllAccounts = PreTaxTotalWithdrawal + PreTax457bTotalWithdrawal + RothTotalWithdrawal + \
                                       CashWithdrawal + PostTaxTotalWithdrawal

    RMD = ProjArrays['RMD']

    # Create OutputDict
    OutputDict = {'PreTaxIV': PreTaxIV,
                  'PreTaxFinalBal': PreTaxFinalBal,
                  'PreTaxWithdrawal': PreTaxWithdrawal,
                  'PreTaxTotalWithdrawal': PreTaxTotalWithdrawal,
                  'PreTax457bIV': PreTax457bIV,
                  'PreTax457bFinalBal': PreTax457bFinalBal,
                  'PreTax457bWithdrawal': PreTax457bWithdrawal,
                  'PreTax457bTotalWithdrawal': PreTax457bTotalWithdrawal,
                  'ConversionOccurred': ConversionOccurred,
                  'ConversionAmount': ConversionAmount,
                  'RothIV': RothIV,
                  'RothFinalBal': RothFinalBal,
                  'RothWithdrawal': RothWithdrawal,
                  'RothTotalWithdrawal': RothTotalWithdrawal,
                  'CashIV': CashIV,
                  'CashFinalBal': CashFinalBal,
                  'CashWithdrawal': CashWithdrawal,
                  'PostTaxIV': PostTaxIV,
                  'PostTaxFinalBal': PostTaxFinalBal,
                  'PostTaxWithdrawal': PostTaxWithdrawal,
                  'PostTaxTotalWithdrawal': PostTaxTotalWithdrawal,
                  'PostTaxIVCG': PostTaxIVCG,
                  'PostTaxFinalCG': PostTaxFinalCG,
                  'PostTaxFinalCGtotal': PostTaxFinalCGtotal,
                  'TotalCash': TotalCash,
                  'TotalCashNeeded': TotalCashNeeded,
                  'ExcessCash': ExcessCash,
                  'StdIncomeGoal': StdIncomeGoal,
                  'StdIncomeAchieved': StdIncomeAchieved,
                  'LTCGincomeGoal': LTCGincomeGoal,
                  'LTCGincomeAchieved': LTCGincomeAchieved,
                  'TotalIncomeGoal': TotalIncomeGoal,
                  'TotalIncomeAchieved': TotalIncomeAchieved,
                  'Taxes': Taxes,
                  'Penalties': Penalties,
                  'TotalIV': TotalIV,
                  'TotalFinalBal': TotalFinalBal,
                  'TotalWithdrawalAcrossAllAccounts': TotalWithdrawalAcrossAllAccounts,
                  'Refund': Refund,
                  'TaxesStillOwed': TaxesStillOwed,
                  'EstimatedTaxesToPayThisYear': EstimatedTaxesToPayThisYear,
                  'RMD': RMD,
                  'SubsidyDelta': SubsidyDelta}

    return OutputDict
