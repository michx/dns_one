from datetime import datetime
from pymongo import MongoClient
import struct, socket
import sys


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def route_lookup(database, ip):
    output = list()
    ip_check_num = ip2int(ip)
    query = {"Start IP Num": {"$lt": ip_check_num}, "End IP num": {"$gt": ip_check_num}}
    result = database.find(query)
    i = 0
    for items in result:
        output.append(
            {'id': i, 'subnet_len': items['End IP num'] - items['Start IP Num'], 'AS Number': items['AS Number'],
             'AS Description': items['AS Description'], 'AS Country': items['AS Country']})
        i += 1
    eq = [x['subnet_len'] for x in output]
    for item in output:
        if item['subnet_len'] == min(eq):
            return {'AS Number': item['AS Number'], 'AS Description': item['AS Description'],
                    'AS Country': item['AS Country']}


def find_a(domain,db):
    try:
        result=list(db.find({"Domain": domain,"Type": 1}))
    except:
        return 'none'
    return result

client = MongoClient('mongodb://192.168.183.167/dns')
db = client.dns
table_all=db.dns
table_aquery=db.aquery
table_asn=db.asn

print "Resolving Type 5:"
result=list(table_all.find())
for items in result:
    if items['Type']==5:
        a_solved=find_a(items['IP'],table_all)
        if a_solved<>'none':
            for resolutions in a_solved:
                sys.stdout.write('.')
                name = items['Domain']
                IP = resolutions['IP']
                now = items['Last_seen']
                data = {'Domain': name, 'IP': IP, 'Last_seen':now}
                result = table_aquery.find_one_and_update(
                    {'Domain': name, 'IP': IP},
                    {"$set": {'Last_seen': now}},
                   # {"$setoninsert": {'Domain': name, 'IP': IP,'AS Number':ASN,'AS Description':ASD}},
                    upsert=True,
                )
        else: print "None"
    if items['Type']==1:
            sys.stdout.write('.')
            name = items['Domain']
            IP = items['IP']
            now = items['Last_seen']
            data = {'Domain': name, 'IP': IP, 'Last_seen': now}
            result = table_aquery.find_one_and_update(
                  {'Domain': name, 'IP': IP},
                  {"$set": {'Last_seen': now}},
                   # {"$setoninsert": {'Domain': name, 'IP': IP,'AS Number':ASN,'AS Description':ASD}},
                    upsert=True,
              )

print "Adding AS Informations...."
for items in table_aquery.find().sort([("IP",1)]):
    ip=items['IP']
    if ip:
        ASN_query= route_lookup(table_asn,ip)
        ASN=ASN_query['AS Number']
        ASD = ASN_query['AS Description']
        res=table_aquery.update_one({'_id':items['_id']},{"$set": {'AS_Number':ASN,'AS Description':ASD}})