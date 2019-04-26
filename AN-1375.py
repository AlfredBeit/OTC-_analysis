#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 11:40:23 2019

@author: a.bittaraev
"""
import warnings
warnings.filterwarnings('ignore')
import scipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from scipy.optimize import minimize 




df = pd.read_csv('/Users/a.bittaraev/desktop/usdjpy_otc.csv', index_col=0)

df.head()

df['created_at'] = pd.to_datetime(df['created_at'], format='%Y%m%d %H:%M:%S.%f')

#df['weekday'] = df['created_at'].apply( lambda obj: obj.dayofweek) 

#df_WD = df.loc[df['weekday'] < 5 ] #include only 

df_WD=df

""" 
for OTC include weekends, for regular exclude

"""

df_WD["quote"] = df_WD["close"].astype(float)

df_WD.drop("close", axis=1, inplace=True)
 
df_WD.head()



"""
sqrt_root (perc)

param = perc is a percentile
of log-ret
Returns dict with keys = (dt,quantiles)
dts is a  time step of log-ret
quantiles  is a data quantile of corresponding log-ret distribution
defined by parameter perc

"""

def sqrt_root (perc):

     d = {'dts': [], 'quantiles': []}

     dt=1 #initial time step
     
     
     while dt <= 300:
 
         df_sec = df_WD.loc[ (df_WD.index%dt)==0 ]
     
         df_sec.loc[:,'log_ret'] = np.log(df_sec.quote)  - np.log(df_sec.quote.shift(1))
         
         df_sec.loc[:,'log_returns'] = df_sec.log_ret.fillna(0)
         
         df_sec.loc[:,'log_returns_pct']=100*df_sec.log_returns
         
         df_sec.drop(['log_returns', 'log_ret'], axis=1, inplace=True)
         
         df_sec['log_returns_pct'] =  abs(df_sec['log_returns_pct'])
 
         quant=np.percentile(df_sec['log_returns_pct'], perc)
         
         d['quantiles'].append(quant)
         
         d['dts'].append(dt)
         
         dt=dt+1 #increase time step by 1 sec
         
     return (d)
 
 
 
# E.g. Median of log-ret of 1 sec, 2 sec etc up to 300 sec
 
dts=pd.DataFrame(sqrt_root(50))
 
"""
Compute  data quantile that covers 50% of all log-returns
Use this for SMN,
For SMN divide by 100.
"""
np.percentile(dts['quantiles'], 50)


# Plot of quantiles linear (bx+a) fit by sqrt(dt)
coefs = scipy.optimize.curve_fit(lambda x,a,b  : a+b*np.sqrt(x), dts['dts'], dts['quantiles']) [0]
 
 
Y_pred =  coefs[0]+coefs[1]*np.sqrt(dts['dts'])
 
plt.figure(figsize=(6, 4))
 
plt.scatter(dts['dts'], dts['quantiles'], label='Data')
 
plt.plot(dts['dts'],Y_pred,
          label='Fitted function', color = 'red')
 
plt.legend(loc='best')
plt.ylim(ymin=0)
plt.ylim(ymax=max(Y_pred))
 
plt.show()
         