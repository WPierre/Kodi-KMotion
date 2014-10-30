# -*- coding: utf-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Nolife Online addon for XBMC
Authors:     gormux, DeusP
"""

import os, re, xbmcplugin, xbmcgui, xbmcaddon, urllib, urllib2, sys, cookielib, pickle, datetime
from BeautifulSoup import BeautifulSoup
import json, urllib2, HTMLParser
from collections import OrderedDict
"""
Class used as a C-struct to store video informations
"""
class videoInfo:
    pass

"""
Class used to report login error
"""
class loginExpcetion(Exception):
    pass

# Global variable definition
## Header for every log in this plugin
pluginLogHeader = "[XBMC_KMOTION] "

## Values for the mode parameter
MODE_LAST_SHOWS, MODE_CATEGORIES, MODE_SEARCH, MODE_SHOW_BY_URL, MODE_LINKS = range(5)
MODE_COMMUNITIES_LIST = 1
MODE_PLAYLISTS_LIST = 2
MODE_COMMUNITY_SHOW = 3
MODE_PLAYLIST_SHOW = 4
MODE_SEARCH = 5

settings  = xbmcaddon.Addon(id='plugin.video.kmotion')
kmotion_url       = 'http://www.kmotion.fr/api-box'
url = kmotion_url
name      = 'KMotion XBMC'
mode      = None
version   = settings.getAddonInfo('version')
useragent = "XBMC KMotion-plugin/" + version
language = settings.getLocalizedString
fanartimage = os.path.join(settings.getAddonInfo("path"), "kmotion_background.jpg")


def remove_html_tags(data):
    """Permits to remove all HTML tags
        
    This function removes the differents HTML tags of a string
    """
    page = re.compile(r'<.*?>')
    return page.sub('', data)

def requestinput():
    """Request input from user
        
    Uses the XBMC's keyboard to get a string
    """
    kbd = xbmc.Keyboard('default', 'heading', True)
    kbd.setDefault('')
    kbd.setHeading('Recherche')
    kbd.setHiddenInput(False)
    kbd.doModal()
    if (kbd.isConfirmed()):
        name_confirmed  = kbd.getText()
        return name_confirmed
    else:
        return 'Null'

def Error_message(message):
    dialog = xbmcgui.Dialog()
    dialog.ok(unicode(language(30023)), unicode(language(message)))

def api_call(ctx, cmd, mod):
    api_parameters = {'ctx':ctx, 'cmd':cmd, 'mod':mod}
    #api_parameters = json.loads('{"ctx":"'+ctx+'","cmd":"'+cmd+'","mod":{'+mod+'}}')
    requestHandler = urllib2.build_opener()
    post_data = {'request': json.dumps(api_parameters)}
    # Form data must be provided already urlencoded.
    postfields = urllib.urlencode(post_data)
    page = requestHandler.open(kmotion_url, postfields)
    body = page.read()
    #print body
    #r = requests.post('http://preprod.kmotion.fr/api-box',params=postfields)
    #print r.text
    #body = urllib.unquote(r.text)
    #print(body)
    h = HTMLParser.HTMLParser()
    body = h.unescape(body)
    #xbmc.log(msg=pluginLogHeader + "Request content :"+body,level=xbmc.LOGDEBUG)
    retour = json.loads(body, object_pairs_hook=OrderedDict)
    print json.dumps(retour, sort_keys=False, indent=4, separators=(',', ': '))
    return retour


def login():
    """Log into the KMotion website
        
    This method log the user into the website, checks credentials and return the current
    """
    
    xbmc.log(msg=pluginLogHeader + "Logging in",level=xbmc.LOGDEBUG)
    settings = xbmcaddon.Addon(id='plugin.video.kmotion')
    user     = settings.getSetting( "username" )
    pwd      = settings.getSetting( "password" )
    mod_params = {}
    mod_params['login'] = "login"
    mod_params['login_method'] = "FULL"
    mod_params['username'] = user
    mod_params['password'] = pwd

    try:
        retour = api_call("kmotion_api_login", "login",mod_params)
    except:
        settings.setSetting('user_id', "")
        settings.setSetting('token', "")

        err = xbmcgui.Dialog()
        err.ok(unicode(language(30023)), unicode(language(30017)), unicode(language(30018)))
        xbmc.executebuiltin('Addon.OpenSettings("plugin.video.kmotion")')
        return
    if retour['status'] != 200:
        xbmc.log(msg=pluginLogHeader + "Invalid username, aborting",level=xbmc.LOGFATAL)
        err = xbmcgui.Dialog()
        err.ok(unicode(language(30023)), unicode(language(30017)), unicode(language(30018)))
        settings.setSetting('user_id', "")
        settings.setSetting('token', "")
        raise loginExpcetion()
    else:
        xbmc.log(msg=pluginLogHeader + "User logged in",level=xbmc.LOGDEBUG)
        settings.setSetting("user_id", str(retour['content']['user_id']))
        settings.setSetting("token", retour['content']['kmotion_token'])
        settings.setSetting("static_cache_url", retour['content']['static_cache_url'])
        settings.setSetting("video_cache_url", retour['content']['video_cache_url'])

def getCommunities():
    xbmc.log(msg=pluginLogHeader + "Getting communities",level=xbmc.LOGDEBUG)
    settings = xbmcaddon.Addon(id='plugin.video.kmotion')
    mod_params = {}
    mod_params['kmotion_token'] = settings.getSetting("token")
    mod_params['type'] = "user"
    mod_params['domain'] = "ALL"
    mod_params['range'] = "0-1000"
    mod_params['query'] = settings.getSetting("user_id")
    mod_params['order_by'] = "NAME"
    mod_params['order_scheme'] = "ASC"

    try:
        retour = api_call("kmotion_api_communities","search",mod_params)
    except:
        Error_message(30030)
        return

    if retour['status'] != 200:
        xbmc.log(msg=pluginLogHeader + "Error while retrieving communities",level=xbmc.LOGFATAL)
        err = xbmcgui.Dialog()
        #TODO : change error text
        err.ok(unicode(language(30023)), unicode(language(30017)), unicode(language(30018)))
        raise loginExpcetion()
    else:
        xbmc.log(msg=pluginLogHeader + "User logged in",level=xbmc.LOGDEBUG)
        for (community_id, community) in retour['content'].items():
            add_dir(community['name'],community_id, MODE_COMMUNITY_SHOW, settings.getSetting('static_cache_url')+community['community_image']+"/w_m.jpg")

def getCommunityVideos(url):
    xbmc.log(msg=pluginLogHeader + "Getting videos for community "+url,level=xbmc.LOGDEBUG)
    mod_params = {}
    mod_params['kmotion_token'] = settings.getSetting("token")
    mod_params['type'] = "multi"
    mod_params['range'] = "0-1000"
    mod_params['query'] = {"community":url}
    mod_params['order_by'] = "NAME"
    mod_params['order_scheme'] = "ASC"

    try:
        retour = api_call("kmotion_api_video","search",mod_params)
        for (video_id, video) in retour['content'].items():
            addlinkKmotion(video)
    except:
        Error_message(30031)
        return
#http://video1.kmotion.fr/?video_id=9153&username=Pierre_&settings_id=15&key=081e82c2d4a4df6014df06ace593b2f3&action=get
#

def getPlaylists():
    xbmc.log(msg=pluginLogHeader + "Getting playlists",level=xbmc.LOGDEBUG)
    settings = xbmcaddon.Addon(id='plugin.video.kmotion')
    mod_params = {}
    mod_params['kmotion_token'] = settings.getSetting("token")
    mod_params['type'] = "multi"
    mod_params['domain'] = "ALL"
    mod_params['range'] = "0-1000"
    mod_params['user'] = settings.getSetting("user_id")
    mod_params['query'] = settings.getSetting("user_id")
    mod_params['order_by'] = "NAME"
    mod_params['order_scheme'] = "ASC"

    try:
        retour = api_call("kmotion_api_playlists","search",mod_params)
    except:
        Error_message(30032)
        return

    if retour['status'] != 200:
        xbmc.log(msg=pluginLogHeader + "Error while retrieving playlists",level=xbmc.LOGFATAL)
        err = xbmcgui.Dialog()
        #TODO : change error text
        err.ok(unicode(language(30023)), unicode(language(30017)), unicode(language(30018)))
        raise loginExpcetion()
    else:
        xbmc.log(msg=pluginLogHeader + "User logged in",level=xbmc.LOGDEBUG)
        for (playlist_id, playlist) in retour['content'].items():
            if playlist['playlist_image'] is None :
                image_url = ""
            else:
                image_url = settings.getSetting('static_cache_url')+playlist['playlist_image']+"/w_m.jpg"
            add_dir(playlist['name'],playlist_id, MODE_PLAYLIST_SHOW, image_url)

def getPlaylistVideos(url):
    xbmc.log(msg=pluginLogHeader + "Getting videos for playlist "+url,level=xbmc.LOGDEBUG)
    mod_params = {}
    mod_params['kmotion_token'] = settings.getSetting("token")
    mod_params['type'] = "multi"
    mod_params['range'] = "0-1000"
    mod_params['query'] = {"playlist":url}
    mod_params['order_by'] = "NAME"
    mod_params['order_scheme'] = "ASC"

    try:
        retour = api_call("kmotion_api_video","search",mod_params)
        for (video_id, video) in retour['content'].items():
            addlinkKmotion(video)
    except:
        Error_message(30033)
        return
#http://video1.kmotion.fr/?video_id=9153&username=Pierre_&settings_id=15&key=081e82c2d4a4df6014df06ace593b2f3&action=get
#


def initialIndex():
    """Creates initial index
    
    Create the initial menu with the right identification values for the add-on to know which option have been selected
    """
    add_dir(unicode(language(30014)), '', MODE_COMMUNITIES_LIST, '')
    add_dir(unicode(language(30015)), '', MODE_PLAYLISTS_LIST, '')
    add_dir(unicode(language(30016)), '', MODE_SEARCH, '')

def search():
    """Searches a video on  website
        
    This function allows to search for a show
    """

def get_params():
    """
    Get parameters
    """
    param       = []
    paramstring = sys.argv[2]

    if len(paramstring) >= 2:
        params        = sys.argv[2]
        cleanedparams = params.replace('?','')

        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]

        pairsofparams = cleanedparams.split('&')
        param = {}

        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def addlinkKmotion(video):
    video_url = settings.getSetting('video_cache_url')+"?video_id="+str(video['file_id'])+"&username="+settings.getSetting("username")
    video_url += "&settings_id="+str(video['settings_id'])+"&key="+str(video['key'])+"&action=get"
    xbmc.log(msg=pluginLogHeader + "Added video link "+video_url,level=xbmc.LOGDEBUG)
    if video['video_image'] is None:
            image_link = ''
    else:
        image_link = settings.getSetting("static_cache_url")+video['video_image']+"/w_l.jpg"
    duration = str(video['duration'])
    duration = duration[:5]
    temp_time=duration.split(":")
    duration = int(temp_time[0])*60+int(temp_time[1])
    xbmc.log(msg=pluginLogHeader + "Added video image "+image_link,level=xbmc.LOGDEBUG)
    #addlink(video['title'],video_url,image_link,duration,)
    rating = float(str(video['rating'])+".0")*2
    if "genre" in video['tags']:
        genre = int(video['tags']['genre'][0])
    else:
        genre = None


    if "year" in video['tags']:
        year = int(video['tags']['year'][0])
    else:
        year = None

    if "actor" in video['tags']:
        actor = video['tags']['actor']
    else:
        actor = None
    liz = xbmcgui.ListItem(video['title'],
                           iconImage=image_link,
                           thumbnailImage=image_link)
    #On met dans un try au cas où la skin ne supporterait pas
    try:
        liz.setProperty("fanart_image",image_link)
    except:
        fanartimage_temp = None
    liz.setInfo(
                 type="Video",
                 infoLabels={ "title": video['title'],
                              "playcount": int(0),
                              "plot": video['description'],
                              "rating":rating,
                              "year": year,
                              "genre": genre,
                              #"cast": actor
                            }
               )
    liz.addStreamInfo("video", { 'duration':duration })
    liz.setProperty("IsPlayable","true")
    liz.setProperty("mimetype","video/mp4")

    #xbmc.log(msg=pluginLogHeader + "Added video title "+video['title'],level=xbmc.LOGDEBUG)
    #xbmc.log(msg=pluginLogHeader + "Le handle utilise : " + sys.argv[1],level=xbmc.LOGDEBUG)
    ok  = xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]),
                                       url=video_url,
                                       listitem=liz,
                                       isFolder=False )
    return ok

def add_dir(name, url, mode, iconimage):
    """
    Adds a directory to the list
    """
    ok  = True
    
    # Hack to avoid incompatiblity of urllib with unicode string
    if isinstance(name, str):
        url = sys.argv[0]+"?url="+urllib.quote_plus(url)+\
            "&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    else:
        url = sys.argv[0]+"?url="+urllib.quote_plus(url)+\
        "&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("ascii", "ignore"))
    showid = url.split('?')[1].split('&')[0].split('=')[1]
    thumbnailimage = os.path.join(settings.getAddonInfo("path"), 'resources', 'images', showid + '.jpeg')
    if not iconimage == '':
        liz = xbmcgui.ListItem(name,
                               iconImage=iconimage,
                               thumbnailImage=iconimage)
    else:
        liz = xbmcgui.ListItem(name,
                               iconImage=thumbnailimage,
                               thumbnailImage=thumbnailimage)

    liz.setInfo( 
                 type="Video", 
                 infoLabels={ "Title": name } 
               )
    liz.setProperty('fanart_image', fanartimage)
    ok  = xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), 
                                       url=url, 
                                       listitem=liz, 
                                       isFolder=True )
    return ok

## Start of the add-on
xbmc.log(msg=pluginLogHeader + "-----------------------",level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "KMotion plugin main loop",level=xbmc.LOGDEBUG)
pluginHandle = int(sys.argv[1])

## Reading parameters given to the add-on
params = get_params()
xbmc.log(msg=pluginLogHeader + "Parameters read",level=xbmc.LOGDEBUG)

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    _id = int(params["id"])
except:
    _id = 0
xbmcplugin.setContent 	(pluginHandle,"movies")
xbmc.log(msg=pluginLogHeader + "requested mode : " + str(mode),level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "requested url : " + url,level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "requested id : " + str(_id),level=xbmc.LOGDEBUG)

requestHandler = urllib2.build_opener()



if settings.getSetting("username") == "":
     xbmc.executebuiltin('Addon.OpenSettings("plugin.video.kmotion")')
else:
    login()

    if settings.getSetting("token") != "":
        # Determining and executing action
        if( mode == None or url == None or len(url) < 1 ) and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Loading initial index",level=xbmc.LOGDEBUG)
            initialIndex()
        elif mode == MODE_COMMUNITIES_LIST and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Retrieving communities list",level=xbmc.LOGDEBUG)
            getCommunities()
        elif mode == MODE_COMMUNITY_SHOW and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Retrieving community video",level=xbmc.LOGDEBUG)
            getCommunityVideos(url)
        elif mode == MODE_PLAYLISTS_LIST and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Retrieving playlists list",level=xbmc.LOGDEBUG)
            getPlaylists()
        elif mode == MODE_PLAYLIST_SHOW and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Retrieving playlist video",level=xbmc.LOGDEBUG)
            getPlaylistVideos(url)
        elif mode == MODE_SEARCH and _id == 0:
            xbmc.log(msg=pluginLogHeader + "Starting a search",level=xbmc.LOGDEBUG)
            search()


#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
