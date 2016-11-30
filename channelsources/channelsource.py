USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"


class ChannelSource(object):

    def get_channel_playlist(self, name):
        raise Exception("CHANNEL NOT FOUND")

    def preprocess_video_playlist(self, playlist, channel):
        return playlist

    def channels(self):
        return []
