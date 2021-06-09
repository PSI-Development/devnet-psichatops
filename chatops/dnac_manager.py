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

# Class for handling call to DNAC API and preprocess data before bring it to frontend (webexteams facing)
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
            data= "**Here is the list of devices on your network:**" + line_separator
            device_idx = 1
            for device in device_list['response']:
                    if device is not None:
                        data = data + str(device_idx) + ". " + "**HostName:** "+ device['hostname']+"\n"
                        data = data + ">**platformId:** " + device['platformId'].upper() + "\n"
                        data = data + ">**IpAddr:** " + device['managementIpAddress'].upper() + "\n"
                        data = data + ">**S/N:** " + device['serialNumber'].upper() + "\n"
                        device_idx+=1
            msg = data
            return(msg)
        except (ApiError, dnacentersdkException) as e:
            print(e)
            msg = "DNAC cannot be accessed currently"
            return(msg)
        
    def device_topology(self):
        try:
            physical_topo = self.dnac.topology.get_physical_topology(node_type="device")
            node_id = []
            node_name = []
            for node in physical_topo["response"]["nodes"] :
                wlc = ["Wireless Controller"]
                if not node["family"] in wlc :
                    node_id.append(node["id"])
                    node_name.append(node["label"])
                    src_node_df = pd.DataFrame({"source" : node_id, "src_node_name" : node_name})
                    target_node_df = pd.DataFrame({"target" : node_id, "target_node_name" : node_name})
            source = []
            target = []
            start_port = []
            end_port = []
            for link in physical_topo["response"]["links"] :
                id_wlc= ["d6823c59-fe0e-42fb-8183-1cf383d00629"]
                if not link["source"] in id_wlc :
                    print(id_wlc)
                    print(link["source"])
                    source.append(link["source"])
                    target.append(link["target"])
                    start_port.append(link["startPortName"])
                    end_port.append(link["endPortName"])
                    link_df = pd.DataFrame({"source" : source, "target" : target , "start_port" : start_port , "end_port" : end_port})
            join_topo_src_df = pd.merge(link_df, src_node_df, how ="left" ,on=["source"] )
            join_topo_src_target_df = pd.merge(join_topo_src_df, target_node_df, how ="left" ,on=["target"] )
            all_node = pd.concat([join_topo_src_target_df["src_node_name"] , join_topo_src_target_df["target_node_name"]])
            remove_duplicate_df = all_node.drop_duplicates()
            node_graph = remove_duplicate_df.values.tolist()
            all_node_link = join_topo_src_target_df.values.tolist()
            edge_graph = []
            for node in all_node_link :
                edge_graph.append([node[4],node[5], node[2]+ "-" +node[3]])
            dot = Digraph(comment="DNAC Device Topology:", format='png')
            dot.graph_attr['splines'] = "ortho"
            dot.attr('node', shape="rectangle" ,style="rounded,filled" ,gradientangle="270",fillcolor="#990033:#f5404f", color="#991111",fontcolor="#ffffff", fontname="Arial")
            #dot.attr('node', image="./switch.png")
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

    def device_uuid_list(self):
        devices = self.dnac.devices.get_device_list()
        devicesuid_list = []
        for device in devices.response:
            if device.family == 'Switches and Hubs':
                devicesuid_list.append(device.id)
    
    def cmd_run(self,device,command):
        run_cmd = self.dnac.command_runner.run_read_only_commands_on_devices(commands=[command],deviceUuids=[device])
        task_info = self.dnac.task.get_task_by_id(run_cmd.response.taskId)
        task_progress = task_info.response.progress
        while task_progress == 'CLI Runner request creation':
            task_progress = self.dnac.task.get_task_by_id(run_cmd.response.taskId).response.progress
        task_progress= json.loads(task_progress)
        fileid = task_progress['fileId']
        current_directory= pathlib.Path().absolute()
        current_directory= pathlib.Path().absolute()
        filename, cmd_output = self.__process_file(fileid=fileid,commands=command)
        filepath = str(current_directory)+"/"+filename
        return filepath
       
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

    def action_issue(self):
        try:
            event_list = self.dnac.event_management.get_notifications(sortBy = "timestamp", order = "desc" , limit = 1)
            instance_id =[]
            #print(event_list)
            for event in event_list :
                instance_id.append(event["instanceId"])
            instance = instance_id[0]
            #print(instance)
            headers = {
                        'entity_type': "issue_id",
                        'entity_value': instance
                        }
            issue = self.dnac.custom_caller.call_api('GET','/dna/intent/api/v1/issue-enrichment-details',headers=headers)
            #print(issue)
            line_separator = "\n******************************************************************************************\n"
            #print(device_list)
            data=  line_separator + "**ACTION** SUGESTED **ACTION**" + line_separator
            action_idx = 1
            if issue['errorCode'] is not None :
                msg = "errorCode : {} \n\n errorDescription :  {} ".format(issue['errorCode'],issue['errorDescription'],) 
                return (msg)
            else:   
                isu1 = issue["issueDetails"]["issue"][0]["suggestedActions"]
                #print (json.dumps(isu1, indent =4 ))
                for isu_all in issue["issueDetails"]["issue"]:
                    for isu_det in isu_all["suggestedActions"]:
                        #print (isu_det)
                        #message_action.append(isu_det["message"])
                        #print(message_action)
                        data = data + str(action_idx) + ". " + isu_det["message"]+"\n"
                        action_idx+=1
                msg = data
                #print (msg)
                return(msg)
        except (ApiError, dnacentersdkException) as e:
            print(e)
            return f'DNAC might not be accessible currently'