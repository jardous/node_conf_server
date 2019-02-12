#!/usr/bin/env python3
# @author: Jiri Popek <jiri.popek@gmail.com>
#
# Server providing a configuration for IoT nodes in JSON format
#
# Configuration files are expected to be stored in "nodes"
# directory (this script's path). They have to define
# Python dictionary with changed values (default dict will be updated).
#
# Example of configuration for node "lake" (stored as nodes/lake.py):
#
# dict(
#     sleep_interval = 10,  # log every minute
#     dfrobot_moisture = True
# )
#


import json
import logging
import os

from http.server import BaseHTTPRequestHandler, HTTPServer


# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    filename="config_server.log",
                    filemode='a')

logger = logging.getLogger()


default_conf = dict(
    sleep_interval = 10*60,    # sleep time in second
    local_influxdb = True,     # log to a local InfluxDB
    adafruit_io = False,       # log to a Adafruit IO
    dht11_temp = False,        # read and log temperature from DHT11 sensor
    dht11_humidity = False,    # read and log humidity from DHT11 sensor
    ds18b20_temp = False,      # read and log temperature from DS18B20 sensor
    dfrobot_moisture = False,  # read and log moisture from a capacitive moisture sensor
    door_opened = False        # read and log value from a magnetic contact switch
)


class Configuration:

    def __getitem__(self, name):
        custom_conf = {}
        conf = default_conf.copy()
        dn = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dn, "nodes", name + ".py")
        try:
            with open(filename, "rt") as f:
                custom_conf = eval(f.read())
            conf.update(custom_conf)
            return conf
        except IOError:
            logger.error("Error: config for '{}' not found".format(filename))
        return conf


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        # do not handle empty and favicon (for testing from a browser)
        if self.path in ("", "/favicon.ico"):
            logger.info("Skipping path '{}'".format(self.path))
            return

        conf = Configuration()[self.path.strip('/').replace('-', '_')]
        content = json.dumps(conf).encode()
        logger.debug("Serving to {}".format(self.client_address))
        self.wfile.write(content)
        return


if __name__ == "__main__":
    server = HTTPServer(("", 5000), RequestHandler)
    print("Starting node config server at http://localhost:5000")
    server.serve_forever()
