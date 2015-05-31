"""Plex plugin for AudioAddict (sky.fm, di.fm, etc)."""
# pylint: disable=undefined-variable, relative-import, invalid-name, line-too-long

import sys

# print 'sys.path:\n\t' + '\n\t'.join(sys.path)

from __builtin__ import globals, vars


# try:
if "Plugin" not in globals():
    import plexpluginstub
    from plexpluginstub.stubs import *
    sys.stderr.write("Imported stub code and shouldn't have\n")
# except:
#     pass

# Utility class
#import Framework
from audioaddict import AudioAddict

# Plex
MUSIC_PREFIX = '/music/audioaddict'

NAME = 'AudioAddict'

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

####################################################################################################

def Start():
    """This is called when the plugin is loaded."""

    # Initialize the plugin
    Log.Info('[AudioAddict] Start() called. Identifier %s' % Plugin.Identifier)

    # trying different views (doesn't effect web)
    #menu=1
    Plugin.AddViewGroup('AudioAddict:Pictures', viewMode='Pictures', mediaType='items', summary=1)
    Plugin.AddViewGroup('AudioAddict:Showcase', viewMode='List', mediaType='items') #458810
    Plugin.AddViewGroup('AudioAddict:PanelStream', viewMode='PanelStream', mediaType='items', menu=1, summary=1) #
    Plugin.AddViewGroup('AudioAddict:InfoList', viewMode='InfoList', mediaType='items') # 65592

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    ObjectContainer.view_group = 'AudioAddict:Pictures'
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR

    Log.Info("**** ViewGroups %s" % Plugin.ViewGroups)

    if Prefs['debug'] and hasattr(JSON, '_encode_compactly'):
        setattr(JSON, '_encode_compactly', False)

# view_modes = {
#   "List": 65586, "InfoList": 65592, "MediaPreview": 458803, "Showcase": 458810, "Coverflow": 65591,
#   "PanelStream": 131124, "WallStream": 131125, "Songs": 65593, "Seasons": 65593, "Albums": 131123,
#   "Episodes": 65590,"ImageStream":458809,"Pictures":131123
# }

def ValidatePrefs():
    """This doesn't do anything useful yet."""
    pass


@handler(MUSIC_PREFIX, NAME, art=ART, thumb=ICON)
def MusicMainMenu():
    """The desired service is selected here."""

    oc = ObjectContainer()
    # look up services
    services = AudioAddict.validServices

    for serv in sorted(services, key=services.get):
        oc.add(DirectoryObject(
            key=Callback(GetChannels, serv=serv),
            title=services[serv]['name'],
            thumb=services[serv]['image']
        ))
    oc.view_group = 'AudioAddict:Pictures'
    return oc

def GetHelper(serv=None):
    """Instantiate the utility object, this is due to AudioAddict not being thread safe"""
    # Instantiate the utility object
    AA = AudioAddict()
    # Set some preferences. It really makes life easier if they're set.
    AA.set_listenkey(Prefs['listen_key'])
    if serv != None:
        AA.service = serv
        AA.streampref = Prefs['stream_pref_' + serv]
    AA.sourcepref = Prefs['source_pref']
    return AA

@route(MUSIC_PREFIX + '/service/{serv}')
def GetChannels(serv):
    """This produces the list of channels for a given service."""

    # Instantiate the utility object
    AA = GetHelper(serv)

    oc = ObjectContainer(title1=AA.get_servicename(serv), view_group = 'AudioAddict:Showcase')

    fmt = AA.get_streamdetails()['codec']
    bitrate = AA.get_streamdetails()['bitrate']

    for channel in AA.get_batchinfo(refresh=True):
        oc.add(CreateChannelObject(
            serv=serv,
            channel=channel['key'],
            title=channel['name'],
            summary=channel['description'],
            fmt=fmt,
            bitrate=bitrate
        ))

#     oc.view_group = "AudioAddict:PanelStream"
    oc.objects.sort(key=lambda obj: obj.title)
    return oc

