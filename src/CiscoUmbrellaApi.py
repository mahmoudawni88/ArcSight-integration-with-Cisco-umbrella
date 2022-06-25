import cisco_umbrella
import sys
import requests
from bs4 import BeautifulSoup
import os
import urllib3
import re
import time
import datetime
import json


class ciscoUmbrellaAPI(cisco_umbrella.ciscoUmbrellaConstant):
    def __init__(self,org_number):
        super().__init__(org_number)
        self.session=requests.Session()
        self.aux = cisco_umbrella.ciscoUmbrellaAuxilary()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #get hidden_keys  ==> expected output is getting the hidden value: formtoken
    def getFormtoken(self,url,header):
        try:
            response = self.session.get(url,headers=header,verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text,'html.parser')
                inputs = soup.findAll('input',attrs={'type':'hidden'} )
                formtoken = [x['value'] for x in inputs if x['name'] == 'formtoken']
            return formtoken[0]
        except Exception as err:
            self.aux.logFile('[-] not able to get formtoken :( \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    #login function ==> expected ouptut is a new login cookie
    def login(self,url,header,token,username,password):
        data = f'username={username}&password={password}&return_to=https%3A%2F%2Flogin.umbrella.com%2F&formtoken={token}&loginToken='
        try:
            response = self.session.post(url=url,headers=header,data=data,verify=False)
        except Exception as err:
            self.aux.logFile('[-] not able to login :( \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    #Expected is getting api-session & csrf_token
    def orgInfo(self,url,header):
        try:
            response = self.session.get(url=url,headers=header)
            api = re.search('\"api-session\":\"(.*)\"\,\"fetch_default_limit.*',response.text)
            csrf = re.search('\"csrf_token\":\"(.*)\"\,\"samlAppUrl.*',response.text)
            if api and csrf:
                api_session = api.group(1)
                csrf_token = csrf.group(1)
            else:
                self.aux.logFile('[-] Not able to extrace correct API_session & CSRF_Token \n')
                self.aux.logFile('[+]########################################################################## \n')
                sys.exit(-1)
            return api_session, csrf_token
        except Exception as err:
            self.aux.logFile('[-] there is issue in orgInfo function :(')
            sys.exit(-1)

    #Expecter to reterive bearer token
    def getBearerToken(self,url,header,api_session,org_number):
        try:
            data = f'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion={api_session}&scope=org%2F{org_number}'
            respone = self.session.post(url=url,data=data,headers=header,verify=False)
            respone_json=respone.json()
            bearer_token = respone_json.get('access_token')
            return bearer_token
        except Exception as err:
            self.aux.logFile('[-] not able to get bearer token :(')
            sys.exit(-1)

    #run search
    def activitySearch(self,url,header,bearer_token):
        time_tuple1 = time.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
        time_from = int(time.mktime(time_tuple1)) - 900
        time_to = int(time.mktime(time_tuple1))
        time_fromStr = str(time_from) + '000'
        time_toStr = str(time_to) + '000'
        header["Authorization"] = f'Bearer {bearer_token}'
        params = (
            ('verdict', 'blocked'),
            ('filternoisydomains', 'true'),
            ('from', '{0}'.format(time_fromStr)),
            ('to', '{0}'.format(time_toStr)),
            ('limit', '100'),
            ('order', 'desc'),
            ('offset', '0'),
        )
        try:
            response = self.session.get(url=url, headers=header, params=params, verify=False)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                redirect = response_dict["data"]["redirect"]
                start = re.search('.*from=(.*)&to.*', redirect)
                end = re.search('.*to=(.*)&limit.*', redirect)
                part_url = re.search('.*(verdict.*)&limit.*', redirect)
                if start and end and part_url:
                    start = start.group(1)
                    end = end.group(1)
                    part_url = part_url.group(1)
                    return start[0:10], end[0:10], part_url
                else:
                    self.aux.logFile('[-] Not able to get start, end & part_url form activity_search function')
                    sys.exit(-1)
            else:
                self.aux.logFile('[-] not able to do a seach! \n')
                self.aux.logFile('[+]########################################################################## \n')
                sys.exit(-1)
        except Exception as err:
            self.aux.logFile('[-] not able to search. may be the seach takes long time :( \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    #renew token
    def getToken(self,url,header,csrf_token):
        header['x-csrf-token'] = csrf_token
        try:
            respnse = self.session.get(url=url,headers=header,verify=False)
            response_json = respnse.json()
            return response_json['token']
        except Exception as err:
            self.aux.logFile('[-] not able to generate a new token \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    #create csv
    def createCSV(self,url,header,new_token,start,end,part_uri):
        header["Authorization"] = f'Bearer {new_token}'
        data = {'emailWhenReady': False,
            'filters':
                {
                    'action': ['blocked'],
                    'end': end,
                    'includeNoisyDomains': False,
                    'mspId': 0,
                    'noBucketing': True,
                    'order': 'desc',
                    'selectedDateRangeIdx': 4,
                    'start': start,
                    'timezone': 'Asia/Riyadh',
                    'trafficType': 'all'},
            'limit': '1000000',
            'queryString': part_uri + '&order=desc&timezone=UTC',
            'reportType': 'Activity Search',
            'slug': 'v2:activity',
            'title': 'test-api123'}
        data_str = json.dumps(data)
        params = (('outputFormat', 'jsonHttpStatusOverride'),)
        response = self.session.post(url=url, headers=header, params=params, data=data_str, verify=False)
        response_json = response.json()
        return response_json['data']['id']

    def checkURL(self,url,header):
        params = (('outputFormat', 'jsonHttpStatusOverride'),)
        try:
            response = self.session.get(url=url,headers=header,verify=False)
            return response.json()
        except Exception as err:
            self.aux.logFile('[-] there was issue when I\'m waiitng the search is ended \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    def getReportURL(self,header,org_number,report_id,token):
        get_report_url = f"https://api.opendns.com/v3/organizations/{org_number}/exportedreports/{report_id}"
        header["Authorization"] = f'Bearer {token}'
        params = (('outputFormat', 'jsonHttpStatusOverride'),)
        response = self.session.get(url=get_report_url, headers=header,params=params,verify=False)
        response_dict = json.loads(response.text)
        return response_dict["data"]["url"]

    def getReportData(self,url,header):
        try:
            response = self.session.get(url=url,headers=header,verify=False)
            return response
        except Exception as err:
            self.aux.logFile('[-] unable to get reportData :( \n')
            self.aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    def delReport(self,header,token,report_id,org_numb):
        header["Authorization"] = f'Bearer {token}'
        params = (('outputFormat', 'jsonHttpStatusOverride'),)
        delete_url = f"https://api.opendns.com/v3/organizations/{org_numb}/exportedreportrequests/{report_id}"
        response = self.session.delete(url=delete_url, headers=header, params=params,verify=False)
        if response.status_code == 200:
            self.aux.logFile('[+] The report is deleted permentaly from cisco umbrella')



