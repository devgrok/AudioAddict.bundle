"""AudioAddict utility class."""

# pylint: disable=line-too-long, old-style-class, broad-except, too-many-instance-attributes

import random
import pprint


#################################################
# hack to make pyDev detect some of the types
import sys
from __builtin__ import globals, locals

if "Plugin" not in globals():
    from plexpluginstub.stubs import *
    sys.stderr.write("Imported stub code and shouldn't have\n")
#################################################


# Valid streaming services according to audioaddict.com.
validServices = {
    'radiotunes': {'name':'RadioTunes.com', 'listen':'listen.radiotunes.com', 'image':'http://cdn.audioaddict.com/radiotunes.com/assets/android_app_banner/icon-c9f306a785072b952e1332f652164148.png'},
    'di':         {'name':'DI.fm', 'listen':'listen.di.fm', 'image':'http://cdn.audioaddict.com/di.fm/assets/android_app_banner/icon-36f5a36bcd7f7ee5c58bdc608a006d19.png'},
    'jazzradio':  {'name':'JazzRadio.com', 'listen':'listen.jazzradio.com', 'image':'http://cdn.audioaddict.com/jazzradio.com/assets/android_app_banner/icon-4b52d460d8aeb12041b313884379c5aa.png'},
    'rockradio':  {'name':'RockRadio.com', 'listen':'listen.rockradio.com', 'image':'http://cdn.audioaddict.com/rockradio.com/assets/android_app_banner/icon-84075273994773d881cecfa291621a42.png'},
    'classicalradio':  {'name':'ClassicalRadio.com', 'listen':'listen.classicradio.com', 'image':'http://cdn.audioaddict.com/classicalradio.com/assets/android_app_banner/icon-432772fa0d98d62c67155a6f99bec7df.png'}
}

# Each service proposes a selection of stream types.
# It's worth noting that public3 is the *only* common type.
validStreams = {
    'di': {
        'android_low':              {'codec': 'aac', 'bitrate':  40},
        'android':                  {'codec': 'aac', 'bitrate':  64},
        'android_high':             {'codec': 'mp3', 'bitrate':  96},
        'android_premium_low':      {'codec': 'aac', 'bitrate':  40},
        'android_premium_medium':   {'codec': 'aac', 'bitrate':  64},
        'android_premium':          {'codec': 'aac', 'bitrate': 128},
                'android_premium_high':     {'codec': 'mp3', 'bitrate': 320},
        'public1':                  {'codec': 'aac', 'bitrate':  64},
        'public2':                  {'codec': 'aac', 'bitrate':  40},
        'public3':                  {'codec': 'mp3', 'bitrate':  96},
        'premium_low':              {'codec': 'aac', 'bitrate':  40},
        'premium_medium':           {'codec': 'aac', 'bitrate':  64},
        'premium':                  {'codec': 'aac', 'bitrate': 128},
                'premium_high':             {'codec': 'mp3', 'bitrate': 320}
   },
    'radiotunes': {
        'appleapp_low':             {'codec': 'aac', 'bitrate':  40},
        'appleapp':                 {'codec': 'aac', 'bitrate':  64},
        'appleapp_high':            {'codec': 'mp3', 'bitrate':  96},
        'appleapp_premium_medium':  {'codec': 'aac', 'bitrate':  64},
        'appleapp_premium':         {'codec': 'aac', 'bitrate': 128},
                'appleapp_premium_high':    {'codec': 'mp3', 'bitrate': 320},
        'public1':                  {'codec': 'aac', 'bitrate':  40},
        'public3':                  {'codec': 'mp3', 'bitrate':  96},
        'public5':                  {'codec': 'wma', 'bitrate':  40},
        'premium_low':              {'codec': 'aac', 'bitrate':  40},
        'premium_medium':           {'codec': 'aac', 'bitrate':  64},
        'premium':                  {'codec': 'aac', 'bitrate': 128},
                'premium_high':             {'codec': 'mp3', 'bitrate': 320}
   },
    'jazzradio': {
        'appleapp_low':             {'codec': 'aac', 'bitrate':  40},
        'appleapp':                 {'codec': 'aac', 'bitrate':  64},
        'appleapp_premium_medium':  {'codec': 'aac', 'bitrate':  64},
        'appleapp_premium':         {'codec': 'aac', 'bitrate': 128},
        'appleapp_premium_high':    {'codec': 'mp3', 'bitrate': 256},
        'public1':                  {'codec': 'aac', 'bitrate':  40},
        'public3':                  {'codec': 'mp3', 'bitrate':  64},
        'premium_low':              {'codec': 'aac', 'bitrate':  40},
        'premium_medium':           {'codec': 'aac', 'bitrate':  64},
        'premium':                  {'codec': 'aac', 'bitrate': 128},
        'premium_high':             {'codec': 'mp3', 'bitrate': 256}
   },
    'rockradio': {
        'android_low':              {'codec': 'aac', 'bitrate':  40},
        'android':                  {'codec': 'aac', 'bitrate':  64},
        'android_premium_medium':   {'codec': 'aac', 'bitrate':  64},
        'android_premium':          {'codec': 'aac', 'bitrate': 128},
        'android_premium_high':     {'codec': 'mp3', 'bitrate': 256},
        'public3':                  {'codec': 'mp3', 'bitrate':  96},
   },
    'classicalradio': {
        'public1': {'codec': 'aac', 'bitrate': 40},
        'public3': {'codec': 'mp3', 'bitrate': 64},
        'premium_low': {'codec': 'aac', 'bitrate': 40},
        'premium_medium': {'codec': 'aac', 'bitrate': 64},
        'premium': {'codec': 'aac', 'bitrate': 128},
        'premium_high': {'codec': 'mp3', 'bitrate': 256}
    }
}


