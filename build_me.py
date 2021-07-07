#!/usr/bin/env python3

import os, sys
import requests, urllib3
import json
from datetime import datetime, timedelta
import arrow 
import random
import string


TOKEN = os.environ.get("TOKEN", "")
USER = os.environ.get("USER", "rachel-ng")
URL="https://api.github.com/users/{}".format(USER)
HEADERS = {"Authorization": "token {}".format(TOKEN), "Accept": "application/vnd.github.v3+json", "Time-Zone": "Etc/UTC"}

DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ" 

GREEN = "49a24f"
GREY = "afb6bc"
RED = "b30000"

README_FILE = "README.md"
TEMPLATE_FILE = "src/readme_template.md"
IMG_FILE = "src/img.svg"
LOG_FILE = "src/log.txt"


def read_file(file_name, lines=True):
    with open(file_name,"r") as f:
        if lines:
            contents = f.readlines()
        else: 
            contents = f.read()
        f.close()
        return contents 

def write_file(file_name, contents):
    with open(file_name,"w") as f:
        f.writelines(contents)
        f.close()

def warning_the_following(loc, err):
    img = read_file(IMG_FILE)

    for i in range(len(img)): 
        if "fill" in img[i]:
            img[i] = '        fill="#{}"\n'.format(RED)

    write_file(IMG_FILE, img)

    print("error ({}): {}\t{}\n".format(datetime.utcnow(),loc, err))
    
    #with open(LOG_FILE,"a") as f:
    #    f.writelines("error ({}): {}\t{}\n".format(datetime.utcnow(),loc, err))
    #    f.close()

    sys.exit()


def check_account (url=URL, headers=HEADERS):
    try: 
        r = requests.get(url, headers=headers)
        data = r.json()
        print(data)
        created = data.get("created_at","unknown")
        created = datetime.strptime(created,DT_FORMAT)
        updated = data.get("updated_at","unknown")
        updated = datetime.strptime(updated,DT_FORMAT)
        assert created != None, "created is none"
        assert updated != None, "updated is none"
    except Exception as err: 
        warning_the_following("@line 74", err)
    return created, updated

def check_events (url="{}/events".format(URL), headers=HEADERS, params={"per_page":"1"}):
    last = None
    try: 
        r = requests.get(url,headers=headers,params=params)
        data = r.json()
        print(data)
        if len(data) > 0:
            last = data[0].get("created_at","unknown")
            last = datetime.strptime(last,DT_FORMAT) 
        assert last != None, "last is none"
    except Exception as err: 
        warning_the_following("@line 86", err)
    return last

def first_seen (created):
    seen_at = created 
    print(seen_at)
    return arrow.get(seen_at).humanize() 

def last_seen (updated, last):
    # compare last event with latest account update and choose the closer date
    seen_at = updated if updated > last else last 
    return arrow.get(seen_at) 

def status (seen_at, bonus_char, leeway=-3):
    # "last seen just now" if you were active in the past 3 hours
    timeframe = arrow.utcnow().floor('hour')
    timeframe = timeframe.shift(hours=leeway)

    time_ago = arrow.utcnow() if seen_at.is_between(timeframe, arrow.utcnow()) else seen_at 

    time_passed = arrow.utcnow() - seen_at 
    active = time_passed < timedelta(days=4)

    return active, time_ago.humanize()


def update_readme (file_name, active, time_ago):
    readme = read_file(file_name)
    
    template = read_file(TEMPLATE_FILE, False)

    write_file(file_name, template.format(IMG_FILE, "active" if active else "inactive", time_ago))

def update_img (file_name, active):
    img = read_file(file_name)

    if "fill" in img[9]:
        img[9] = '        fill="#{}"\n'.format(GREEN if active else GREY)

    write_file(file_name, img)


if __name__ == "__main__":
    created, updated = check_account()
    last = check_events()
    
    seen_at = last_seen(updated, last)
    active, time_ago = status(seen_at, "")
    
    update_readme (README_FILE, active, time_ago)
    update_img(IMG_FILE, active)



