# Part 1: Use the following data for this assignment:

import pandas as pd
import numpy as np

np.random.seed(12345)

df = pd.DataFrame([np.random.normal(32000,200000,3650), 
                   np.random.normal(43000,100000,3650), 
                   np.random.normal(43500,140000,3650), 
                   np.random.normal(48000,70000,3650)], 
                  index=[1992,1993,1994,1995])
df

# Part 2

df = df.transpose()

df.describe()

# Part 3: Calculating 95% CondfidenceInterval

import math

mean = list(df.mean())
std = list(df.std())
y1 = []

for i in range (4):
    y1.append(1.975 * (std[i] / math.sqrt(len(df)))) #Formula for S_x
    
y1

# Part 4: Building our Barchart
nearest = 250
Y = 40500

df_p = pd.DataFrame()

df_p['diff'] = nearest*((Y - df.mean())//nearest)

df_p['sign'] = df_p['diff'].abs()/df_p['diff']

old_range = abs(df_p['diff']).min(), abs(df_p['diff']).max()

new_range = .6,2

df_p['shade'] = df_p['sign']*np.interp(abs(df_p['diff']), old_range, new_range)

# changing color of the bars with respect to Y

shade = list(df_p['shade'])

from matplotlib import cm

#Sequential Colormaps from matplotlib (Online Library)
green = cm.Greens
red = cm.Reds

# using shades greens when diff is pos
# using Reds when when diff is neg

color = ['White' if  x == 0 else red(abs(x))
         if x<0 else green(abs(x)) for x in shade]

import matplotlib.pyplot as plt

%matplotlib inline

plt.figure(num=None, figsize=(7, 7), dpi=85, facecolor='whitesmoke', edgecolor='dimgray')

plt.bar(range(len(df.columns)), height = df.values.mean(axis = 0), 
        yerr=y1, error_kw={'capsize': 10, 'elinewidth': 2.5, 'alpha':0.9}, color = color)

plt.axhline(y=Y, color = 'black', label = 'Y')

plt.text(4, 41000, "40500")

plt.xticks(range(len(df.columns)), df.columns)

plt.title('Generated Data Between 1992 - 95')

# remove all the ticks (both axes), and tick labels on the Y axis
plt.tick_params(top='off', bottom='off',  right='off', labelbottom='on')

# remove the frame of the chart
for spine in plt.gca().spines.values():
    spine.set_visible(False)

plt.show()
