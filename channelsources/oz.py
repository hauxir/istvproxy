import datetime
import json

import requests

from channelsource import ChannelSource, USER_AGENT

CLIENT_SECRET = 'PHb7Aw7KZXGMYvgfEz'
CLIENT_ID = 'ClubWebClient'
OZ_CORE_URL = 'https://core.oz.com'
OZ_PLAYLIST_URL = 'https://playlist.oz.com'
CHANNELS_URL = OZ_CORE_URL + '/users/me/channels'
CHANNEL_URL = OZ_CORE_URL + '/channels/%s/now?include=streamUrl,video,collection'


class OZChannels(ChannelSource):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._renew_token()
        self._channels = {
            x['slug']: x
            for x in json.loads(self._get(CHANNELS_URL))['data']
        }
        self._cookies = {}

    def _token_expired(self):
        return (not self._access_token or not self._token_expires
                or self._token_expires < datetime.datetime.now())

    def _renew_token(self):
        request = requests.post(
            OZ_CORE_URL + '/oauth2/token',
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'password',
                'username': self._username,
                'password': self._password
            },
            headers={
                'User-Agent': USER_AGENT
            })
        now = datetime.datetime.now()
        response = request.json()
        try:
            self._access_token = response['access_token']
            self._token_expires = now + \
                datetime.timedelta(seconds=response['expires_in'] / 1000)
        except KeyError:
            raise Exception('Invalid login credentials!')

    def _get_channel_json(self, name):
        c = self._channels[name]
        channel_url = CHANNEL_URL % c['id']
        return json.loads(self._get(channel_url))

    def _renew_cookie(self, channel, channel_json=None):
        if not channel_json:
            channel_json = self._get_channel_json(channel)
        streamUrl = channel_json['data'][0]['streamUrl']
        cookie_name, cookie_token, cookie_url = (streamUrl.get('cookieName'),
                                                 streamUrl.get('token'),
                                                 streamUrl.get('cookieUrl'))
        if cookie_name and cookie_token and cookie_url:
            cookie_response = requests.post(
                cookie_url,
                json=dict(name=str(cookie_name), value=str(cookie_token)),
                headers={
                    'content-type': 'application/json'
                })
            self._cookies[channel] = dict(
                key=cookie_name,
                value=cookie_response.cookies.get(cookie_name))

    def _get(self, url):
        if not self._access_token or self._token_expired():
            self._renew_token()
        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'User-Agent': USER_AGENT
        }
        request = requests.get(url, headers=headers)
        return request.content

    def channels(self):
        return self._channels.iterkeys()

    def get_channel_playlist(self, name):
        channel_json = self._get_channel_json(name)
        if not self._cookies.get(name):
            self._renew_cookie(name, channel_json=channel_json)
        streamUrl = channel_json['data'][0]['streamUrl']
        content = requests.get(
            streamUrl['cdnUrl'], headers={
                'User-Agent': USER_AGENT
            }).content
        return content.replace("/live", OZ_PLAYLIST_URL + "/live")

    def get_headers(self, channel):
        if not self._cookies.get(channel):
            self._renew_cookie(channel)
        if self._cookies.get(channel):
            cookie = self._cookies[channel]
            return {'Cookie': '{}={}'.format(cookie['key'], cookie['value'])}
        return {}
