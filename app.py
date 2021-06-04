
import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import sys
import json
from dnac_manager import DNACManager
from webexteamssdk import WebexTeamsAPI
from cards_factory import generate_cmd_runner_card
from requests_toolbelt.multipart.encoder import MultipartEncoder



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

print(bot_email, teams_token , bot_url, bot_app_name)

# If any of the bot environment variables are missing, terminate the app
if not bot_email or not teams_token or not bot_url or not bot_app_name:
    print(
        "app.py - Missing Environment Variable. Please see the 'Usage'"
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

def action_issue(incoming_msg):
    msg = dnac.action_issue()
    print(msg)
    return msg


def cmd_run(incoming_msg):
    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt="Card", attachment=generate_cmd_runner_card()
    )
    print(c)
    return ""

def handle_cards(api, incoming_msg):
    m = get_attachment_actions(incoming_msg["data"]["id"])
    print(m)
    rid = m.get('roomId')
    selected_device = m['inputs'].get('device_select')
    selected_command = m['inputs'].get('command_select')
    filename = dnac.cmd_run(selected_device, selected_command)
    print('filename: {}'.format(filename))
    if filename is not None:
        if send_message_with_local_file(rid, filename):
            return f'Please refer result in this attached file'
        else:
            return f'something went wrong while posting result'
    else:
        return f'something when wrong while accessing dnac/processing result'

def get_attachment_actions(attachmentid):
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'authorization': 'Bearer ' + teams_token
    }

    url = 'https://api.ciscospark.com/v1/attachment/actions/' + attachmentid
    response = requests.get(url, headers=headers)
    return response.json()

# Temporary function to send a message with a card attachment (not yet
# supported by webexteamssdk, but there are open PRs to add this
# functionality)
def create_message_with_attachment(rid, msgtxt, attachment):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + teams_token,
    }
    card = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": attachment
    }	
    url = "https://api.ciscospark.com/v1/messages"
    data = {"roomId": rid, "attachments": [card], "markdown": msgtxt}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def send_message_with_local_file(rid, filename, fileformat='text/plain'):
    m = MultipartEncoder({'roomId': rid,
                      'text': 'result attached',
                      'files': (filename, open(filename, 'rb'),
                      fileformat)})

    r = requests.post('https://webexapis.com/v1/messages', data=m,
                    headers={'authorization': 'Bearer ' + teams_token,
                    'content-type': m.content_type})
    print('result: {}'.format(r.text))
    if r.ok:
        return True
    else: 
        return False

# Set the bot greeting.
bot.set_greeting(greeting)

# Add new commands to the bot.
bot.add_command("/hello-webex", "Say Hello to Webex Teams", hello_webex)
bot.add_command("/device-list", "DNAC Device Inventory List", device_list)
bot.add_command("/device-topology", "DNAC Physical Network Topology", device_topology)
bot.add_command("/action", "DNAC Suggested Action", action_issue)
bot.add_command("/cmd-run", "DNAC Command Runner Tools", cmd_run)
bot.add_command('attachmentActions', '*', handle_cards)

# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
