

class user():
    @classmethod
    def user_info(cls,firebase,request):
        data = {}
        if "token" in request.headers and "uid" in request.headers:
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
                data = db.child("users/" + uid).child("data").get(token=token).val()
                print(data)
        else:
            print("no header set")
        return data

    @classmethod
    def get_profile(cls,mongo,firebase,request):
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

                return data
        else:
            data = tempdata
        return data