#!/usr/bin/env python

#
# modules
#
import arrow
import ConfigParser
import requests
import ssl
import sys
import xmlrpclib

#
# globals
#
config = ConfigParser.ConfigParser()
config.read('spacewalk-device42.ini')
DEVICE42_CREDS = (config.get('DEVICE42', 'username'), config.get('DEVICE42', 'password'))
SATELLITE_URL = config.get('SPACEWALK', 'apiurl')
SATELLITE_CREDS = dict()
for key, val in config.items('SPACEWALK_ORGS'):
    SATELLITE_CREDS[int(key)] = val.split(',')

#
# login (admin)
#
client = xmlrpclib.Server(SATELLITE_URL, verbose=False, context=ssl._create_unverified_context())
key = client.auth.login(SATELLITE_CREDS[1][0], SATELLITE_CREDS[1][1])

#
# all orgs
#
orgs = client.org.listOrgs(key)
for org in orgs:
    print "=" * 80
    print "Spacewalk Organization: {} ({})".format(org['name'], org['id'])

    #
    # login (orgadmin)
    #
    client2 = xmlrpclib.Server(SATELLITE_URL, verbose=False,
                               context=ssl._create_unverified_context())
    key2 = client2.auth.login(SATELLITE_CREDS[org['id']][0], SATELLITE_CREDS[org['id']][1])

    #
    # all systems
    #
    systems = client2.system.listUserSystems(key2, SATELLITE_CREDS[org['id']][0])
    for system in systems:
        print "-" * 70
        print "  System Name: {} ({})".format(system['name'], system['id'])

        channel = client2.system.getSubscribedBaseChannel(key2, system['id'])
        print "    Channel Name: {} ({})".format(channel['name'], channel['id'])

        actkey = client2.system.listActivationKeys(key2, system['id'])
        print "    Activation Key: {}".format(actkey[0])

        regdate = client2.system.getRegistrationDate(key2, system['id'])
        print "    Registration Date: {}".format(arrow.get(str(regdate), 'YYYYMMDDTHH:mm:ss').format('YYYY-MM-DD'))
        regdate2 = arrow.get(str(regdate), 'YYYYMMDDTHH:mm:ss').format('YYYY-MM-DD')

        #
        # d42: update spacewalk organization, base channel and activation key (bulk)
        #
        payload = {
            'name': system['name'],
            'bulk_fields': 'Spacewalk Organization:{},Spacewalk Base Channel:{},Spacewalk Activation Key:{}'.format(org['name'], channel['name'], actkey[0])
        }
        url = config.get('DEVICE42', 'apiurl')
        r = requests.put(url, auth=DEVICE42_CREDS, data=payload)
        print "      Setting D42 Spacewalk Organization, Base Channel, Activation Key: HTTP {}".format(r.status_code)

        #
        # d42: update spacewalk registration date (can't do it above b/c it's type 'date' not 'text')
        #
        payload = {
            'name': system['name'],
            'type': 'date',
            'key': 'Spacewalk Registration Date',
            'value': regdate2
        }
        url = config.get('DEVICE42', 'apiurl')
        r = requests.put(url, auth=DEVICE42_CREDS, data=payload)
        print "      Setting D42 Spacewalk Registration Date: HTTP {}".format(r.status_code)

    #
    # logout (orgadmin)
    #
    client.auth.logout(key2)

#
# logout (admin)
#
client.auth.logout(key)
