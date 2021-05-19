from dnacentersdk import api , ApiError, dnacentersdkException
import requests
import urllib3
requests.packages.urllib3.disable_warnings() 
import json     
import sys
from graphviz import Digraph
import json
from pandas import DataFrame
import pandas as pd
import os
from requests.auth import HTTPBasicAuth
import pathlib
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
            line_separator = "\n******************************************************************************************\n"
            #print(device_list)
            data= "**Here is the list of devices on your network:**" + line_separator
            device_idx = 1
            for device in device_list['response']:
                    if device is not None:
                        data = data + str(device_idx) + ". " + "**Name:** "+ device['hostname']+"\n"
                        data = data + "**platformId:** " + device['platformId'].upper() + "\n\n"
                        device_idx+=1
            msg = data
            #print(msg)
            return(msg)
        except (ApiError, dnacentersdkException) as e:
            print(e)
            msg = "DNAC cannot be access currently"
            return(msg)
        
    def device_topology(self):
        try:
            physical_topo = self.dnac.topology.get_physical_topology(node_type="device")
            #print(json.dumps(physical_topo, indent= 4))
            node_id = []
            node_name = []
            for node in physical_topo["response"]["nodes"] :
                node_id.append(node["id"])
                node_name.append(node["label"])
                src_node_df = pd.DataFrame({"source" : node_id, "src_node_name" : node_name})
                target_node_df = pd.DataFrame({"target" : node_id, "target_node_name" : node_name})
            #print(src_node_df)
            #print(target_node_df)
            source = []
            target = []
            start_port = []
            end_port = []
            for link in physical_topo["response"]["links"] :
                source.append(link["source"])
                target.append(link["target"])
                start_port.append(link["startPortName"])
                end_port.append(link["endPortName"])
                link_df = pd.DataFrame({"source" : source, "target" : target , "start_port" : start_port , "end_port" : end_port})
            #print(link_df)
            join_topo_src_df = pd.merge(link_df, src_node_df, how ="left" ,on=["source"] )
            join_topo_src_target_df = pd.merge(join_topo_src_df, target_node_df, how ="left" ,on=["target"] )
            #print(join_topo_src_df)
            #print(join_topo_src_target_df)
            all_node = pd.concat([join_topo_src_target_df["src_node_name"] , join_topo_src_target_df["target_node_name"]])
            #print(all_node)
            remove_duplicate_df = all_node.drop_duplicates()
            #print(remove_duplicate_df)
            node_graph = remove_duplicate_df.values.tolist()
            #print(node_graph)
            all_node_link = join_topo_src_target_df.values.tolist()
            #print(all_node_link)
            #print(all_node_link[0][5])
            edge_graph = []
            for node in all_node_link :
                edge_graph.append([node[4],node[5], node[2]+ "-" +node[3]])
            #print(edge_graph)
            dot = Digraph(comment="DNAC Device Topology:", format='png')
            dot.graph_attr['splines'] = "ortho"
            dot.attr('node', shape="rectangle" ,style="rounded,filled" ,gradientangle="270",fillcolor="#990033:#f5404f", color="#991111",fontcolor="#ffffff", fontname="Arial")
            dot.attr('edge', weight='10')
            dot.attr('edge', arrowhead='none')
            dot.body.append(r'label = "\n\nDNAC Device Topology"')
            dot.body.append('fontsize=20')
            for node in node_graph:
                dot.node(node)
            for edge in edge_graph:
                dot.edge(edge[0], edge[1], edge[2] )
            filename = 'DNAC_Device_Topology'
            dot.render(filename=filename)
            current_directory= pathlib.Path().absolute()
            #print(current_directory)
            msg= str(current_directory)+"/"+filename+".png"
            return msg
        except (ApiError, dnacentersdkException) as e:
            print(e)
            msg = "DNAC cannot be access currently"
            return(msg)
    def get_token(self, dnac_ip, dnac_ver, dnac_uname, dnac_pass):
        dnac_uname = os.environ["DNAC_USERNAME"]
        dnac_pass =os.environ["DNAC_PASSWORD"]
        dnac_url = os.environ["DNAC_CONN"]
        dnac_ip = os.environ["DNAC_IP"]
        dnac_ver = os.environ["DNAC_VER"]  
        post_url = "https://"+ dnac_ip +"/api/system/"+ dnac_ver +"/auth/token"
        headers = {'content-type': 'application/json'}
        try:
            r = requests.post(post_url, auth=HTTPBasicAuth(username=dnac_uname, password=dnac_pass), headers=headers,verify=False)
            #print (r.text)
            r.raise_for_status()
            return r.json()["Token"]
        except requests.exceptions.ConnectionError as e:
            return ("Error: %s" % e)
    def device_uuid_list(self):
        devices = self.dnac.devices.get_device_list()
        devicesuid_list = []
        for device in devices.response:
            if device.family == 'Switches and Hubs':
                devicesuid_list.append(device.id)
        #commands=["show int des"]
        #perlu comment buat menghentikan self testing command runner
        #self.cmd_run(device_list=devicesuid_list, commands=commands)
    '''
    def cmd_run(self,device_list,commands):
        for device in device_list:
            run_cmd = self.dnac.command_runner.run_read_only_commands_on_devices(commands=commands,deviceUuids=[device])
            task_info = self.dnac.task.get_task_by_id(run_cmd.response.taskId)
            task_progress = task_info.response.progress
            while task_progress == 'CLI Runner request creation':
                task_progress = self.dnac.task.get_task_by_id(run_cmd.response.taskId).response.progress
            task_progress= json.loads(task_progress)
            fileid = task_progress['fileId']
            current_directory= pathlib.Path().absolute()
            dnac_url= os.environ["DNAC_CONN"]
            cmd_output= self.processFile(dnac_url=dnac_url, fileid=fileid,commands=commands)
            #cmd_output = self.dnac.file.download_a_file_by_fileid(fileid,dirpath=current_directory, save_file= True)
    '''
    '''
    def processFile(self, dnac_url, fileid, commands):
        file_url = dnac_url + f"/api/v1/file/{fileid}"
        dnac_uname = os.environ["DNAC_USERNAME"]
        dnac_pass =os.environ["DNAC_PASSWORD"]
        dnac_url = os.environ["DNAC_CONN"]
        dnac_ip = os.environ["DNAC_IP"]
        dnac_ver = os.environ["DNAC_VER"]  
        token = self.get_token(dnac_ip=dnac_ip,dnac_ver=dnac_ver, dnac_uname=dnac_uname, dnac_pass=dnac_pass)
        headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-auth-Token": token 
                    }
        filename = "cmd_output.txt"
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "w") as f:
            print(f"FileURL: {file_url}")
            response = requests.get(file_url, headers=headers, verify=False ).json()
            for cmd in commands :
                #print(cmd)
                cmd_output= response[0]['commandResponses']['SUCCESS'][cmd]
                print (cmd_output, file=f)
        return( filename, cmd_output)
    '''
#perlu comment buat menghentikan self testing command runner
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
        filename, cmd_output = self.__process_file(fileid=fileid,commands=command)
        return filename
        #cmd_output = self.dnac.file.download_a_file_by_fileid(fileid,dirpath=current_directory, save_file= True)
    '''
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
    '''
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
            print (cmd_output, file=f)
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
msg = dnac.device_uuid_list()
'''