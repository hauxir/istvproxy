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
        self._channels = {x['slug']: x for x in json.loads(
            self._get(CHANNELS_URL))['data']}

    def _token_expired(self):
        return (
            not self._access_token or
            not self._token_expires or
            self._token_expires < datetime.datetime.now()
        )

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
            }
        )
        now = datetime.datetime.now()
        response = request.json()
        try:
            self._access_token = response['access_token']
            self._token_expires = now + \
                datetime.timedelta(seconds=response['expires_in'] / 1000)
        except KeyError:
            raise Exception('Invalid login credentials!')

    def _get(self, url):
        if not self._access_token or self._token_expired():
            self._renew_token()
        headers = {'Authorization': 'Bearer ' +
                   self._access_token, 'User-Agent': USER_AGENT}
        request = requests.get(url,
                               headers=headers
                               )
        return request.content

    def channels(self):
        return self._channels.iterkeys()

    def get_channel_playlist(self, name):
        c = self._channels[name]
        channel_url = CHANNEL_URL % c['id']
        streamUrl = json.loads(self._get(channel_url))[
            'data'][0]['streamUrl']['cdnUrl']
        content = requests.get(streamUrl, headers={'User-Agent': USER_AGENT}).content
        return content.replace("/live", OZ_PLAYLIST_URL + "/live")
