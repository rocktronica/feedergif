from datetime import datetime
import time

from subprocess import call
import os
from glob import glob

def make_time(hour=0, minute=0):
    today = datetime.now()
    return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

ranges = [{
    'start': make_time(7),
    'stop': make_time(7, 8)
},{
    'start': make_time(7 + 12),
    'stop': make_time(7 + 12, 8)
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
    os.system('curl -# -L --compressed http://10.0.0.2/photo > "images/$(date +%s).jpg"')

def output_gif(filename):
    os.system('ffmpeg -pattern_type glob -i \'images/*.jpg\' -r 30 -vf scale=320:-1 "' + filename + '"')

def get_image_slugs():
    images = glob('images/*.jpg')

    if len(images) >= 1:
        return [os.path.basename(filename).split('.')[0] for filename in images]
    return []

if __name__ == '__main__':
    while True:
        now = datetime.now().replace(microsecond=0)
        on = within_ranges(now, ranges)

        print str(now) + "\t" + ('On' if on else 'Off')

        if on:
            download_image()
            print
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
                    delete_images()

                    print
                    print '------------'
                    print

        time.sleep(1)
