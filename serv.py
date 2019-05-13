from flask import Flask
import test
app = Flask(__name__)

c1 = test.MPL3115A2_Chip()
c2 = test.HTU21D_Chip()


@app.route('/')
def hello():
    return "temp: %s" %c1.read_temp(type='f')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
