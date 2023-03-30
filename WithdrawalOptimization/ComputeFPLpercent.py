# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/how-to-compute-aca-obamacare-subsidies/)

# ComputeFPLpercent.py

# Compute percentage of Federal Poverty Level (FPL), for particular income and family size

# 2022 federal poverty levels - used for 2023 ACA coverage (except CHIP eligibility, which uses 2023 FPL)
# For contiguous US: $13,590 for one person, and $4,720 for each additional person.
# For Alaska: $16,990 for one person, and $5900 for each additional person.
# For Hawaii: $15,630 for one person, and $5430 for each additional person.

def ComputeFPLpercent(Income, NumPeople,Residence):

    NumPeopleBeyondOne = NumPeople - 1.

    if Residence == 'Alaska':
        FPL = 16990. + NumPeopleBeyondOne*5900.
    elif Residence == 'Hawaii':
        FPL = 15630. + NumPeopleBeyondOne*5430.
    else:
        FPL = 13590. + NumPeopleBeyondOne*4720.

    FPLpercent = Income/FPL*100.

    return FPLpercent