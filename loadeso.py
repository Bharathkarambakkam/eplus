"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: Load EnergyPlus Hourly output file (*.eso)
"""





from pylab import *
import pandas as pd
import re
import io


def loadeso_old(fname):
    """
    for 8760 data only
    """
    with open(fname,'r') as f: eso = f.read()
    vart = re.findall('([^,]+,[^,]+) !Hourly',eso)
    varn = re.findall('(\d+),([\d.eE-]+)\n',eso)
    s = pd.DataFrame(varn,columns=['var','val'],dtype='float64')
    s['dt']=repeat([datetime.datetime(2012,1,1,0)+datetime.timedelta(hours=i) for i in range(8760)],len(vart))
    eso=s.pivot(index='dt',columns='var',values='val')
    eso.columns=vart
    return eso


def loadeso(fname):
    """
    Works only if all hourly variables are of equal length. 
    """ 
    with open(fname,'r') as f: varstr = f.read()
    colstr,datstr,end = varstr.split('End of')
    cols = pd.read_csv(io.StringIO(colstr),skiprows=6,header=None).set_index(0)
  
    d = pd.DataFrame(re.findall('2,[ 0-9]*,([ 0-9]*),([ 0-9]*),[ 0-1]*,([ 0-9]*),([ 0-9.]*),[ 0-9.]*,[A-Z]',datstr),dtype=np.float).astype(int)
    dtx=pd.to_datetime(2012*100000000 + d[0]*1000000 + d[1]*10000+(d[2]-1)*100+d[3], format='%Y%m%d%H%M')

    eso=pd.DataFrame(pd.read_csv(io.StringIO(re.sub('^2,.*\n','',datstr,flags=re.M)),skiprows=2,header=None,dtype=np.float).groupby(0).groups,index=dtx)
    eso.columns=cols.loc[eso.columns.astype(int).values,[2,3]]
    
    return eso

#plot_date(eso.index,eso['GSHP HW LOOP,Plant Supply Side Heating Demand Rate [W]']*3.412/1000000)
#plot_date(eso.index,eso['CHW LOOP,Plant Supply Side Cooling Demand Rate [W]']*3.412/1000000)
#plot_date(eso.index,eso['DISTRICT HW LOOP,Plant Supply Side Heating Demand Rate [W]']*3.412/1000000)



