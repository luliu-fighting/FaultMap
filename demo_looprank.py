"""
@author: Simon Streicher

"""

import logging
import json
import os

import config_setup
from ranking.noderank import looprank

logging.basicConfig(level=logging.INFO)

dataloc, _ = config_setup.get_locations()
noderank_config = json.load(open(os.path.join(dataloc, 'config'
                                              '_noderank' + '.json')))

writeoutput = noderank_config['writeoutput']
mode = noderank_config['mode']
cases = noderank_config['cases']

for case in cases:
    looprank(mode, case, writeoutput)
