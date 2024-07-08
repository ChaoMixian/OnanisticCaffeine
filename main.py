from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/api', methods=['GET', 'POST'])
def api():
    if request.method == 'POST':
        return 'nothing'
    else:
        return 'nothing'

if (__name__=='__main__'):
    app.run(host = '0.0.0.0', port = 4345, debug=True)