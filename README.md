# 🔃 No TBA for Emby

Hate having your perfect library ruined by a stray episode titled "Episode XX" or "TBA" because the data wasn't available at the time it was scanned in? These scripts will attempt to solve that by collecting episodes with these placeholder titles and periodically refreshing their metadata until an actual title is found.

## Features

* Checks for placeholder titles such as "Episode XX" or "TBA"
* Checks for placeholder thumbnails
* Ability to refresh episodes multiple times until a certain amount of days pass
* View all the episodes being tracked in the database
* Bulk check library. All of the library or by year.

## Requirements

* Emby server API token
* Emby Scripter-X plugin
* Python 3

# Setup

**Start in a directory that your Emby server can see.**

## Clone repository

```bash
git clone https://github.com/stummyhurt/noTBA-scripterx.git no-tba
cd no-tba
```

## Install requirements

```bash
pip3 install -r ./requirements.txt

# NOTE FOR LINUX: Your emby user must be able to see the modules. 
# Either add sudo to previous command or install them under your emby user.
sudo -H -u <EMBY_USER> bash -c 'pip3 install -r ./requirements.txt' 
```

## Complete Config

All that is needed is the `api_token` and `base_url`

```python
#config.py

api_token = ''
base_url = ''

# If you'd like the script to check for thumbnails as well, set to True
check_thumbs = False
```

## Check Current Media (optional)

This will check your current media for episodes with placeholder titles.

### **Warning**
```
I highly recommend having your logging level set to 2 (warn) in config.py when doing this
```

Send a string of the years you want to check in a comma separated list. By default, the script will check media from the year 2021.

```bash 
# checks media from years 2019, 2020 and 2021
python3 ./checkAllEps.py '2019,2020,2021'

# checks media from all years
python3 ./checkAllEps.py all

# checks media from 2021
python3 ./checkAllEps.py
```

## Scripter-X Setup

This Scripter-X setup will allow your server to check episodes as they're added, and automatically refresh metadata of those episodes based on a scheduled task.

**Note for Linux:** Your emby user must be able to write to the directory.

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

Setup is complete!!!

# Extras

There are a couple extra features in this collection of scripts. Namely, viewing the database that all the info is stored in, and checking huge sections of your library for placeholder titles and thumbnails.

* [Viewing the Database](#viewing-the-database)
* [Bulk Checking Episodes](#bulk-checking-episodes)

## Viewing the Database

Viewing the database is as simple as running the following command.

```bash
python3 db.py
```

You will get all the information stored in the database `db.sqlite` in a nice looking table (if your screen is >100 characters wide). Here's an example

```text
 id       series                     last_title                    checked_since      needs   needs
                                                                                      title   thumb
-------- -------------------------- ----------------------------- ------------------ ------- -------
 154883   Super Cool Show            Not a placeholder             2021-09-06 21:25           Y
 154851   Some Anime                 Episode 9                     2021-09-06 12:38   Y
 154824   Rick and Morty             Forgetting Sarick Mortshall   2021-09-05 23:41           Y
 154825   Rick and Morty             Rickmurai Jack                2021-09-05 23:41           Y
```

## Bulk Checking Episodes

At some point you may want to check all of your library for placeholder episode titles or thumbnails. That's exactly what `checkAllEps.py` is for. You also have the choice to check by year.

### **Warning**
```
I highly recommend having your logging level set to 2 (warn) in config.py when doing this
```

Send a string of the years you want to check in a comma separated list. By default, the script will check media from the current year.

```bash 
# checks media from years 2019, 2020 and 2021
python3 ./checkAllEps.py 2019,2020,2021

# checks all media
python3 ./checkAllEps.py all

# checks media from current year
python3 ./checkAllEps.py
```
