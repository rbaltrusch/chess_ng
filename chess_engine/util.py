# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 20:35:48 2021

@author: Korean_Crimson
"""

X_POSITIONS = {k: v for k, v in zip(range(8), 'abcdefgh')}

def convert(position):
    x, y = position
    return X_POSITIONS[x] + str(8 - y)

def convert_str(string):
    y = 8 - int(string[-1])
    for k, v in X_POSITIONS.items():
        if v == string[0]:
            x = k
            break
    return (x, y)
