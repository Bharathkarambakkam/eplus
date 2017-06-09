"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: run parametric runs
"""

import os,shutil,subprocess,time
import readidf,parsetup,exml
import pandas as pd
import numpy as np

def runeplus(idffiles,wea,rem=True,ver='EnergyPlusV8-4-0',showprogress=None):
    status={}
    for ea in idffiles:
        subf = ea.split('.idf')[0]
        if showprogress==None:print('****Starting:'+subf)
        if os.path.exists(subf):shutil.rmtree(subf)
        os.mkdir(subf)
        shutil.copyfile('C:\\'+ver+'\Energy+.idd',subf+'\Energy+.idd')
        shutil.copyfile(wea,subf+'\in.epw')
        shutil.copyfile(ea,subf+'\in.idf')
        status[subf]=subprocess.Popen('C:\\'+ver+'\EnergyPlus.exe',cwd=subf,stdout=showprogress)
		
    while(status):
        lstatus=status.copy()
        for e in lstatus:
            if not status[e].poll()==None:
                with open(e+'\eplusout.err') as f: a=f.readlines()[-1]
                shutil.copyfile(e+'\eplustbl.htm',e+'Table.html')
                if os.path.isfile(e+'\eplustbl.xml'):shutil.copyfile(e+'\eplustbl.xml',e+'Table.xml')	
                if os.path.isfile(e+'\eplusout.eso'):shutil.copyfile(e+'\eplusout.eso',e+'.eso')
                if showprogress==None:print('********'+e+'******'+a)
                if rem:shutil.rmtree(e)
                status.pop(e)



def runpar(parf,parmap,sruns=10):
    pr = pd.read_hdf(parf)
    lidf =  len(pr['idf'].unique()) 
    lwea =  len(pr['wea'].unique()) 
    lsch =  len(pr['inf:sch'].unique()) 
    for ixf,(f,df) in enumerate(pr[~pr['run']].groupby('idf')):
        parbld = readidf.idf(f)
        print('*************************************************'+ f +': ' +str(ixf+1)+' of '+str(lidf))
        for ixw,(w,dw) in enumerate(df.groupby('wea')):
            print('---------------------------------'+ w +': '+str(ixw+1)+' of '+str(lwea))
            for ixs,(s,ds) in enumerate(dw.groupby('inf:sch')):
                parsetup.setsch(parbld,s)
                print('................'+s+': '+str(ixs+1)+' of '+str(lsch))
                lgrp = int(len(ds.index)/sruns)
                for ixk,dk in enumerate(np.array_split(ds,lgrp)):
                    print('Group: '+str(ixk+1)+' of '+str(lgrp))
                    for nr,r in dk.iterrows():
                        parbld.t.sort_index(inplace=True)
                        for c,v in parmap:parbld.t.loc[v]=r[c]
                        parbld.writeidf(str(nr)+'.idf')
                    cases=[str(n)+'.idf' for n in dk.index]
                    runeplus(cases,'C:\\ProgramData\\DesignBuilder\\Weather Data\\'+w,showprogress=False)
                    for n,r in dk.iterrows():
                        xml = exml.exml(str(n)+'Table.xml')
                        pr.loc[n,['EUI','elec','gas','run']]=[
                        xml.getEUI(),
                        xml.getprm().sum()[0],
                        xml.getprm().sum()[1],
                        True
                        ]
                        os.remove(str(n)+'.idf')
                        os.remove(str(n)+'Table.xml')
                        os.remove(str(n)+'Table.html')
                    pr.to_hdf(parf,'w')
