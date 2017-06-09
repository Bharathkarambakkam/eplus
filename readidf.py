"""
Bharath Karambakkam
e-mail:Bharath.karambakkam@imegcorp.com
function: Load energyplus idf file into a pandas dataframe(*.idf)
"""


import re,io
import pandas as pd

class idf(object):

    def __init__(self,name=None):
        self.name=name
        self.t=None
        if name:self.readidf()

    def reload(self):
        None
#        self.__init__(self.name)
    def copy(self):
        idfc=idf()
#        idfc.t=self.t
#        idfc.name=self.name
        return idfc
        

    def readidf(self):
        with open(self.name,'r') as f: idf=re.sub('!.*|\t','',f.read()).replace('\n','')
        

        dstr = '(Output:Variable|Output:Surfaces:Drawing|Output:Meter)'
        idf  = re.sub(' *'+dstr+'.*?;','',idf)

        idf = re.sub(r'( *)(,|;)( *)',r'\2',idf)

        df = pd.DataFrame(idf.split(';')[:-1], columns=['col'])
        idfTable=pd.DataFrame(df['col'].str.split(',').tolist()).set_index([0,1])

        idfTable.columns=idfTable.columns-1
        idfTable[1].fillna('',inplace=True)
        self.t = idfTable.stack().sortlevel(0)
        self.t.name='val'
        self.t.index.set_names(['class','name','par'],inplace=True)

    #Editing groups idfTable.loc['Building',slice(None),2]=3

    def setparnames(self):
        with open('parnames.csv') as f:n = pd.read_csv(f.read())
        self.t=pd.merge(n,self.t.reset_index(),how='outer').ffill(axis=1).drop('par',axis=1)
        self.t.set_index(['class','name','title'],inplace=True)
        self.t.sortlevel(0)

    def writeidf(self,fname):
        s = io.StringIO()
        self.t.unstack().to_csv(s,header=False,line_terminator=',\n')
        s.seek(0)
        with open(fname,'w') as f: f.write(re.sub('[,\s]*\n',';\n',s.read()))

    def getzones(self):
        return self.t.loc['Zone',:,1].reset_index()['name']


    def getsyszones(self):
        sp = self.t.loc['AirLoopHVAC:ZoneSplitter',:,slice(2,1000)].reset_index()[['name','val']]
        
        zn = self.t[self.t.reset_index()['class'].str.contains('AirTerminal:.*Uncontrolled',regex=True).values].loc[:,:,2].reset_index()[['name','val']]
        zn = zn.append(self.t[self.t.reset_index()['class'].str.contains('AirTerminal:.*Reheat',regex=True).values].loc[:,:,3].reset_index()[['name','val']])


        sp['sys'] = pd.DataFrame(sp['name'].str.split(' ').tolist())[0]
        zn['zn'] = pd.DataFrame(zn['name'].str.split(' ').tolist())[0]   #may not work if there is space in zone name.
        sp = sp[['sys','val']]
        zn = zn[['zn','val']]
        return pd.merge(zn,sp)[['zn','sys']].set_index('sys').stack()

    def getclass(self):
        for i in self.t.index.get_level_values(0).unique():print(i)

    def getnames(self,classname):
        for i in self.t.loc[classname].index.get_level_values(0).unique():print(i)        
