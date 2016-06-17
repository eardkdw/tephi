#!/usr/bin/env python
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import os.path, sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime
try:
    from cStringIO import StringIO
except ImportError:
    #python 3
    from io import StringIO

import tephi
from metutils import wetBulbGlobeTemp

metadata = {}
filename = sys.argv[1]
with io.open(filename,'r',encoding='latin1') as f:
   for i in range (0,13):
      metadatain = f.readline()
      metaarray =metadatain.split('\t')
      if(len(metaarray) == 2):
         metadata[metaarray[0].strip()] = metaarray[1].strip()

metadata['datetime'] = datetime.strptime('%s %s' % (metadata['Balloon release date'], metadata['Balloon release time']), '%d/%m/%y %H:%M:%S') 
print(metadata['datetime'].isoformat())

edt_table=pd.read_table(filename, sep='\t', skiprows=list(range(0,13))+[14], header=0)
edt_table.rename(columns=lambda x: x.strip(), inplace=True)


#print edt_table.keys()
'''Index([u'Elapsed time', u'TimeUTC', u'P', u'Temp', u'RH', u'Dewp', u'Speed',
       u'Dir', u'Ecomp', u'Ncomp', u'Lat', u'Lon', u'AscRate', u'HeightMSL',
       u'GpsHeightMSL', u'PotTemp', u'SpHum', u'CompRng', u'CompAz'],
      dtype='object')'''

columns = ['P', 'Dewp', 'Speed', 'Dir', 'Temp']
#s = StringIO()

tempfile = '/tmp/wibble'

#munge to format expected by tephi module
edt_table.to_csv(tempfile, columns=columns, header=False,index=False)

edt_data = tephi.loadtxt(tempfile, column_titles=columns, delimiter=',')


dews = list(zip(edt_data.P, edt_data.Dewp))
temps = list(zip(edt_data.P, edt_data.Temp))
resample = 80
barbs = list(zip(
   edt_data.Speed[::resample] * 1.94384, #convert to knots
   edt_data.Dir[::resample], 
   edt_data.P[::resample]))
tephi.MIN_THETA=-30
tpg = tephi.Tephigram(anchor=[(1002, -31.0), (170,-52.0)], isotherm_locator=tephi.Locator(10),)

p = tpg.plot(dews, label='Dew point', color='blue')
tpg.plot(temps, label='Temperature', color='red')
p.barbs(barbs, gutter=0.1, color='purple')
plt.suptitle('Radiosonde ' + metadata['Sonde serial number'] + ', ' + metadata['Release point latitude'] + ', ' + metadata['Release point longitude'], fontsize=18)
plt.title(metadata['datetime'].isoformat(), fontsize=12)

b = tephi.isopleths.Barbs(p.axes)
b.plot(barbs, gutter=-0.1, color='purple')
from matplotlib import transforms
offset = transforms.ScaledTranslation(10, 0,
  tpg.figure.dpi_scale_trans)
#shadow_transform = b.transData + offset
#print(os.path.splitext(os.path.basename(filename)))

if sys.argv[2]:
   outfile = sys.argv[2]
else:
   outfile = os.path.splitext(os.path.basename(filename))[0] + '.pdf'

plt.savefig(outfile)
