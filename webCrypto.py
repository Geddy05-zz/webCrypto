import json
import subprocess
import csv
import os
import sys

from flask import Flask, jsonify
from flask import render_template
from flask import request
import pyrebase
from MongoDB import MongoDB
from datetime import datetime

mongo = MongoDB()
app = Flask(__name__)
application = app


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
    # Define command and arguments
    command = 'Rscript'
    path2script = 'TwitterCorrelationFullCode.R'

    path =  os.path.dirname(sys.modules['__main__'].__file__)
    print(path)
    # Variable number of args in a list
    args = ['11', '3', '9', '42']

    # Build subprocess command
    # "Rscript --vanilla TwitterCorrelationFullCode.R",
    cmd = [command, path2script]

    # a = r.source(path +"/TwitterScoreBitcoin.R")
    # x = subprocess.open("Rscript --vanilla "+path+"/TwitterScoreBitcoin.R")
    # x = subprocess.check_output("Rscript --vanilla "+path+"/bitcoin.R",stderr=subprocess.STDOUT,shell = True)

    try:
        output = subprocess.check_output("Rscript --vanilla "+path+"/bitcoin.R",stderr=subprocess.STDOUT,shell = True)
        returncode = 0
    except subprocess.CalledProcessError as e:
        output = e.output
        returncode = e.returncode

    print(returncode)

    with open('resultsTwitterScore.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        scores = []
        for row in reader:
            score = {}

            date = datetime.fromtimestamp(
                float(row["tStamp"])
            ).strftime('%d-%m %H:%M')

            score["date"] = date
            score["score"] = row["score"]
            scores.append(score)
    print (scores)
    return json.dumps(scores)


@app.route('/login', methods=['GET', 'POST'])
def loginForm():
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
    tempdata = [["Bitcoin", 0, 0, 0],
            ["Ethereum", 0, 0, 0],
            ["Litecoin", 0, 0, 0],
            ["Monero", 0, 0, 0],
            ["Ripple", 0, 0, 0]]

    data = []
    if request.method == 'POST':
        if ("token" in request.headers):
            token = request.headers["token"]
            uid = request.headers["uid"]
            db = firebase.database()
            currentPrice = mongo.get_current_value_big_five()
            userdata = db.child("users/" + uid).child("data").get(token=token).val()
            print(userdata["currencies"])
            print(currentPrice)

            for currency in tempdata:
                coin = currency[0]
                currency[1] = currentPrice[coin]["current_value"]
                if coin in userdata["currencies"]:
                    currency[2] = userdata["currencies"][coin]
                currency[3] = currency[1] * currency[2]
                data.append(currency)

            return json.dumps(data)



    if len(data) == 0:
        data = [["Bitcoin" , 0,2,1712],
                ["Ethereum" , 0,2,1712],
                ["Litecoin" , 0,2,1712],
                ["Monero" , 0,2,1712],
                ["Ripple" , 0,2,1712]]

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
    data ={}
    if("token" in request.headers and "uid" in request.headers):
        token = request.headers["token"]
        uid = request.headers["uid"]
        print(token)
        if token:
            data["budget"] = 500
            # Get a reference to the database service
            db = firebase.database()
            #
            # # data to save
            # save = {
            #     "budget": 10000,
            #     "currencies" :{"Bitcoin": 0}
            # }
            # results = db.child("users/"+uid).child("data").set(save, token)
            data = db.child("users/"+uid).child("data").get(token=token).val()
            print(data)
    else:
        print("no header set")
    return json.dumps(data)


@app.route('/buyCurrency', methods=['POST'])
def buy_currency():
    db = firebase.database()
    token = request.headers["token"]
    uid = request.headers["uid"]
    data = request.json
    budget = db.child("users/" + uid).child("data").get(token=token).val()['budget']

    owned_currency = db.child("users/" + uid).child("data").get(token=token).val()['currencies']
    print(owned_currency)
    if (float(data['price']) < float(budget)):
        newbudget = float(budget) - float(data['price'])
        owned_currency[data["currency"]] += float(data["amount"])
        save = {
            "budget": newbudget,
            "currencies": owned_currency,
        }
        db.child("users/" + uid).child("data").update(save, token=token)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    return json.dumps({'success':False}), 200, {'ContentType':'application/json'}


@app.route('/sellCurrency', methods=['POST'])
def sell_currency():
    db = firebase.database()
    token = request.headers["token"]
    uid = request.headers["uid"]
    data = request.json
    budget = db.child("users/" + uid).child("data").get(token=token).val()['budget']

    owned_currency = db.child("users/" + uid).child("data").get(token=token).val()['currencies']
    print(owned_currency)
    if (float(data['price']) < float(budget)):
        newbudget = float(budget) + float(data['price'])
        owned_currency[data["currency"]] -= float(data["amount"])
        save = {
            "budget": newbudget,
            "currency": owned_currency,
        }
        db.child("users/" + uid).child("data").update(save, token=token)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    return json.dumps({'success':False}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    # app.config["SECRET_KEY"] = "WOLFOFWALLSTREET"
    firebase = pyrebase.initialize_app(config)
    app.debug = True
    app.run(host='0.0.0.0' , port=8000)

