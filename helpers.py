import importlib
import json
import logging
import re
import sys
from functools import lru_cache
from os import mkdir, path

import requests

dir = path.split(path.abspath(__file__))[0]

# import config
conf = importlib.import_module('config')
if path.isfile(f'{dir}/config_local.py'):
    conf = importlib.import_module('config_local')

api_token = conf.api_token
base_url = conf.base_url
check_thumbs = conf.check_thumbs
logging_level = conf.logging_level

api_json = {"X-Emby-Token": api_token}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}
headers.update(api_json)

regex = r"^(Episode )([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|)|(TBA)$"        # This regex checks for 'Episode xxx' and 'TBA'

def parse_json(json_text):
    try:
        json_obj = json.loads(json_text)
        out = json.dumps(json_obj, indent=4)
        logging.debug(out)
        return json_obj
    except json.JSONDecodeError:
        out = json_text
        logging.error(f'Error parsing JSON - {out}')

def get_current_title_by_id(item_id):
    raw_data = {
        'Ids': item_id,
        'IsMissing': False
    }
    res = requests.get(f'{base_url}/Items', params=raw_data, headers=headers)
    try:
        data = json.loads(res.text)
        logging.debug('Response received and parsed!')

        current_title = data.get("Items")[0].get("Name").strip()
        series_name = data.get("Items")[0].get("SeriesName").strip()
        return current_title, series_name
    except json.JSONDecodeError:
        logging.critical(f'Failed to parse as JSON! Response={res.status_code} {res.text}')
        sys.exit()
    except IndexError:
        if data.get("TotalRecordCount") == 0:
            return None, None

        logging.critical(f'Bro wtf hapen idk what happened {item_id} {res.text}')
        sys.exit()

def is_placeholder_title(title:str):
    return True if re.findall(regex, title) else False

def get_images_by_id(id):
    url = f'{base_url}/Items/{id}/Images'
    logging.debug(f'Requesting images from {url}')
    res = requests.get(url, headers=headers)
    return parse_json(res.text)

@lru_cache(maxsize=5)
def hxw_is_good(height, width):
    if width != 400:
        return True
    if abs(height - 567) < 5:
        return False
    return True

def has_placeholder_thumb(item_id):
    if not check_thumbs:
        return False
    episode_images = get_images_by_id(item_id)
    # print(episode_images, len(episode_images))
    if not episode_images:
        return True
        
    primary_img_data = episode_images[0]
    h = primary_img_data.get("Height")
    w = primary_img_data.get("Width")
    is_good = hxw_is_good(h, w)
    return not is_good

def logging_setup(file:str):
    try:
        mkdir(f'{dir}/logs')
    except FileExistsError:
        pass
    switcher = {
        4: logging.DEBUG,
        3: logging.INFO,
        2: logging.WARNING,
        1: logging.ERROR,
        0: logging.CRITICAL
    }
    logging.basicConfig(filename=f'{dir}/logs/{path.basename(file).split(".")[0]}.log',
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
