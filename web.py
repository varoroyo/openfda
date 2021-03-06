# Copyright [2017] [Álvaro Román]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# Author : Álvaro Román Royo (alvaro.varo98@gmail.com)


import http.server
import http.client
import json
import socketserver

class OpenFDAClient():

    OPENFDA_API_URL = "api.fda.gov"
    OPENFDA_API_EVENT = "/drug/event.json"

    def get_med(self,drug):
        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_EVENT + '?search=patient.drug.medicinalproduct:'+drug+'&limit=10')
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events

    def get_medicinalproduct(self,com_num):
        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_EVENT + '?search=companynumb:'+com_num+'&limit=10')
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events

    def get_event(self, limit):

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_EVENT + '?limit='+limit)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events

class OpenFDAHTML():

    def get_main_page(self):
        html = '''
        <html>
            <head>
                <title>OpenFDA app</title>
            </head>
            <body>
                <h1>OpenFDA Client</h1>
                <form method='get' action='listDrugs'>
                    <input type='submit' value='List Drugs'></input>
                    limit: <input type='text' name='limit'></input>

                </form>
                <form method='get' action='searchDrug'>
                    drug: <input type='text' name='drug'></input>
                    <input type='submit' value='Search Drug'></input>
                </form>
                <form method='get' action='listCompanies'>
                    <input type='submit' value='List Companies'></input>
                    limit: <input type='text' name='limit'></input>
                </form>
                <form method='get' action='searchCompany'>
                    company: <input type='text' name='company'></input>
                    <input type='submit' value='Search Company'></input>
                </form>
                <form method='get' action='listGender'>
                    <input type='submit' value='Get gender'></input>
                    limit: <input type= 'text' name='limit'></input>
            </body>
        </html>
                '''
        return html
    def drug_page(self,medicamentos):
        s=''
        for drug in medicamentos:
            s += "<li>"+drug+"</li>"
        html='''
        <html>
            <head></head>
                <body>
                    <ol>
                        %s
                    </ol>
                </body>
        </html>''' %(s)
        return html

    def error_html(self):
        html='''
        <html>
            <head>
                <title>file not found</title>
            </head>
                <body>
                <h1>Error 404</h1>
                File not found
                Error 404
                </body>
        </html>'''

        return html

class OpenFDAParser():

    def get_drug(self, events):
        medicamentos=[]
        for event in events['results']:
            medicamentos+=[event['patient']['drug'][0]['medicinalproduct']]

        return medicamentos

    def get_com_num(self, events):
        com_num=[]
        for event in events['results']:
            com_num+=[event['companynumb']]
        return com_num

    def get_gender(self, events):
        gender=[]
        for event in events['results']:
            gender+=[event['patient']['patientsex']]
        return gender

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        client = OpenFDAClient()
        HTMLcode = OpenFDAHTML()
        parser = OpenFDAParser()
        print (self.path)
        response = 200
        h1 = 'Content-type'
        h2 = 'text/html'
        if self.path == '/' :
            html = HTMLcode.get_main_page()


        elif 'listDrugs' in self.path:
            limit = self.path.split('=')[1]
            events = client.get_event(limit)
            medicamentos = parser.get_drug(events)
            html = HTMLcode.drug_page(medicamentos)


        elif 'searchDrug' in self.path:
            drug=self.path.split('=')[1]
            events = client.get_med(drug)
            com_num = parser.get_com_num(events)
            html = HTMLcode.drug_page(com_num)


        elif 'listCompanies' in self.path:
            limit = self.path.split('=')[1]
            events = client.get_event(limit)
            com_num = parser.get_com_num(events)
            html = HTMLcode.drug_page(com_num)


        elif 'searchCompany' in self.path:
            com_num = self.path.split('=')[1]
            print (com_num)
            events = client.get_medicinalproduct(com_num)
            medicinalproduct = parser.get_drug(events)
            html = HTMLcode.drug_page(medicinalproduct)


        elif 'listGender' in self.path:
            limit = self.path.split('=')[1]
            events = client.get_event(limit)
            gender = parser.get_gender(events)
            html = HTMLcode.drug_page(gender)


        elif 'secret' in self.path:
            response = 401
            h1 = 'WWW-Authenticate'
            h2 = 'Basic realm="My Realm"'

        elif 'redirect' in self.path:
            response = 302
            h1='location'
            h2='http://localhost:8000/'

        else:
            html=HTMLcode.error_html()
            response = 404
            h1 = 'Content-type'
            h2 = 'text/html'

        self.send_response(response)
        self.send_header(h1,h2)
        self.end_headers()

        if response == 200 or response == 404:
            self.wfile.write(bytes(html,'utf8'))



        return
