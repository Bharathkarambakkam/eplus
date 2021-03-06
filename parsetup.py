"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: utlity functions for setting up parametric runs
companion1: parzonetemplate.idf for the template zones
companion2: sch.idf for template schedules
"""


import re
import pandas as pd
import readidf


def templateZones(paridf):
    paridf.t.drop(['Zone',
                 'BuildingSurface:Detailed',
                 'FenestrationSurface:Detailed',
                 'BuildingSurface:Detailed'],inplace=True,errors='ignore')

    te = readidf.idf('C:\\Projects\\Tools\\ePlus\\parzones.idf')
    paridf.t = paridf.t.append(te.t).sort_index(level=0)


def setsch(paridf,libsch, sch):
    paridf.t.drop(['ThermostatSetpoint:DualSetpoint'],level=0,inplace=True,errors='ignore')
    paridf.t = paridf.t.loc[~((paridf.t.index.get_level_values(1).str.contains(sch)) & (paridf.t.index.get_level_values(0) == 'Schedule:Compact'))] # Remove duplicate entries
    paridf.t = paridf.t.loc[~paridf.t.index.get_level_values(1).str.contains('Heating Setpoint Schedule')]
    paridf.t = paridf.t.loc[~paridf.t.index.get_level_values(1).str.contains('Cooling Setpoint Schedule')]

    paridf.t = paridf.t.sort_index(level=0)   
    paridf.t.loc['ZoneControl:Thermostat',:,4] = 'dual_' + sch
    paridf.t.loc['PEOPLE',:,2] = 'occ_' + sch
    paridf.t.loc['Lights',:,2] = 'lt_' + sch
    paridf.t.loc['ElectricEquipment',:,2] = 'lt_' + sch


    paridf.t.loc['Controller:OutdoorAir',:,16] = 'fan_'+ sch # Set no OA at night
    paridf.t.loc['AvailabilityManager:NightCycle',:,2] = 'fan_'+ sch # Set night Cycle Sch
    paridf.t.loc[paridf.t.index.get_level_values(0).str.contains('Fan'),:,1] = 'fan_'+ sch # Set fan cycle

    paridf.t = paridf.t.append(libsch.t.loc[libsch.t.index.get_level_values(1).str.contains(sch)]) #append schedules from library
    paridf.t = paridf.t.append(pd.DataFrame({'class':['ThermostatSetpoint:DualSetpoint']*2,'name':['dual_'+sch]*2,'par':[1,2],'val':['ht_'+sch,'cl_'+sch]}).set_index(['class','name','par'])['val']).sort_index(level= 0)

