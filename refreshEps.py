import asyncio
import importlib
import logging
from datetime import datetime, timedelta
from os import path
from queue import Queue
from time import sleep

import requests
from tinydb import TinyDB, table, where

from helpers import (get_current_title_by_id, has_placeholder_thumb,
                     is_placeholder_title, logging_setup)

dir = path.split(path.abspath(__file__))[0]

# import config
conf = importlib.import_module('config')
if path.isfile(f'{dir}/config_local.py'):
    conf = importlib.import_module('config_local')

api_token = conf.api_token
base_url = conf.base_url
days_before_giving_up = conf.days_before_giving_up
logging_level = conf.logging_level
recheck_wait_time = conf.recheck_wait_time
limit_concurrent_requests = conf.limit_concurrent_requests

logging_setup(__file__)

api_json = {"X-Emby-Token": api_token}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}
headers.update(api_json)


async def refresh_ep(ep:object, episodes:table.Table):
    item_id = ep['id']
    # needs_thumb = ep['needs_thumb']
    # needs_title = ep['needs_title']
    checked_since = datetime.strptime(ep['checked_since'], '%Y-%m-%d %H:%M')
    
    # get current name of item
    current_title, series_name = get_current_title_by_id(item_id)
    if current_title == None and series_name == None:
        logging.error(f'DELETING item {item_id} - Item doesnt exist on Emby')
        episodes.remove(where('id')==item_id)
        return
    
    needs_title = is_placeholder_title(current_title)
    needs_thumb = has_placeholder_thumb(item_id)

    if not needs_title and not needs_thumb:   
        # does not have dummy episode title, dont write it back to the file
        logging.warning(f'DELETING item {item_id} - {series_name} - {current_title} - Thumb and title already good')
        episodes.remove(where('id') == item_id)
        return
    
    # has filler episode title, refresh it
    logging.warning(f'REFRESHING item {item_id} - {series_name} - {current_title} needs:{" thumb" if needs_thumb else ""}{" title" if needs_title else ""}')

    raw_data = {
        'Id': item_id,
        'ReplaceAllMetadata': True,
        'ReplaceAllImages': True
    }
    res = requests.post(f'{base_url}/Items/{item_id}/Refresh', params=raw_data, headers=headers)
    if(res.status_code < 400):
        logging.debug(f'Successfully refreshed ID {item_id}')
    else:
        logging.critical(f'Something went wrong refreshing {item_id}! Returned {res.status_code} - {res.text}')
    
    
    # wait then check if name has changed
    sleep(recheck_wait_time)
    logging.debug(f'Checking name of {item_id} to see if it changed.')
    current_title, series_name = get_current_title_by_id(item_id)

    needs_title = is_placeholder_title(current_title)
    needs_thumb = has_placeholder_thumb(item_id)

    if not needs_title and not needs_thumb:   
        # does not have dummy episode title, dont write it back to the file
        logging.warning(f'DELETING item {item_id} - {series_name} - {current_title} - Thumb and title good')
        episodes.remove(where('id') == item_id)
        return

    if datetime.now() - checked_since >= timedelta(days=days_before_giving_up):
        logging.warning(f'GIVING UP on {item_id} - {series_name} - {current_title} - needs:{" thumb" if needs_thumb else ""}{" title" if needs_title else ""}')
        episodes.remove(where('id') == item_id)
    
    logging.info(f'Item {item_id} - {series_name} - {current_title} - needs:{" thumb" if needs_thumb else ""}{" title" if needs_title else ""}')

    episodes.update({
        'series': series_name,
        'last_title': current_title,
        'needs_title': needs_title,
        'needs_thumb': needs_thumb
    }, where('id') == item_id)


async def main():
    db = TinyDB(f'{dir}/db.json', sort_keys=True, indent=4, separators=(',', ': '))
    episodes = db.table('Episodes', cache_size=3)

    try:
        ps = Queue()
        for ep in episodes.all():
            while ps.qsize() > limit_concurrent_requests:
                logging.info('Queue too big! Waiting for some to finish')
                await ps.get()
            ps.put(asyncio.create_task(refresh_ep(ep, episodes)))

        while not ps.empty():
            await ps.get()
    except:
        pass
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
