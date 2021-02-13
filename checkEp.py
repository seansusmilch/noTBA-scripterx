import asyncio
import json
import logging
import re
import sys
from datetime import datetime
from os import mkdir, path

import requests
from tinydb import TinyDB, where

# from configlocal import api_token, base_url, logging_level
from config import api_token, base_url, logging_level

dir = path.split(path.abspath(__file__))[0]
# logging setup
try:
    mkdir(dir+'/logs')
except FileExistsError:
    pass
switcher = {
    4: logging.DEBUG,
    3: logging.INFO,
    2: logging.WARNING,
    1: logging.ERROR,
    0: logging.CRITICAL
}
logging.basicConfig(filename=dir+'/logs/addNewId.log',
    level=switcher.get(logging_level, logging.DEBUG),
    datefmt="%Y-%m-%d %H:%M:%S",
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
cons = logging.StreamHandler()
cons.setLevel(switcher.get(logging_level, logging.DEBUG))
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
cons.setFormatter(fmt)
logging.getLogger('').addHandler(cons)
logging.debug('Started script!')

api_json = {"X-Emby-Token": {api_token}}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}

regex = r"^(Episode )([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|)|(TBA)$"        # This regex checks for 'Episode xxx' and 'TBA'

async def check_episode(item_id, episodes):

    logging.info(f'CHECKING item {item_id}')
    raw_data = {
        'Ids': {item_id}
    }
    raw_data.update(api_json)
    logging.debug('Sending request...')
    res = requests.get(base_url+'/Items', params=raw_data, headers=headers)

    try:
        data = json.loads(res.text)
        logging.debug('Response received and parsed!')
    except json.decoder.JSONDecodeError as e:
        e=e
        logging.critical('Failed to parse as JSON! Response=' + res.status_code + '@' + res.text)

    item_name = data.get("Items")[0].get("Name")
    item_series = data.get('Items')[0].get('SeriesName')

    if re.findall(regex, item_name):
        # add to list of items that need an update
        # creation_date = datetime.fromtimestamp(path.getmtime(item_path)).strftime('%D %H:%M:%S')
        if episodes.contains(where('id') == item_id):
            logging.info(f'This id is already in the database. {item_id}')
            return

        logging.warning(f'ADDING item {item_id} - {item_series} - {item_name}')
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        episodes.insert({
            'id': item_id,
            'series': item_series,
            'last_title': item_name,
            'checked_since': now
        })
    else:
        logging.debug('Episode title changed! LETS GOOOOO')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        args = []
        for a in sys.argv: args.append(a)
        logging.error('Incorrect number of arguments! ARGS=%s' % args)
        sys.exit()

    item_type = sys.argv[1]
    item_id = sys.argv[2]
    item_isvirtual = sys.argv[3].lower() in ['1', 'true']

    if item_type != 'Episode' or item_isvirtual:        # Exit if item is virtual or is not an episode
        logging.warning(f'Item is virtual. Exiting. ARGS={item_id};{item_type};{item_isvirtual}')
        sys.exit()
    db = TinyDB(f'{dir}/db.json')
    episodes = db.table('Episodes')
    asyncio.run(check_episode(item_id, episodes))
    db.close()
