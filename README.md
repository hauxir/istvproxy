# IS TV Proxy
Proxy for Icelandic TV Streams that strips out geoblocking and authentication.
## Requirements:
* Python 2.7.x
* Virtualenv
* [Docker](https://www.docker.com/)

## Installation:
You can choose between running the service in a virtual environment or run the service as a Docker image.

### Virtualenv:
```bash
virtualenv venv

source venv/bin/activate

pip install -r requirements.txt
```
```bash
python istvproxy.py --port <PORT>(optional, default=13377) --host <HOST>(optional) --ozusername <USERNAME>(optional) --ozpassword <PASSWORD>(optional) --siminndeviceid <DEVICE_ID>(optional)
```

HTTP server gets started at the chosen port. If the ozusername and ozpassword parameters are provided, it connects to Oz and adds the available channels for the user to the server. If not, only the RUV tv streams are added which don't require authentication.

### Docker:
Build and run the image.
```bash
docker build -t istvproxy:latest .

docker run -d -t -p 13377:13377 istvproxy
```

If you need to run the service on other host or port the -p flag needs to be edited. 

```bash
-p 0.0.0.0:13377:13377
```

Edit the Dockerfile if any additional flags are needed. If you need to change the host or port edit the following docker run command. 

```bash 
CMD ["istvproxy.py", "--ozusername", "<USERNAME>", "--ozpassword", "<PASSWORD>", "--siminndeviceid", "<DEVICE_ID>"]
``` 


## Usage:
This server needs to be run on a computer with an Icelandic IP Address because of geoblocking.

* http://host:port/ Gives you a web HLS player with a channel selector

* http://host:port/channels.json gives a JSON list of channel streams that can be used in other applications such as Kodi, Plex or Emby.

## Screenshots:
![ruv](https://cloud.githubusercontent.com/assets/2439255/20775985/bb414582-b755-11e6-96cb-8fdc8218b2a4.PNG)
![chanlist](https://cloud.githubusercontent.com/assets/2439255/20776010/dfc11432-b755-11e6-8967-03bbfeba6ef9.PNG)
