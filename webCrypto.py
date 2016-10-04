from flask import Flask ,jsonify
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    user = {'nickname': 'Miguel'}
    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()

