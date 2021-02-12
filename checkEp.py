import json
import logging
import re
import sys
from datetime import datetime
from os import mkdir, path

import requests

# from configlocal import api_token, base_url, logging_level
from config import api_token, base_url, logging_level

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

# fake_args = ['that one path', 'Episode', '146603', 'B:/media/Sonarr/Weeb/Gangsta/Season 01/Gangsta. - S01E01 - Bluray-1080p.mkv', False]
# item_type = fake_args[1]
# item_id = fake_args[2]
# item_path = fake_args[3]
# item_isvirtual = fake_args[4]

api_json = {"X-Emby-Token": {api_token}}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}

regex = r"^(Episode )([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|)|(TBA)$"        # This regex checks for 'Episode xxx' and 'TBA'

def check_episode(item_id):

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
        creation_date = datetime.now().strftime('%D %H:%M:%S')

        with open(dir+'/data.dat') as ids_file:
            text = ids_file.read()

        with open(dir+'/data.dat', 'a') as ids_file:
            if not text.endswith('\n') and text != '':
                ids_file.write('\n')
            ids_file.write(f'{creation_date}\t{item_id}\t{item_series}\t{item_name}')
            logging.warning(f'ADDING item {item_id} - {item_series} - {item_name}')
            ids_file.close()
    else:
        logging.debug('Episode title changed! LETS GOOOOO')

# check_episode(item_id, item_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        args = []
        for a in sys.argv: args.append(a)
        logging.error('Incorrect number of arguments! ARGS=%s' % args)
        sys.exit()

    item_type = sys.argv[1]
    item_id = sys.argv[2]
    # item_path = sys.argv[3]
    item_isvirtual = sys.argv[3].lower() in ['1', 'true']

    if item_type != 'Episode' or item_isvirtual:        # Exit if item is virtual or is not an episode
        print('exiting ', item_type, ' ', item_isvirtual)
        sys.exit()

    # make sure data.dat exists
    try:
        open(dir+'/data.dat', mode='x')
    except FileExistsError:
        pass

    check_episode(item_id)
