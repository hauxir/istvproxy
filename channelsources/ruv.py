import re
import requests

from channelsource import ChannelSource, USER_AGENT


RUV_ROOT_URL = 'http://ruvruv-live.hls.adaptive.level3.net/ruv'


class RUVChannels(ChannelSource):

    def channels(self):
        return ['ruv', 'ruv2']

    def get_channel_playlist(self, name):
        json_response = requests.get("https://geo.spilari.ruv.is/channel/{}".format(name)).json()
        url = json_response["url"]
        self.root_url = url.replace("index.m3u8", "")
        playlist = requests.get(
            url, headers={'User-Agent': USER_AGENT}).content
        playlist = playlist.replace(
           'index/', str(self.root_url) + str('index/')
        )
        playlist = re.sub(r'(\S+\.m3u8)', self.root_url + r"\1", playlist)
        playlist = re.sub(r'URI="(\S+\.m3u8)"', 'URI="' + self.root_url + r'\1"', playlist)
        return playlist

    def preprocess_video_playlist(self, playlist, channel):
        playlist = re.sub(r'(stream.*\.(ts|vtt))', self.root_url + "/index/" + r'\1', playlist)
        playlist = re.sub(r'(\S+\.ts)', self.root_url + r"\1", playlist)
        return playlist
