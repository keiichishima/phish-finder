#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes
from builtins import str

import argparse
from functools import reduce
from hashlib import md5

import numpy as np

def _normalize(_v):
    _norm = np.linalg.norm(_v)
    if _norm == 0:
        return _v
    return _v / _norm

def _ngram(_string, _n=3):
    assert (_n > 1)
    if len(_string) < _n:
        return [_string]
    return [_string[_i:_i+_n] for _i in range(len(_string) - _n + 1)]

#
# URL to bag of bytes shifting 4 bits in its bytestream
#
class BagOfBytes(object):
    @classmethod
    def _str2bagofbytes(cls, _string):
        _bytes = bytearray(_string, encoding='ascii')
        _vec = np.zeros(256, dtype=int)
        for _idx in range(len(_bytes) - 1):
            _vec[_bytes[_idx]] += 1
            _vec[((_bytes[_idx] & 0xf) << 4)
                 | (_bytes[_idx + 1] >> 4)] += 1
        _vec[_bytes[-1]] += 1
        return _vec

    @classmethod
    def vectorize(cls, _string, **kwargs):
        return _normalize(cls._str2bagofbytes(_string))

def _str2bagofbytes(_string, **kwargs):
    return BagOfBytes.vectorize(_string, **kwargs)

#
# URL 2 feature hashing vector
#
def _default_hashfunc(_string):
    _hash = md5(bytes(_string, encoding='ascii'))
    _digest = _hash.digest()
    return reduce(lambda x, y: x<<8|y, _digest, 0)

class FeatureHashing(object):
    @classmethod
    def _str2fhash(cls, _string, **kwargs):
        _n = 3
        _hashfunc = _default_hashfunc
        _hashsize = 256

        if '_n' in kwargs:
            _n = kwargs['_n']
        if '_hashfunc' in kwargs:
            _hashfunc = kwargs['_hashfunc']
        if '_hashsize' in kwargs:
            _hashsize = kwargs['_hashsize']

        _strings = _ngram(_string, _n)
        _vec = np.zeros(shape=(_hashsize,), dtype=np.int)
        for _s in _strings:
            _hash = _hashfunc(_s)
            _e = -1 if (_hash & (1<<17)) == 0 else 1
            _idx = _hash % _hashsize
            _vec[_idx] += _e
        return _vec

    @classmethod
    def vectorize(cls, _string, **kwargs):
        return _normalize(cls._str2fhash(_string, **kwargs))

def _str2fhash(_string, **kwargs):
    return FeatureHashing.vectorize(_string, **kwargs)


#
# simple byte array
#
def _str2bytes(_string, **kwargs):
    return np.asarray(bytearray(_string, encoding='ascii'),
                      dtype=np.int32)

#
# FQDN to vectors by sho
#
class FQDNHack(object):
    @classmethod
    def _fqdnhack(cls, _domain):
        _vec = []
        from collections import Counter
        _ngram_words = _ngram(_string, _n=2)
        _word_counts = np.array(Counter(_ngram_words))

        # ngram features
        _vec.append(_word_counts / np.sum(_word_counts))
        # entropy features
        _vec.append(cf.calculate_entropy(domain, 0))
        _vec.append(cf.calculate_domain_level(domain))
        _vec.append(cf.calculate_domain_length(domain, 0))
        _vec.append(cf.calculate_domain_length(domain, ld=2))
        _vec.append(cf.calculate_domain_length(domain, ld=3))
        _vec.append(cf.calculate_alpha_rate(domain))
        return _vec

    @classmethod
    def vectorize(_string, **kwargs):
        return _fqdnhack(_string)


if __name__ == '__main__':
    print(BagOfBytes.vectorize('hogehoge'))
    print(_str2bagofbytes('hogehoge'))
    print(FeatureHashing.vectorize('hogehoge'))
    print(_str2fhash('hogehoge'))
