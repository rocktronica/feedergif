from datetime import datetime
import time

from subprocess import call
import os
from glob import glob

from ConfigParser import ConfigParser
config = ConfigParser()
config.read('settings.ini')

HOST = config.get('settings', 'host')
DURATION_MINUTES = int(config.get('settings', 'duration_minutes'))
BREAKFAST_HOUR = int(config.get('settings', 'breakfast_hour'))
DINNER_HOUR = int(config.get('settings', 'dinner_hour'))
SLEEP = int(config.get('settings', 'sleep'))
DROPBOX_ACCESS_TOKEN = config.get('dropbox', 'access_token')

import dropbox
dropbox_client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)

def upload(path, short_url=True):
    dropbox_path = os.path.basename(path)
    dropbox_client.put_file('/' + dropbox_path, open(path, 'rb'))
    share_response = dropbox_client.share(dropbox_path, short_url=short_url)
    return share_response['url']

def make_time(hour=0, minute=0):
    today = datetime.now()
    return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

ranges = [{
    'start': make_time(BREAKFAST_HOUR),
    'stop': make_time(BREAKFAST_HOUR, DURATION_MINUTES)
},{
    'start': make_time(DINNER_HOUR),
    'stop': make_time(DINNER_HOUR, DURATION_MINUTES)
}]

def within_range(now, start, stop):
    return (start <= now and stop >= now)

def within_ranges(now, ranges=[]):
    for range in ranges:
        if within_range(now, range['start'], range['stop']):
            return True
    return False

def test_within_range():
    hour = 0
    while (hour < 24):
        minute = 0
        while (minute < 60):
            time = make_time(hour, minute)
            on = within_ranges(time, ranges)

            print str(time) + "\t" + str(on)
            minute = minute + 1
        hour = hour + 1

def delete_images():
    os.system('rm -f images/*')

def download_image():
    os.system('curl -# -L --compressed ' + HOST + '/photo > "images/$(date +%s).jpg"')

def output_gif(filename):
    os.system('ffmpeg -pattern_type glob -i \'images/*.jpg\' -r 30 -vf scale=320:-1 "' + filename + '"')

def get_image_slugs():
    images = glob('images/*.jpg')

    if len(images) >= 1:
        return [os.path.basename(filename).split('.')[0] for filename in images]
    return []

def set_torch(on):
    os.system('curl --silent ' + HOST + '/parameters?torch=' + str(int(on)) + \
        ' > /dev/null')

if __name__ == '__main__':
    on = False

    while True:
        previously_on = on
        now = datetime.now().replace(microsecond=0)
        on = within_ranges(now, ranges)

        if (on and not previously_on):
            set_torch(True)

        print str(now) + "\t" + ('On' if on else 'Off')

        if on:
            download_image()
        else:
            images = get_image_slugs()

            if len(images) >= 1:
                first = images[0]
                last = images[-1]

                path = 'output/' + last.split('.')[0] + '.gif'

                if not os.path.isfile(path):
                    print
                    print '------------'
                    print

                    print 'BUILDING ' + path + \
                        ' FROM ' + str(len(images)) + ' IMAGES: ' \
                        + first + ' TO ' + last
                    print

                    output_gif(path)
                    print
                    print upload(path)
                    delete_images()
                    set_torch(False)

                    print
                    print '------------'
                    print

        time.sleep(SLEEP)
