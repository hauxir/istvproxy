import requests

from channelsource import ChannelSource, USER_AGENT

RUV_ROOT_URL = 'http://ruvruv-live.hls.adaptive.level3.net/ruv'
RUV_STREAM_URL = RUV_ROOT_URL + '/ruv/index.m3u8'
RUV2_STREAM_URL = RUV_ROOT_URL + '/ruv2/index.m3u8'


class RUVChannels(ChannelSource):

    def channels(self):
        return ["ruv", "ruv2"]

    def get_channel_playlist(self, name):
        if name == "ruv":
            url = RUV_STREAM_URL
        elif name == "ruv2":
            url = RUV2_STREAM_URL
        playlist = requests.get(
            url, headers={"User-Agent": USER_AGENT}).content
        if name == "ruv":
            playlist = playlist.replace(
                "index", RUV_ROOT_URL + "/ruv/index"
            )
        elif name == "ruv2":
            playlist = playlist.replace(
                "index", RUV_ROOT_URL + "/ruv2/index"
            )
        return playlist

    def preprocess_video_playlist(self, playlist, channel):
        if channel == "ruv":
            playlist = playlist.replace(
                "stream", RUV_ROOT_URL + "/ruv/index/stream"
            )
        elif channel == "ruv2":
            playlist = playlist.replace(
                "stream", RUV_ROOT_URL + "/ruv2/index/stream"
            )
        return playlist
