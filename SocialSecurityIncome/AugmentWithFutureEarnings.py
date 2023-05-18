# Copyright (c) 2023 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/computing-social-security-income/)

# AugmentWithFutureEarnings.py

import numpy as np

# Augment Income array if future earnings expected

def AugmentWithFutureEarnings(Income,BirthDate,StartingAge):

    # Unpack needed dicts
    ExpectedFutureIncome = Income['ExpectedFutureIncome']
    ExpectedFutureIncomeNumYears = Income['ExpectedFutureIncomeNumYears']
    BirthYear = BirthDate['Year']
    BirthMonth = BirthDate['Month']

    BirthYearPlusMonth = BirthYear + (BirthMonth-1)/12

    if ExpectedFutureIncomeNumYears > 0 and ExpectedFutureIncome > 0.:
        for ct in range(0,ExpectedFutureIncomeNumYears):
            AddedYear = Income['IncomeYears'][-1]+1
            # Note: if the future year of earnings reaches the year you start RIB, ignore those expected earnings
            if AddedYear < np.floor(BirthYearPlusMonth + StartingAge):
                Income['IncomeYears'] = np.append(Income['IncomeYears'],AddedYear)
                Income['IncomeArray'] = np.append(Income['IncomeArray'],ExpectedFutureIncome)
            else:
                break
