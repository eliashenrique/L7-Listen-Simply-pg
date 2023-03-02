# !/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, date
import time


class Spread:

    def __init__(self, datas, psql):
        self.psql = psql
        self.datas = datas
        self.dict_logs = {}
        self.millis = int(round(time.time() * 1000))
        self.info_router = datas.split('out:')[0].replace(',', '').split()
        self.d = datas.split(',')[0].replace('<', '').split('>')[1].split()
        self.d = [
            val for idx, val in enumerate(self.d)
            if val or (not val and self.d[idx - 1])
        ]

        self.name_router = self.d[3]
        mes, year = self.d[0], date.today().strftime("%Y")
        self.date_log = datetime.strptime(
            f'{self.d[1]}-{mes}-{year} {self.d[2]}', '%d-%b-%Y %H:%M:%S')

    def handling(self):
        mac, protocol, private, public, length, srch = None, None, [
            None, None
        ], [None, None], None, None
        stt = self.datas.split(',')[1:]
        aux = []

        for i in stt:
            val = i.split()
            if len(val) < 2:
                aux.append(['request', val[0]])
            else:
                aux.append(val)

        for j in aux:
            if 'src-mac' in j[0]:
                mac = j[1]
            elif 'proto' in j[0]:
                protocol = j[1]
            elif 'request' in j[0]:
                request = j[1].split('->')[0]
                result = self.whois(request)

                if result == 'private':
                    private = request.split(':')
                    srch = private[0]
                else:
                    public = request.split(':')
                    srch = public[0]

            elif 'NAT' in j[0]:
                lst = j[1].replace('(', '').replace(')', '').split('->')
                private = lst[0].split(':')
                public = lst[1].split(':')
                srch = private[0]
            elif 'len' in j[0]:
                length = j[1]

        dict_logs = {
            'id': self.millis,
            'connection_date': str(self.date_log),
            'router_name': self.name_router,
            'router_mac': mac,
            'protocol': protocol,
            'private_ip': private[0],
            'private_port': private[1],
            'public_ip': public[0],
            'public_port': public[1],
            'len': length,
            'raw': self.datas
        }

        for key, value in dict(dict_logs).items():
            if value is None:
                del dict_logs[key]

        return dict_logs

    def cgnat(self):
        self.psql.store(self.handling())

    def ipv4(self):
        self.psql.store(self.handling())

    @staticmethod
    def whois(ip):
        list_ip = ip.split('.')
        if not ((list_ip[0] == '192' and list_ip[1] == '168') or
                (list_ip[0] == '10') or ((list_ip[0] == '172') and
                                         (int(list_ip[1]) in range(16, 31))) or
                ((list_ip[0] == '100') and
                 (int(list_ip[1]) in range(0, 127)))):
            return 'public'
        else:
            return 'private'