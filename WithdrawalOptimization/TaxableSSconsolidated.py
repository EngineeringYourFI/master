# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-much-of-my-social-security-income-will-be-taxed/)

# TaxableSSconsolidated.py
import sys

# Compute how much of SS income is taxable, using more consolidated form of algorithm (vs using the IRS worksheet language)

def TaxableSSconsolidated(NonSSincome,TotalSSincome,FilingStatus):

    # Bracket info based on filing status
    if FilingStatus=='MarriedFilingJointly':
        MinOtherIncomeForSStoBeTaxed = 32000.   #MI
        DeltaToTopOf50percentTaxableBracket = 12000.  #\Delta
    elif FilingStatus=='Single' or FilingStatus=='HeadOfHousehold' or FilingStatus=='MarriedFilingSeparately' or \
            FilingStatus=='QualifyingWidow(er)':
        MinOtherIncomeForSStoBeTaxed = 25000.   #MI
        DeltaToTopOf50percentTaxableBracket = 9000.  #\Delta
    else:
        print('Filing Status not recognized. Exiting.')
        sys.exit()

    # If total non-SS income plus half the SS income do not reach minimum income, then none of the SSincome is taxable
    if (TotalSSincome*0.5 + NonSSincome) < MinOtherIncomeForSStoBeTaxed:
        TaxableSSincome = 0.
        return TaxableSSincome

    # If total non-SS income plus half the SS income MINUS minimum income (so the amount over that min income value)
    # exceeds DeltaToTopOf50percentTaxableBracket (range between the bottom and top of the 50% bracket):
    if (TotalSSincome*0.5 + NonSSincome - MinOtherIncomeForSStoBeTaxed) > DeltaToTopOf50percentTaxableBracket:
        # Then compute amount over the top of the 50% bracket
        DeltaOver50percentTaxableBracket = TotalSSincome*0.5 + NonSSincome - MinOtherIncomeForSStoBeTaxed - \
                                           DeltaToTopOf50percentTaxableBracket

        # And set the taxable amount in the 50% bracket as the smaller of the bracket length * 0.5 or half the TotalSSincome
        if TotalSSincome*0.5 > DeltaToTopOf50percentTaxableBracket/2.:
            TaxableSSin50percentBracket = DeltaToTopOf50percentTaxableBracket/2.
        else:
            TaxableSSin50percentBracket = TotalSSincome*0.5

    else: # Then nothing over the top of the 50% bracket
        DeltaOver50percentTaxableBracket = 0.

        # And set the taxable amount in the 50% bracket as the smaller of (TotalSSincome*0.5 + NonSSincome -
        # MinOtherIncomeForSStoBeTaxed)/2 or half the TotalSSincome
        if TotalSSincome*0.5 > (TotalSSincome*0.5 + NonSSincome - MinOtherIncomeForSStoBeTaxed)/2.:
            TaxableSSin50percentBracket = (TotalSSincome*0.5 + NonSSincome - MinOtherIncomeForSStoBeTaxed)/2.
        else:
            TaxableSSin50percentBracket = TotalSSincome*0.5

    # The taxable amount of SSincome is equal to TaxableSSin50percentBracket + 85% of amount over 50% bracket, until it
    # reaches 85% of the SSincome, at which it's set to 85% of SSincome for all higher values
    # Thus set TaxableSSincome to the smaller of TaxableSSin50percentBracket+0.85*DeltaOver50percentTaxableBracket vs
    # 0.85*TotalSSincome
    if 0.85*TotalSSincome > TaxableSSin50percentBracket+0.85*DeltaOver50percentTaxableBracket:
        TaxableSSincome = TaxableSSin50percentBracket+0.85*DeltaOver50percentTaxableBracket
    else:
        TaxableSSincome = 0.85*TotalSSincome

    return TaxableSSincome
