#! /usr/bin/env python2
import itertools
import numpy as np

def stack(t1, t2, f):
    t1.data = f((t1.data, t2.data))
    return t1

class TrialData:
    header = None
    fields = []
    data = None
    f = lambda s,x: map(float, x.split())
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

    def get_avg_columns(self,names):
        if len(self.data.shape) == 3:
            return self.get_columns(names).mean(axis=2)
        else:
            return self.get_columns(names)

    def get_err(self, n1, n2):
        c1 = self.get_columns(n1)
        c2 = self.get_columns(n2)
        return c1-c2

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

def stack_iterator(iterable,**kwargs):
    last_header = None
    datasets = {}
    for trial in iterator(iterable,**kwargs):
        if trial.header in datasets:
            datasets[trial.header].stack(trial, trunc_stack)
        else:
            if last_header != None:
                yield datasets[last_header]
            last_header = trial.header
            datasets[trial.header] = trial
        if last_header == None:
            last_header = trial.header
    yield datasets[datasets.keys()[0]]

def sum_stack((np1,np2)):
    size = min(np1.shape[0], np2.shape[0])
    return np1+np2

def trunc_stack((np1, np2)):
    size = min(np1.shape[0], np2.shape[0])
    return np.dstack((np1[:size,:],np2[:size,:]))
    
if __name__=='__main__':
    import sys
    import numpy as np
    import fileinput
    
    for stack in stack_iterator(fileinput.input(), data_post=np.array):
        print "{} : {} : {}".format(stack.header, stack.fields, stack.data.shape)


