import pyrebase


class trade_currency():

    @classmethod
    def buy_currency(cls,firebase,request):
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
            return True
        return False

    @classmethod
    def sell_currency(cls, firebase, request):
        db = firebase.database()
        token = request.headers["token"]
        uid = request.headers["uid"]
        data = request.json
        budget = db.child("users/" + uid).child("data").get(token=token).val()['budget']

        owned_currency = db.child("users/" + uid).child("data").get(token=token).val()['currencies']

        newbudget = float(budget) + float(data['price'])
        owned_currency[data["currency"]] -= float(data["amount"])
        save = {
            "budget": newbudget,
            "currency": owned_currency,
        }
        db.child("users/" + uid).child("data").update(save, token=token)