class AudioAddict(object):
    """AudioAddict utility class."""

    def __init__(self, service):
        """Init. You know."""

        self.p_listenkey = None

        self.p_stream_pref = 'public3'
        self.p_source_pref = None

        self.p_service = None
        self.p_service_config = {}
        self.p_streams = {}
        self.p_stream = None

        # All streaming services use a common API service.
        self.apihost = 'api.audioaddict.com'

        # The batch API endpoint requires a static dummy auth header.
        self.authheader = ['Authorization', 'Basic ZXBoZW1lcm9uOmRheWVpcGgwbmVAcHA=']
        self.batchinfo = {}

        self.service = service

    def get_apihost(self, url=True, ssl=False):
        """Get the AA API host; normally used as part of a URL."""

        if not url:
            return self.apihost

        obj = '://' + self.apihost + '/v1'

        if ssl:
            obj = 'https' + obj
        else:
            obj = 'http' + obj

        return obj

    @property
    def listenkey(self):
        """Get the listen_key; normally used as part of a URL."""

        if self.p_listenkey is None:
            return ''
        else:
            return '?listen_key=' + self.p_listenkey

    @listenkey.setter
    def listenkey(self, listenkey=None):
        """Set the listen_key."""

        self.p_listenkey = listenkey

    @property
    def service(self):
        """Get which service we're using."""

        return self.p_service

    @service.setter
    def service(self, serv):
        """Set which service we're using."""
        Log.Debug("inside setter")
        self.p_service = serv
        if serv is None:
            self.p_service_config = {}
            self.p_streams = {}
            return

        if not serv in validServices.keys():
            raise Exception('Invalid service')

        self.p_service_config = validServices[serv]
        self.p_streams = validStreams[serv]

    @property
    def service_config(self):
        # type: () -> dict
        """Get the config of the current service."""
        if self.p_service_config is None:
            raise Exception('Invalid service')
        return self.p_service_config

    @property
    def servicename(self):
        # type: str
        """Get the name of a given service."""

        return self.service_config['name']

    @property
    def serviceurl(self):
        """Get the service URL for the service we're using."""
        prefix = 'listen'
        url = 'http://' + prefix + '.' + self.servicename()
        url = url.lower()

        return url

    @property
    def streampref(self):
        """Get the preferred stream."""

        return self.p_stream_pref

    @streampref.setter
    def streampref(self, stream):
        """Set the preferred stream."""

        if self.service is None:
            raise Exception('Invalid service')
        if stream not in validStreams[self.service]:
            raise Exception('Invalid stream')

        self.p_stream_pref = stream
        self.p_stream = validStreams[self.service][stream]

    @property
    def streamdetails(self):
        """Get the details for a stream (these are static values)."""

        return self.p_stream

    @property
    def sourcepref(self):
        """Get the preferred source."""

        return self.p_source_pref

    @sourcepref.setter
    def sourcepref(self, source):
        """Set the preferred source."""

        self.p_source_pref = source

    def get_chanlist(self, refresh=False):
        """Get the master channel list."""

        try:
            return JSON.ObjectFromURL(self.serviceurl + '/' + self.streampref, cacheTime=CACHE_1HOUR)
        except Exception:
            raise

    def get_chaninfo(self, key):
        """Get the info for a particular channel."""

        chan_info = None
        for chan in self.get_chanlist():
            if chan['key'] == key:
                chan_info = chan.copy()
                break

        if chan_info is None:
            raise Exception('Invalid channel')

        return chan_info

    def get_streamurl(self, key):
        """Generate a streamable URL for a channel."""

        channel_url = self.serviceurl + '/' + self.streampref + '/' + key + self.listenkey
        sources = JSON.ObjectFromURL(channel_url, cacheTime=CACHE_1HOUR)
        stream_url = None

        # Look through the list for the preferred source.
        if self.sourcepref is not None:
            for source in sources:
                if self.sourcepref in source:
                    stream_url = source
                    break

        # If there is no preferred source or one was not found, pick at random.
        if stream_url is None:
            stream_url = (random.choice(sources))

        return stream_url

    def get_chanhist(self, key):
        """Get track history for a channel."""

        channel_info = self.getChannelInfo(key)
        channelId = channel_info['id']
        service_url = self.get_apihost() + '/' + self.service + '/' + 'track_history/channel/' + str(channelId)

        history = JSON.ObjectFromURL(service_url, cacheTime=CACHE_1HOUR)

        return history

    def get_nowplaying(self, key):
        """Get current track for a channel."""

        # Normally the current song is position 0, but if an advertisement
        # was played in the public stream, it will pollute the history -
        # in that case, we pick the track from position 1.

        channelHistory = self.get_chanhist(key)
        for track in channelHistory:
            if not 'ad' in track:
                return track

        return None

    def get_batchinfo(self, refresh=False):
        """Get the massive batch info blob."""

        if self.service in cached_services and len(cached_services[self.service]) and not refresh:
            return self.batchinfo

        url = self.get_apihost() + '/' + self.service + '/mobile/batch_update?stream_set_key=' + self.streampref
        if Prefs['debug']:
            Log.Debug('opening %s' % url)
        batch = JSON.ObjectFromURL(url, cacheTime=CACHE_1HOUR, headers=[self.authheader])

        # Only the "All" channel filter is interesting for now.
        for i in batch['channel_filters']:
            if i['name'] == 'All':
                self.batchinfo = i['channels']
                StoreChannels(self.service, i['channels'])
                return self.batchinfo

    def getChannelInfo(self, channel):
        if self.service not in cached_services:
            self.get_batchinfo(True)

        return GetCachedChannelInfo(self.service, channel)



####################################################################################################
cached_services = {}


def StoreChannels(service, channels):
    channelByName = {}

    for channel in channels:
        channelByName[channel['key']] = channel

    cached_services[service] = channelByName


def GetCachedChannelInfo(service, channel):
    if service in cached_services:
        if channel in cached_services[service]:
            return cached_services[service][channel]
    return None
