
from flask import Flask

app = Flask(__name__)

ncalls = 0


@app.route('/scale/testapp')
def scale_check():
    global ncalls
    ncalls += 1
    if ncalls % 5 == 0:
        return 'UP', 503

    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True)
