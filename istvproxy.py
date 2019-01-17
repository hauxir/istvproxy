#!/usr/bin/python
import argparse

import requests
import urllib3
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

from channelsources.channelsource import USER_AGENT
from channelsources.oz import OZChannels
from channelsources.ruv import RUVChannels
from channelsources.siminn import SiminnChannels

if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser(description='Proxy for OZ Live Channels.')
    parser.add_argument('--host', type=str, help='Host for the webserver')
    parser.add_argument('--port', type=int, help='Port for the webserver')
    parser.add_argument('--ozusername', type=str, help='Username for OZ')
    parser.add_argument('--ozpassword', type=str, help='Password for OZ')
    parser.add_argument(
        '--siminndeviceid', type=str, help='Device ID for Siminn Sjonvarp')
    args = parser.parse_args()
    port = args.port or 13377
    sources = {'ruv': RUVChannels()}
    if args.ozusername and args.ozpassword:
        sources['oz'] = OZChannels(args.ozusername, args.ozpassword)
    if args.siminndeviceid:
        sources['siminn'] = SiminnChannels(args.siminndeviceid)
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
                    channelslug] = 'http://%s/c/%s/%s.m3u8' % (host,
                                                               sourceslug,
                                                               channelslug)
        return jsonify(**response_obj)

    @app.route('/c/<string:sourceslug>/<string:channelslug>.m3u8')
    def channel(sourceslug, channelslug):
        host = args.host or request.host
        protocol = "https://" if request.url.startswith('https://') else "http://"
        source = sources[sourceslug]
        playlist = source.get_channel_playlist(channelslug)
        playlist = playlist.replace(
            'http://', protocol + host +
            ('/v_pl/%s/?channel=' % sourceslug) + channelslug + '&url=http://')
        playlist = playlist.replace('https://', protocol + host +
                                    ('/v_pl/%s/?channel=' % sourceslug) +
                                    channelslug + '&url=https://')
        return Response(playlist, content_type='application/vnd.apple.mpegURL')

    @app.route('/v_pl/<string:sourceslug>/')
    def video_playlist(sourceslug):
        host = args.host or request.host
        protocol = "https://" if request.url.startswith('https://') else "http://"
        source = sources[sourceslug]
        url = request.args['url']
        channelslug = request.args['channel']
        req = requests.get(url, headers={'User-Agent': USER_AGENT})
        playlist = req.content
        playlist = source.preprocess_video_playlist(playlist, channelslug)
        playlist = playlist.replace('http://',
                                    protocol + host + '/proxy/' + sourceslug +
                                    '/' + channelslug + '/?url=http://')
        playlist = playlist.replace('https://',
                                    protocol + host + '/proxy/' + sourceslug +
                                    '/' + channelslug + '/?url=https://')
        return Response(playlist, content_type='application/vnd.apple.mpegURL')

    @app.route('/proxy/<string:sourceslug>/<string:channelslug>/')
    def proxy(sourceslug, channelslug):
        source = sources[sourceslug]
        source.get_headers(channelslug)
        headers = {'User-Agent': USER_AGENT}
        headers.update(source.get_headers(channelslug))
        url = request.args['url']
        req = requests.get(url, headers=headers, stream=True, verify=False)
        return Response(
            req.iter_content(chunk_size=10 * 1024),
            content_type=req.headers.get('content-type'))

    app.run(host='0.0.0.0', port=port, threaded=True)
