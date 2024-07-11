from flask import Flask, render_template, redirect, url_for, request
import socket

app = Flask(__name__)

class Flask_server:

    def __init__(self):
        
        web_host = "192.168.122.56"
        web_page = "http://192.168.122.56:8080/"
        app.run(host=web_host, port=8080, debug=True)
    



    @app.route('/', methods=['GET', 'POST'])
    def main_page(self):
        return render_template('start.html')

    @app.route('/start', methods=['GET', 'POST'])
    def start(self):
        if request.method == 'POST':
            self.app.start = True
            return render_template('main.html')
        return redirect(url_for('main_page'))

    @app.route('/test1', methods=['GET', 'POST'])
    def test1(self):
        if request.method == 'POST':
            self.app.test2 = 1  
            return render_template('main.html')
        return redirect(url_for('main_page'))
        
    @app.route('/test2', methods=['GET', 'POST'])
    def test2(self):
        if request.method == 'POST':
            self.app.test2 = 2
            return render_template('main.html')
        return redirect(url_for('main_page'))