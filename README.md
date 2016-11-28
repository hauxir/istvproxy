# oz-mediaproxy
Proxy for OZ streams that strips out Auth and Geoblocking

##Installation:

virtualenv venv

source venv/bin/activate

pip install -r requirements.txt

##Usage:

python oz_mediaproxy --username <USERNAME> --password <PASSWORD> --port <PORT>(optional)

HTTP server gets started at the chosen port

/ Gives you a web HLS player with a channel selector

/channels.json for list of channel streams for use in other applications
