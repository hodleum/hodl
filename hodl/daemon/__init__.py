from .daemon import app


def start():
    app.run(host='0.0.0.0', port=8001)


if __name__ == '__main__':
    start()
