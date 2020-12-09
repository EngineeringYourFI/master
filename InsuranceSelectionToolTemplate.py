# Copyright (c) 2019 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular engineeringyourfi.com/choosing-your-health-insurance-plan-with-math)

# InsuranceSelectionToolTemplate.py

# To decide on Standard plan vs High Deductible Health Plan (HDHP)

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------------------------------------------
# Inputs

# Monthly premiums:
StandardPremium = 93
HDHPpremium = 61

# Copays / office visit cost
StandardPrimaryCopay = 30
StandardSpecialistCopay = 40

HDHPprimaryOfficeVisitCost = 103.05
# HDHPspecialistCost = ???
HDHPurgentCareVisit = 165

# Deductible (in network)
StandardDeductibleIndividual = 1000
StandardDeductibleFamily = 3000

# HDHPdeductibleIndividual = 1600 - not relevant for families, must meet family deductible for individuals within family plan
HDHPdeductibleFamily = 3200

# Co-insurance
StandardCoinsurance = 0.8
HDHPcoinsurance = 0.8

# Out of pocket max
Standard_OOPmaxIndividual = 4500
Standard_OOPmaxFamily = 9000

HDHP_OOPmaxIndividual = 6850
HDHP_OOPmaxFamily = 10000

# Company HSA contribution ($125*12 monthly payments)
Company_HSAcontribution = 1500

# Employee + Dependents can contribute up to $7100 per year (includes the Company contribution)
HSAmaxContribution = 5600 # 7100-1500
# Pro-rated if not at company the entire year though

# The maximum you can contribute if you have the standard plan
FSAmaxContribution = 2750

# Prescriptions:
StandardPrescriptionCopay = 10
HDHPexpectedPrescriptionCost = 15 # Conservative
# HDHP pays full cost of drugs until deductible met, then starts paying the Coinsurance rate of 80% - just like other
# medical expenses

# Tax savings rate - federal income tax rate + FICA
TaxSavingsRate = 0.22 + 0.0765

# --------------------------------------------------------------------------------------------------------------
# The cost of an individual within a employee+dependents plan

# x axis = medical expense (other than pharmacy or office visits)
Expense = np.arange(0,30001)

# Initialize
StandardCost = np.zeros(len(Expense))
HDHPcost = np.zeros(len(Expense))

StandardBasePremium = (1-TaxSavingsRate)*StandardPremium*12
HDHPbasePremium = (1-TaxSavingsRate)*HDHPpremium*12 - Company_HSAcontribution

