#!/usr/bin/env python
import gzip
import os
import re
from datetime import datetime
import pytz
import sys
import getopt
import csv

tz = pytz.timezone('UTC')

lineformat = re.compile(r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(HTTP\/1\.1")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (rt=(?P<rt>\d{1,3}\.\d{1,3})) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""", re.IGNORECASE)

STATUS_NOT_VALID = [302, 101, 301, 499]


def main(argv):
    inputdir = ''
    filename = ''
    try:
        opts, args = getopt.getopt(argv, "hd:n:", ["dir=", "name="])
    except getopt.GetoptError:
        print('nginx_parser.py -d <inputdir> -n <filename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('nginx_parser.py -d <inputdir> -n <filename>')
            sys.exit()
        elif opt in ("-d", "--dir"):
            inputdir = arg
        elif opt in ("-n", "--name"):
            filename = arg
    if not inputdir or not filename:
        print('nginx_parser.py -d <inputdir> -n <filename>')
        sys.exit()
    INPUT_DIR = inputdir
    output = csv.writer(sys.stdout)
    output.writerow([
        'Datetime',
        'URL',
        'Status',
        'Method',
        'Response time',
        'User Agent',
        'BytesSent'])
    for f in os.listdir(inputdir):
        if not f.startswith(filename):
            continue
        file_gzip = False
        if f.endswith(".gz"):
            logfile = gzip.open(os.path.join(INPUT_DIR, f))
            file_gzip = True
        else:
            logfile = open(os.path.join(INPUT_DIR, f))
        for l in logfile.readlines():
            if file_gzip:
                data = re.search(lineformat, l.decode('ascii'))
            else:
                data = re.search(lineformat, l)
            if data:
                datadict = data.groupdict()
                datetimeobj = datetime.strptime(datadict["dateandtime"], "%d/%b/%Y:%H:%M:%S %z") # Converting string to datetime obj
                url = datadict["url"]
                useragent = datadict["useragent"]
                bytessent = datadict['bytessent']
                status = datadict["statuscode"]
                response_time = datadict['rt']
                method = data.group(6)
                if int(status) in STATUS_NOT_VALID:
                    continue
                url = url.replace(' ', '')
                if url.startswith('/static') or url.startswith('/assets') or url.endswith('js'):
                    continue
                output.writerow([
                    tz.normalize(datetimeobj),
                    url,
                    status,
                    method,
                    response_time,
                    useragent,
                    bytessent])
        logfile.close()


if __name__ == "__main__":
    main(sys.argv[1:])
