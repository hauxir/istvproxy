import requests

from channelsource import ChannelSource, USER_AGENT

RUV_ROOT_URL = 'http://ruvruv-live.hls.adaptive.level3.net/ruv'
STREAM_URL = RUV_ROOT_URL + '/%s/index.m3u8'


class RUVChannels(ChannelSource):

    def channels(self):
        return ['ruv', 'ruv2']

    def get_channel_playlist(self, name):
        playlist = requests.get(
            STREAM_URL % name, headers={'User-Agent': USER_AGENT}).content
        playlist = playlist.replace(
           'index', RUV_ROOT_URL + '/%s/index' % name
        )
        return playlist

    def preprocess_video_playlist(self, playlist, channel):
        playlist = playlist.replace(
           'stream', RUV_ROOT_URL + '/%s/index/stream' % channel
        )
        return playlist
