from flask import Flask, render_template, jsonify
from bluetooth_scan import scan_devices

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('partials/dashboard.html')

@app.route('/live')
def live():
    devices = scan_devices()
    return jsonify(devices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
