from dnacentersdk import api , ApiError, dnacentersdkException
import requests
import urllib3
requests.packages.urllib3.disable_warnings() 
import json     
import sys
import json
import os
from requests.auth import HTTPBasicAuth
import pathlib
from datetime import datetime , timedelta
from webexteamssdk import WebexTeamsAPI

class WebhookManager():

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

    def handle_event(self, dnac, event):
        message = self.format_event(dnac, event)
        print(message)
        self.post_message(message)

    def post_message(self, msg) :
        #slack_data = {'text': message }
        teams_token = os.getenv("TEAMS_BOT_TOKEN")
        ROOM_ID = os.getenv("TEAMS_ROOM_ID")
        #ROOM_ID = "Y2lzY29zcGFyazovL3VzL1JPT00vY2M1NDRkMjAtYjI0MC0xMWViLTk0ZDctMTlkZDEzYjU1YzYy"
        api = WebexTeamsAPI(access_token=teams_token)
        #DEMO_MESSAGE = u"Webex Teams rocks!  \ud83d\ude0e"
        DEMO_MESSAGE = msg
        message = api.messages.create(ROOM_ID, text=DEMO_MESSAGE) 

    def old_format_event(self, event):
        msg = "Old Format Event"
        return msg

    def new_format_event(self,dnac,event):
        data=  "**ALERT** **Notification** **ALERT**" +"\n"
        data = data + event['details']['Assurance Issue Details']+"\n"
        msg = data
        return msg
    def format_event(self, dnac,event):
        if 'title' in event:
            return(self.old_format_event(event))
        else:
            return (self.new_format_event(dnac,event))

