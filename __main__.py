import cisco_umbrella
import argparse
import requests
import time , datetime
import sys

def create_parser():
    parser = argparse.ArgumentParser(prog="ciscoUmbrella")
    parser.add_argument('-o','--org_number',dest='org_number',required=True,help='cisoc umbrella\'s organisation number')
    return parser

def main(options):
    #define variables
    umbrellaClient = cisco_umbrella.ciscoUmbrellaAPI(options.org_number)
    cons = cisco_umbrella.ciscoUmbrellaConstant(options.org_number)
    aux = cisco_umbrella.ciscoUmbrellaAuxilary()
    username, password = aux.getAuth()

    #authentication
    formtoken = umbrellaClient.getFormtoken(url=cons.urls.get('login_url'),header=cons.header)
    umbrellaClient.login(url=cons.urls.get('login_url'),header=cons.header,token=formtoken,username=username,password=password)
    api_session, csrf_token = umbrellaClient.orgInfo(url=cons.urls.get('org_info'),header=cons.org_info)
    bearer_token = umbrellaClient.getBearerToken(url=cons.urls.get('bearer_token'),header=cons.bearer_token,api_session=api_session,org_number=options.org_number)
    aux.logFile(f'[+] API token is created sucessfully: {bearer_token} \n')

    #Start search
    aux.logFile('[+] starting searching \n')
    start,end,part_uri = umbrellaClient.activitySearch(url=cons.urls.get('activity_search'),header=cons.activity_search,bearer_token=bearer_token)
    token = umbrellaClient.getToken(url=cons.urls.get('token'),header=cons.token,csrf_token=csrf_token)

    #Create CSV in cisco Umbrella itself
    aux.logFile('[+] Asking cisco umbrella to export the data in CSV file \n')
    report_id=umbrellaClient.createCSV(url=cons.urls.get('create_csv'),header=cons.create_csv,new_token=token,start=start,end=end,part_uri=part_uri)


    #check the search is finished & the report is ready for downloading
    aux.logFile('[+] waiting till the search is ended \n')
    flag, count=True, 0
    while flag:
        response = umbrellaClient.checkURL(url=cons.urls.get('create_csv'),header=cons.create_csv)
        aux.logFile(f'[+] is search ended: {response} \n')
        if isinstance(response,list):
            for data in response:
                if data["id"] == report_id and data["downloadUrl"] != '':
                    flag = False
            count+=1
            if count == 3:  # Generate a new token
                token = umbrellaClient.getToken(url=cons.urls.get('token'), header=cons.token,csrf_token=csrf_token)
                count = 0
            time.sleep(5)
        else:
            aux.logFile(f'[-] error during the creating report: {response["error"]} \n')
            aux.logFile('[+]########################################################################## \n')
            sys.exit(-1)

    #Generate a new Token
    aux.logFile('[+] Search is ended. Creating a new token to get the repurt ID and then report URL \n')
    token = umbrellaClient.getToken(url=cons.urls.get('token'), header=cons.token, csrf_token=csrf_token)

    # #Get Report URL
    aux.logFile('[+] Getting report url \n')
    reportURL=umbrellaClient.getReportURL(header=cons.create_csv,org_number=options.org_number,report_id=report_id,token=token)

    # #Get report data
    aux.logFile('[+] Getting report data \n')
    reportData = umbrellaClient.getReportData(url=reportURL,header=cons.get_data)

    #Save the data in CSV file
    aux.logFile('[+] save the report data in csv file to convert it to CEF file \n')
    aux.saveDataCSV(data=reportData)
    #Generate a new token again
    aux.logFile('[+] Generate a new token again for deleting the report from cisco umbrella \n')
    token = umbrellaClient.getToken(url=cons.urls.get('token'), header=cons.token, csrf_token=csrf_token)
    #delete the report from cisco umbrella
    aux.logFile('[+] Deleting the report from cisco umbrella \n')
    umbrellaClient.delReport(header=cons.create_csv,token=token,report_id=report_id,org_numb=options.org_number)

    #convert to cef and save in file
    aux.logFile('[+] converting data to CEF file and save it. \n')
    aux.convertCEF()

    #delete csv file
    aux.logFile('[+] delete CSV file \n')
    aux.delCSV()
    aux.logFile('[+]########################################################################## \n')

def get_parser(parser):
    return parser.parse_args()

if __name__ == '__main__':
    main(get_parser(create_parser()))
