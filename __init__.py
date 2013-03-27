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
            if lin == 'STIMULUS\n':
                inside_stimulus = True
            if lin == 'END_STIMULUS\n':
                if inside_stimulus:
                    data_stim.append([])
                inside_stimulus = False
            if lin == 'TRACE\n':
                inside_trace = True
            if lin == 'END_TRACE\n':
                inside_trace = False
                data_trace.append([])
            if lin == 'PARAMS\n':
                inside_params = True
            if lin == 'END_PARAMS\n':
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


    def _str_list_conv(self,str_list):
        ret = []
        for tra in str_list:
            if len(tra)>0 and tra[1] == 'channel=1\n':
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
        self.traces = self.traces[ind,:]
