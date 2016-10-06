from flask import Flask ,jsonify
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('index.html',
                           title='Home',
                           user=user)
@app.route('/btc')
def bitcoin():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('btc.html',
                           title='Bitcoin',
                           user=user)
@app.route('/eth')
def eth():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('eth.html',
                           title='Bitcoin',
                           user=user)

@app.route('/ltc')
def ltc():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('ltc.html',
                           title='Bitcoin',
                           user=user)

@app.route('/xmr')
def xmr():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xmr.html',
                           title='Bitcoin',
                           user=user)

@app.route('/xrp')
def xrp():
    user = {'nickname': 'Wolf of Bitcoin'}
    return render_template('xrp.html',
                           title='Bitcoin',
                           user=user)

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()

