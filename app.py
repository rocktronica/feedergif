import argparse
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import pysftp
import glob
import os
import sys
import subprocess
import time

def has_program(program):
    try:
        subprocess.check_call(['which', program])
    except subprocess.CalledProcessError:
        return False
    else:
        return True

if (not has_program('ffmpeg')):
    print 'Missing ffmpeg dependency'
    sys.exit(1)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(TimedRotatingFileHandler('logs/debug.log',
   when="d",
   interval=1,
   backupCount=7))

parser = argparse.ArgumentParser(
    description='GIFing my cat eating!',
    usage='app.py [arguments]')

parser.add_argument("--url", type=str,
    help="Camera photo capture url",
    default='http://localhost/capture')
parser.add_argument("--sleep", type=float,
    metavar='SECONDS',
    help="number of seconds to sleep between taking photos",
    default=5)
parser.add_argument("--width", type=int,
    metavar='WIDTH',
    help="width of final gif",
    default=400)
parser.add_argument("--debug", action="store_true",
    help="run in debug mode")
parser.add_argument("--duration", type=float,
    metavar='MINUTES',
    help="duration of meal/capture, in minutes",
    default=8)
parser.add_argument("--breakfast", type=float,
    metavar='HOUR',
    help="breakfast hour",
    default=8)
parser.add_argument("--dinner", type=float,
    metavar='HOUR',
    help="dinner hour",
    default=20)
parser.add_argument("--sftp", nargs=4, type=str,
    metavar=("HOST","USERNAME","PASSWORD","PATH"),
    help="SFTP info for uploading completed GIFs")
parser.add_argument("--ifttt", type=str, nargs=3,
    metavar=("MAKER_KEY", "START_EVENT", "END_EVENT"),
    help="IFTTT info for convenient external triggering")

args = parser.parse_args()

def make_time(hour=0, minute=0):
    today = datetime.datetime.now()
    return datetime.datetime.time(
        today.replace(hour=hour, minute=minute, second=0, microsecond=0)
    )

ranges = [{
    'start': make_time(args.breakfast),
    'stop': make_time(args.breakfast, args.duration)
},{
    'start': make_time(args.dinner),
    'stop': make_time(args.dinner, args.duration)
}]

def upload(path):
    if not args.sftp: return

    (sftp_host, sftp_username, sftp_password, sftp_path) = args.sftp

    try:
        srv = pysftp.Connection(
            host=sftp_host,
            username=sftp_username,
            password=sftp_password)

        with srv.cd(sftp_path):
            srv.put(path)

        srv.close()

        return 'http://' + sftp_path + '/' + os.path.basename(path)
    except Exception as e:
        logger.debug('The SFTP upload failed: ' + str(e))

def within_ranges(now, ranges=[], debug=False):
    if debug:
        return bool(datetime.datetime.now().minute % 2)

    def within_range(now, start, stop):
        return (start <= now and stop >= now)

    for range in ranges:
        if within_range(now, range['start'], range['stop']):
            return True
    return False

def delete_images():
    call('rm -f images/*')

def download_image():
    call('curl -# -L --compressed ' + args.url + ' > "images/$(date +%s).jpg"')

def call(command):
    try:
        logger.debug(subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True))
    except subprocess.CalledProcessError, e:
        logger.error(e.output)

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

def trigger_ifttt(start, value1=None):
    if not args.ifttt: return

    (maker_key, start_event, end_event) = args.ifttt

    ifttt_url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(
        start_event if start else end_event, maker_key)

    if value1 is not None:
        ifttt_url = ifttt_url + '?value1=' + value1

    call('curl --silent ' + ifttt_url + ' > /dev/null')

def test_ranges():
    hour = 0
    while (hour < 24):
        minute = 0
        while (minute < 60):
            time = make_time(hour, minute)
            on = within_ranges(time, ranges)

            logger.debug(str(time) + "\t" + str(on))
            minute = minute + 1
        hour = hour + 1

def main(sleep, width, debug):
    on = False

    while True:
        previously_on = on
        now = datetime.datetime.now()
        time_now = datetime.datetime.time(now)
        on = within_ranges(time_now, ranges, debug=debug)

        if (on and not previously_on):
            trigger_ifttt(True)

        logger.debug(now.strftime("%Y-%m-%d %H:%M:%S")
            + "\t" + ('On' if on else 'Off'))

        if on:
            download_image()
        else:
            images = get_image_slugs()

            if len(images) >= 1:
                first = images[0]
                last = images[-1]

                path = 'output/' + last.split('.')[0] + '.gif'

                if not os.path.isfile(path):
                    logger.debug('------------')

                    logger.debug('BUILDING ' + path + \
                        ' FROM ' + str(len(images)) + ' IMAGES: ' \
                        + first + ' TO ' + last)

                    output_gif(path, width)
                    uploaded_path = upload(path)

                    if uploaded_path:
                        logger.debug(uploaded_path)

                    trigger_ifttt(False, value1=uploaded_path or '')
                    delete_images()

        time.sleep(sleep)

if __name__ == '__main__':
    main(sleep=args.sleep, width=args.width, debug=args.debug)
