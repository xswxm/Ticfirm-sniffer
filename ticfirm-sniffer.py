#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests, threading
import sys, logging, time

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='A tool for sniffing Ticwatch firmwares, enjoy!')
parser.add_argument('-d', '--debug', help='display debug info', action='store_true')
parser.add_argument('-a', '--app', type=str, default='ticwatch', 
    help='device type (check in "Settings - About - Device type"). e.g.: ticwatch, ticwatch2-i18n. default=ticwatch')
parser.add_argument('-c', '--channel', type=str, default='release', 
    help='firmware type. e.g.: alpha, beta, release. default=release')
parser.add_argument('-u', '--uid', type=str, default='', 
    help='device id (check in "Settings - About - Device id"). default=none')
parser.add_argument('-v', '--versions', type=int, nargs='+', 
    help='versions. defualt=412000 413000, which means checking the version number from 412000 to 413000.', default=[412000, 413000])
parser.add_argument('-t', '--thread_number', type=int, 
    help='number of multi-threading, the larger the faster. default=100', default=100)

args = parser.parse_args()
if args.debug:
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
print('Device type:\t{0}'.format(args.app))
print('Channel:\t{0}'.format(args.channel))
print('Device ID:\t{0}'.format(args.uid))
print('Versions:\t{0} - {1}'.format(args.versions[0], args.versions[1]))
print('Thread number:\t{0}'.format(args.thread_number))
print('Debug mode:\t{0}'.format(args.debug))

class myThread(threading.Thread):
    def __init__(self, threadID, api, app, channel, version=0):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.api = api
        self.app = app
        self.channel = channel
        self.version = version
    def run(self):
        global versionNext, versionLimit, uid
        if self.version == 0:
            curversion = versionNext
        else:
            curversion = self.version
        while curversion <= versionLimit:
            if self.version == 0:
                versionNext += 1
            url = self.api + "app=" + self.app + '&channel=' + self.channel + '&version=' + str(curversion)
            if uid != '':
                url += '&uid=' + str(uid)
            try:
                FirmCheck(url)
                logging.info('Thread {0}: \tVersion {1} \tchecked!'.format(self.threadID, curversion))
            except:
                logging.info('Thread {0}: \tVersion {1} \tcheck failed, rechecking!'.format(self.threadID, curversion))
                global threads
                threads[self.threadID] = myThread(self.threadID, self.api, self.app, self.channel)
                threads[self.threadID].start()
            curversion = versionNext

_lock = threading.RLock()
def FirmCheck(url):
    cont = requests.get(url).content
    dict = eval(cont.replace('true', 'True').replace('false', 'False'))
    if dict['number'] != 0:
        versionDetected.append(dict['number'])
        with _lock:
            csv = CSVGen(dict)
            CSVWriter(csv)

def CSVGen(dict):
    csv = ''
    csv += CSVAdd(dict, True, 'changelog')
    csv += ',' + CSVAdd(dict, True, 'createDateStr')
    csv += ',' + CSVAdd(dict, True, 'description')
    csv += ',' + CSVAdd(dict, True, 'remark')
    csv += ',' + CSVAdd(dict, False, 'forceUpdate')
    csv += ',' + CSVAdd(dict, False, 'enableTest')
    csv += ',' + CSVAdd(dict, True, 'url')
    csv += ',' + CSVAdd(dict, True, 'testUserIds')
    csv += ',' + CSVAdd(dict, False, 'valid')
    csv += ',' + CSVAdd(dict, False, 'number')
    csv += ',' + CSVAdd(dict, False, 'upgradeScale')
    csv += ',' + CSVAdd(dict, False, 'createdDate')
    csv += ',' + CSVAdd(dict, False, 'size')
    csv += ',' + CSVAdd(dict, False, 'enable')
    csv += ',' + CSVAdd(dict, True, 'name')
    csv += ',' + CSVAdd(dict, True, 'id')
    csv += ',' + CSVAdd(dict, False, 'difSrcVersions')
    csv += ',' + CSVAdd(dict, True, 'difUpgradeFrom')
    csv += ',' + CSVAdd(dict, True, 'compatibility')
    csv += ',' + CSVAdd(dict, False, 'downloadCount')
    csv += ',' + CSVAdd(dict, True, 'md5')
    csv += ',' + CSVAdd(dict, True, 'ossPath') + '\n'
    return csv

def CSVAdd(dict, type, key):
    if key in dict:
        if type == True:
            return '"' + dict[key] + '"'
        else:
            return str(dict[key])
    else:
        if type == True:
            return '""'
        else:
            return ''

def CSVWriter(s):
    with open('output.csv', 'a') as csvFile:
        csvFile.write(s)

# Start Here
api = 'http://mushroom.chumenwenwen.com/api/version.json?'
app = args.app
channel = args.channel
versionInitial = args.versions[0]
versionNext = versionInitial
versionLimit = args.versions[1]
uid = args.uid
threadNumber = args.thread_number
count = versionLimit - versionInitial
versionDetected = []
# Initialize Threads
threads = []
for i in range(threadNumber):
    threads.append(myThread(i, api, app, channel))

# Start Threads
for thread in threads:
    thread.start()


while True:
    threadsAliveNum = 0
    for i in range(threadNumber):
        if threads[i].isAlive():
            threadsAliveNum += 1

    if not args.debug:
        process = (versionNext-versionInitial-threadsAliveNum)*100/count
        str1 = '>'*(process//2)+' '*((100-process+1)//2)
        sys.stdout.write('\r'+str1+'[%s%%]'%(process))
        sys.stdout.flush()

    if versionNext > versionLimit and threadsAliveNum == 0:
        print('')
        print('Version detected: {0}'.format(versionDetected))
        print('All the results have been saved in "output.csv".')
        quit()
    time.sleep(0.1)
