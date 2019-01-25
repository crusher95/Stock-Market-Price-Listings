import json
import os
from io import BytesIO

import requests, csv, zipfile
from datetime import timedelta, datetime

from DBConnectivity import Redis


class Download:
    def __init__(self, date):
        self.__date = datetime.strftime(date - timedelta(1), '%d%m%y')
        self.__base_url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{}_CSV.ZIP"
        self.file_name = "EQ{}.CSV"
        self.__current_path = os.path.abspath(os.path.dirname(__file__))
        self.__keys = {'SC_CODE': 'code', 'SC_NAME': 'name', 'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low',
                       'CLOSE': 'close'}

    def download(self):
        r = requests.get(self.__base_url.format(self.__date), timeout=3)
        if r.status_code == 200:
            zipfile.ZipFile(BytesIO(r.content)).extractall(path='tmp/')
            data = {'code': '', 'name': '', 'open': '', 'high': '', 'low': '', 'close': ''}
            redis = Redis()
            with open(self.__current_path+'/tmp/' + self.file_name.format(self.__date), 'r') as f:
                for row in self.__csv_to_dict(csv.reader(f)):
                    for key, value in self.__keys.items():
                        data[value] = row[key]
                    redis.redis_set(value=json.dumps(data), key=data['name'].strip())

    @staticmethod
    def __csv_to_dict(csv_reader):
        headers = next(csv_reader)
        result = []
        for row in csv_reader:
            result.append(dict(zip(headers, row)))
        return result