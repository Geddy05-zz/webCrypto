import json

from flask import Flask, jsonify
from flask import render_template
from flask import request
import pyrebase
from MongoDB import MongoDB

from analyzed import analyzed
from trade_currency import trade_currency
from user import user

mongo = MongoDB()
app = Flask(__name__)
application = app
debug = False

# configuration for firebase
config = {
  "apiKey": "AIzaSyAU9tWB9Op8u9ABG91vznQOMZWQARxLBio",
  "authDomain": "wolfofwallstreet-dec9b.firebaseapp.com",
  "databaseURL": "https://wolfofwallstreet-dec9b.firebaseio.com",
  "storageBucket": "93386450068"
}

@app.route('/')
def index():
    data = mongo.get_current_value_big_five()
    return render_template('index.html',
                           title='Home',
                           currency_value=data)

@app.route('/twitter', methods=['GET','POST'])
def rscript():
    coin = request.args.get("coin")
    analyzed.ta(coin = coin,debug=debug)

    scores = analyzed().twitter(coin = coin,debug=debug)
    return json.dumps(scores)

@app.route('/ta', methods=['GET','POST'])
def ta():
    coin = request.args.get("coin")
    isPositief = analyzed.ta(coin=coin, debug=debug)
    return json.dumps(isPositief)

@app.route('/sentiment', methods=['GET','POST'])
def sentiment():
    coin = request.args.get("coin")
    scores = analyzed.sentiment(coin = coin,debug=debug)
    return json.dumps(scores)


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        try:
            auth = firebase.auth()
            data = request.form
            user = auth.sign_in_with_email_and_password(data['username'], data['password'])
            print(user["localId"])
            print(user["idToken"])
            token = {"token":user['idToken'] , "uid": user["localId"]}

        except:
            token = {}

        return jsonify(**token)

    else:
        return render_template('login.html',
                               title='Home')


@app.route('/btc')
def bitcoin():
    data = mongo.get_current_values("Bitcoin")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('btc.html',
                           title='Bitcoin',
                           url="https://coinmarketcap.com/static/img/coins/16x16/bitcoin.png",
                           user=user,
                           currency_value=data
                           )


@app.route('/eth')
def eth():
    data = mongo.get_current_values("Ethereum")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('eth.html',
                           title='Ethereum',
                           url="https://coinmarketcap.com/static/img/coins/16x16/ethereum.png",
                           user=user,
                           currency_value=data
                           )


@app.route('/ltc')
def ltc():
    data = mongo.get_current_values("Litecoin")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('ltc.html',
                           title='Litecoin',
                           url="https://coinmarketcap.com/static/img/coins/16x16/litecoin.png",
                           user=user,
                           currency_value=data
                           )

@app.route('/xmr')
def xmr():
    data = mongo.get_current_values("Monero")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xmr.html',
                           title='Monero',
                           url = "https://coinmarketcap.com/static/img/coins/16x16/monero.png",
                           user=user,
                           currency_value=data
                           )

@app.route('/xrp')
def xrp():
    data = mongo.get_current_values("Ripple")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xrp.html',
                           title='Ripple',
                           url="https://coinmarketcap.com/static/img/coins/16x16/ripple.png",
                           user=user,
                           currency_value=data
                           )

@app.route('/profile', methods=['GET', 'POST'])
def getprofile():
    data = user().get_profile(mongo, firebase, request)

    if data:
        return json.dump(data)

    return render_template('profile.html',
                           title='Bitcoin',
                           data=data
                           )

@app.route('/get_last_tick_data')
def get_last_hours():
    coin = request.args.get('title')
    data = mongo.get_tick_values_of_last_12_hour(coin)
    return json.dumps(data)

@app.route('/getUserInfo')
def get_user_info():
    data = user().user_info(firebase,request)
    return json.dumps(data)


@app.route('/buyCurrency', methods=['POST'])
def buy_currency():
    trade = trade_currency().buy_currency(firebase,request)

    return json.dumps({'success':trade}), 200, {'ContentType':'application/json'}


@app.route('/sellCurrency', methods=['POST'])
def sell_currency():
    trade_currency().sell_currency(firebase,request)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    # app.config["SECRET_KEY"] = "WOLFOFWALLSTREET"
    firebase = pyrebase.initialize_app(config)
    app.debug = True
    app.run(host='0.0.0.0' , port=8000)

