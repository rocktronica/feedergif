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

@app.route('/')
def index():
    return flask.render_template('index.html',
        log = get_log_tail(),
        output_gif_list = sorted(
            glob.glob('output/*.gif'),
            key=os.path.getmtime,
            reverse=True
        ),
    )

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)
