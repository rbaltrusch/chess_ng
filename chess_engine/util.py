# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 20:35:48 2021

@author: Korean_Crimson
"""

X_POSITIONS = {k: v for k, v in zip(range(8), 'abcdefgh')}

def convert(position):
    x, y = position
    return X_POSITIONS[x] + str(8 - y)
