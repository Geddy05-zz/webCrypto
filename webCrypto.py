import json

from flask import Flask, jsonify
from flask import render_template
from flask import request
import pyrebase
from MongoDB import MongoDB

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
                           user=user,
                           currency_value=data
                           )


@app.route('/eth')
def eth():
    data = mongo.get_current_values("Ethereum")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('eth.html',
                           title='Ethereum',
                           user=user,
                           currency_value=data
                           )


@app.route('/ltc')
def ltc():
    data = mongo.get_current_values("Litecoin")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('ltc.html',
                           title='Litecoin',
                           user=user,
                           currency_value=data
                           )


@app.route('/xmr')
def xmr():
    data = mongo.get_current_values("Monero")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xmr.html',
                           title='Monero',
                           user=user,
                           currency_value=data
                           )


@app.route('/xrp')
def xrp():
    data = mongo.get_current_values("Ripple")
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xrp.html',
                           title='Bitcoin',
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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         login_user(user)
#
#         Flask.flash('Logged in successfully.')
#
#         next = Flask.request.args.get('next')
#         # is_safe_url should check if the url is safe for redirects.
#         # See http://flask.pocoo.org/snippets/62/ for an example.
#         # if not is_safe_url(next):
#             # return Flask.abort(400)
#
#         return Flask.redirect(next or Flask.url_for('index'))
#     return Flask.render_template('login.html', form=form)




if __name__ == '__main__':
    # app.config["SECRET_KEY"] = "WOLFOFWALLSTREET"
    firebase = pyrebase.initialize_app(config)
    app.debug = True
    app.run()

