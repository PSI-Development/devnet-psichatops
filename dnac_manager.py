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
        self.dnac = self.__connect()
        if self.dnac is not None:
            print('DNAC Initialization Successful')
        else:
            print('DNAC Initialization fails')

    def __connect(self):
        self.dnac_username = os.environ["DNAC_USERNAME"]
        self.dnac_password =os.environ["DNAC_PASSWORD"]
        self.dnac_url = os.environ["DNAC_CONN"]
        self.dnac_version = "v1"
        dnac = api.DNACenterAPI(base_url=self.dnac_url, username=self.dnac_username, password=self.dnac_password, verify=False)
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

    # def cmd_run_show(self, commands = "", deviceUuids = ""):
    #     cmd_resp = []
    #     try:
    #         payload = { 
    #             'commands': [commands], #COMMAND harus dalam bentuk LIST/ARRAY
    #             'deviceUuids':[deviceUuids] #UUID harus dalam bentuk LIST/ARRAY
    #             }
    #         print("Payload: {}".format(payload))
    #         resp = self.__dnac_api_post(api="network-device-poller/cli/read-request", payload = payload )
    #         status = resp.status_code
    #         print (status)
    #         response_json = resp.json()
    #         task_url = response_json['response']['url']
    #         task = self.__wait_task(task_url)
    #         print (task)
    #         fileId = json.loads(task['response']['progress'])
    #         print(commands)
    #         filename, cmd_output = self.__process_file(fileId['fileId'],commands=commands)
    #         #self.__send_cmd_slack(filename[0],  channel_id)
    #         return filename
    #     except ValueError:
    #         return f'DNAC might not be accessible currently'
    
    def cmd_run(self,device,command):
        run_cmd = self.dnac.command_runner.run_read_only_commands_on_devices(commands=[command],deviceUuids=[device])
        task_info = self.dnac.task.get_task_by_id(run_cmd.response.taskId)
        task_progress = task_info.response.progress
        while task_progress == 'CLI Runner request creation':
            task_progress = self.dnac.task.get_task_by_id(run_cmd.response.taskId).response.progress
        task_progress= json.loads(task_progress)
        fileid = task_progress['fileId']
        current_directory= pathlib.Path().absolute()
        filename, cmd_output = self.__processFile(fileid=fileid,commands=commands)
        return filename
        #cmd_output = self.dnac.file.download_a_file_by_fileid(fileid,dirpath=current_directory, save_file= True)

    def __dnac_api_post(self, api='', params='', payload = ''):
        #url = self.dnac_url + "/api/" + self.dnac_version + "/" + api
        url = self.dnac_url + "/dna/intent/api/" + self.dnac_version + "/" + api
        print("API post url: {}".format(url))
        token = self.__get_token()
        print(token)
        headers = {"X-Auth-Token": token, "Accept": "application/json" , "Content-Type": "application/json"}
        data=json.dumps(payload)
        try:
            r = requests.post(url,headers=headers,params=params,data=data ,verify = False)
            return(r)
        except:
            return f'DNAC might not be accessible currently',api
    
    def __wait_task(self, task_url):
        token = self.__get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-auth-Token": token
            }
        for i in range(10):
            time.sleep(1)
            response_task =  requests.get(self.dnac_url + task_url, headers=headers, verify=False).json()
            if response_task['response']['isError']:
                print("Error")
            if "endTime" in response_task['response']:
                return response_task
    
    def __process_file(self, fileid, commands):
        file_url = self.dnac_url + f"/api/v1/file/{fileid}"
        token = self.__get_token()
        headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-auth-Token": token 
                }
        filename = "cmd_output.txt"
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "w") as f:
            response = requests.get(file_url, headers=headers, verify=False ).json()
            cmd_output= response[0]['commandResponses']['SUCCESS'][commands]
        return (filename, cmd_output)
    
    def __get_token(self):
        #post_url = "https://"+ip+"/api/system/"+ ver +"/auth/token"
        post_url = self.dnac_url + "/api/system/" + self.dnac_version + "/auth/token"
        headers = {'content-type': 'application/json'}
        try:
            r = requests.post(post_url, auth=HTTPBasicAuth(username=self.dnac_username, password=self.dnac_password), headers=headers,verify=False)
            r.raise_for_status()
            return r.json()["Token"]
        except requests.exceptions.ConnectionError as e:
            return ("Error: %s" % e)
    

'''
dnac = DNACManager()
msg = dnac.device_list()
print(msg)
'''
