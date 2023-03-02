from datetime import datetime, date
import time


class Spread:

    def __init__(self, datas, psql):
        self.psql = psql
        self.datas = datas
        self.millis = int(round(time.time() * 1000))
        self.info_router = datas.split('out:')[0].replace(',', '').split()

        parts = [
            val for val in datas.split(',')[0].replace('<', '').split('>')
            [1].split() if val or (not val and parts[idx - 1])
        ]

        self.name_router = parts[3]
        mes, year = self.d[0], date.today().strftime("%Y")
        self.date_log = datetime.strptime(f'{self.d[1]}-{mes}-{year} {self.d[2]}', '%d-%b-%Y %H:%M:%S')

    def handling(self):
        mac, protocol, private, public, length = None, None, (None, None), (
            None, None), None
        parts = self.datas.split(',')[1:]

        for part in parts:
            key, value = part.split()[0], part.split()[1:]
            if len(value) > 0:
                value = value[0]
            else:
                value = None

            if 'src-mac' in key:
                mac = value
            elif 'proto' in key:
                protocol = value
            elif 'request' in key:
                request = value.split('->')[0]
                result = self.whois(request)

                if result == 'private':
                    private = tuple(request.split(':'))
                else:
                    public = tuple(request.split(':'))
            elif 'NAT' in key:
                lst = value.replace('(', '').replace(')', '').split('->')
                private = tuple(lst[0].split(':'))
                public = tuple(lst[1].split(':'))
            elif 'len' in key:
                length = value

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
            'pppoe_user': None,
            'pppoe_mac': None,
            'raw': self.datas
        }

        dict_logs = {k: v for k, v in dict_logs.items() if v is not None}

        return dict_logs

    def store_log(self, method_name):
        getattr(self.psql, method_name)(self.handling())

    def cgnat(self):
        self.store_log('store')

    def ipv4(self):
        self.store_log('store')

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
