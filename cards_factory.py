import json

# static / predefine device and command list
device_list = ["border-1.packet-systems.web.id", "edge-1.packet-systems.web.id", "fusion-1.packet-systems.web.id"]
device_uuid_dict = {"border-1.packet-systems.web.id":"26015FFE-E3D2-4E88-B1DD-EBFB8845045C",
                    "edge-1.packet-systems.web.id":"85DBE66D-2E62-46F3-B5FA-74F36CB64F8E",
                    "fusion-1.packet-systems.web.id":"E96D2871-F3C8-42EA-A77B-4015F8A2348F"}
cmd_list = ["show env", "show int desc", "show run"]

# template based on ms card format for selecting device and command
cmd_runner_template = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "PSI ChatOps",
                            "weight": "Lighter",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "DNAC Command Runner Dialog",
                            "wrap": True,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Please select device from list below and select command to be executed on the selected device:",
            "wrap": True
        },
        {
            "type": "Input.ChoiceSet",
            "choices": [
                {
                    "title": "Choice 1",
                    "value": "Choice 1"
                },
                {
                    "title": "Choice 2",
                    "value": "Choice 2"
                }
            ],
            "placeholder": "Select Device..",
            "id": "device_select"
        },
        {
            "type": "Input.ChoiceSet",
            "choices": [
                {
                    "title": "Choice 1",
                    "value": "Choice 1"
                },
                {
                    "title": "Choice 2",
                    "value": "Choice 2"
                }
            ],
            "placeholder": "Select command to be executed..",
            "id": "command_select"
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Submit",
                    "data": {
                        "subscribe": True
                    },
                    "style": "positive"
                }
            ],
            "spacing": "None",
            "horizontalAlignment": "Right",
            "separator": True
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
    }

# generate card with predefined device and cmd list based on card template
def generate_cmd_runner_card(template=cmd_runner_template, device_list=device_list, cmd_list=cmd_list):
    card = template
    device_select = [{"title": device, "value": device_uuid_dict.get(device)} for device in device_list]
    cmd_select = [{"title": cmd, "value": cmd} for cmd in cmd_list]
    card_body = card.get("body")
    for item in card_body:
        id = item.get("id")
        if id == "device_select" :
            item['choices'] = device_select
        elif id == "command_select" :
            item['choices'] = cmd_select
    card["body"] = card_body
    print("card result: {}".format(json.dumps(card)))
    return card