import asyncio
import importlib
import json
import logging
import sys
from datetime import datetime
from os import path

import requests
from tinydb import TinyDB

from checkEp import check_episode

dir = path.split(path.abspath(__file__))[0]

# logging setup
logging.StreamHandler()

async def main():
    if not api_token or not base_url:
        logging.critical('Either your api_token or base_url is blank!')
        sys.exit()
    api_json = {"X-Emby-Token": api_token}
    headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}
    headers.update(api_json)

    years = datetime.now().year if len(sys.argv)==1 else None if sys.argv[1].lower() in ['all','none'] else sys.argv[1]
    logging.warning(f'Years={years}')
    raw_data = {
        'IncludeItemTypes': 'Episode',
        'Years': years,
        'Recursive': True,
        'IsMissing': False,
    }

    def get_items(params):
        res = requests.get(f'{base_url}/Items', params=params, headers=headers)
        try:
            data = json.loads(res.text)
        except json.decoder.JSONDecodeError:
            print(res.text)
            return []
        items = []
        for item in data.get('Items'):
            id = item.get("Id")
            items.append(id)
        return items

    ids = []
    if not check_thumbs:
        for q in ['Episode ', 'TBA']:
            raw_data.update({'NameStartsWith': q})
            ids += get_items(raw_data)

    if check_thumbs:
        ids = get_items(raw_data)

    logging.warning(f'Checking {len(ids)} ids!')
    db = TinyDB(f'{dir}/db.json', indent=4, separators=(',', ': '))
    episodes = db.table('Episodes', cache_size=3)
    
    ps = [asyncio.create_task(check_episode(id, episodes)) for id in ids]
    await asyncio.wait(ps)
    db.close()
 
if __name__ == '__main__':
    conf = importlib.import_module('config')
    if path.isfile(f'{dir}/config_local.py'):
        conf = importlib.import_module('config_local')

    api_token = conf.api_token
    base_url = conf.base_url
    check_thumbs = conf.check_thumbs

    asyncio.run(main())
