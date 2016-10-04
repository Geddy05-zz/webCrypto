from flask import Flask ,jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return 'Geddy is the Hacker'


@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()

