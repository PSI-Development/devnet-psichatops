import json

# static / predefine device and command list
device_list = ["device01", "device02", "device03"]
cmd_list = ["show env all", "show run"]

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
    device_select = [{"title": device, "value": device.replace(" ", "_")} for device in device_list]
    cmd_select = [{"title": cmd, "value": cmd.replace(" ", "_")} for cmd in cmd_list]
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