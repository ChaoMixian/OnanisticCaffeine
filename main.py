from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Test'

@app.route('/api', methods=['GET', 'POST'])
def api():
    if request.method == 'POST':
        return 'nothing'
    else:
        return 'nothing'

if (__name__=='__main__'):
    app.run(host = '0.0.0.0', port = 4345, debug=True)