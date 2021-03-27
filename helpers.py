import logging
from config import api_token, base_url
import json
import requests
import sys
from tinydb import table, where

api_json = {"X-Emby-Token": api_token}
headers={"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36"}
headers.update(api_json)


def get_current_title(item_id, episodes:table.Table=None):
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
        if episodes == None:
            return
        if data.get("TotalRecordCount") == 0:
            logging.error(f'DELETING item {item_id} - Item doesnt exist on Emby')
            episodes.remove(where('id')==item_id)
            return None, None

        logging.critical(f'Bro wtf hapen idk what happened {item_id} {res.text}')
        sys.exit()