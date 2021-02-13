# 🔃 No TBA for Emby

Hate having your perfect library ruined by a stray episode titled "Episode XX" or "TBA" because the data wasn't available at the time it was scanned in? These scripts will attempt to solve that by collecting episodes with these placeholder titles and periodically refreshing their metadata until an actual title is found.

## Requirements

* Emby server API token
* Emby Scripter-X plugin
* Python 3

# Setup

**Start in a directory that your Emby server can see. This is so that Scripter-X will be able to run them.**

## Clone repository

```bash
git clone https://github.com/stummyhurt/noTBA-scripterx.git no-tba
cd no-tba
```

## Install requirements

```bash
pip install -r ./requirements.txt
```

## Complete Config

All that is needed is the `api_token` and `base_url`

```python
#config.py

api_token = ''
base_url = ''
```

## Check Current Media (optional)

This will check your current media for episodes with placeholder titles.

### **Warning**
```
I highly recommend having your logging level set to 2 (warn) in config.py when doing this
```

This process may take awhile depending on how much media is on your server. Send a string of the years you want to check in a comma separated list. By default, the script will check media from the year 2021.

```bash 
# checks media from years 2019, 2020 and 2021
python ./checkAllEps.py '2019,2020,2021'

# checks ALL media
python ./checkAllEps.py 'None'

# checks media from 2021
python ./checkAllEps.py
```

## Scripter-X Setup

This Scripter-X setup will allow your server to check episodes as they're added, and automatically refresh metadata of those episodes based on a scheduled task.

### Find Python

First, we need to know the path for python.

```bash
# For UNIX
which python3
```
```powershell
# For PowerShell
Get-Command python

# For CMD
where python
```

In my case, python is located at `/usr/bin/python3`

### Add Task for **onMediaItemAddedComplete**

Under the Scripter-X plugin page, find the event **onMediaItemAddedComplete** and add a task that matches the following.

```bash
# Scipt File
/path/to/checkEp.py

# Interpreter
/path/to/python3

# Parameters (Quotes are needed!)
"%item.type%" "%item.id%" %item.isvirtual%
```
Don't forget to click the check mark.

![Example](https://i.imgur.com/3Jyha6r.png)

### Add Task for **onScheduledTask**

Under the Scripter-X plugin page, find the event **onScheduledTask** and add a task that matches the following.

```bash
# Scipt File
/path/to/refreshEps.py

# Interpreter
/path/to/python3
```
Don't forget to click the check mark.

![Example](https://i.imgur.com/aqgIy78.png)

### Set Schedule for **onScheduledTask**

Under Emby's `Scheduled Tasks` page, find `Emby ScripterX Scheduled Task` and set it to run on your desired schedule. An example would be to run the script daily at 4am.

![Example](https://i.imgur.com/GZdjkQv.png)

Under Emby's `Scheduled Tasks` page, find `Emby ScripterX Scheduled Task` and set it to run on your desired schedule. I recommend daily at 4am.
