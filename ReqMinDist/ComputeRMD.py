# Copyright (c) 2022 Engineering Your FI #
# This work is licensed under a Creative Commons Attribution 4.0 International License. #
# Thus, feel free to modify/add content as desired, and repost as desired, but please provide attribution to
# engineeringyourfi.com (in particular https://engineeringyourfi.com/the-irs-wont-wait-forever-required-minimum-distributions/)

# ComputeRMD.py

import numpy as np

def ComputeRMD(PreTax,Age):

    # Ages for RMDs
    TableAges = np.arange(72,121,1)
    # Distribution Periods - 2022 values
    DistPer = np.array([27.4,26.5,25.5,24.6,23.7,22.9,22.0,21.1,20.2,19.4,18.5,17.7,16.8,16.0,15.2,14.4,13.7,12.9,12.2,
                        11.5,10.8,10.1,9.5,8.9,8.4,7.8,7.3,6.8,6.4,6.0,5.6,5.2,4.9,4.6,4.3,4.1,3.9,3.7,3.5,3.4,3.3,3.1,
                        3.0,2.9,2.8,2.7,2.5,2.3,2.0])

    RMD = np.round(PreTax / DistPer[np.where(TableAges==Age)[0][0]],2)
    # Withdrawal rate %
    WR = np.round(1. / DistPer[np.where(TableAges==Age)[0][0]] * 100.,2)

    return RMD, WR
