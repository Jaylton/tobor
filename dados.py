# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 19:48:20 2022

@author: jaylt
"""
import matplotlib.pyplot as plt
import pandas as pd 

base = pd.read_csv('erro.csv')
#base = base.iloc[0:900,:]
base['time'] = base['time'] - min(base['time'])
time = base['time']
print('tempo: {:.2f}s'.format(max(time)))
position_x = base['position_x']
position_y = base['position_y']
error = abs(base['error'])

plt.plot(time, error)
plt.figure()
plt.plot(position_x, position_y)
plt.xlim([-3, 3])
plt.show()