import json
import logging
import re
import sys
from datetime import datetime, timedelta
from os import mkdir, path, read
from time import sleep

import requests
from tinydb import TinyDB, where
from helpers import get_current_title

from config import (api_token, base_url, days_before_giving_up, logging_level,
                    recheck_wait_time)

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
logging.basicConfig(filename=dir+'/logs/refreshIds.log',
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

api_json = {"X-Emby-Token": api_token}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}
headers.update(api_json)

regex = r"^(Episode )([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|)|(TBA)$"        # This regex checks for 'Episode xxx' and 'TBA'

def refresh_ep(ep:object):
    item_id = ep['id']
    checked_since = datetime.strptime(ep['checked_since'], '%Y-%m-%d %H:%M')
    
    # get current name of item
    current_title, series_name = get_current_title(item_id, episodes)
    if current_title == None:
        return
    
    if not re.findall(regex, current_title):   
        # does not have dummy episode title, dont write it back to the file
        logging.warning(f'DELETING item {item_id} - {series_name} - {current_title}')
        episodes.remove(where('id') == item_id)
        return
    
    # has filler episode title, refresh it
    logging.warning(f'REFRESHING item {item_id} - {series_name} - {current_title}')

    raw_data = {
        'Id': item_id,
        'ReplaceAllMetadata': True
    }
    res = requests.post(f'{base_url}/Items/{item_id}/Refresh', params=raw_data, headers=headers)
    if(res.status_code < 400):
        logging.debug(f'Successfully refreshed ID {item_id}')
    else:
        logging.critical(f'Something went wrong refreshing {item_id}! Returned code {res.status_code}, {res.text}')
    
    
    # wait then check if name has changed
    sleep(recheck_wait_time)
    logging.debug(f'Checking name of {item_id} to see if it changed.')
    current_title, series_name = get_current_title(item_id, episodes)
    
    if not re.findall(regex, current_title):
        # does not have dummy episode title, dont write it back to the file
        logging.warning(f'DELETING item {item_id} - {series_name} - {current_title}')
        episodes.remove(where('id') == item_id)
        return

    if datetime.now() - checked_since >= timedelta(days=days_before_giving_up):
        logging.warning(f'GIVING UP on {item_id} - {series_name} - {current_title}')
        episodes.remove(where('id') == item_id)
    logging.debug(f'Episode title still looks like a placeholder. {item_id} - {current_title}')
    episodes.update({
        'series': series_name,
        'last_title': current_title
    }, where('id') == item_id)

if __name__ == '__main__':
    db = TinyDB(f'{dir}/db.json')
    episodes = db.table('Episodes')

    for ep in episodes.all():
        refresh_ep(ep)

    db.close()