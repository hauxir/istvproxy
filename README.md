# IS TV Proxy
Proxy for Icelandic TV Streams that strips out geoblocking and authentication.

##Installation:

virtualenv venv

source venv/bin/activate

pip install -r requirements.txt

##Usage:

python istvproxy.py --ozusername <USERNAME>(optional) --ozpassword <PASSWORD>(optional) --port <PORT>(optional, default=13377) --host <HOST>(optional)

HTTP server gets started at the chosen port. If the ozusername and ozpassword parameters are provided, it connects to Oz and adds the available channels for the user to the server. If not, only the RUV tv streams are added which don't require authentication.

This server needs to be run on a computer with an Icelandic IP Address because of geoblocking.

/ Gives you a web HLS player with a channel selector

/channels.json for list of channel streams for use in other applications such as Kodi, Plex or Emby.
