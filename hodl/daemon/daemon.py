from flask import *
from flask_restplus import *

version = "0.1"
app = Flask(__name__)
api = Api(app, version=version)


class Sender:
    pass


@app.route('/status')
def status():
    return f'HDN is available. Version of daemon: {version}'


if __name__ == '__main__':
    app.run(port=7979)
