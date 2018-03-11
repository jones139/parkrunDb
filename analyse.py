#!/usr/bin/python

import pandas
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#pd.set_option('display.mpl_style', 'default') # Make the graphs a bit prettier
plt.style.use('ggplot')

f = open('partstats.json','r')
partstats = json.load(f)
f.close()

df = pd.DataFrame.from_records(partstats)
df['nTot'] = df['nRun']+df['nVol']
df.sort_values('nRun',ascending=False, inplace=True)

print df[:20]
print "Total Number of runners in the period"
print df[['name']].count()
print "Total Number of runs in the period"
print df[['nRun']].sum()
print "Number of Runners who have run more than 5 times in the period"
print df[['name']][df['nRun']>5].count()
print "Number of Runners who have run more than 10 times in the period"
print df[['name']][df['nRun']>10].count()
print df[['name','nRun','nVol','ratio']][df['nRun']>10]
print "Number of Runners who have run more than 10 times in period, but not volunteered"
print df[['name']][(df['nRun']>10) & (df['nVol']==0)].count()
print df[['name','nRun','nVol']][(df['nRun']>10) & (df['nVol']==0)]
print "Number of Runners who have run more than 10 times in period, who have volunteered"
print df[['name']][(df['nRun']>10) & (df['nVol']>0)].count()


df.sort_values('nVol',ascending=False, inplace=True)
df['cumVol'] = df.nVol.cumsum()
df['cumVolpc'] = 100*df.cumVol/df.nVol.sum()
print "Top 20 volunteers"
print df[['name','nRun','nVol','cumVol','cumVolpc']][:20]

df['cumVolpc'][:20].plot(kind='bar')



#plt.figure()
#df['nTot'].plot()

#ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
#ts = ts.cumsum()
#ts.plot()
