#!/usr/bin/env python

from datetime import datetime
import json
import logging
import logging.handlers
import math
import os
import platform
HOSTNAME = platform.uname()[1]
import sys
import time
from urllib.parse import urlparse

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
WEBSOCKET_SERVER_URL='ws://127.0.0.1:5678'

# URL storage
_url_buffer = []

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

def _log_results(_res_json):
    _now = datetime.now()
    _log_dir = '{logdir}/{year:04d}/{month:02d}/{day:02d}/{hour:02d}'.format(
        logdir=_args.logdir,
        year=_now.year,
        month=_now.month,
        day=_now.day,
        hour=_now.hour)
    os.makedirs(_log_dir, exist_ok=True)
    _log_file = '{log_dir}/{min:02d}'.format(
        log_dir=_log_dir, min=_now.minute)
    with open(_log_file, 'w') as _f:
        _f.write(_res_json + '\n')

_month_text = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_syslog_format = '{datetime} {hostname} CEF: 0|NML Project|Phish Finder|0.1b|100101|WEB_THREAT_DETECTION|{severity}|dvchost={hostname} app=HTTP appGroup=HTTP dst={dstip} src={srcip} request={url} msg=Suspicious rt={ldatetime}'
def _syslog_results(_res):
    _now = datetime.now()
    for _r in _res:
        if _r['prob'] < _args.logthresh:
            continue
        _sev = int(_r['prob'] * 10)
        _datetime = '{m} {d:2d} {H:02d}:{M:02d}:{S:02d}'.format(
            m=_month_text[_now.month - 1], d=_now.day,
            H=_now.hour, M=_now.minute, S=_now.second)
        _syslog_text = _syslog_format.format(
            datetime=_datetime, hostname=HOSTNAME,
            severity=_sev, srcip=_r['src'], dstip=_r['dst'],
            url='http://' + _r['url'],
            ldatetime=_datetime + ' GMT+0900')
        _logger.warn(_syslog_text)

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
             'src': _u['src'],
             'dst': _u['dst'],
             'score': float(_s),
             'prob': 0.5 * (math.tanh(_s) + 1)}
            for _u, _s in zip(_url_buffer, _scores)]
    _syslog_results(_res)
    _res_json = json.dumps(_res)
    _log_results(_res_json)
    _ws.send(_res_json)

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
        _src = _pkt[IP].src
        _dst = _pkt[IP].dst
    elif IPv6 in _pkt:
        _src = _pkt[IPv6].src
        _dst = _pkt[IPv6].dst
    _http_layer = _pkt.getlayer(http.HTTPRequest)
    _host = _http_layer.fields['Host'].decode('utf-8')
    _path = _http_layer.fields['Path'].decode('utf-8')
    _store_url({'time': _pkt.time,
                'host': _host,
                'path': _path,
                'src': str(_src),
                'dst': str(_dst)})

def _urldump_callback(_src, _dst, _url):
    if not _url.startswith('http://'):
        _url = 'http://'+ _url
    _time = time.time()
    _u = urlparse(_url)
    _host = _dst if _u.netloc == '' else _u.netloc
    _path = '/' if _u.path == '' else _u.path
    _path += _u.query
    _store_url({'time': _time,
                'host': _host,
                'path': _path,
                'src': _src,
                'dst': _dst})

if __name__ == '__main__':
    import argparse

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-i',
                         dest='interface',
                         required=True,
                         help='Interface name')
    _parser.add_argument('-d',
                         dest='logdir',
                         default='log',
                         help='Log directory')
    _parser.add_argument('-l',
                         dest='loghost',
                         default='127.0.0.1',
                         help='Syslog host')
    _parser.add_argument('-p',
                         dest='logport',
                         default=logging.handlers.SYSLOG_UDP_PORT,
                         help='Syslog port')
    _parser.add_argument('-t',
                         dest='logthresh',
                         default=0.6,
                         help='Syslog trigger threshold')
    _args = _parser.parse_args()

    # Restore the neural network model
    _model = L.Classifier(MiyamotoModel(_n_units=256,
                                        _n_out=1,
                                        _dropout_ratio=0.75),
                          lossfun=F.sigmoid_cross_entropy,
                          accfun=F.binary_accuracy)
    serializers.load_npz('Miyamoto_20170425.model.npz', _model)

    # Setup a websocket handler
    _ws = websocket.create_connection(WEBSOCKET_SERVER_URL)

    # Setup a syslog handler
    _logger = logging.getLogger('Phish_Finder')
    _logger.setLevel(logging.DEBUG)
    _lhandler = logging.handlers.SysLogHandler(address=(_args.loghost,
                                                        _args.logport))
    _lhandler.setLevel(logging.WARN)
    _logger.addHandler(_lhandler)

    if _args.interface == 'urldump':
        _line = sys.stdin.readline()
        while _line:
            # format from urldump should be 'srcip,dstip,url'
            _src, _dst, _url = _line.rstrip().split(',', 2)
            _urldump_callback(_src, _dst, _url)
            _line = sys.stdin.readline()
    else:
        sniff(iface=_args.interface,
              prn=_pkt_callback,
              filter='tcp port 80',
              store=0)
