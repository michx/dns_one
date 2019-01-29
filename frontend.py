
from flask import Flask, render_template
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json, requests

dns_types=dict()
dns_types['1']='A'
dns_types['5']='CNAME'
dns_types['15']='MX'
dns_types['28']='AAAA'
dns_types['16']='TXT'

app = Flask(__name__,static_url_path='/static')



@app.route('/')
def get_all_stars():
  response = requests.get('http://127.0.0.1:8111/dns/limit?limit=100')
  count_r = requests.get('http://127.0.0.1:8111/count_all')
  hit_r = requests.get('http://127.0.0.1:8111/count_hit')
  data = response.json()
  count=count_r.json()
  hit=hit_r.json()
  totsize=int(requests.get('http://127.0.0.1:8111/total_size').json()['result'])/1000
  meansize=requests.get('http://127.0.0.1:8111/mean_size').json()
  try:
    return render_template("index.html", title='DNS Prober', data=data['result'],count=count,hit=hit,totsize=int(totsize),meansize=meansize)
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

@app.route('/ott', methods=['GET', 'POST'])
def get_ott_table():
    try:
      domain = request.args.get('dom')
      dnstype = request.args.get('asn')
      response = requests.get('http://127.0.0.1:8111/aquery/regex/?dom=' + domain + '&asn=' + dnstype)
    except:
      response = requests.get('http://127.0.0.1:8111/aquery')
    data = response.json()
    try:
      return render_template("ott.html", title='DNS Prober', data=data['result'])
    except Exception, e:
      return str(e)

@app.route('/charts', methods=['GET', 'POST'])
def get_charts():
    pie=list()
    response = requests.get('http://127.0.0.1:8111/count_all_type')
    data = response.json()
    for item in data['result']:
      pie.append({'type':dns_types[str(item['_id'])],'value':item['count']})
    try:
      return render_template("charts.html", title='DNS Prober', pie=pie)
    except Exception, e:
      return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)