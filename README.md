# devnet-psichatops

ChatOps is a supplementary application that offer network monitoring and automation through mobile collaboration platform, especially for day 2 operation.
It is a solution that enable integration between management and operation plane of network element with a collaboration tool.
ChatOps application consists of Webex Teams messaging platform, compute engine (a chatbot  API end point and network management engine that organized collection of data for network notification and suggested solution), and Endpoint API (Cisco and Solarwind API).

![image](https://user-images.githubusercontent.com/40487431/121645576-8b9f4500-cabe-11eb-9521-080ab56d4d93.png)

1. Webex Teams Apps.
A ChatBot: Network Monitoring System. Use pre defined “slash command” to ease fault, configuration and performance process
2. Compute Engine.
An ChatBot API Endpoint and Network Mgmt Engine that organized collection of data for network problem and step by step solutions
3. Endpoint API.
Using DNA-Center Rest API, NXOS API, IOS XE, Solarwinds API and ACI-toolkit to subtract information from Cisco Devices


# Making the App work

1. Create Bot

Creating a Webex Bot is super easy. If you're logged in, select My Webex Apps from the menu under your avatar at the top of this page, click "Create a New App" then "Create a Bot" to start the wizard.
https://developer.webex.com/my-apps/new/bot

You'll be asked to provide some basic information about the bot: bot name, bot username, and an icon.
The bot's access token will only be displayed once.

![image](https://user-images.githubusercontent.com/40487431/121646716-ca81ca80-cabf-11eb-9029-178108da2b11.png)


please take a note and for the following information will be need to get the Pass to work
TEAMS_BOT_EMAIL=bot-username
TEAMS_BOT_TOKEN=bot-access-token
TEAMS_BOT_APP_NAME=bot-display-name

2. Fill environment variable

Open file # docker-compose.yml
please fill below variable :

    environment:
      - TEAMS_BOT_EMAIL=bot-username
      - TEAMS_BOT_TOKEN=bot-access-token
      - TEAMS_BOT_URL=http://ipaddress for compute app running
      - TEAMS_BOT_APP_NAME=bot-display-name
      - DNAC_USERNAME=admin
      - DNAC_PASSWORD=P@ssw0rd
      - DNAC_CONN=https://dnacipaddress url
      - DNAC_IP=10.250.1.10
      - DNAC_VER=v1
      - TEAMS_ROOM_ID=room id or channel where the bot is add

3. Set Notification on DNAC

in the Cisco DNA Center GUI, click the Menu icon () and choose Systems > Settings > External > Destination.

![image](https://user-images.githubusercontent.com/40487431/121649656-fb173380-cac2-11eb-9579-6b9c21bfe4b6.png)


to subscribe an event click the Menu icon () and choose Platform > Developer Toolkit > Event 

![image](https://user-images.githubusercontent.com/40487431/121651262-9eb51380-cac4-11eb-95a5-83361c478ec2.png)


clik subrcibe and select the endpoint , for the notification messagess, we currently use in this code https://x.x.x.x:4999

![image](https://user-images.githubusercontent.com/40487431/121651434-d0c67580-cac4-11eb-98f8-82363bd84e07.png)

4. Running the Apps

for running the apps, you need your server to install docker compose and docker engine

https://docs.docker.com/compose/install/

after is done:
run docker-compose build & docker-compose up

![image](https://user-images.githubusercontent.com/40487431/121651992-69f58c00-cac5-11eb-8245-9557f522ce0a.png)



please see this video for our apps demo




