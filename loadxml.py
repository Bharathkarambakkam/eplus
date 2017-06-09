"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: Load EnergyPlus output xml file (*.xml)
"""



from xml.etree.ElementTree import parse
from numpy import array
import pandas as pd
import calendar



def loadxml(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=elem.find('SensibleHeatGainSummary')
	x=c.findall('AnnualBuildingSensibleHeatGainComponents')[-1]

	ld = array([e.text for e in list(x)])
	ldtags = [e.tag for e in list(x)]
	ldunits = [list(e.attrib.values())[0] for e in list(x)[1:]]
	clld = dict(keys =('Lights','Equip','People-Sens','Infil','Windows','Envelope'), values=ld[[6,7,5,10,8,11]])
	htld = dict(keys =('Lights','Equip','People-Sens','Infil','Windows','Envelope'), values=ld[[6,7,5,10,8,11]])
	return clld,htld


def loadenduses(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=elem.find('AnnualBuildingUtilityPerformanceSummary')
	x=c.findall('EndUses')[:9]

	cat= [e.find('name').text for e in x]
	elec  = [e.find('Electricity').text for e in x]
	gas = [e.find('NaturalGas').text for e in x]
	distCl = [e.find('DistrictCooling').text for e in x]
	distHt = [e.find('DistrictHeating').text for e in x]
	enduse = pd.DataFrame(dict(zip(['elec','gas','distCl','distHt'],[elec,gas,distCl,distHt])),index=cat).convert_objects(convert_numeric=True)
	return enduse

def loadEUI(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=elem.find('AnnualBuildingUtilityPerformanceSummary')
	x=c.findall('SiteAndSourceEnergy')[1]
	return float(x.find('EnergyPerTotalBuildingArea').text)
	
def loadenergymetrics(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=elem.find('AnnualBuildingUtilityPerformanceSummary')
	area = float(c.find('BuildingArea').getchildren()[1].text)
	r=loadenduses(fname)/area
	return r.sum(axis=1)

def loadmonthlyelectric(fname):
	tree = parse(fname)
	elem = tree.getroot()
	monelec=pd.DataFrame(index=[calendar.month_abbr[i+1] for i in range(12)])
	l=elem.find('Enduseenergyconsumptionelectricitymonthly').getchildren()[1:]
	for n in l:
		monelec[n[0].text]= [i.text for i in n[1:13]]
	return monelec

def loadmonthlygas(fname):
	tree = parse(fname)
	elem = tree.getroot()
	mongas=pd.DataFrame(index=[calendar.month_abbr[i+1] for i in range(12)])
	l=elem.find('Enduseenergyconsumptionnaturalgasmonthly').getchildren()[1:]
	for n in l:
		mongas[n[0].text]= [i.text for i in n[1:13]]
	return mongas

def loadunmethours(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=elem.find('AnnualBuildingUtilityPerformanceSummary').find('ComfortAndSetpointNotMetSummary').getchildren()
	return {c[1].tag:float(c[1].text),c[2].tag:float(c[2].text)}


def loadsyscfm(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=[i for i in elem.find('HvacSizingSummary').getchildren()[1:] if i.tag=='SystemDesignAirFlowRates']

	sys = [i.getchildren()[0].text for i in c]
	clgcfm = [i.getchildren()[1].text for i in c]
	htgcfm = [i.getchildren()[3].text for i in c]
	return pd.DataFrame(data={'clg-cfm':clgcfm,'htg-cfm':htgcfm},index=sys).convert_objects(convert_numeric=True)

def loadzoneOA(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=[i for i in elem.find('OutdoorAirSummary').getchildren() if i.tag=='AverageOutdoorAirDuringOccupiedHours']

	zone = [i.getchildren()[0].text for i in c]
	vol = array([i.getchildren()[3].text for i in c]).astype(float)
	ach = array([i.getchildren()[4].text for i in c]).astype(float)
	return pd.DataFrame(data={'OACFM':vol*ach},index=zone)

def loadUnmetZones(fname):
        tree = parse(fname)
        elem = tree.getroot()
        x=elem.find('SystemSummary').findall('TimeSetpointNotMet')
        zone = [e.find('name').text for e in x]
        heating = [e.find('DuringOccupiedHeating').text for e in x]
        Cooling = [e.find('DuringOccupiedCooling').text for e in x]
        return pd.DataFrame(data={'heating':heating,'cooling':cooling},index=zone).convert_objects(convert_numeric=True)



def loadzoneenergy(fname):
	tree = parse(fname)
	elem = tree.getroot()
	c=[i for i in elem.find('EnergyMeters').getchildren() if i.tag=='AnnualAndPeakValuesOther']
	name = [i.getchildren()[0].text for i in c]
	AnnualkBtu = array([i.getchildren()[1].text for i in c]).astype(float)
	cl = AnnualkBtu[[i for i,s in enumerate(name) if ('Cooling' in s) and ('Zone' in s)]]
	ht = AnnualkBtu[[i for i,s in enumerate(name) if ('Heating' in s) and ('Zone' in s)]]
	z = [s.split('Zone')[1] for i,s in enumerate(name) if ('Cooling' in s) and ('Zone' in s)]
	return pd.DataFrame(data={'CoolingkBtu':cl,'HeatingkBtu':ht},index=z)







# 0,Name
# 1,HvacInputSensibleAirHeating
# 2,HvacInputSensibleAirCooling
# 3,HvacInputHeatedSurfaceHeating
# 4,HvacInputCooledSurfaceCooling
# 5,PeopleSensibleHeatAddition
# 6,LightsSensibleHeatAddition
# 7,EquipmentSensibleHeatAddition
# 8,WindowHeatAddition
# 9,InterzoneAirTransferHeatAddition
# 10,InfiltrationHeatAddition
# 11,OpaqueSurfaceConductionAndOtherHeatAddition
# 12,EquipmentSensibleHeatRemoval
# 13,WindowHeatRemoval
# 14,InterzoneAirTransferHeatRemoval
# 15,InfiltrationHeatRemoval
# 16,OpaqueSurfaceConductionAndOtherHeatRemoval

	#ld = dict([(e.tag,float(e.text)) for e in list(x)[1:]])






