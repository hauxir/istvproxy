#!/usr/bin/python
import argparse
import datetime
import json

import requests
from flask import Flask, Response, request, render_template, jsonify
from flask_cors import CORS

OZ_CORE_URL = 'https://core.oz.com'
CLIENT_SECRET = "PHb7Aw7KZXGMYvgfEz"
CLIENT_ID = "ClubWebClient"

CHANNELS_URL = OZ_CORE_URL + '/users/me/channels'
CHANNEL_URL = OZ_CORE_URL + '/channels/%s/now?include=streamUrl,video,collection'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"


class OZClient(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.renew_token()
        self.channels = {}
        channels = json.loads(self.get(CHANNELS_URL))['data']
        for c in channels:
            slug = c['slug']
            self.channels[slug] = c['id']

    def token_expired(self):
        return (not self.access_token or
                not self.token_expires or
                self.token_expires < datetime.datetime.now()
                )

    def renew_token(self):
        request = requests.post(
            OZ_CORE_URL + '/oauth2/token',
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "password",
                "username": self.username,
                "password": self.password
            },
            headers={
                "User-Agent": USER_AGENT
            }
        )
        now = datetime.datetime.now()
        response = json.loads(request.content)
        try:
            self.access_token = response['access_token']
            self.token_expires = now + \
                datetime.timedelta(seconds=response['expires_in'] / 1000)
        except KeyError:
            raise Exception("Invalid login credentials!")

    def get(self, url):
        if not self.access_token or self.token_expired():
            self.renew_token()
        headers = {"Authorization": "Bearer " +
                   self.access_token, "User-Agent": USER_AGENT}
        request = requests.get(url,
                               headers=headers
                               )
        return request.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Proxy for OZ Live Channels.')
    parser.add_argument('--port', type=int, help='Port for the webserver')
    parser.add_argument('--username', type=str, help='Username for OZ', required=True)
    parser.add_argument('--password', type=str, help='Password for OZ', required=True)
    args = parser.parse_args()
    port = args.port or 13377
    client = OZClient(args.username, args.password)
    app = Flask(__name__, template_folder=".")
    CORS(app)

    @app.route('/crossdomain.xml')
    def crossdomain():
        return '''
         <?xml version="1.0"?>
           <!DOCTYPE cross-domain-policy SYSTEM
             "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
             <cross-domain-policy>
               <allow-access-from domain="*"/>
             </cross-domain-policy>
        '''

    def transform_playlist(channel_url):
        streamUrl = json.loads(client.get(channel_url))[
            'data'][0]['streamUrl']['url']
        playlist = requests.get(
            streamUrl, headers={"User-Agent": USER_AGENT}).content
        playlist = playlist.replace(
            "http://", "http://" + request.host + "/ch_pl/?url=http://")
        playlist = playlist.replace(
            "https://", "http://" + request.host + "/ch_pl/?url=https://")
        return playlist

    # ROUTES

    @app.route('/ch_pl/')
    def channel_playlist():
        url = request.args.get('url')
        req = requests.get(url, headers={"User-Agent": USER_AGENT})
        content = req.content
        content = content.replace(
            "http://", "http://" + request.host + "/proxy/?url=http://")
        content = content.replace(
            "https://", "http://" + request.host + "/proxy/?url=https://")
        return Response(content, content_type='application/vnd.apple.mpegURL')

    @app.route('/proxy/')
    def proxy():
        url = request.args.get('url')
        req = requests.get(
            url, headers={"User-Agent": USER_AGENT}, stream=True)
        return Response(req.iter_content(chunk_size=10 * 1024), content_type=req.headers['content-type'])

    @app.route('/c/<string:slug>.m3u8')
    def channel(slug):
        channel_id = client.channels[slug]
        return Response(transform_playlist(CHANNEL_URL % (channel_id)),
                        content_type='application/vnd.apple.mpegURL')

    @app.route('/channels.json')
    def channels():
        channels_obj = {}
        for k in client.channels.iterkeys():
            channels_obj[k] = 'http://%s/c/%s.m3u8' % (request.host, k)
        return jsonify(**channels_obj)

    @app.route('/')
    def index():
        return render_template("index.html")

    app.run(host='0.0.0.0', port=port, threaded=True)
