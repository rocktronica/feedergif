import argparse
import flask
import glob
import os
import subprocess

app = flask.Flask(
    __name__,
    template_folder='templates',
    static_folder='output'
)

@app.route('/log')
def get_log_tail():
    return subprocess.check_output('tail -20 logs/debug.log', shell=True)

@app.route('/stats')
def get_stats(jsonify=True):
    df_output = subprocess.check_output(
            'df -h | grep "/" | head -1',
            stderr=subprocess.STDOUT,
            shell=True
        ).split()

    stats = dict(
        size = df_output[1],
        used = df_output[2],
        available = df_output[3],
        percent_used = df_output[4]
    )

    return flask.jsonify(stats) if jsonify else stats

@app.route('/')
def index():
    return flask.render_template('index.html',
        log = get_log_tail(),
        stats = get_stats(False),
        output_gif_list = sorted(
            glob.glob('output/*.gif'),
            key=os.path.getmtime,
            reverse=True
        ),
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='0.0.0.0')
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--debug", type=bool, default=True)
    arguments = parser.parse_args()

    app.debug = arguments.debug
    app.run(host=arguments.host, port=arguments.port)
