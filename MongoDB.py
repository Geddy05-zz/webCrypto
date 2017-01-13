from pymongo import MongoClient
from datetime import datetime
import time

'''
This class is used for al the mongoDB interaction
'''


class MongoDB:
    database = None
    coins = ["Bitcoin", "Ethereum", "Litecoin", "Monero", "Ripple"]

    def __init__(self):
        client = MongoClient('145.24.222.182:8001', connect=False)
        self.database = client.test

    # get a document by title
    def get_document(self, title):
        cursor = None
        if self.database:
            cursor = self.database.testDb.find_one({"title": title})

        return cursor

    def get_current_values(self,coin):
        title = self.create_document_title(coin)
        cursor = self.database.testDb.find_one({"title": title})
        latest_tick = self.get_latest_tick(cursor["ticks"])
        return latest_tick


    # return the 5 currencies we shown on index page
    def get_current_value_big_five(self):
        latest_currency = {}
        if self.database:
            for coin in self.coins:
                title = self.create_document_title(coin)
                cursor = self.database.testDb.find_one({"title": title})

                tick_day_ago = self.get_tick_number_hours_ago(cursor["ticks"])
                latest_tick = float(self.get_latest_tick(cursor["ticks"])["price_usd"])
                print(latest_tick)
                print (tick_day_ago)
                currency_data = {"current_value": latest_tick,
                                 "change": round(float(100 - (tick_day_ago / latest_tick  * 100)), 2)
                                 }
                latest_currency[coin] = currency_data

        return latest_currency

    def get_tick_values_of_last_12_hour(self, coin):
        data_with_time = []
        if self.database:
            title = self.create_document_title(coin)
            data = None
            cursor = self.database.testDb.find_one({"title":title})["ticks"]
            if len(cursor) > 72:
                data = cursor[-72:]
            else:
                data = cursor

            for item in data:
                unix_time = int(item["last_updated"])
                date = datetime.fromtimestamp(
                    unix_time
                ).strftime('%d-%m %H:%M')
                item["last_updated"] = date
                data_with_time.append(item)
        return data_with_time

    @staticmethod
    def get_tick_number_hours_ago(ticks):
        import datetime

        date_now = datetime.datetime.now()
        print(date_now)
        date_min = datetime.timedelta(1)
        print(date_min)
        yesterday = date_now - date_min
        print (yesterday)
        unix_time = time.mktime(yesterday.timetuple())
        # unix_time = float(yesterday.strftime("%S"))
        different = None
        tick_day_ago = None
        for tick in ticks:
            late = float(tick["last_updated"])
            if different:
                if abs(late - unix_time) < different:
                    different = abs(late - unix_time )
                    print(different)
                    tick_day_ago = tick
            else:
                different = float(tick["last_updated"])
                tick_day_ago = tick
        return float(tick_day_ago["price_usd"])

    @staticmethod
    def get_latest_tick(ticks):
        latest_tick = None
        for tick in ticks:
            if latest_tick:
                if latest_tick["last_updated"] < tick["last_updated"]:
                    latest_tick = tick
            else:
                latest_tick = tick
        return latest_tick

    # create the document title for mondoDB
    @staticmethod
    def create_document_title(title):
        date_now = datetime.now()
        start_document_title = "%d_%d_" % (date_now.year, date_now.isocalendar()[1])
        return start_document_title + title
