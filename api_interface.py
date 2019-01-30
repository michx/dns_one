
import flask


# mongo.py

from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import socket, struct

from pymongo import MongoClient

def ip2int(addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
        return socket.inet_ntoa(struct.pack("!I", addr))

def route_lookup(database,ip):
  output=list()
  ip_check_num = ip2int(ip)
  query = {"Start IP Num": {"$lt": ip_check_num}, "End IP num": {"$gt": ip_check_num}}
  result = database.find(query)
  i = 0
  for items in result:
    output.append({'id': i, 'subnet_len': items['End IP num'] - items['Start IP Num'], 'AS Number': items['AS Number'],
                   'AS Description': items['AS Description'],'AS Country': items['AS Country']})
    i += 1
  eq = [x['subnet_len'] for x in output]
  for item in output:
    if item['subnet_len'] == min(eq):
      return {'AS Number': item['AS Number'], 'AS Description':item['AS Description'],'AS Country':item['AS Country']}


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'dns'
app.config['MONGO_URI'] = 'mongodb://192.168.183.167:27017/dns'

mongo = PyMongo(app)

@app.route('/count_all', methods=['GET'])
def get_count():
  items = mongo.db.dns
  all=items.find()
  return jsonify({'result' : all.count()})

@app.route('/count_all_type', methods=['GET'])
def get_count_type():
  items = mongo.db.dns
  result=items.aggregate([
		{"$group" : {"_id":"$Type", "count":{"$sum":1}}}
	])
  result_list=list(result)
  return jsonify({'result' : result_list})

@app.route('/count_hit', methods=['GET'])
def get_count_hit():
  items = mongo.db.dns
  query=[{ '$group': { '_id':  'total' , 'Total hit' : { '$sum': '$occurrence' }, }  }  ]
  hit=list(items.aggregate(query))
  all=items.find()
  return jsonify({'result' : hit[0]['Total hit']})

@app.route('/total_size', methods=['GET'])
def get_total_size():
  size=mongo.db.command("collstats","dns")['storageSize']
  return jsonify({'result' :size})

@app.route('/mean_size', methods=['GET'])
def get_mean_size():
  size = mongo.db.command("collstats", "dns")['avgObjSize']
  return jsonify({'result': size})

@app.route('/dns', methods=['GET'])
def get_all_stars():
  items = mongo.db.dns
  output = []
  for s in items.find().sort([("occurrence",-1)]):
    output.append({'Domain' : s['Domain'], 'Resolution' : s['IP'], 'Type' : s['Type'], 'Count' : s['occurrence']})
  return jsonify({'result' : output})

@app.route('/aquery', methods=['GET'])
def get_all_aquery():
  items = mongo.db.aquery
  output = []
  for s in items.find():
    output.append({'Domain' : s['Domain'], 'Resolution' : s['IP'],'AS Description': s['AS Description'],'AS Number': s['AS_Number']})
  return jsonify({'result' : output})

@app.route('/dns/limit', methods=['GET'])
def get_all_limit():
  try:
    limit=int(request.args.get('limit'))
  except:
      limit=10
  items = mongo.db.dns
  output = []
  for s in items.find().sort([("occurrence",-1)]).limit(limit):
    output.append({'Domain' : s['Domain'], 'Resolution' : s['IP'], 'Type' : s['Type'], 'Count' : s['occurrence']})
  return jsonify({'result' : output})


@app.route('/dns/<name>', methods=['GET'])
def get_one_star(name):
  items = mongo.db.dns
  s = items.find_one({'Domain' : name}).sort([("occurrence",-1)])
  if s:
    output = {'Domain' : s['Domain'], 'Resolution' : s['IP'], 'Type' : s['Type'], 'Count' : s['occurrence']}
  else:
    output = "No such Domain"
  return jsonify({'result' : output})


@app.route('/ipresolve/<ip>', methods=['GET'])
def resolve_ip(ip):
  items = mongo.db.asn
  s = route_lookup(items,ip)
  if s:
    return jsonify({'AS Number':s['AS Number'],'AS Description':s['AS Description'],'AS Country':s['AS Country']})
  else:
    return jsonify({'result' : ip+' '+str(ip_check_num)+' None'})

@app.route('/dns/regex/<name>', methods=['GET'])
def get_regex_star(name):
  tpe = int(request.args.get('type'))
  items = mongo.db.dns
  s = items.find({'Domain' : {'$regex':name,'$options':'i'},'Type':tpe}).sort([("occurrence",-1)])
  if s:
    output=list()
    for item in s:
      output.append({'Domain' : item['Domain'], 'Resolution' : item['IP'], 'Type' : item['Type'], 'Count' : item['occurrence']})
  else:
    output = "No such Domain"
  return jsonify({'result' : output})

@app.route('/aquery/regex/', methods=['GET'])
def get_regex_asn():
  domain = request.args.get('dom')
  asn=request.args.get('asn')
  items = mongo.db.aquery
  if domain and asn:
    s = items.find({'Domain' : {'$regex':domain,'$options':'i'},'AS Description' : {'$regex':asn,'$options':'i'}}).sort([("occurrence",-1)])
  elif domain:
    s = items.find({'Domain' : {'$regex':domain,'$options':'i'}}).sort([("occurrence",-1)])
  elif asn:
    s = items.find({'AS Description' : {'$regex':asn,'$options':'i'}}).sort([("occurrence",-1)])
  if s:
    output=list()
    for item in s:
      output.append({'Domain' : item['Domain'],'Resolution':item['IP'],'AS Description' : item['AS Description'],'AS Number' : item['AS_Number']})
  else:
    output = "No such Domain"
  return jsonify({'result' : output})

@app.route('/dns/regex-limit/<name>', methods=['GET'])
def get_regex_limit(name):
  tpe=int(request.args.get('type'))
  items = mongo.db.dns
  s = items.find({'Domain' : {'$regex':name,'$options':'i'},'Type':tpe}).sort([("occurrence",-1)]).limit(10)
  if s:
    output=list()
    for item in s:
      output.append({'Domain' : item['Domain'], 'Resolution' : item['IP'], 'Type' : item['Type'], 'Count' : item['occurrence']})
  else:
    output = "No such Domain"
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111, debug=True)