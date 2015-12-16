import ConfigParser
import datetime
import dropbox
import glob
import os
import time

config = ConfigParser.ConfigParser()
config.read('settings.ini')

HOST = config.get('settings', 'host')
DURATION_MINUTES = int(config.get('settings', 'duration_minutes'))
BREAKFAST_HOUR = int(config.get('settings', 'breakfast_hour'))
DINNER_HOUR = int(config.get('settings', 'dinner_hour'))
SLEEP = int(config.get('settings', 'sleep'))
SCALE = int(config.get('settings', 'scale'))
DROPBOX_ACCESS_TOKEN = config.get('dropbox', 'access_token')
IFTTT_HUE_LIGHTS_ON = config.get('ifttt', 'hue_lights_on')
IFTTT_HUE_LIGHTS_OFF = config.get('ifttt', 'hue_lights_off')

def make_time(hour=0, minute=0):
    today = datetime.datetime.now()
    return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

ranges = [{
    'start': make_time(BREAKFAST_HOUR),
    'stop': make_time(BREAKFAST_HOUR, DURATION_MINUTES)
},{
    'start': make_time(DINNER_HOUR),
    'stop': make_time(DINNER_HOUR, DURATION_MINUTES)
}]

dropbox_client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)

def upload(path, short_url=True):
    dropbox_path = os.path.basename(path)
    dropbox_client.put_file('/' + dropbox_path, open(path, 'rb'))
    share_response = dropbox_client.share(dropbox_path, short_url=short_url)
    return share_response['url']

def within_ranges(now, ranges=[]):
    def within_range(now, start, stop):
        return (start <= now and stop >= now)

    for range in ranges:
        if within_range(now, range['start'], range['stop']):
            return True
    return False

def delete_images():
    os.system('rm -f images/*')

def download_image():
    os.system('curl -# -L --compressed ' + HOST + '/photo > "images/$(date +%s).jpg"')

def output_gif(filename, width=None):
    command = 'ffmpeg -pattern_type glob -i \'images/*.jpg\' -r 30'

    if width:
        command = command + ' -vf scale=' + str(width) + ':-1'

    command = command + ' ' + filename

    os.system(command)

def get_image_slugs():
    images = glob.glob('images/*.jpg')

    if len(images) >= 1:
        return [os.path.basename(filename).split('.')[0] for filename in images]
    return []

def set_lights(on):
    ifttt_url = IFTTT_HUE_LIGHTS_ON if on else IFTTT_HUE_LIGHTS_OFF
    os.system('curl --silent ' + ifttt_url + ' > /dev/null')

def test_ranges():
    hour = 0
    while (hour < 24):
        minute = 0
        while (minute < 60):
            time = make_time(hour, minute)
            on = within_ranges(time, ranges)

            print str(time) + "\t" + str(on)
            minute = minute + 1
        hour = hour + 1

def main():
    on = False

    while True:
        previously_on = on
        now = datetime.datetime.now().replace(microsecond=0)
        on = within_ranges(now, ranges)

        if (on and not previously_on):
            set_lights(True)

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

                    output_gif(path, SCALE)
                    print
                    print upload(path)
                    delete_images()
                    set_lights(False)

                    print
                    print '------------'
                    print

        time.sleep(SLEEP)

if __name__ == '__main__':
    main()
