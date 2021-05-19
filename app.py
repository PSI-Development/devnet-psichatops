
import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import sys
import json
from dnac_manager import DNACManager
from webexteamssdk import WebexTeamsAPI

'''
os.environ["TEAMS_BOT_EMAIL"] = "psi-chatops@webex.bot"
os.environ["TEAMS_BOT_TOKEN"] = "NTA0MDczM2EtMzI0YS00MjgxLWEyNzQtMzNkMDRhMThhNWUxZjNhNzdiMWItZWZj_PF84_8992f87e-6618-4a3c-b512-1b3b50b6f6f3"
os.environ["TEAMS_BOT_URL"] = "http://222.165.234.92"
os.environ["TEAMS_BOT_APP_NAME"] = "psi-chatops"
'''
# Initialized managed entitities (e.g. DNAC, APIC, IOS, SolarWind)
dnac = DNACManager()

# Retrieve required details from environment variables
bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

# If any of the bot environment variables are missing, terminate the app
if not bot_email or not teams_token or not bot_url or not bot_app_name:
    print(
        "sample.py - Missing Environment Variable. Please see the 'Usage'"
        " section in the README."
    )
    if not bot_email:
        print("TEAMS_BOT_EMAIL")
    if not teams_token:
        print("TEAMS_BOT_TOKEN")
    if not bot_url:
        print("TEAMS_BOT_URL")
    if not bot_app_name:
        print("TEAMS_BOT_APP_NAME")
    sys.exit()

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
#   Note: the `approved_users=approved_users` line commented out and shown as reference
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    # approved_users=approved_users,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},
    ],
)

# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a psi-chatops bot. ".format(sender.firstName)
    response.markdown += "See what I can do by asking for **/help**."
    return response


# Create functions that will be linked to bot commands to add capabilities
# ------------------------------------------------------------------------

# A simple command that returns a basic string that will be sent as a reply
def hello_webex(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    return "Hello  Webex from Python  - {}".format(incoming_msg.text)

def device_list(incoming_msg):
    msg = dnac.device_list()
    print(msg)
    return msg

def local_file_upload():
    ROOM_ID = "Y2lzY29zcGFyazovL3VzL1JPT00vY2M1NDRkMjAtYjI0MC0xMWViLTk0ZDctMTlkZDEzYjU1YzYy"
    FILE_PATH = dnac.device_topology()
    api = WebexTeamsAPI(access_token=teams_token)
    if not os.path.isfile(FILE_PATH):
        print("ERROR: File {} does not exist.".format(FILE_PATH))
    abs_path = os.path.abspath(FILE_PATH)
    file_list = [abs_path]
    file_upload = api.messages.create(roomId=ROOM_ID, files=file_list)
    return file_upload

def device_topology(incoming_msg):
    file_upload= local_file_upload()
    return file_upload

def export_inventory(incoming_msg):
    return "Export Inventory - DNAC"

def cmd_run(incoming_msg):
    return "Command Runner - DNAC"

# Set the bot greeting.
bot.set_greeting(greeting)

# Add new commands to the bot.
bot.add_command("/hello-webex", "Say Hello to Webex Teams", hello_webex)
bot.add_command("/device-list", "DNAC Device Inventory List", device_list)
bot.add_command("/device-topology", "DNAC Physical Network Topology", device_topology)
bot.add_command("/export-inventory", "DNAC export Inventory Report", export_inventory)
bot.add_command("/cmd-run", "DNAC Command Runner Tools", cmd_run)

# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)