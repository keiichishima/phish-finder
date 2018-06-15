#!/usr/bin/env python

import argparse
import json
import os

import pandas as pd

_parser = argparse.ArgumentParser()
_parser.add_argument('-r',
                     dest='root',
                     required=True,
                     help='preload root directory')
_args = _parser.parse_args()

_filepaths = []
for _root, _dirs, _filenames in os.walk(_args.root):
    _filepaths.extend([os.path.join(_root, _filename)
                      for _filename in _filenames])

_url_prob = {'url': [], 'prob': []}
for _filepath in _filepaths:
    if _filepath.endswith('txz'):
        continue
    with open(_filepath, 'r') as _f:
        for _line in _f:
            for _r in json.loads(_line.rstrip()):
                _url_prob['url'].append(_r['url'])
                _url_prob['prob'].append(int(_r['prob'] * 100))

_df = pd.DataFrame(data=_url_prob)
_df = _df.groupby(['url', 'prob']).size().reset_index()
_df.columns = ['url', 'prob', 'size']
_df = _df.sort_values(by=['size', 'prob'], ascending=False)

for _u in _df[_df['prob']>90]['url'].head(50):
    print(_u)

#print(_df[_df['prob']>80].head(50))
