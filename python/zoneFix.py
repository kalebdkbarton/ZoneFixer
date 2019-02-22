import sys
from flask import Flask
from flask_restful import Api, Resource, reqparse
import json

app = Flask(__name__)
api = Api(app)

class Record(Resource): #allow input of records line by line
    def post(self,record):
        parser = reqparse.RequestParser()
        parser.add_argument("line")
        record.append(record)
        f = open('fixMe.txt','a')
        f.write(record) #write records to file
        f.close()
        return record, 201

class Origin(Resource): #allow input of origin
    def post(self,origin):
        parser = reqparse.RequestParser()
        parser.add_argument("origin")
        origin.append(origin)
        return origin, 201

api.add_resource(Record)
api.add_resource(Origin)
app.run(debug=True)
@app.route("/zonefix")
def zoneFix():
    origin=json.loads(Origin) #grab the origin from the API input
    zone="fixMe.txt" #grab the file
    originDot = (origin+".")
    dotOrigindot = ("."+origin+".") #all origin variations found
    if "ORIGIN" not in zone:
        f = open('zone.json','w')
        f.write("$ORIGIN "+origin) #add the origin
        f.close()
    fh = open(zone)
    for line in fh: #run file line by line
        if ";" in line: #remove comments
            continue
        if "ORIGIN" not in line: #remove the origin domain from the FQDN
            removeDomain1 = line.replace(dotOrigindot, "")
            removeDomain2 = removeDomain1.replace(originDot, "@")
            removeDomain3 = removeDomain2.replace(origin, "@")
        else:
            continue #don't output if $ORIGIN is in the line
        if "SOA" in line:
            continue #get rid of the SOA
        elif "CNAME" in line:  #all of these grab the record type or lack thereof
            recordType="CNAME"
        elif "A" in line:
            recordType="A"
        elif "TXT" in line:
            recordType="TXT"
        elif "SPF" in line:
            recordType="SPF"
        elif "MX" in line:
            recordType="MX"
        elif "CAA" in line:
            recordType="CAA"
        elif "PTR" in line:
            recordType="PTR"
        elif "SRV" in line:
            recordType="SRV"
        elif "NS" in line:
            recordType="NS"
        else:
            recordType="none"
        if (recordType != "none"):
            if "IN" not in line:
                withIn = ("IN\t"+recordType) 
                output = removeDomain3.replace(recordType, withIn) #add the IN
            else:
                output = removeDomain3 #IN is already there
        else:
            continue
        if (recordType == "NS"):
            if "@" in output: #get rid of the root NS Records
                continue
        if (recordType == "CNAME"): #no root CNAME Records
            if "@" in output:
                f = open('zone.json','w')
                f.write("\033[1;31;40m ERROR: CANNOT HAVE CNAME FOR THE ROOT DOMAIN  \n")
                f.close()
                break
        if (recordType == "SRV"): #no root SRV Records
            if "@" in output:
                f = open('zone.json','w')
                f.write("\033[1;31;40m ERROR: CANNOT HAVE SRV FOR THE ROOT DOMAIN  \n")
                f.close()
                break
        if line.strip(): #no blank lines
            f = open('zone.json','a')
            f.write(output) #write output to file
            f.close()
    fh.close()

if __name__ == "__main__":
        app.run("142.93.86.122",5010)