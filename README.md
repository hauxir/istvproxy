# IS TV Proxy
Proxy for Icelandic TV Streams that strips out geoblocking and authentication.
##Requirements:
* Python 2.7.x
* Virtualenv

##Installation:
```bash
virtualenv venv

source venv/bin/activate

pip install -r requirements.txt
```
##Usage:
```bash
python istvproxy.py --ozusername <USERNAME>(optional) --ozpassword <PASSWORD>(optional) --port <PORT>(optional, default=13377) --host <HOST>(optional)
```

HTTP server gets started at the chosen port. If the ozusername and ozpassword parameters are provided, it connects to Oz and adds the available channels for the user to the server. If not, only the RUV tv streams are added which don't require authentication.

This server needs to be run on a computer with an Icelandic IP Address because of geoblocking.

* http://host:port/ Gives you a web HLS player with a channel selector

* http://host:port//channels.json gives a JSON list of channel streams that can be used in other applications such as Kodi, Plex or Emby.
