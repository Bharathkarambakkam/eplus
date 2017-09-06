"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: Load EnergyPlus output xml file (*.xml)
"""


from xml.etree.ElementTree import parse 
from numpy import array
import pandas as pd
import calendar
from xmljson import parker as pr

class exml(object):

 def __init__(self,fname):
      self.fname=fname
      tree = parse(self.fname)
      self.elem = tree.getroot()

 def reload(self):
      self.__init__(self.fname)

 def getprm(self):
      c=self.elem.find('AnnualBuildingUtilityPerformanceSummary')
      x=c.findall('EndUses')[:-1]
      cat= [e.find('name').text for e in x]
      elec  = pd.Series([e.find('Electricity').text for e in x],dtype=float,index=cat)/3.4144
      gas = pd.Series([e.find('NaturalGas').text for e in x],dtype=float,index=cat)/1e2
      distCl = pd.Series([e.find('DistrictCooling').text for e in x],dtype=float,index=cat)
      distHt = pd.Series([e.find('DistrictHeating').text for e in x],dtype=float,index=cat)
      prm = pd.DataFrame({'elec[kWh]':elec,'gas[therm]':gas,'distCl[kBtu]':distCl,'distHt[kBtu]':distHt})
      return prm.loc[prm.any(1),prm.any()]

 def getEUI(self):
      c=self.elem.find('AnnualBuildingUtilityPerformanceSummary')
      x=c.findall('SiteAndSourceEnergy')[1]
      return float(x.find('EnergyPerTotalBuildingArea').text)
      

 def getunmethours(self):
      x= self.elem.find('SystemSummary').findall('TimeSetpointNotMet')[-1]
      return pd.Series(pr.data(x))

 def getunmetzones(self):
      x= self.elem.find('SystemSummary').findall('TimeSetpointNotMet')[:-1]
      return pd.DataFrame(pr.data(x)['TimeSetpointNotMet'])[:-1].set_index('name')

 def getall(self):
      r = pr.data(self.elem)
      for ea in['BuildingName','EnvironmentName','WeatherFileLocationTitle'
              ,'ProgramVersion','SimulationTimestamp']:
          r.pop(ea,None)
      for ea in r:
          if not 'monthly' in ea:  
              for j in ['for','note','footnote','General']: r[ea].pop(j,None)
              for j in r[ea]:
                  if type(r[ea][j]) is list:
                      self.__setattr__(j,pd.DataFrame(r[ea][j]).set_index('name'))
                  else:
                      self.__setattr__(j,pd.Series(r[ea][j]))

 def getmonthly(self):
      r = pr.data(self.elem)
      for ea in r:
          if 'monthly' in ea:
              if type(r[ea]) is list:
                  s = pd.DataFrame()
                  for j in r[ea]:
                      v=pd.DataFrame(j['CustomMonthlyReport'])
                      v['zone'] = j['for']
                      s=pd.concat([s,v])
                  s=s.set_index(['zone','name'])     
                  self.__setattr__(ea,s)
              else:
                  pd.DataFrame(r[ea]['CustomMonthlyReport'])
                  self.__setattr__(ea,pd.DataFrame(r[ea]['CustomMonthlyReport']))

 def getstd(self):
     c=self.elem.find('LeedSummary').findall('Eap245PerformanceRatingMethodCompliance')
     s=pd.DataFrame(pr.data(c)['Eap245PerformanceRatingMethodCompliance'])[:-1].melt(id_vars='name')
     s = s[s['value']>0]
     s = s.set_index(s.name+':'+s.variable)['value']
     
     c = self.elem.find('SystemSummary').findall('TimeSetpointNotMet')[-1]
     s=s.append(pd.Series(pr.data(c))[1:])
     
     s['EUI']=float(self.elem.find('AnnualBuildingUtilityPerformanceSummary').findall('SiteAndSourceEnergy')[1].find('EnergyPerTotalBuildingArea').text)
     
     coils=pr.data(self.elem.find('EquipmentSummary').findall('CoolingCoils'))['CoolingCoils']
     s['ClCoilSens']=pd.DataFrame(coils,index=range(max(1,isinstance(coils,list)*len(coils))))[['NominalSensibleCapacity']].sum()[0]
     
     coils=pr.data(self.elem.find('EquipmentSummary').findall('CoolingCoils'))['CoolingCoils']
     s['ClcoilLat']=pd.DataFrame(coils,index=range(max(1,isinstance(coils,list)*len(coils))))[['NominalLatentCapacity']].sum()[0]
     
     coils=pr.data(self.elem.find('EquipmentSummary').findall('HeatingCoils'))['HeatingCoils']
     s['HtCoil']=pd.DataFrame(coils,index=range(max(1,isinstance(coils,list)*len(coils))))[['NominalTotalCapacity']].sum()[0]
     
     s['clgCFM'] = pd.DataFrame(pr.data(self.elem.find('HvacSizingSummary').findall('ZoneSensibleCooling'))['ZoneSensibleCooling'])['UserDesignAirFlow'].sum()
     
     s['oaCFM'] = pd.DataFrame(pr.data(self.elem.find('HvacSizingSummary').findall('ZoneSensibleCooling'))['ZoneSensibleCooling'])['MinimumOutdoorAirFlowRate'].sum()
     
     s['htgCFM'] = pd.DataFrame(pr.data(self.elem.find('HvacSizingSummary').findall('ZoneSensibleHeating'))['ZoneSensibleHeating'])['UserDesignAirFlow'].sum()
     return s

