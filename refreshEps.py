import json
import logging
import re
import sys
from datetime import datetime
from os import mkdir, path, read
from time import sleep

import requests

# from configlocal import api_token, base_url, logging_level, recheck_wait_time
from config import api_token, base_url, logging_level, recheck_wait_time

dir = path.split(path.abspath(__file__))
dir = dir[0]
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


api_json = {"X-Emby-Token": {api_token}}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}

regex = r"^(Episode )([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|)|(TBA)$"        # This regex checks for 'Episode xxx' and 'TBA'

# refresh items found in data.dat
try:
    dat_file = open(dir+'/data.dat', mode='r+')
except FileNotFoundError:
    open(dir+'/data.dat', 'x')
    logging.info(f'File not found at {dir}/data.dat created empty file and stopping.')
    sys.exit()
logging.debug('Reading data...')
readlines = dat_file.readlines()
if not readlines:
    logging.debug('No data found. Exiting...')
    sys.exit()
dat_file.seek(0)

# Check for duplicate id numbers
logging.info('Checking for duplicates.')
lines_dedupe = []
ids = []
for line in readlines:
    # item = [timestamp, item_id, series_name, episode title]
    item = line.strip().split('\t')
    if item[1] not in ids:
        lines_dedupe.append(line)
        ids.append(item[1])

for line in lines_dedupe:
    # item = [timestamp, item_id, series_name, episode title]
    item = line.strip().split('\t')
    item_id = item[1]
    # get current name of item
    raw_data = {
        'Ids': {item_id},
        'IsMissing': False
    }
    raw_data.update(api_json)
    res = requests.get(base_url+'/Items', params=raw_data, headers=headers)
    try:
        data = json.loads(res.text)
        logging.debug('Response received and parsed!')
    except json.JSONDecodeError as e:
        e=e
        logging.critical('Failed to parse as JSON! Response= %d %s' % (res.status_code, res.text))
        sys.exit()

    try:
        current_title = data.get("Items")[0].get("Name").strip()
        series_name = data.get('Items')[0].get('SeriesName')
    except IndexError as e:
        if data.get("TotalRecordCount") == 0:
            logging.info('No items returned. Deleting line : %s' % line)
            continue
        else:
            logging.critical(f'Bro wtf hapen idk what happen heres res.text: {res.text}')
            sys.exit()
    
    if re.findall(regex, current_title):     
        # has filler episode title, refresh it
        logging.warning(f'REFRESHING item {item_id} - {series_name} - {current_title}')

        raw_data = {
            'Id': item_id,
            'ReplaceAllMetadata': True
        }
        raw_data.update(api_json)
        res = requests.post(base_url+'/Items/%s/Refresh' % (item_id), params=raw_data, headers=headers)
        
        if(res.status_code < 400):
            logging.debug('Successfully refreshed ID %s' % (item_id))
        else:
            logging.critical('Something went wrong refreshing %s! Returned code %s, %s' % (item_id, res.status_code, res.text))
        
        
        # wait then check if name has changed
        sleep(recheck_wait_time)
        logging.debug('Checking name of %s to see if it changed.' % (item_id))
        raw_data = {
            'Ids': {item_id}
        }
        raw_data.update(api_json)
        res = requests.get(base_url+'/Items', params=raw_data, headers=headers)
        try:
            data = json.loads(res.text)
            logging.debug('Response received and parsed!')
        except json.JSONDecodeError as e:
            e=e
            logging.critical('Failed to parse as JSON! Response= %d %s' % (res.status_code, res.text))
            sys.exit()
        current_title = data.get("Items")[0].get("Name").strip()
        if re.findall(regex, current_title):
            # update timestamp and write back to file
            logging.debug('Writing %s back to file with updated timestamp.' % item_id)
            item[0] = datetime.now().strftime('%D %H:%M:%S')
            dat_file.write('%s\t%s\t%s\t%s' % (item[0],item[1],item[2],item[3]) + '\n')
        else:
            # does not have dummy episode title, dont write it back to the file
            logging.warning(f'DELETING item {item_id} - {series_name} - {current_title}')
    else:
        # does not have dummy episode title, dont write it back to the file
        logging.warning(f'DELETING item {item_id} - {series_name} - {current_title}')
    # sleep(5)

dat_file.truncate()