for ct in range(0,len(Expense)):

    # Premiums - pay no matter what
    StandardCost[ct] = StandardBasePremium
    # Adding deductible
    if Expense[ct] < StandardDeductibleIndividual:
        # StandardCost[ct] += Expense[ct] # assuming not doing FSA
        StandardCost[ct] += (1-TaxSavingsRate)*Expense[ct] # assuming doing max FSA (FSAmaxContribution), which is > StandardDeductibleIndividual
    else:
        StandardCost[ct] += (1-TaxSavingsRate)*StandardDeductibleIndividual # assuming FSAmaxContribution (2650) > StandardDeductibleIndividual (1000)
        # Then add the 20% you must pay after deductible
        AmountOverDeductible=Expense[ct]-StandardDeductibleIndividual
        AmountOverDeductibleCoinsurance=(1-StandardCoinsurance)*AmountOverDeductible #the 20% we'd pay
        if (StandardDeductibleIndividual+AmountOverDeductibleCoinsurance)<FSAmaxContribution: #so can use FSA funds
            StandardCost[ct]+=(1-TaxSavingsRate)*AmountOverDeductibleCoinsurance
        else:
            StandardCost[ct]+=(1-TaxSavingsRate)*(FSAmaxContribution-StandardDeductibleIndividual)
            StandardCost[ct]+=(StandardDeductibleIndividual+AmountOverDeductibleCoinsurance)-FSAmaxContribution

        # And cut off at max OOP if you reach that
        if (StandardDeductibleIndividual+AmountOverDeductibleCoinsurance)>=Standard_OOPmaxIndividual:
            # If Standard_OOPmaxIndividual (4500) < FSAmaxContribution (2650), then can just use Standard_OOPmaxIndividual
            if Standard_OOPmaxIndividual<FSAmaxContribution: # unlikely to ever be true - only true for HSA when maxing
                # The base premium (which already has the tax savings), plus the max OOP (with tax savings)
                StandardCost[ct]=StandardBasePremium+(1-TaxSavingsRate)*Standard_OOPmaxIndividual
            else:
                # The base premium (which already has the tax savings), plus the max HSA account (with tax savings)
                StandardCost[ct]=StandardBasePremium+(1-TaxSavingsRate)*FSAmaxContribution
                # Then add the remaining amount up to the OOP max
                StandardCost[ct]+=Standard_OOPmaxIndividual-FSAmaxContribution


    HDHPcost[ct] = HDHPbasePremium
    if Expense[ct] < HDHPdeductibleFamily:
        HDHPcost[ct] += (1-TaxSavingsRate)*Expense[ct]
    else:
        HDHPcost[ct] += (1-TaxSavingsRate)*HDHPdeductibleFamily # assuming we have enough in HSA to cover deductible
        # Then add the 20% you must pay after deductible
        AmountOverDeductible = Expense[ct] - HDHPdeductibleFamily
        AmountOverDeductibleCoinsurance = (1 - HDHPcoinsurance)*AmountOverDeductible # the 20% we'd pay
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)<(HSAmaxContribution+Company_HSAcontribution): # so can use HSA funds
            HDHPcost[ct] += (1-TaxSavingsRate)*AmountOverDeductibleCoinsurance
        else:
            HDHPcost[ct] += (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution-HDHPdeductibleFamily)
            HDHPcost[ct] += (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance) - (HSAmaxContribution+Company_HSAcontribution)

        # And cut off at max OOP if you reach that
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)>=HDHP_OOPmaxIndividual:
            # If HDHP_OOPmaxIndividual < HSAmaxContribution+Company_HSAcontribution, then can just use HDHP_OOPmaxIndividual
            if HDHP_OOPmaxIndividual < (HSAmaxContribution+Company_HSAcontribution):
                # The base premium (which already has the tax savings), plus the max OOP (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * HDHP_OOPmaxIndividual
            else:
                # The base premium (which already has the tax savings), plus the max HSA account (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution)
                # Then add the remaining amount up to the OOP max
                HDHPcost[ct] += HDHP_OOPmaxIndividual - (HSAmaxContribution + Company_HSAcontribution)

plt.figure(1)
plt.plot(Expense, StandardCost, 'r-',label='Standard')
plt.plot(Expense, HDHPcost, 'b-',label='HDHP')
plt.plot(Expense, StandardCost-HDHPcost, 'g-', label='Standard-HDHP')
plt.xlabel('Medical Expenses ($)')
plt.ylabel('Out Of Pocket Expenses ($)')
plt.legend(loc='best')
plt.grid()
# plt.savefig('CostComparison.png',dpi=1000)
plt.savefig('CostComparison.png')
plt.close()

# --------------------------------------------------------------------------------------------------------------
# Now doing the same analysis for full family expenses (vs individual within family)

# Initialize
# x axis = medical expense (other than pharmacy or office visits)
Expense = np.arange(0,50001) # must be further out than individual
StandardCost = np.zeros(len(Expense))
HDHPcost = np.zeros(len(Expense))

