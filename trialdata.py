#! /usr/bin/env python2
import itertools

def stack(t1, t2, f):
    t1.data = f((t1.data, t2.data))
    return t1

class TrialData:
    header = None
    fields = []
    data = None
    f = lambda s,x: x.split()
    data_post = lambda s,x: x
    def __init__(self,header,**kwargs):
        if 'data_post' in kwargs:
            self.data_post = kwargs['data_post']

        self.header = header

    def add_data(self,data):
        if not self.data:
            self.data = [self.f(data)]
        else:
            self.data.append(self.f(data))
    def set_fields(self,data):
        self.fields = data.split()

    def stack(self,td,f):
        self.data = f((self.data, td.data))

    def get_columns(self, names):
        I = []
        for n in names:
            try:
                I.append(self.fields.index(n))
            except ValueError as e:
                raise ValueError("'{}' not in {}".format(n,self.fields))
        return self.data[:,I]

    def post(self):
        self.data = self.data_post(self.data)
        return self

    def __str__(self):
        return "h: {}\nf: {}\n{}".format(self.header, self.fields, self.data)
            

def iterator(iterable,**kwargs):
    states = itertools.cycle(['header','fields','data'])
    state = states.next()

    for line in map(str.strip, iterable):
        (nothing,sep,rest) = map(str.strip, line.partition('#'))
        if state=='header':
            if sep:
                trial = TrialData(rest,**kwargs)
                state = states.next()
                continue

        if state=='fields':
            if sep:
                trial.set_fields(rest)
                state = states.next()
                continue

        if state=='data':
            if sep:
                yield trial.post()
                state = states.next()
                assert(state == 'header')
                trial = TrialData(rest,**kwargs)
                state = states.next()
                continue
            else:
                trial.add_data(line)
    yield trial.post()

def sum_stack((np1,np2)):
    size = min(np1.shape[0], np2.shape[0])
    return np1+np2

def trunc_stack((np1, np2)):
    size = min(np1.shape[0], np2.shape[0])
    #try:
    #    np1.shape[2]
    #    return np.concatenate((np1[:size,:,:],np2[:size,:]),axis=2)
    #except IndexError:
    return np.dstack((np1[:size,:],np2[:size,:]))


    
if __name__=='__main__':
    import sys
    import numpy as np

    datasets = {}
    for trial in iterator(sys.stdin,data_post=np.array):
        if trial.header in datasets:
            datasets[trial.header].stack(trial, trunc_stack)
        else:
            datasets[trial.header] = trial
        
    for mset in datasets:
        dset = datasets[mset]
        print "{} shape: {}\n".format(mset, dset.data.shape)
        data = dset.get_columns(['y','z'])
        print data[:,:,0]
#avg = datasets[mset].data.mean(axis=2)
