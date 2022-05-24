#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2021 Opensource ICT Solutions B.V.
# https://oicts.com
#
#version: 2.0.0
#date: 24-05-2022


###############################################################################################################
### Place this script in a directory on your zabbix server and make sure it is accesible by the zabbix user.###
### Make sure there is a API user present and update the variable below                                     ###
###                                                                                                         ###
### Usage: python <dir>/<scriptname> MODE(create/delete) "{HOST.HOST}"" <period> (in seconds)               ###
### Example: Script is placed in /frontend scripts. we create maintenance for 1 day:                        ###
### python /usr/lib/zabbix/frontend-scripts/maintenace.py create "{HOST.HOST}" 86400                        ###
###                                                                                                         ###
###############################################################################################################

import requests
import json
import time
import sys
from datetime import datetime

url = 'http://zabbix-url/zabbix/api_jsonrpc.php?'
token = "API Token here"

hostname = sys.argv[2]
period = sys.argv[3]
headers = {'Content-Type': 'application/json'}


def main():
    if sys.argv[1].lower() == 'create':
        hostid = hostid_get(token)
        maintenance_id = maintenance_get(token, hostid)
        # print(maintenance_id)
        if maintenance_id is not False:
            new_epoch = maintenance_update(token, maintenance_id, hostid)
        else:
            new_epoch = maintenance_set(token, hostid)
        message(new_epoch)
        maintenance_get(token, hostid)
    elif sys.argv[1] == 'delete':
        hostid = hostid_get(token)
        maintenance_id = maintenance_get(token, hostid)
        if maintenance_id:
            maintenance_delete(token, maintenance_id)
            message_delete()
        else:
            message_delete()

# --------------------
# Delete maintenance period of the selected host
# --------------------
def maintenance_delete(token, maintenance_id):
    payload = {}
    payload['jsonrpc'] = '2.0'
    payload['method'] = 'maintenance.delete'
    payload['params'] = {}
    payload['params'] = [maintenance_id]
    payload['auth'] = token
    payload['id'] = 1
    request = requests.post(url, data=json.dumps(payload), headers=headers)

    response = request.json()



# --------------------
# Message to confirm maintenance was deleted
# --------------------

def message_delete():
    print("The maintenance period of " + hostname + " was successfully removed.\r\nYou may close this window")


# --------------------
# Get maintenance period, if exists
# --------------------
def maintenance_get(token, hostid):
    payload = {}
    payload['jsonrpc'] = '2.0'
    payload['method'] = 'maintenance.get'
    payload['params'] = {}
    payload['params']['output'] = 'extend'
    payload['params']['hostids']= hostid
    payload['params']['selectTimeperiods'] = 'timeperiodid'
    payload['params']['search'] = {"description": "This maintenance period is created by a script."}
    payload['auth'] = token
    payload['id'] = 1
    request = requests.post(url, data=json.dumps(payload), headers=headers)

    response = request.json()

    if len(response["result"]) > 0:
        if 'maintenanceid' in response["result"][0]:
            return (response["result"][0]["maintenanceid"])
                    #response["result"][0]["timeperiods"][0]["timeperiodid"],)
    else:
        return (False)


# -------------------
# End of get maintenance
# -------------------

# -------------------
# Update existing maintenance
# ------------------
def maintenance_update(token, maintenance_id, hostid):
    epoch = datetime(1970, 1, 1)
    i = datetime.utcnow()
    current_epoch = int((i - epoch).total_seconds())
    new_epoch = current_epoch + int(period)

    payload = {}
    payload['jsonrpc'] = '2.0'
    payload['method'] = 'maintenance.update'
    payload['params'] = {}
    payload['params']['maintenanceid'] = maintenance_id
    payload['params']['active_since'] = current_epoch
    payload['params']['active_till'] = new_epoch
    payload['params']['hosts'] = []
    hosts = {}
    hosts['hostid'] = hostid
    payload['params']['hosts'].append(hosts)
    payload['params']['timeperiods'] = []
    timeperiods = {}
    timeperiods['start_date'] = current_epoch
    timeperiods['period'] = period
    payload['params']['timeperiods'].append(timeperiods)
    payload['auth'] = token
    payload['id'] = 1

    request = requests.post(url, data=json.dumps(payload), headers=headers)

    return new_epoch


# ---------------------
# Get hostID
# ---------------------
def hostid_get(token):
    payload = {}
    payload['jsonrpc'] = '2.0'
    payload['method'] = 'host.get'
    payload['params'] = {}
    payload['params']['output'] = ['hostid']
    payload['params']['filter'] = {}
    payload['params']['filter']['host'] = hostname
    payload['auth'] = token
    payload['id'] = 1


    request = requests.post(url, data=json.dumps(payload), headers=headers)

    response = request.json()
    hostid = response['result'][0]['hostid']
    return hostid


# ---------------------
# End of get hostID
# ---------------------

# ---------------------
# Setting maintenance
# ---------------------

def maintenance_set(token, hostid):
    epoch = datetime(1970, 1, 1)
    i = datetime.utcnow()
    current_epoch = int((i - epoch).total_seconds())

    new_epoch = current_epoch + int(period)

    payload = {}
    payload['jsonrpc'] = '2.0'
    payload['method'] = 'maintenance.create'
    payload['params'] = {}
    payload['params']['name'] = "Maintenance period for: " + hostname + ""
    payload['params']['active_since'] = current_epoch
    payload['params']['active_till'] = new_epoch
    payload['params']['hosts'] = []
    hosts = {}
    hosts['hostid'] = hostid
    payload['params']['hosts'].append(hosts)
    payload['params']['description'] = "This maintenance period is created by a script."
    payload['params']['timeperiods'] = []
    timeperiods = {}
    timeperiods['timeperiod_type'] = 0
    timeperiods['period'] = period
    payload['params']['timeperiods'].append(timeperiods)
    payload['auth'] = token
    payload['id'] = 1

    request = requests.post(url, data=json.dumps(payload), headers=headers)

    return new_epoch


def message(new_epoch):
    x = datetime.fromtimestamp(float(new_epoch))

    print("The host " + hostname + " was placed into maintenance. The period ends at: " + str(x) + "\r\nYou may close this window")


if __name__ == '__main__':
    main()