for ct in range(0,len(Expense)):

    # Premiums - pay no matter what
    StandardCost[ct] = StandardBasePremium
    # Adding deductible
    if Expense[ct] < StandardDeductibleFamily:
        StandardCost[ct] += Expense[ct] # assuming not doing FSA, since can't know as easily
    else:
        StandardCost[ct] += StandardDeductibleFamily
        # Then add the 20% you must pay after deductible
        StandardCost[ct] += (1-StandardCoinsurance)*(Expense[ct]-StandardDeductibleFamily)
        # And cut off at max OOP if you reach that
        if ((StandardCost[ct]-StandardBasePremium) >= Standard_OOPmaxFamily):
            StandardCost[ct] = StandardBasePremium + Standard_OOPmaxFamily

    HDHPcost[ct] = HDHPbasePremium
    if Expense[ct] < HDHPdeductibleFamily:
        HDHPcost[ct] += (1-TaxSavingsRate)*Expense[ct]
    else:
        HDHPcost[ct] += (1-TaxSavingsRate)*HDHPdeductibleFamily # assuming we have enough in HSA to cover deductible
        # Then add the 20% you must pay after deductible
        AmountOverDeductible = Expense[ct] - HDHPdeductibleFamily
        AmountOverDeductibleCoinsurance = (1 - HDHPcoinsurance)*AmountOverDeductible #the 20% we'd pay
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)<(HSAmaxContribution+Company_HSAcontribution): #so can use HSA funds
            HDHPcost[ct] += (1-TaxSavingsRate)*AmountOverDeductibleCoinsurance
        else:
            HDHPcost[ct] += (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution-HDHPdeductibleFamily)
            HDHPcost[ct] += (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance) - (HSAmaxContribution+Company_HSAcontribution)

        # And cut off at max OOP if you reach that
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)>=HDHP_OOPmaxFamily:
            # If HDHP_OOPmaxIndividual < HSAmaxContribution+Company_HSAcontribution, then can just use HDHP_OOPmaxIndividual
            if HDHP_OOPmaxFamily < (HSAmaxContribution+Company_HSAcontribution):
                # The base premium (which already has the tax savings), plus the max OOP (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * HDHP_OOPmaxFamily
            else:
                # The base premium (which already has the tax savings), plus the max HSA account (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution)
                # Then add the remaining amount up to the OOP max
                HDHPcost[ct] += HDHP_OOPmaxFamily - (HSAmaxContribution + Company_HSAcontribution)

plt.figure(2)
plt.plot(Expense, StandardCost, 'r-',label='Standard')
plt.plot(Expense, HDHPcost, 'b-',label='HDHP')
plt.plot(Expense, StandardCost-HDHPcost, 'g-', label='Standard-HDHP')
plt.xlabel('Medical Expenses ($)')
plt.ylabel('Out Of Pocket Expenses ($)')
plt.legend(loc='best')
plt.grid()
# plt.savefig('CostComparisonFullFamilyExpense.png',dpi=1000)
plt.savefig('CostComparisonFullFamilyExpense.png')
plt.close()


# --------------------------------------------------------------------------------------------------------------
# Look at number of doctor visits, see if/when it makes standard plan more viable
# This is worst case scenario for HDHP with no other medical expenses, because if there were other medical expenses,
# you'd hit your deductible a lot faster with these office visits
# Start with primary care visit, which is $30 on Standard (standard plan) and $103.05 for HDHP
# StandardPrimaryCopay = 30 from above
# HDHPprimaryOfficeVisitCost = 103.05 from above
# Below is for an individual within a family plan:

# x axis = number of visits
VisitQuantity = np.arange(1,101)

# Initialize
StandardCost = np.zeros(len(VisitQuantity))
HDHPcost = np.zeros(len(VisitQuantity))

StandardBasePremium = (1-TaxSavingsRate)*StandardPremium*12
HDHPbasePremium = (1-TaxSavingsRate)*HDHPpremium*12 - Company_HSAcontribution

