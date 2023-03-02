import subprocess
import socketserver
import logging
from lib.dao import Dao, get_config
from lib.spread import Spread


class SmartLog(socketserver.BaseRequestHandler):

    def handle(self):
        datas = bytes.decode(self.request[0].strip(), encoding="utf-8")
        try:
            dao = Dao(get_config(), 'dev')
            spread = Spread(datas, dao)
            if ' NAT ' in datas:
                spread.cgnat()
            else:
                spread.ipv4()
        except IndexError:
            pass

    def setup(self):
        logging.info(f"Connection from {self.client_address[0]}")

    def finish(self):
        logging.info(f"Connection closed with {self.client_address[0]}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")

    try:
        ips_list = subprocess.getoutput('hostname --all-ip-addresses').split(
            ' ')
        HOST, PORT = str(ips_list[0]), 514

        with socketserver.UDPServer((HOST, PORT), SmartLog) as server:
            logging.info(f"Listening on {HOST}:{PORT}")
            server.serve_forever()

    except KeyboardInterrupt:
        logging.info("Stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.warning("Finished logging service")
