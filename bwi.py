#!/usr/bin/env python
# coding:utf-8
# author TL

""" bandwagonhost vps info look up """
import os
import sys
import ConfigParser
import requests
from bs4 import BeautifulSoup

def readcfg(path):
    """ read cfg file """
    cfgdict = {}
    try:
        if os.path.isfile(path) and os.access(path, os.R_OK):
            parser = ConfigParser.RawConfigParser()
            if len(parser.read(path)) <= 0:
                sys.exit('no cfg file')
            try:
                cfgdict['local_use'] = parser.getint('info', 'local_use')
                cfgdict['manage_pass'] = parser.get('info', 'manage_pass')
            except ConfigParser.Error as ex:
                sys.exit(ex)
            if cfgdict['local_use'] == 0:
                if parser.has_option('info', 'vps_ip'):
                    cfgdict['vps_ip'] = parser.get('info', 'vps_ip')
            else:
                cfgdict['vps_ip'] = getlocalip()

        else:
            sys.exit('not a regular file or can\'t read')
    except (OSError, TypeError) as ex:
        sys.exit(ex)
    return cfgdict

def getlocalip():
    """ getlocalip """
    import socket
    return ([(s.connect(('8.8.8.8', 80)), \
            s.getsockname()[0], s.close()) \
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])

def reqstatus(cfgdict):
    """ request to bandwagonhost kiwivm """
    infodict = {}
    payload = {}

    payload['login'] = cfgdict['vps_ip']
    payload['password'] = cfgdict['manage_pass']
    req = requests.post('https://kiwivm.it7.net/?mode=login', data=payload)
    # only 200 is success not other code (run once)
    if req.status_code != 200:
        sys.exit('req not success')
    else:
        req = requests.get('https://kiwivm.it7.net/kiwi-main-controls.php',\
                cookies=req.cookies)
        soup = BeautifulSoup(req.text)
        # quick and dirty
        infolist = [tag for tag in soup.find_all('font')]
        if len(infolist) == 5:
            infodict['ram'] = infolist[0].string
            infodict['swap'] = infolist[1].string
            infodict['disk'] = infolist[2].string
            infodict['reset'] = infolist[3].string
            infodict['bandwidth'] = infolist[4].string
        else:
            sys.exit('parse error and exit.')
    return infodict

def showinfo(cfgdict, infodict):
    """ show info """
    print '----------------------------------------'
    print 'Node IP: ' + cfgdict['vps_ip']
    print 'RAM:     ' + infodict['ram']
    print 'SWAP:    ' + infodict['swap']
    print 'DISK:    ' + infodict['disk']
    print 'Reset:   ' + infodict['reset']
    print 'BW:      ' + infodict['bandwidth']
    print '----------------------------------------'


def main():
    """ main """
    cfgdict = readcfg('./bwi.cfg')
    infodict = reqstatus(cfgdict)
    showinfo(cfgdict, infodict)

if __name__ == '__main__':
    main()

