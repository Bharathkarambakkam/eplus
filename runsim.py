import sys
sys.path.append('C:\\Projects\\Tools\ePlus')
from importlib import reload

from copy import deepcopy as dc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


from runeplus import runeplus
import loadeso
import exml
import readidf
import parsetup

reload(parsetup)
reload(exml)

cases = [
        'svoh.idf',
        'svoh_basecase.idf',
        ]


sv=readidf.idf('C:\\EnergyPlusV8-1-0\\svoh.idf')

sv.t.loc['RunPeriod',:,[1,2,3,4]]=[1,1,12,31]
sv.writeidf("svoh.idf")

svb=readidf.idf('C:\\EnergyPlusV8-1-0\\svoh_basecase.idf')
svb.writeidf("svoh_basecase.idf")
outputs =  [#'Output:Variable,Floor2:Office5,Zone Heating Setpoint Not Met Time,hourly; !- Zone Sum [hr]',
            #'Output:Variable,*,Zone Heating Setpoint Not Met While Occupied Time,hourly; !- Zone Sum [hr]',
            #'Output:Variable,L1:DataCenter,Zone Cooling Setpoint Not Met While Occupied Time,hourly; !- Zone Sum [hr]',
            #'Output:Variable,*,Zone Mean Air Temperature,hourly; !- Zone Average [C]',
            #'Output:Variable,*,Air System Mixed Air Mass Flow Rate,hourly; !- HVAC Average [kg/s]',
            'Output:Variable,*,Air System Outdoor Air Mass Flow Rate,hourly; !- HVAC Average [kg/s]',
            #'Output:Variable,*,Air System Total Heating Energy,hourly; !- HVAC Sum [J]',
            #'Output:Variable,*,Zone Air System Sensible Heating Energy,hourly; !- HVAC Sum [J]',
            #'Output:Variable,*,District Heating Hot Water Energy,hourly; !- HVAC Sum [J]',
            #"Output:Variable,*,Fan Electric Power,hourly; !- HVAC Average [W]"
]



for ea in cases:
#    idf = readidf.idf(ea)
#    infiltration 0.15 cfm/sqft =0.15*0.00508 m3/s/m2
#    idf.t.loc['ZoneInfiltration:DesignFlowRate',:,3] ='Flow/ExteriorWallArea'
#    idf.t.loc['ZoneInfiltration:DesignFlowRate',:,6] = 0.000402
#    idf.writeidf(ea)

    with open(ea,'r') as f: idf=f.read().replace('CommaAndHTML','XMLandHTML')#.replace('HTML','XMLandHTML')
    for ei in outputs:idf=idf+ei+'\n'
    with open(ea,'w') as w:w.write(idf)
   
runeplus(cases,'C:\\ProgramData\\DesignBuilder\\Weather Data\\USA_IN_EVANSVILLE REGIONAL AP_TMY3.epw',rem=False) 
elec=pd.DataFrame()
gas=pd.DataFrame()
cost=pd.DataFrame()

ut=pd.Series([0.071,0.7,0.01144*1000,0.01032*1000],index=['elec[kWh]','gas[therm]','distCl[Mbh]','distHt[Mbh]'])# Utility rates
for r in cases:
    ca=r.split('.idf')[0]
    xml = exml.exml(ca+'Table.xml')
    vars()['x'+ca]= xml
    eso=loadeso.loadeso(ca+'.eso')
    vars()['e'+ca]=eso
    print(ca+'- EUI: '+str(xml.getEUI()))
    elec[ca] = xml.getprm()['elec[kWh]']
    gas[ca] = xml.getprm()['gas[therm]']
    cost[ca] = (xml.getprm() * ut).dropna(axis=1).sum(axis=1)


#plot(eLegacy_test[[2]][eLegacy_test[[2]]==1].dropna().index.hour,'+')

#idf.t.loc[idf.t.index.get_level_values(1).str.contains('Heating Setpoint')]
print('Process ratio:'+str(cost.loc['InteriorEquipment','svoh']/cost.sum()*100))