for ct in range(0,len(VisitQuantity)):

    # Premiums - pay no matter what
    StandardCost[ct] = StandardBasePremium

    # Confirmed that copays do NOT count towards deductible (and thus I assume they also do not count toward OOP max):
    # "Deductible amounts are separate from and not reduced by Copayments."

    # assuming doing max FSA (FSAmaxContribution)
    if StandardPrimaryCopay*VisitQuantity[ct] < FSAmaxContribution:
        StandardCost[ct] += (1-TaxSavingsRate)*StandardPrimaryCopay*VisitQuantity[ct]
    else:
        StandardCost[ct] += (1-TaxSavingsRate)*FSAmaxContribution
        StandardCost[ct] += StandardPrimaryCopay*VisitQuantity[ct] - FSAmaxContribution

    # Premiums - pay no matter what
    HDHPcost[ct] = HDHPbasePremium

    # assuming doing max HSA (HSAmaxContribution+Company_HSAcontribution = 7100)

    # Since paying for visits in full, definitely does count toward deductible
    if HDHPprimaryOfficeVisitCost*VisitQuantity[ct] < HDHPdeductibleFamily:
        HDHPcost[ct] += (1-TaxSavingsRate)*HDHPprimaryOfficeVisitCost*VisitQuantity[ct]
    else:
        HDHPcost[ct]+=(1-TaxSavingsRate)*HDHPdeductibleFamily # assuming we have enough in HSA to cover deductible
        # Then add the 20% you must pay after deductible
        AmountOverDeductible = HDHPprimaryOfficeVisitCost*VisitQuantity[ct] - HDHPdeductibleFamily
        AmountOverDeductibleCoinsurance = (1 - HDHPcoinsurance)*AmountOverDeductible #the 20% we'd pay
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)<(HSAmaxContribution+Company_HSAcontribution):  #so can use HSA funds
            HDHPcost[ct] += (1-TaxSavingsRate)*AmountOverDeductibleCoinsurance
        else:
            HDHPcost[ct] += (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution-HDHPdeductibleFamily)
            HDHPcost[ct] += (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance) - (HSAmaxContribution+Company_HSAcontribution)

        # And cut off at max OOP if you reach that
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)>=HDHP_OOPmaxIndividual:
            # If HDHP_OOPmaxIndividual < HSAmaxContribution+Company_HSAcontribution, then can just use HDHP_OOPmaxIndividual
            if HDHP_OOPmaxIndividual < (HSAmaxContribution+Company_HSAcontribution):
                # The base premium (which already has the tax savings), plus the max OOP (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * HDHP_OOPmaxIndividual
            else:
                # The base premium (which already has the tax savings), plus the max HSA account (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution)
                # Then add the remaining amount up to the OOP max
                HDHPcost[ct] += HDHP_OOPmaxIndividual - (HSAmaxContribution + Company_HSAcontribution)

plt.figure(1)
plt.plot(VisitQuantity, StandardCost, 'r-',label='Standard')
plt.plot(VisitQuantity, HDHPcost, 'b-',label='HDHP')
plt.plot(VisitQuantity, StandardCost-HDHPcost, 'g-', label='Standard-HDHP')
plt.xlabel('Number of Primary Care Physician Visits')
plt.ylabel('Out Of Pocket Expenses ($)')
plt.legend(loc='best')
plt.grid()
# plt.savefig('PrimaryCareVisitCostComparison.png',dpi=1000)
plt.savefig('PrimaryCareVisitCostComparison.png')
plt.close()



# --------------------------------------------------------------------------------------------------------------
# Now looking at number of urgent care visits, see if/when it makes standard plan more viable
# This is worst case scenario for HDHP with no other medical expenses, because if there were other medical expenses,
# you'd hit your deductible a lot faster with these office visits
# Assume urgent care visits are $30 on Standard plan (optimistic) and $165 for HDHP
# StandardPrimaryCopay = 30 from above
# HDHPurgentCareVisit = 165 from above
# Below is for an individual within a family plan:

# x axis = number of visits
VisitQuantity = np.arange(1,101)

# Initialize
StandardCost = np.zeros(len(VisitQuantity))
HDHPcost = np.zeros(len(VisitQuantity))

