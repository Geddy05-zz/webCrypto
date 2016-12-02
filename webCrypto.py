from flask import Flask
from flask import render_template
from flask import request
from MongoDB import MongoDB
import json

mongo = MongoDB()
app = Flask(__name__)


@app.route('/')
def index():
    data = mongo.get_current_value_big_five()
    return render_template('index.html',
                           title='Home',
                           currency_value=data)


@app.route('/btc')
def bitcoin():
    data = mongo.get_current_values("Bitcoin")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('btc.html',
                           title='Bitcoin',
                           user=user)


@app.route('/eth')
def eth():
    data = mongo.get_current_values("Ethereum")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('eth.html',
                           title='Ethereum',
                           user=user)


@app.route('/ltc')
def ltc():
    data = mongo.get_current_values("Litecoin")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('ltc.html',
                           title='Litecoin',
                           user=user)


@app.route('/xmr')
def xmr():
    data = mongo.get_current_values("Monero")
    print(mongo.get_tick_values_of_last_12_hour("Monero"))
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xmr.html',
                           title='Monero',
                           user=user,
                           currency_value=data
                           )


@app.route('/get_last_tick_data')
def get_last_hours():
    coin = request.args.get('title')
    data = mongo.get_tick_values_of_last_12_hour(coin)
    return json.dumps(data)


@app.route('/xrp')
def xrp():
    data = mongo.get_current_values("Ripple")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xrp.html',
                           title='Bitcoin',
                           user=user)


if __name__ == '__main__':
    app.run()

