import subprocess
import csv
import os
import sys
from datetime import datetime


class analyzed():

    @classmethod
    def twitter(cls,coin ,debug = False):
        path = os.path.dirname(sys.modules['__main__'].__file__)

        if debug:
            x = subprocess.check_output("Rscript --vanilla " + path + "/twitterCombi" + coin + ".R",
                                        stderr=subprocess.STDOUT, shell=True)

        else:
            try:
                output = subprocess.check_output("echo h7Dx34|sudo -S Rscript --vanilla /home/webCrypto/twitterCombi"+coin+".R",stderr=subprocess.STDOUT,shell = True)
                returncode = 0
            except subprocess.CalledProcessError as e:
                output = e.output
                returncode = e.returncode

        with open(path+'/twitterScore.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            scores = []
            for row in reader:
                score = {}

                date = datetime.fromtimestamp(
                    float(row["tStamp"])
                ).strftime('%d-%m %H:%M')

                score["date"] = date
                score["score"] = row["score"]
                score["sentiment"] = row["scoreSentiment"]
                scores.append(score)
        return scores

    @classmethod
    def sentiment(cls,coin, debug = False):
        scores = []
        path = os.path.dirname(sys.modules['__main__'].__file__)
        print(coin)
        if debug:
            x = subprocess.check_output("Rscript --vanilla " + path + "/EventScore" + coin + ".R",
                                        stderr=subprocess.STDOUT, shell=True)
        else:
            output = subprocess.check_output("echo h7Dx34|sudo -S Rscript --vanilla EventScore"+coin+".R",
                                             stderr=subprocess.STDOUT,shell = True)
            returncode = 0


        with open('sentimentEventScore.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                count += 1
                score = {}
                if count > 1:
                    score['event'] = row['event']
                    score['percentage'] = row['percentage']
                    score['pos'] = row['pos.neg']
                    scores.append(score)

        return scores
