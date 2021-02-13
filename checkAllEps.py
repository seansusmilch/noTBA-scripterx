import asyncio
import json
import logging
import sys
from os import path

import requests
from tinydb import TinyDB

from checkEp import check_episode
# from configlocal import api_token, base_url, logging_level, recheck_wait_time
from config import api_token, base_url, logging_level, recheck_wait_time

dir = path.split(path.abspath(__file__))[0]
# logging setup
logging.StreamHandler()

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
    'IsMissing': False,
}
raw_data.update(api_json)

ids = []
for q in ['Episode ', 'TBA']:

    raw_data.update({'NameStartsWith': q})

    res = requests.get(base_url+'/Items', params=raw_data, headers=headers)
    try:
        data = json.loads(res.text)
    except json.decoder.JSONDecodeError:
        print(res.text)

    for item in data.get('Items'):
        id = item.get("Id")
        ids.append(id)

async def run():    
    print('Checking %s ids!' % len(ids))
    db = TinyDB(f'{dir}/db.json')
    episodes = db.table('Episodes')

    ps = [asyncio.create_task(check_episode(id, episodes)) for id in ids]
    done,pending = await asyncio.wait(ps)

asyncio.run(run())
