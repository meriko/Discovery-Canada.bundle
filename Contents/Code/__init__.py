PREFIX = '/video/discoveryca'

TITLE = 'Discovery Channel Canada'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.discovery.ca'

API_BASE_URL = String.Decode('aHR0cDovL2NhcGkuOWM5bWVkaWEuY29tL2Rlc3RpbmF0aW9ucy9kaXNjb3Zlcnlfd2ViL3BsYXRmb3Jtcy9kZXNrdG9wLw==')
FEATURED_URL = API_BASE_URL + 'collections/155/contents?&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'
POPULAR_URL = API_BASE_URL + 'collections/3/contents?&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'
RECENT_URL = API_BASE_URL + 'collections/2/contents?&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'
LAST_CHANCE_URL = API_BASE_URL + 'collections/330/contents?&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'
SHOWS_URL = API_BASE_URL + 'collections/67/medias?&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'
EPISODES_URL = API_BASE_URL + 'medias/%s/contents?$sort=BroadcastDate&$order=desc&$include=[authentication,broadcastdate,broadcasttime,contentpackages,desc,episode,id,images,media,name,runtime,season,shortdesc,type]&Images.Type=thumbnail'


VIDEOS_PER_PAGE = 25

##########################################################################################
def Start():

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR

##########################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()
    
    if Client.Platform in ('Android'):
        oc.header = 'Not compatible'
        oc.message = 'This channel is not compatible with Android clients.'
    
    title = 'Featured'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Episodes,
                    title = title,
                    url = FEATURED_URL
                ),
            title = title
        )
    )
    
    title = 'Most Popular'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Episodes,
                    title = title,
                    url = POPULAR_URL
                ),
            title = title
        )
    )
    
    title = 'Most Recent'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Episodes,
                    title = title,
                    url = RECENT_URL
                ),
            title = title
        )
    )
    
    title = 'Last Chance'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Episodes,
                    title = title,
                    url = LAST_CHANCE_URL
                ),
            title = title
        )
    )
    
    title = 'All Shows'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Shows,
                    title = title
                ),
            title = title
        )
    )
    
    return oc
    
##########################################################################################
@route(PREFIX + '/Shows')
def Shows(title):
    oc = ObjectContainer(title2 = title)
    
    data = JSON.ObjectFromURL(SHOWS_URL)
    
    for show in data['Items']:
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Episodes,
                        title = show['Name'],
                        url = EPISODES_URL % show['Id']
                    ),
                title = show['Name'],
                summary = show['Desc'],
                thumb = Callback(GetImage, url = show['Images'][0]['Url'])
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + '/Episodes', offset = int)
def Episodes(title, url, offset = 0):
    oc = ObjectContainer(title2 = title)
    
    episodes_data = JSON.ObjectFromURL(url)
    
    videos = 0
    for episode in episodes_data['Items'][offset:]:
        try:
            if episode['Authentication']['Required']:
                continue
        except:
            pass

        oc.add(
            EpisodeObject(
                url = BASE_URL + '/Video?vid=%s' % episode['Id'],
                title = episode['Name'],
                summary = episode['Desc'],
                show = episode['Media']['Name'],
                index = episode['Episode'],
                season = episode['Season']['Number'],
                thumb = Callback(GetImage, url = episode['Images'][0]['Url']),
                art = Callback(GetImage, url = episode['Media']['Images'][0]['Url']),
                originally_available_at = Datetime.ParseDate(episode['BroadcastDate']).date(),
                duration = int(episode['ContentPackages'][0]['Duration'] * 1000)
            )
        )
        
        videos = videos + 1
        
        if videos >= VIDEOS_PER_PAGE and (len(episodes_data['Items']) - offset > 0):
            oc.add(
                NextPageObject(
                    key =
                        Callback(
                            Episodes,
                            title = title,
                            url = url,
                            offset = offset + VIDEOS_PER_PAGE
                        )
                )
            )
            
            return oc
    
    if len(oc) < 1:
        return ObjectContainer(header="Sorry", message="There aren't any videos currently available for this show.")
    else:
        return oc
        
##########################################################################################
@route(PREFIX + '/GetImage')
def GetImage(url):
    if url.startswith('http'):
        return HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    else:
        return url
