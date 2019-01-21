
from flask import Flask, render_template


# mongo.py

from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json, requests
app = Flask(__name__,static_url_path='/static')



@app.route('/')
def get_all_stars():
  response = requests.get('http://127.0.0.1:8111/dns/limit?limit=100')
  data = response.json()
  try:
    return render_template("index.html", title='DNS Prober', data=data['result'])
  except Exception, e:
    return str(e)

@app.route('/table',methods=['GET','POST'])
def get_all_table():
  try:
    domain=request.args.get('dom')
    dnstype=request.args.get('dom_type')
    response = requests.get('http://127.0.0.1:8111/dns/regex/'+domain+'?type='+dnstype)
  except:
    response = requests.get('http://127.0.0.1:8111/dns/limit?limit=100')
  data = response.json()
  try:
    return render_template("tables.html", title='DNS Prober', data=data['result'])
  except Exception, e:
    return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)