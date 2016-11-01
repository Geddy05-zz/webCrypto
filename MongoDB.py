from pymongo import MongoClient
from datetime import datetime

'''
This class is used for al the mongoDB interaction
'''
class MongoDB:
    database = None
    coins = ["Bitcoin", "Ethereum", "Litecoin", "Monero", "Ripple"]

    def __init__(self):
        client = MongoClient('145.24.222.182')
        self.database = client.test

    def get_Document(self,title):
        # get a document by title
        cursor = None
        if self.database:
            cursor = self.database.testDb.find_one({"title": title})

        return cursor

    # return the 5 currencies we shown on index page
    def get_current_value_big_five(self):
        latestCurrency = {}
        if self.database:
            for coin in self.coins:
                title = self.create_document_title(coin)
                cursor = self.database.testDb.find_one({"title": title})
                latestCurrency[coin] = self.get_latest_tick(cursor["ticks"])
        return latestCurrency

    def get_change_of_big_five(self):
        latestCurrency = {}
        if self.database:
            for coin in self.coins:
                title = self.create_document_title(coin)
                cursor = self.database.testDb.find_one({"title": title})
                tickDayAgo = self.get_tick_Number_hours_ago()
                latestTick = self.get_latest_tick(cursor["ticks"])
                latestCurrency[coin] = latestTick / tickDayAgo * 100
        latestCurrency

    @staticmethod
    def get_tick_Number_hours_ago(ticks):
        yesterday = datetime.date.today() - datetime.timedelta(1)
        unix_time = yesterday.strftime("%s")
        different = None
        tickDayAgo = None
        for tick in ticks:
            late = tick["last_updated"]
            if different:
                if abs(unix_time - late) < different:
                    different = abs(unix_time-late)
                    tickDayAgo = tick
            else:
                different = tick["last_updated"]
                tickDayAgo = tick
        return tickDayAgo


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
        datet = datetime.now()
        start_document_title = "%d_%d_" % (datet.year, datet.isocalendar()[1])
        return start_document_title + title
