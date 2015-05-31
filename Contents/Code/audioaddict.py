"""AudioAddict utility class."""

# pylint: disable=line-too-long, old-style-class, broad-except, too-many-instance-attributes

import urllib2
import json
import random, sys
from __builtin__ import globals, vars

# try:
if "Plugin" not in globals():
    import plexpluginstub
    from plexpluginstub.stubs import *
    sys.stderr.write("Imported stub code and shouldn't have\n")
# except:
#     pass

class AudioAddict:
    """AudioAddict utility class."""


    # Valid streaming services according to audioaddict.com.
    validServices = {
        'radiotunes': {'name':'RadioTunes.com', 'listen':'listen.radiotunes.com', 'image':'http://www.audioaddict.com/assets/client/radiotunes-c01cd3335f7f9c7d8049a7883602f1ec.jpg'},
        'di':         {'name':'DI.fm', 'listen':'listen.di.fm', 'image':'http://www.audioaddict.com/assets/client/di-28348ac139cb6bd3144d869bcc149777.jpg'},
        'jazzradio':  {'name':'JazzRadio.com', 'listen':'listen.jazzradio.com', 'image':'http://www.audioaddict.com/assets/client/jazz-b0e8c70e6af84ed930329f4288b13c9d.jpg'},
        'rockradio':  {'name':'RockRadio.com', 'listen':'listen.rockradio.com', 'image':'http://www.audioaddict.com/assets/client/rock-89a0c28d5e422bff401993c77d324d7b.jpg'},
        'classicalradio':  {'name':'ClassicalRadio.com', 'listen':'listen.classicradio.com', 'image':''}
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
            'android_premium_high':     {'codec': 'mp3', 'bitrate': 256},
            'public1':                  {'codec': 'aac', 'bitrate':  64},
            'public2':                  {'codec': 'aac', 'bitrate':  40},
            'public3':                  {'codec': 'mp3', 'bitrate':  96},
            'premium_low':              {'codec': 'aac', 'bitrate':  40},
            'premium_medium':           {'codec': 'aac', 'bitrate':  64},
            'premium':                  {'codec': 'aac', 'bitrate': 128},
            'premium_high':             {'codec': 'mp3', 'bitrate': 256}
       },
        'radiotunes': {
            'appleapp_low':             {'codec': 'aac', 'bitrate':  40},
            'appleapp':                 {'codec': 'aac', 'bitrate':  64},
            'appleapp_high':            {'codec': 'mp3', 'bitrate':  96},
            'appleapp_premium_medium':  {'codec': 'aac', 'bitrate':  64},
            'appleapp_premium':         {'codec': 'aac', 'bitrate': 128},
            'appleapp_premium_high':    {'codec': 'mp3', 'bitrate': 256},
            'public1':                  {'codec': 'aac', 'bitrate':  40},
            'public3':                  {'codec': 'mp3', 'bitrate':  96},
            'public5':                  {'codec': 'wma', 'bitrate':  40},
            'premium_low':              {'codec': 'aac', 'bitrate':  40},
            'premium_medium':           {'codec': 'aac', 'bitrate':  64},
            'premium':                  {'codec': 'aac', 'bitrate': 128},
            'premium_high':             {'codec': 'mp3', 'bitrate': 256}
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

    def __init__(self):
        """Init. You know."""

#         Log.Debug("globals:     %s" % sorted(globals().keys()))
        self.listenkey = None

        self.p_streampref = 'public3'
        self.p_sourcepref = None

        self.p_service = None
        self.chanlist = []

        # All streaming services use a common API service.
        self.apihost = 'api.audioaddict.com'

        # The batch API endpoint requires a static dummy auth header.
        self.authheader = ['Authorization', 'Basic ZXBoZW1lcm9uOmRheWVpcGgwbmVAcHA=']
        self.batchinfo = {}

    def get_apihost(self, url=True, ssl=False):
        """Get the AA API host; normally used as part of a URL."""

        if url == False:
            return self.apihost

        obj = '://' + self.apihost + '/v1'

        if ssl == True:
            obj = 'https' + obj
        else:
            obj = 'http' + obj

        return obj

    def set_listenkey(self, listenkey=None):
        """Set the listen_key."""

        self.listenkey = listenkey

    def get_listenkey(self, url=True):
        """Get the listen_key; normally used as part of a URL."""

        if self.listenkey == None:
            return ''
        elif url == False:
            return self.listenkey
        else:
            return '?listen_key=' + self.listenkey

    @property
    def service(self):
        """Get which service we're using."""

        return self.p_service

    @service.setter
    def service(self, serv):
        """Set which service we're using."""

        if not serv in self.validServices.keys():
            raise Exception('Invalid service')

        self.p_service = serv

    def get_servicename(self, serv=None):
        """Get the name of a given service."""

        if serv == None:
            serv = self.service

        if not serv in self.validServices.keys():
            raise Exception('Invalid service')

        return self.validServices[serv]['name']

    def get_serviceurl(self, serv=None, prefix='listen'):
        """Get the service URL for the service we're using."""

        if serv == None:
            serv = self.service

        url = 'http://' + prefix + '.' + self.get_servicename(serv)
        url = url.lower()

        return url

    @property
    def streampref(self):
        """Get the preferred stream."""

        return self.p_streampref

    @streampref.setter
    def streampref(self, stream):
        """Set the preferred stream."""

        if not stream in self.validStreams[self.service]:
            raise Exception('Invalid stream')

        self.p_streampref = stream

    def get_streamdetails(self, service=None):
        """Get the details for a stream (these are static values)."""

        details = {}
        if service == None:
            service = self.service

        if self.streampref in self.validStreams[service]:
            details = self.validStreams[service][self.streampref]

        return details

    @property
    def sourcepref(self):
        """Get the preferred source."""

        return self.p_sourcepref

    @sourcepref.setter
    def sourcepref(self, source):
        """Set the preferred source."""

        self.p_sourcepref = source

    def get_chanlist(self, refresh=False):
        """Get the master channel list."""

        #if len(self.chanlist) < 1 or refresh == True:
        try:
#             data = urllib2.urlopen(self.get_serviceurl() + '/' + self.streampref)
#             self.chanlist = json.loads(data.read())
            self.chanlist = JSON.ObjectFromURL(self.get_serviceurl() + '/' + self.streampref, cacheTime=360)
        except Exception:
            raise

        return self.chanlist

    def get_chaninfo(self, key):
        """Get the info for a particular channel."""

        chaninfo = None

        for chan in self.get_chanlist():
            if chan['key'] == key:
                chaninfo = chan.copy()

        if chaninfo == None:
            raise Exception('Invalid channel')

        return chaninfo

    def get_streamurl(self, key):
        """Generate a streamable URL for a channel."""

        channelurl = self.get_serviceurl() + '/' + self.streampref + '/' + key + self.get_listenkey()

#         data = urllib2.urlopen(channelurl)
#         sources = json.loads(data.read())
        sources = JSON.ObjectFromURL(channelurl, cacheTime=360)

        streamurl = None

        # Look through the list for the preferred source.
        if not self.sourcepref == None:
            for source in sources:
                if self.sourcepref in source:
                    streamurl = source

        # If there is no preferred source or one was not found, pick at random.
        if streamurl == None:
            streamurl = (random.choice(sources))

        return streamurl

    def get_chanhist(self, key):
        """Get track history for a channel."""

        channelInfo = getChannelInfo(self.service, key)
        if channelInfo != None:
            #use cached data
            channelId = channelInfo['id']
        else:
            #fall back to old style
            channelId = self.get_chaninfo(key)['id']
        servurl = self.get_apihost() + '/' + self.service + '/' + 'track_history/channel/' + str(channelId)

        history = JSON.ObjectFromURL(servurl, cacheTime=360)

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

        if self.service in services and len(services[self.service]) and refresh == False:
            return self.batchinfo

        url = self.get_apihost() + '/' + self.service + '/mobile/batch_update?stream_set_key=' + self.streampref

        #req = urllib2.Request(url)
        #req.add_header(*self.authheader)
        if Prefs['debug']:
            Log.Debug('opening %s' % url)
        #data = urllib2.urlopen(req).read()
        #batch = json.loads(data)

        batch = JSON.ObjectFromURL(url, cacheTime=360, headers=[self.authheader])

        # Only the "All" channel filter is interesting for now.
        for i in batch['channel_filters']:
            if i['name'] == 'All':
                self.batchinfo = i['channels']
                storeChannels(self.service, i['channels'])
                return self.batchinfo

    def getChannelInfo(self, channel):
        if not self.service in services:
            self.get_batchinfo(True)

        return getChannelInfo(self.service, channel)

####################################################################################################
services = {}

def storeChannels(service, channels):
    channelByName = {}

    for channel in channels:
        channelByName[channel['key']] = channel

    services[service] = channelByName

def getChannelInfo(service, channel):
    if service in services:
        if channel in services[service]:
            return services[service][channel]
    return None