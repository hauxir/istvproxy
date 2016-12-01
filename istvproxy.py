#!/usr/bin/python
import argparse

import requests
from flask import Flask, Response, request, render_template, jsonify
from flask_cors import CORS

from channelsources.ruv import RUVChannels
from channelsources.oz import OZChannels
from channelsources.channelsource import USER_AGENT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Proxy for OZ Live Channels.')
    parser.add_argument('--host', type=int, help='Host for the webserver')
    parser.add_argument('--port', type=int, help='Port for the webserver')
    parser.add_argument('--ozusername', type=str, help='Username for OZ')
    parser.add_argument('--ozpassword', type=str, help='Password for OZ')
    args = parser.parse_args()
    port = args.port or 13377
    sources = {'ruv': RUVChannels()}
    if args.ozusername and args.ozpassword:
        sources['oz'] = OZChannels(args.ozusername, args.ozpassword)
    app = Flask(__name__, template_folder='.')
    CORS(app)

    @app.route('/crossdomain.xml')
    def crossdomain():
        return '''
         <?xml version='1.0'?>
           <!DOCTYPE cross-domain-policy SYSTEM
             'http://www.adobe.com/xml/dtds/cross-domain-policy.dtd'>
             <cross-domain-policy>
               <allow-access-from domain='*'/>
             </cross-domain-policy>
        '''

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/channels.json')
    def channels():
        host = args.host or request.host
        response_obj = {}
        for sourceslug, source in sources.iteritems():
            response_obj[sourceslug] = {}
            for channelslug in source.channels():
                response_obj[sourceslug][
                    channelslug] = 'http://%s/c/%s/%s.m3u8' % (host, sourceslug, channelslug)
        return jsonify(**response_obj)

    @app.route('/c/<string:sourceslug>/<string:channelslug>.m3u8')
    def channel(sourceslug, channelslug):
        host = args.host or request.host
        source = sources[sourceslug]
        playlist = source.get_channel_playlist(channelslug)
        playlist = playlist.replace(
            'http://', 'http://' + host + ('/v_pl/%s/?channel=' % sourceslug) + channelslug + '&url=http://')
        playlist = playlist.replace(
            'https://', 'http://' + host + ('/v_pl/%s/?channel=' % sourceslug) + channelslug + '&url=https://')
        return Response(playlist, content_type='application/vnd.apple.mpegURL')

    @app.route('/v_pl/<string:sourceslug>/')
    def video_playlist(sourceslug):
        host = args.host or request.host
        source = sources[sourceslug]
        url = request.args['url']
        channelslug = request.args['channel']
        req = requests.get(url, headers={'User-Agent': USER_AGENT})
        playlist = req.content
        playlist = source.preprocess_video_playlist(playlist, channelslug)
        playlist = playlist.replace(
            'http://', 'http://' + host + '/proxy/?url=http://')
        playlist = playlist.replace(
            'https://', 'http://' + host + '/proxy/?url=https://')
        return Response(playlist, content_type='application/vnd.apple.mpegURL')

    @app.route('/proxy/')
    def proxy():
        url = request.args['url']
        req = requests.get(
            url, headers={'User-Agent': USER_AGENT}, stream=True)
        return Response(req.iter_content(chunk_size=10 * 1024), content_type=req.headers['content-type'])

    app.run(host='0.0.0.0', port=port, threaded=True)
