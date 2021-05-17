import asyncio
from helpers import get_db
import importlib
import json
import logging
import sys
from datetime import datetime
from os import path
from queue import Queue

import requests
from alive_progress import alive_bar

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
    with alive_bar(len(ids), bar='blocks', spinner='dots_waves2') as bar:
        db = get_db()

        async def run_with_progress(id):
            await check_episode(id, db)
            bar()

        # Optimal qsize limit might be 8
        # 3 = 59.9
        # 5 = 61.4
        # 7 = 58.5
        # 8 = 64
        # 9 = 59.5
        # 10 = 57.6

        ps = Queue()
        for id in ids:
            while ps.qsize() > limit_concurrent_requests:
                await ps.get()
            ps.put(asyncio.create_task(run_with_progress(id)))

        while not ps.empty():
            await ps.get()
    
    db.close()
 
if __name__ == '__main__':
    conf = importlib.import_module('config')
    if path.isfile(f'{dir}/config_local.py'):
        conf = importlib.import_module('config_local')

    api_token = conf.api_token
    base_url = conf.base_url
    check_thumbs = conf.check_thumbs
    limit_concurrent_requests = conf.limit_concurrent_requests

    asyncio.run(main())
