from pymongo import MongoClient
from datetime import datetime


class MongoDB:
    database = None

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
        coins = ["Bitcoin","Ethereum","Litecoin","Monero","Ripple"]
        if self.database:
            for coin in coins:
                title = self.create_document_title(coin)
                cursor = self.database.testDb.find_one({"title": title})
                print(coin)
                self.get_latest_tick(cursor["ticks"])

    def get_latest_tick(self,ticks):
        for tick in ticks:
            print(tick)

    # create the document title for mondoDB
    @staticmethod
    def create_document_title(title):
        datet = datetime.now()
        start_document_title = "%d_%d_" % (datet.year, datet.isocalendar()[1])
        return start_document_title + title
