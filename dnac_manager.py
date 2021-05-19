from dnacentersdk import api , ApiError, dnacentersdkException
import requests
import urllib3
requests.packages.urllib3.disable_warnings() 
import json     
import sys
#from graphviz import Digraph
import json
# from pandas import DataFrame
# import pandas as pd
import os
import time
from requests.auth import HTTPBasicAuth
# import sqlite3 as db
# from xlsxwriter.workbook import Workbook
from datetime import datetime , timedelta


class DNACManager():

    def __init__(self):
        self.dnac = self._connect()
        if self.dnac is not None:
            print('DNAC Initialization Successful')
        else:
            print('DNAC Initialization fails')

    def _connect(self):
        dnac_uname = os.environ["DNAC_USERNAME"]
        dnac_pass =os.environ["DNAC_PASSWORD"]
        dnac_url = os.environ["DNAC_CONN"]
        print(dnac_uname,dnac_pass,dnac_url)
        dnac = api.DNACenterAPI(base_url=dnac_url, username=dnac_uname, password=dnac_pass, verify=False)
        if dnac is not None:
            return dnac
        else:
            print('dnac client fails to connect')
            return None

    def device_list(self):
        try :
            device_list = self.dnac.devices.get_device_list()
            #print(device_list)
            msg_content_list = []
            title_mrkdown = ("Device List in DNAC are: \n")
            device_idx = 1
            for device in device_list['response']:
                    if device is not None:
                                    #print(device)
                                    site_mrkdown = ("*{}. Hostname:* {} ".format(device_idx, device['hostname']))
                                    site_mrkdown_status = ( "`IpAddress: {}`  `platformId: {}` `macAddress: {}`".format(device['managementIpAddress'], device['platformId'],device['macAddress']))
                                    msg_content_list.append(site_mrkdown)
                                    msg_content_list.append(site_mrkdown_status)
                                    #print(msg_content_list)
                                    device_idx+=1
            msg = msg_content_list
            #print(msg)
            return(msg)
        except (ApiError, dnacentersdkException) as e:
            print(e)
            msg = "DNAC cannot be access currently"
            return(msg)

'''
dnac = DNACManager()
msg = dnac.device_list()
print(msg)
'''
