import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import sys
import json
from webexteamssdk import WebexTeamsAPI
from cards_factory import generate_cmd_runner_card
from requests_toolbelt.multipart.encoder import MultipartEncoder
from flask import Flask, request
from webhook import WebhookManager

# Initialized managed entitities (e.g. DNAC, APIC, IOS, SolarWind)
webhook = WebhookManager()






flask_app = Flask(__name__)

# Register Webhook routes to Flask app
@flask_app.route('/', defaults={'path': ''}, methods=['GET','POST'])
@flask_app.route('/<path:path>', methods=["GET","PUT","POST","DELETE"])
def get_all(path):
    print ("============================")
    print (path)
    print("Method {}, URI {}".format(request.method,request.path))
    if request.method == "POST":
        print (request.headers)
        print (request.json)
        if request.json != {}:
            webhook.handle_event(request.remote_addr, request.json)
        else:
            print("skipping - empty")
    else:
        print (request.headers)
        print (request.json)
        if request.json != {}:
            webhook.handle_event(request.remote_addr, request.json)
        else:
            print("skipping - empty")
    return ("OK")

# Run ChatOps REST Endpoint (Flask HTTP)
if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=4999, debug=True, ssl_context='adhoc')
    #flask_app.run(host='0.0.0.0', port=3999, debug=True)

