from flask import *
from flask_restplus import *
version = "0.1"
app = Flask(__name__)
api = Api(app, version=version)

class Sender():
  pass

@app.route('/hdn/status')
def status():
    return 'HDN is available. Version of daemon: {}'.format(version)


@api.route('/sc/<sc_n>/<int:idn>', doc={'params': {'sc_n': 'An ID of your smart-contract.', 'idn': "DMA Address"
                                                                                                " of your item."}})
class ItemWork(Resource):
    def get(self, sc_n, idn):
        return Sender.get_item(sc_id=sc_n, item=idn)


    def put(self, sc_n, idn):
        data = request.form['data']
        return Sender.push_item(sc_id=sc_n, item=idn, data=data)

    def delete(self, sc_n, idn):
        return Sender.delete_item(sc_id=sc_n, item=idn)

if __name__ == '__main__':
    app.run(port=7979)
