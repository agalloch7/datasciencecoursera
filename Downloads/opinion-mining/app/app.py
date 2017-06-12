from flask import Flask, render_template, redirect, jsonify, request, url_for
from werkzeug import secure_filename
import os
from pymongo import MongoClient
import jinja2

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = ['csv']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# ROUTES:

@app.route('/')
def index():
	return redirect('/dashboard')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
	# get list of business names/ids from mongo
	businesses =[b for b in db.summaries.find()]
	return render_template('index.html.jinja', businesses = businesses)


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        print(file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('index.html.jinja')
    return jsonify({'error': 'Please upload only csv file!'})


@app.route('/processdate', methods = ['POST'])
def process():
	startdate = request.form['start']
	enddate = request.form['end']

	if startdate and enddate:
		return jsonify({startdate, enddate})

	return jsonify({'error': 'Missing either start date or end date'})


@app.route('/summaries/<b_id>')
def summary(b_id):
	summary = db.summaries.find_one({'business_id': b_id})
	return render_template('summary.html.jinja', summary=summary)
	

@app.template_filter()
def less_than_ten(number):
	return number <= 10

if __name__ == "__main__":

	# Setup db connection
	client = MongoClient()
	db = client.scoretestJune10
	print "Connected to Mongo database"

	app.jinja_env.filters['less_than_ten'] = less_than_ten

	app.run(host='127.0.0.1', port=54770, debug=True)
