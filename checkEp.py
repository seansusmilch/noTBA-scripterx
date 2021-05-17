import asyncio
import logging
import sys
from datetime import datetime
from os import path

from db import theSqliteDict
from helpers import (get_current_title_by_id, get_db, has_placeholder_thumb,
                     is_placeholder_title, logging_setup)

dir = path.split(path.abspath(__file__))[0]

logging_setup(__file__)

async def check_episode(item_id, episodes:theSqliteDict):

    logging.info(f'CHECKING item {item_id}')

    current_title, series_name = get_current_title_by_id(item_id)

    if current_title == None and series_name == None:
        logging.error(f'Item {item_id} doesnt exist on Emby')
        return

    needs_thumb = has_placeholder_thumb(item_id)
    needs_title = is_placeholder_title(current_title)

    if not needs_title and not needs_thumb:
        logging.debug('Episode has valid title & thumbnail!')
        return
    
    # item needs to be refreshed. add to database.
    if episodes._contains(item_id):
        logging.info(f'This id is already in the database. Updaing values. {item_id} {current_title} needs:{" thumb" if needs_thumb else ""}{" title" if needs_title else ""}')
        episodes._update({
            'needs_thumb': needs_thumb,
            'needs_title': needs_title
        }, item_id)
        return

    logging.warning(f'ADDING item {item_id} - {series_name} - {current_title} - needs:{" thumb" if needs_thumb else ""}{" title" if needs_title else ""}')
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    episodes._set(item_id, {
        'id': item_id,
        'series': series_name,
        'last_title': current_title,
        'checked_since': now,
        'needs_title': needs_title,
        'needs_thumb': needs_thumb
    })

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
        logging.info(f'Item is virtual. Exiting. ARGS={item_id};{item_type};{item_isvirtual}')
        sys.exit()
    db = get_db()
    asyncio.run(check_episode(item_id, db))
    db.close()
