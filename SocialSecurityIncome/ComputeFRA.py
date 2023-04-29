# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# ComputeFRA.py

# Compute Full Retirement Age (FRA) (also called Normal Retirement Age (NRA))

def ComputeFRA(BirthYear):

    # https://www.ssa.gov/oact/ProgData/nra.html

    # Year of Birth     Full Retirement Age
    # 1937 or earlier   65
    # 1938              65 and 2 months
    # 1939              65 and 4 months
    # 1940              65 and 6 months
    # 1941              65 and 8 months
    # 1942              65 and 10 months
    # 1943-1954	        66
    # 1955              66 and 2 months
    # 1956              66 and 4 months
    # 1957              66 and 6 months
    # 1958              66 and 8 months
    # 1959              66 and 10 months
    # 1960 or later     67

    if BirthYear <= 1937:
        FRA = 65.
    elif BirthYear == 1938:
        FRA = 65. + 2./12.
    elif BirthYear == 1939:
        FRA = 65. + 4./12.
    elif BirthYear == 1940:
        FRA = 65. + 6./12.
    elif BirthYear == 1941:
        FRA = 65. + 8./12.
    elif BirthYear == 1942:
        FRA = 65. + 10./12.
    elif BirthYear >= 1943 and BirthYear <= 1954:
        FRA = 66.
    elif BirthYear == 1955:
        FRA = 66. + 2./12.
    elif BirthYear == 1956:
        FRA = 66. + 4./12.
    elif BirthYear == 1957:
        FRA = 66. + 6./12.
    elif BirthYear == 1958:
        FRA = 66. + 8./12.
    elif BirthYear == 1959:
        FRA = 66. + 10./12.
    else: # 1960 or later
        FRA = 67.

    return FRA