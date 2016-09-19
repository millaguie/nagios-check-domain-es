#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#
#    This script help us to check expiration date of domain from Spain (.es)
#    Use it with nagios. Execute check_domain -h for help
#
#    Author(es):
#    * Juan Pedro Escalona Rueda <jpescalona@otioti.com>
#
# Dependecies
#	- pycurl
#	- dateutil
#
#
# Changelog:
#       - 17/09/12 v1.0.6: Checks availability for domains
#               - Returns "UNKNOW - Domain is not registered yet" if domains is avaible.
#       - 12/01/11 v1.0.4: Whois webpage changed
#               - centrored.es added captchap protection.
#       - 07/04/10 v1.0.2: Whois webpage changed
#               - whs.es stopped to respond. It was changed to www.centrored.com
#       - 02/03/10 v1.0.1: New feature
#               - Response controller for "I'm sorry, domain is unavaible." response.
# vi:ts=4:et
# $Id: check_domain.py,v 1.0 2009/12/03 11:09:11 mfx Exp $
########################################
import sys
import pycurl
import getopt
from datetime import datetime, date, time

VER='1.0.4'
EXPR='Expiraci&oacute;n:'
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_WARNING=1
STATE_OK=0

class Request:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf

def usage():
    print """
    check_domain_es - v%s
    Copyright (c) 2011 Juan Pedro Escalona Rueda <jpescalona@otioti.com> under GPL License
    This plugin checks the expiration date of a domain name.

    Usage: check_domain_es -h | -d <domain> [-c <critical>] [-w <warning>]
    NOTE: -d must be specified

       -h: Print detailed help

       -d: domain name to check

       -w: Response time to result in warning status (days). 30 days by default

       -c: Response time to result in critical status (days). 7 days by default

       This plugin will use whois service to get the expiration date for the domain name. 
       Example:
             check_domain_es.py -d iavante.es -w 30 -c 10
    """ % VER

def main(argv):
    critical=7
    warning=30
    extension = ".es"
    domain = "iavante"
    diff = -1


    try:
        opts, args = getopt.getopt(argv, "hd:c:w:", ["help", "domain=", "critical=", "warning="])
    except getopt.GetoptError:
        usage()
        sys.exit(3)

    for opt, arg in opts:
        if opt in ("-h", "help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--domain"):
            tld = arg.split('.')
            if len(tld) != 2:
                usage()
                sys.exit(3)
            domain = tld[0]
            extension = ".%s" % tld[1]
            if extension != ".es":
                usage()
                sys.exit(3)

        elif opt in ("-c", "--critical"):
            critical = int(arg)
        elif opt in ("-w", "--warning"):
            warning = int(arg)

    t = Request()
    c = pycurl.Curl()

    # Old requests

    # WHS.es
    #c.setopt(c.URL, 'https://www.whs.es/operations/checkDom.php')
    #c.setopt(c.POSTFIELDS, 'extension=%s&dominio=%s&fCheck=1' % (extension, domain))

    # CentroRed.com
    #c.setopt(c.URL, 'https://www.centrored.com/registro-dominios/')
    #c.setopt(c.POSTFIELDS, 'accion=whois&dominio=%s&tld=%s' % (domain, extension[1:len(extension)]))

    # New Request
    # Whoises.es
    c.setopt(c.URL, 'http://www.whoises.com/%s.%s' % (domain, extension[1:len(extension)]))

    #c.setopt(c.POST, 1)
    c.setopt(pycurl.SSL_VERIFYPEER,0)
    c.setopt(c.WRITEFUNCTION, t.body_callback)
    c.perform()
    c.close()

    if t.contents.find("No match for domain") > 1:
      print "UNKNOW - Domain is not registered yet" 
      sys.exit(STATE_UNKNOWN)

    if t.contents.find("I'm sorry, domain is unavaible.") == -1:

      position_a = t.contents.find(EXPR)
      position_inic = t.contents[position_a+len(EXPR):].find("<td class")
      position_inic = position_a + len(EXPR) + position_inic + len("<td class='a'>")

      position_fin = t.contents[position_inic:].find('</td>') + position_inic
      expdate = datetime.strptime(t.contents[position_inic:position_fin], "%d-%b-%Y")
      today = datetime.now()

      diff = (expdate - today).days

    if not diff == -1:
        if diff < 0:
            print "CRITICAL - Domain will expire in %s days" % abs(diff)
            sys.exit(STATE_CRITICAL)
        if diff < critical:
            print "CRITICAL - Domain will expire in %s days" % diff
            sys.exit(STATE_CRITICAL)
        if diff < warning:
            print "WARNING - Domain will expire in %s days" % diff
            sys.exit(STATE_WARNING)

        print "OK - Domain will expire in %s days" % diff
        sys.exit(STATE_OK)

    else:
        print "UNKNOW - Expiration date cannot be checked" 
        sys.exit(STATE_UNKNOWN)
    
if __name__ == "__main__":
    main(sys.argv[1:])
