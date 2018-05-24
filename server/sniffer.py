#!/usr/bin/env python

from datetime import datetime
import json
import time

import chainer
from chainer import Chain, serializers
from chainer.datasets import TupleDataset
import chainer.functions as F
import chainer.links as L
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from scapy.all import IP, IPv6, sniff
from scapy.layers import http
import websocket

from url2vec import _str2bagofbytes as bob

BATCHSIZE = 100

_url_buffer = []
_ws = websocket.create_connection('ws://127.0.0.1:5678')

class MiyamotoModel(Chain):
    def __init__(self, _n_units, _n_out, _dropout_ratio):
        super(MiyamotoModel, self).__init__()
        with self.init_scope():
            self.l1 = L.Linear(None, _n_units)
            self.l2 = L.Linear(None, _n_units)
            self.l3 = L.Linear(None, _n_out)
        self._dropout = _dropout_ratio

    def __call__(self, x):
        _h1 = F.dropout(F.relu(self.l1(x)), ratio=self._dropout)
        _h2 = F.dropout(F.relu(self.l2(_h1)), ratio=self._dropout)
        _y = self.l3(_h2)
        return _y.reshape((len(_y),))

def _verify(_model, _dataset):
    _res = []
    _batchsize = BATCHSIZE

    for _i in range((len(_dataset)//_batchsize) + 1):
        _idx = _i * _batchsize
        if _idx + _batchsize < len(_dataset):
            _dsub = _dataset[_idx:_idx+_batchsize]
        else:
            _dsub = _dataset[_idx:]
        _x = [_d[0] for _d in _dsub]
        #_t = [_d[1] for _d in _dsub]

        _x = _model.xp.asarray(_x)
        with chainer.using_config('train', False):
            _y = _model.predictor(_x)
        _y = _y.array
        # _y = to_cpu(_y)
        _res.extend(_y)

    return _res

def _eval_urls():
    _vectors = np.asarray([np.concatenate(
        (bob(_u['host']), bob(_u['path'])))
                           for _u in _url_buffer],
                          dtype=np.float32)
    _labels = np.zeros(len(_vectors), dtype=np.int32)
    _ds = TupleDataset(_vectors, _labels)
    _scores = _verify(_model, _ds)
    _res = [{'time': _u['time'],
             'url': _u['host']+_u['path'],
             'dst': _u['dst'],
             'score': float(_s)}
            for _u, _s in zip(_url_buffer, _scores)]
    _ws.send(json.dumps(_res))

_last_eval = time.time()
def _store_url(_u):
    global _last_eval
    _url_buffer.append(_u)
    _now = time.time()
    if (_now - _last_eval) < 1:
        return
    _eval_urls()
    _last_eval = _now
    del _url_buffer[:]

def _pkt_callback(_pkt):
    if not _pkt.haslayer(http.HTTPRequest):
        return
    if IP in _pkt:
        _dst = _pkt[IP].dst
    elif IPv6 in _pkt:
        _dst = _pkt[IPv6].dst
    _http_layer = _pkt.getlayer(http.HTTPRequest)
    _host = _http_layer.fields['Host'].decode('utf-8')
    _path = _http_layer.fields['Path'].decode('utf-8')
    _store_url({'time': _pkt.time,
                'host': _host,
                'path': _path,
                'dst': str(_dst)})

if __name__ == '__main__':
    import argparse

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-i',
                         dest='interface',
                         required=True,
                         help='Interface name')
    _args = _parser.parse_args()

    _model = L.Classifier(MiyamotoModel(_n_units=256,
                                        _n_out=1,
                                        _dropout_ratio=0.75),
                          lossfun=F.sigmoid_cross_entropy,
                          accfun=F.binary_accuracy)
    serializers.load_npz('Miyamoto_20170425.model.npz', _model)

    sniff(iface=_args.interface,
          prn=_pkt_callback,
          filter='tcp port 80',
          store=0)
