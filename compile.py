# -*- coding: utf-8 -*-
"""
Clean up DOE budget data
"""

import os
import sys
import numpy as np
import pandas as pd

repo = # INSERT REPO HERE
raw = os.path.join(repo, 'data', 'raw')
output = os.path.join(repo, 'data', 'output')

# Import dataset
basedf = pd.read_excel(os.path.join(repo, 'data', 'raw', 'DOE Proposed Budget.xlsx'))

# Wide df
wdf = basedf[basedf['Fiscal Year'] == 'FY2024'].copy()
wdf = wdf[['Office', 'Suboffice', 'Program', 'Value']]
wdf = wdf.rename(columns = {'Value': 'Value_FY2024'})

for y in ['2025', '2026']:
    ydf = basedf[basedf['Fiscal Year'] == 'FY' + y].copy()
    ydf = ydf[['Office', 'Suboffice', 'Program', 'Value']]
    ydf = ydf.rename(columns = {'Value': 'Value_FY'+y})
    wdf = wdf.merge(ydf, 
                    left_on = ['Office', 'Suboffice', 'Program'],
                    right_on = ['Office', 'Suboffice', 'Program'], 
                    how = 'inner')

wdf['PercChange_25to26'] = (wdf['Value_FY2026'] - wdf['Value_FY2025'])/wdf['Value_FY2025']
  
# Full DOE budget composition (stacked bar, color by office)
df = wdf.groupby(['Office'])[['Value_FY2024', 'Value_FY2025', 'Value_FY2026']].sum().reset_index()
df.to_csv(os.path.join(output, 'by_office.csv'))

# Which programs are going to 0
df = wdf.copy()
df = df[(df['Value_FY2026'] == 0) & (df['Value_FY2025'] > 0)]
df.to_csv(os.path.join(output, 'by_program_to0.csv'))

# Which programs are losing > 50% of its budget
df = wdf.copy()
df = df[df['PercChange_25to26'] < -0.5]
df = df[df['Value_FY2025'] > 0]
df.to_csv(os.path.join(output, 'by_program_50pcut.csv'))

# Which programs are losing > 90% of its budget
df = wdf.copy()
df = df[df['PercChange_25to26'] < -0.9]
df = df[df['Value_FY2025'] > 0]
df.to_csv(os.path.join(output, 'by_program_90pcut.csv'))

# Which programs are increasing funding
df = wdf.copy()
df = df[df['PercChange_25to26'] > 0]
df['PercChange_25to26'] = np.where(df['PercChange_25to26'] > 1000, #infinity
                                   1, df['PercChange_25to26'])
df.to_csv(os.path.join(output, 'by_program_increase.csv'))
