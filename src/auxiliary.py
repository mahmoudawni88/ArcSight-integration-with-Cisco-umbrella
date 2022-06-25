import cisco_umbrella
import csv
import os
import sys
from csv import reader
import datetime
import pytz
import time

class ciscoUmbrellaAuxilary():
    def __init__(self):
        self.cons = cisco_umbrella.ciscoUmbrellaConstant(2438412)
        self.file_csv = self.cons.filename + '.csv'
        self.file_cef = self.cons.filename + '.cef'


    def getAuth(self):
        if os.environ['ciscoUmbrellaUserName'] and os.environ['ciscoUmbrellaPassword']:
            username = os.getenv('ciscoUmbrellaUserName')
            password = os.getenv('ciscoUmbrellaPassword')
            return username, password
        else:
            print('[-] Please add ciscoUmbrellaUserName & ciscoUmbrellaPassword in os enviroment variable')
            sys.exit(-1)

    def saveDataCSV(self,data):
        with open(self.file_csv,'a') as file:
            file.writelines(data.text)

    def convertCEF(self):
        cef_result=[]
        with open(self.file_csv, "r") as read_obj:
            csv_reader = reader(read_obj)
            header = next(csv_reader)
            for row in csv_reader:
                dateTime_str = row[1] + " " + row[2]
                dateTime = datetime.datetime.strptime(dateTime_str, '%Y-%m-%d %H:%M:%S')
                DateTimeFormat_aware = dateTime.replace(tzinfo=pytz.UTC)  # a ware TimeZone
                DateTime_Riyadh = DateTimeFormat_aware.astimezone(pytz.timezone("Asia/Riyadh"))  # Riyadh TimeZone
                cef_result.append(
                    'CEF:0|CISCO|Umbrella|1|' + str(202619694) + '|' + row[9] + '|' + '3| ' + 'dvchost=' + 'umbrella.com'
                    + ' dhost=' + row[10]
                    + ' src=' + row[7]
                    + ' sourceTranslatedAddress=' + row[8]
                    + ' cs1Label=' + 'Categories'
                    + ' cs1=' + row[13]
                    + ' cs2Label=' + 'Tags'
                    + ' cs2=' + str(None)
                    + ' cs3Label=' + 'originType'
                    + ' cs3=' + row[4]
                    + ' flexString1Label=' + 'originLabel'
                    + ' flexString1=' + str(row[3])
                    + ' act=' + row[9]
                    + ' end=' + str(DateTime_Riyadh)
                )
        with open(self.file_cef,'a') as cefFile:
            for line in cef_result:
                cefFile.writelines(line + '\n')

    def delCSV(self):
        if os.path.isfile(self.file_csv):
            os.remove(self.file_csv)

    def logFile(self,line):
        with open('ciscoUmbrellaAPI.log','a') as logfile:
            logfile.write(str(datetime.datetime.now()) + str( line))