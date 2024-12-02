from flask import Flask, render_template, url_for, redirect, send_from_directory,request
import os
from myfunctions import *

app = Flask(__name__)

@app.route("/")
def home():

	return render_template("index.html")
@app.route("/lyrics.txt")
def lyrics():

	return render_template("index.html")

@app.route("/process")
def process():
	code()
	invokePython()
	return render_template("process.html")
def code():
    print("It worked!")

def invokePython():
	return "Hello"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/ytprocess")
def ytprocessmain():
	link = request.args.get('link')
	ytprocess(link)
	return render_template("acknowledge.html")
	

@app.route("/acknowledge")
def acknowledge():
	return render_template("acknowledge.html")

if __name__ == "__main__":
	app.run(debug=True, port =9094)