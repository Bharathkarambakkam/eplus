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
      c=self.elem.find('AnnualBuildingUtilityPerformanceSummary').find('ComfortAndSetpointNotMetSummary').getchildren()
      return {c[1].tag:float(c[1].text),c[2].tag:float(c[2].text)}

 def getunmetzones(self,minh=30):
      x= self.elem.find('SystemSummary').findall('TimeSetpointNotMet')[:-1]
      zone = [e.find('name').text for e in x]
      heating = [e.find('DuringOccupiedHeating').text for e in x]
      cooling = [e.find('DuringOccupiedCooling').text for e in x]
      fdf = pd.DataFrame(data={'heating':heating,'cooling':cooling},index=zone).convert_objects(convert_numeric=True)
      cdf=fdf[(fdf>minh).any(axis=1)]
      return cdf.reindex(cdf.max(axis=1).order(ascending=False).index)

 def getall(self):
      r = pr.data(self.elem)
      for ea in['BuildingName','EnvironmentName','WeatherFileLocationTitle'
              ,'ProgramVersion','SimulationTimestamp']:
          r.pop(ea,None)
      for ea in r:
          for j in ['for','note','footnote','General']: r[ea].pop(j,None)
          for j in r[ea]:
              if type(r[ea][j]) is list:
                  self.__setattr__(j,pd.DataFrame(r[ea][j]).set_index('name'))
              else:
                  self.__setattr__(j,pd.Series(r[ea][j]))