@route(MUSIC_PREFIX + '/info/{serv}')
def channelInfo(serv):
    """ Purely for debugging, not needed by the channel """
    setattr(JSON, '_encode_compactly', False)

    AA = GetHelper(serv)

    batchinfo = AA.get_batchinfo(refresh=True)
    formatted = JSON.StringFromObject(batchinfo)
    return formatted


@route(MUSIC_PREFIX + '/channel/{serv}/{channel}')
def CreateChannelObject(
        serv,
        channel,
        title,
        summary,
        fmt,
        bitrate,
        include_container=False
    ):
    """Build yon streamable object, ye mighty."""

    AA = GetHelper(serv)
    channelInfo = AA.getChannelInfo(channel)
    if channelInfo == None:
        Log.Error("Missing channel details for %s/%s" % (serv, channel))
        return ObjectContainer(header=L('Error'), message=L('Missing channel data'))

    #art_url is the large image showed when in single channel view
    if channelInfo['banner_url'] != None:
        art_url = 'http:' + channelInfo['banner_url']
    else:
        art_url = 'http:' + channelInfo['asset_url']
    thumb = 'http:' + channelInfo['asset_url']

    if fmt == 'mp3':
        container = Container.MP3
        audio_codec = AudioCodec.MP3
    elif fmt == 'aac':
        container = Container.MP4
        audio_codec = AudioCodec.AAC

    # Display details for debugging purposes.
    debug_summary = []
    debug_summary.append(summary)
    if Prefs['debug']:
        debug_summary.append('[%s, %s]' % (fmt, bitrate))
        debug_summary.append('[%s]' % url)

    # depending on the detail level (channel listing or viewing one channel) the
    artistVal = None # maps to grandparentTitle in xml
    albumVal = None # maps to parentTitle in xml
    titleVal = title # maps to title in xml
    if include_container:
        # assume drill down detail so loookup currently streaming track
        AA = GetHelper(serv)
        Log.Debug("Looking up now playing")
        track = AA.get_nowplaying(channel)
        if track != None:
            playingTrack = " [" + track['track'] + "]"
            Log.Debug("Currently playing track %s" % playingTrack)
            artistVal = title
            albumVal = track['artist']
            titleVal = track['title']
#         if channelInfo != None:
#             debug_summary.append(JSON.StringFromObject(channelInfo))

    # need to create a stream manually so it doesn't create a video stream as well
    stream = AudioStreamObject(index=0, id=1, codec=audio_codec, channels=2)
    track_object = TrackObject(
        key=Callback(CreateChannelObject,
            serv=serv,
            channel=channel,
            title=title,
            summary=' '.join(debug_summary),
            fmt=fmt,
            bitrate=bitrate,
            include_container=True
            ),
        rating_key=Callback(PlayAudio, serv=serv, channel=channel, ext=container),
        artist=artistVal,
        title=titleVal,
        album=albumVal,
        summary=' '.join(debug_summary),
        thumb=Resource.ContentsOfURLWithFallback(thumb),
        art=art_url,
        items=[
            MediaObject(
                parts=[
                    #uses a callback for playing so the streaming url can be looked up on demand
                    PartObject(
                    key=Callback(PlayAudio, serv=serv, channel=channel, ext=container),
                    streams=[stream])
                ],
                container=container,
                audio_codec=audio_codec,
                bitrate=bitrate,
                audio_channels=2,
                #this was taken from some other plugin, need to verify if needed
                optimized_for_streaming=True if Client.Product not in ['Plex Web'] else False
            )
        ]
    )

    if include_container:
        #this is the single channel view
        return ObjectContainer(objects=[track_object], view_group='AudioAddict:InfoList', title2=title)
    else:
        return track_object


####################################################################################################
@route(MUSIC_PREFIX + '/play/{serv}/{channel}')
def PlayAudio(serv, channel):
    AA = GetHelper(serv)
    streamUrl = AA.get_streamurl(channel)
    Log.Debug("Using %s to stream" % streamUrl)
    return Redirect(streamUrl)
