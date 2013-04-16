import numpy as np

class Stimulation:
    def __init__(self,fname,depvar_sort=True):
        self.load_data(fname)
        if depvar_sort:
            self.depvar_sort()

    def load_data(self,fname):
        fid = open(fname)
        lines = fid.readlines()
        data_trace = [[]]
        data_stim = [[]]
        inside_trace = False
        inside_stimulus = False
        inside_params = False
        depvar = []
        params = dict()
        for lin in lines:
            lin = lin.strip()
            if lin == 'STIMULUS':
                inside_stimulus = True
            if lin == 'END_STIMULUS':
                if inside_stimulus:
                    data_stim.append([])
                inside_stimulus = False
            if lin == 'TRACE':
                inside_trace = True
            if lin == 'END_TRACE':
                inside_trace = False
                data_trace.append([])
            if lin == 'PARAMS':
                inside_params = True
            if lin == 'END_PARAMS':
                inside_params = False
            if inside_params and lin.find('=')>0 and lin[0]!=';':
                p = lin[lin.find('=')+1:].strip()
                try:
                    p = float(p)
                    if np.floor(p) == p:
                        p = int(p)
                except ValueError:
                    pass
                params[lin[0:lin.find('=')]] = p
            if inside_trace:
                data_trace[-1].append(lin)
            if inside_stimulus:
                data_stim[-1].append(lin)
            if lin[0:6] == 'depvar' and len(lin)>16:
                depvar.append(int(lin[lin.find('=')+1:lin.find('<')]))
        self.traces = self._str_list_conv(data_trace)
        self.stim = self._str_list_conv(data_stim)
        self.depvar = np.array(depvar)
        self.params = params
        if len(self.traces) > 0:
            self.times = np.arange(0.,float(self.traces.shape[1]))/(
                    float(self.traces.shape[1]))*self.params['Epoch']
        else: self.times = None
        self.clickfile = False
        self.longnoise = False
        if self.params['depvar'] == 'itd (us)':
            self.freqs = self.depvar.copy()
            if ('itd.stim' not in self.params.keys()):
                self.freqs.fill(0.)
                if (self.params['prefs.page'+str(self.params['prefs.page'])] == 'click'):
                    self.clickfile = True
                if (self.params['prefs.page'+str(self.params['prefs.page'])] == 'longnoise'):
                    self.longnoise = True
            elif self.params['itd.stim']=='BB':
                #noise stimulation. TODO: figure out what the ts parameters mean
                self.freqs.fill(0.)
            else:
                self.freqs.fill(self.params['itd.stim'])
            #spontaneous stimulations get marked by -6666
            self.freqs[np.where(self.depvar < -6000)] = -6666
        if self.params['depvar'] == 'bf (Hz)':
            self.freqs = self.depvar

        #parse the timestamp as a python datetime if present
        if 'timestamp' in self.params.keys():
            from datetime import datetime
            self.timestamp = datetime.fromtimestamp(
                    self.params['timestamp'])



    def _str_list_conv(self,str_list):
        ret = []
        for tra in str_list:
            if len(tra)>0 and tra[1] == 'channel=1':
                ret.append([])
                for lin in tra[2:]:
                    for n in range(len(lin)/4):
                        ret[-1].append(int(lin[4*n:4*(n+1)],16))
        ret = np.array(ret)
        return ret - (ret > 32767)*65536

    def depvar_sort(self):
        ind = self.depvar.argsort()
        self.depvar = self.depvar[ind]
        #not all files contain the stimulus
        if len(self.stim) == len(self.depvar):
            self.stim = self.stim[ind,:]
        if len(self.traces) == len(self.depvar):
            self.traces = self.traces[ind,:]
        self.freqs = self.freqs[ind,:]
