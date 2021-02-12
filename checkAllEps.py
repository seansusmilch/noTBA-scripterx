import json
import subprocess
import sys
from os import path
from queue import Queue

import requests

# from configlocal import api_token, base_url, logging_level, recheck_wait_time
from config import api_token, base_url, logging_level, recheck_wait_time

dir = path.split(path.abspath(__file__))
dir = dir[0]

api_json = {"X-Emby-Token": {api_token}}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}

years = '2021'

if len(sys.argv) > 1:
    if sys.argv[1] == 'None':
        years = None
    else:
        years = sys.argv[1]

## check all episodes 
raw_data = {
    'IncludeItemTypes': 'Episode',
    'Years': years,
    'Recursive': True,
    'IsMissing': False
}
raw_data.update(api_json)
res = requests.get(base_url+'/Items', params=raw_data, headers=headers)
try:
    data = json.loads(res.text)
    # print('response received!')
except json.decoder.JSONDecodeError as e:
    print(res.text)

ids = []
for item in data.get('Items'):
    id = item.get("Id")
    ids.append(id)
print('Checking %s ids!' % len(ids))
ps = Queue()
for id in ids:
    if ps.qsize() > 50:
        while ps.qsize() >= 20:
            ps.get().communicate()
    ps.put(subprocess.Popen(f'python checkEp.py Episode {id} false'))


# Check for duplicate id numbers
print('Checking for duplicates.')
dat_file = open(dir+'/data.dat', mode='r')
readlines = dat_file.readlines()

dat_filew = open(dir+'/data.dat', mode='w')
lines_dedupe = []
ids = []
for line in readlines:
    # item = [timestamp, item_id, series_name, episode title]
    item = line.strip().split('\t')
    if item[1] not in ids:
        lines_dedupe.append(line)
        dat_filew.write(line)
        ids.append(item[1])

dat_file.close()
dat_filew.close()