StandardBasePremium = (1-TaxSavingsRate)*StandardPremium*12
HDHPbasePremium = (1-TaxSavingsRate)*HDHPpremium*12 - Company_HSAcontribution

for ct in range(0,len(VisitQuantity)):

    # Premiums - pay no matter what
    StandardCost[ct] = StandardBasePremium

    # Confirmed that copays do NOT count towards deductible (and thus I assume they also do not count toward OOP max):
    # "Deductible amounts are separate from and not reduced by Copayments."

    # assuming doing max FSA (FSAmaxContribution)
    if StandardPrimaryCopay*VisitQuantity[ct] < FSAmaxContribution:
        StandardCost[ct] += (1-TaxSavingsRate)*StandardPrimaryCopay*VisitQuantity[ct]
    else:
        StandardCost[ct] += (1-TaxSavingsRate)*FSAmaxContribution
        StandardCost[ct] += StandardPrimaryCopay*VisitQuantity[ct] - FSAmaxContribution

    # Premiums - pay no matter what
    HDHPcost[ct] = HDHPbasePremium

    # assuming doing max HSA (HSAmaxContribution+Company_HSAcontribution = 7100)

    # Since paying for visits in full, definitely does count toward deductible
    if HDHPurgentCareVisit*VisitQuantity[ct] < HDHPdeductibleFamily:
        HDHPcost[ct] += (1-TaxSavingsRate)*HDHPurgentCareVisit*VisitQuantity[ct]
    else:
        HDHPcost[ct]+=(1-TaxSavingsRate)*HDHPdeductibleFamily # assuming we have enough in HSA to cover deductible
        # Then add the 20% you must pay after deductible
        AmountOverDeductible = HDHPurgentCareVisit*VisitQuantity[ct] - HDHPdeductibleFamily
        AmountOverDeductibleCoinsurance = (1 - HDHPcoinsurance)*AmountOverDeductible #the 20% we'd pay
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)<(HSAmaxContribution+Company_HSAcontribution):  #so can use HSA funds
            HDHPcost[ct] += (1-TaxSavingsRate)*AmountOverDeductibleCoinsurance
        else:
            HDHPcost[ct] += (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution-HDHPdeductibleFamily)
            HDHPcost[ct] += (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance) - (HSAmaxContribution+Company_HSAcontribution)

        # And cut off at max OOP if you reach that
        if (HDHPdeductibleFamily+AmountOverDeductibleCoinsurance)>=HDHP_OOPmaxIndividual:
            # If HDHP_OOPmaxIndividual < HSAmaxContribution+Company_HSAcontribution, then can just use HDHP_OOPmaxIndividual
            if HDHP_OOPmaxIndividual < (HSAmaxContribution+Company_HSAcontribution):
                # The base premium (which already has the tax savings), plus the max OOP (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * HDHP_OOPmaxIndividual
            else:
                # The base premium (which already has the tax savings), plus the max HSA account (with tax savings)
                HDHPcost[ct] = HDHPbasePremium + (1 - TaxSavingsRate) * (HSAmaxContribution+Company_HSAcontribution)
                # Then add the remaining amount up to the OOP max
                HDHPcost[ct] += HDHP_OOPmaxIndividual - (HSAmaxContribution + Company_HSAcontribution)

plt.figure(1)
plt.plot(VisitQuantity, StandardCost, 'r-',label='Standard')
plt.plot(VisitQuantity, HDHPcost, 'b-',label='HDHP')
plt.plot(VisitQuantity, StandardCost-HDHPcost, 'g-', label='Standard-HDHP')
plt.xlabel('Number of Urgent Care Visits')
plt.ylabel('Out Of Pocket Expenses ($)')
plt.legend(loc='best')
plt.grid()
# plt.savefig('UrgentCareVisitCostComparison.png',dpi=1000)
plt.savefig('UrgentCareVisitCostComparison.png')
plt.close()
