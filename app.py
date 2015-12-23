import argparse
import ConfigParser
import datetime
import logging
import pysftp
import glob
import os
import sys
import subprocess
import time

logging.basicConfig(filename='logs/debug.log', level=logging.DEBUG)

config = ConfigParser.ConfigParser()
config.read('settings.ini')

HOST = config.get('settings', 'host')
DURATION_MINUTES = int(config.get('settings', 'duration_minutes'))
BREAKFAST_HOUR = int(config.get('settings', 'breakfast_hour'))
DINNER_HOUR = int(config.get('settings', 'dinner_hour'))
SFTP_HOST = config.get('sftp', 'host')
SFTP_USERNAME = config.get('sftp', 'username')
SFTP_PASSWORD = config.get('sftp', 'password')
SFTP_PATH = config.get('sftp', 'path')
IFTTT_HUE_LIGHTS_ON = config.get('ifttt', 'hue_lights_on')
IFTTT_HUE_LIGHTS_OFF = config.get('ifttt', 'hue_lights_off')

def make_time(hour=0, minute=0):
    today = datetime.datetime.now()
    return datetime.datetime.time(
        today.replace(hour=hour, minute=minute, second=0, microsecond=0)
    )

ranges = [{
    'start': make_time(BREAKFAST_HOUR),
    'stop': make_time(BREAKFAST_HOUR, DURATION_MINUTES)
},{
    'start': make_time(DINNER_HOUR),
    'stop': make_time(DINNER_HOUR, DURATION_MINUTES)
}]

def upload(path):
    srv = pysftp.Connection(
        host=SFTP_HOST,
        username=SFTP_USERNAME,
        password=SFTP_PASSWORD)

    with srv.cd(SFTP_PATH):
        srv.put(path)

    srv.close()

    return 'http://' + SFTP_PATH + '/' + os.path.basename(path)

def within_ranges(now, ranges=[]):
    def within_range(now, start, stop):
        return (start <= now and stop >= now)

    for range in ranges:
        if within_range(now, range['start'], range['stop']):
            return True
    return False

def delete_images():
    call('rm -f images/*')

def download_image():
    call('curl -# -L --compressed ' + HOST + '/photo > "images/$(date +%s).jpg"')

def call(command):
    try:
        logging.debug(subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True))
    except subprocess.CalledProcessError, e:
        logging.error(e.output)

def output_gif(filename, width=None):
    command = 'ffmpeg -pattern_type glob -i \'images/*.jpg\' -r 30'

    if width:
        command = command + ' -vf scale=' + str(width) + ':-1'

    command = command + ' ' + filename
    call(command)

def get_image_slugs():
    images = glob.glob('images/*.jpg')

    if len(images) >= 1:
        return [os.path.basename(filename).split('.')[0] for filename in images]
    return []

def set_lights(on):
    ifttt_url = IFTTT_HUE_LIGHTS_ON if on else IFTTT_HUE_LIGHTS_OFF
    call('curl --silent ' + ifttt_url + ' > /dev/null')

def test_ranges():
    hour = 0
    while (hour < 24):
        minute = 0
        while (minute < 60):
            time = make_time(hour, minute)
            on = within_ranges(time, ranges)

            logging.debug(str(time) + "\t" + str(on))
            minute = minute + 1
        hour = hour + 1

def main(sleep, width):
    on = False

    while True:
        previously_on = on
        now = datetime.datetime.time(
            datetime.datetime.now()
        )
        on = within_ranges(now, ranges)

        if (on and not previously_on):
            set_lights(True)

        logging.debug(str(now) + "\t" + ('On' if on else 'Off'))

        if on:
            download_image()
        else:
            images = get_image_slugs()

            if len(images) >= 1:
                first = images[0]
                last = images[-1]

                path = 'output/' + last.split('.')[0] + '.gif'

                if not os.path.isfile(path):
                    set_lights(False)

                    logging.debug('------------')

                    logging.debug('BUILDING ' + path + \
                        ' FROM ' + str(len(images)) + ' IMAGES: ' \
                        + first + ' TO ' + last)

                    output_gif(path, width)

                    uploaded_path = upload(path)
                    logging.debug(uploaded_path)
                    delete_images()

        time.sleep(sleep)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--sleep", type=float,
        help="number of seconds to sleep between taking photos",
        default=float(config.get('settings', 'sleep')))

    parser.add_argument("-w", "--width", type=int, help="width of final gif",
        default=int(config.get('settings', 'scale')))

    args = parser.parse_args()

    main(sleep=args.sleep, width=args.width)
