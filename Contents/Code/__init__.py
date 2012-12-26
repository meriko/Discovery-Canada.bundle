####################################################################################################
TITLE = "Discovery Channel Canada"
ART = 'art-discovery.jpg'
ICON = 'icon-discovery.png'
NAMESPACES = {'ctv': 'http://www.ctv.ca'}

# iOS app video feed, must be parsed manually
# They say: "This bin contains all the videos that will be picked up by the iOS Discovery app. Show specific clips will be filtered using video/clip title field."
FEED_URL="http://www.discovery.ca/feeds/videos.aspx" 

# show listings as served for the iOS app (and assuming other things on their site)
SHOWS_URL="http://www.discovery.ca/feeds/shows.aspx"


# CTV Shows List:
# http://www.ctv.ca/feeds/iOS/ShowsList.aspx
# data.xpath("//Show/IsMobileEnabled[text()='true']/ancestor::Show")
# Name, Id, PipeShowTypeId(?)


# CTV All Videos:
# http://esi.ctv.ca/noesi/datafeedrss/bindata.aspx?bid=15291
# item/ctv:clipList/item/ctv:id (clipId) -> use this to look up m3u8, change master to index_7 , etc ...
# each <ctv:type>PSERVICE</ctv:type> seems to list a new show.  Not all are mobile enabled so not sure if they will work or not but worth looking into, there are a LOT more shows listed in this huge listing and it would make life easier if we just parse the one file the same as the other CTVGlobeMedia channels use



# Show Details:
# http://www.ctv.ca/feeds/iOS/ShowDetails.aspx?id=18564 (not sure which id this is, dunno if we need it or not anyway)
# 


##########################################################################################
def Start():
	Plugin.AddPrefixHandler("/video/discoveryca", MainMenu, TITLE, ICON, ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = TITLE
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	EpisodeObject.thumb = R(ICON)
	EpisodeObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR

##########################################################################################
def MainMenu():
	return GetShowList()

@route("/video/discoveryca/getshowlist")
def GetShowList():
 	oc = ObjectContainer()
	data = XML.ObjectFromURL(SHOWS_URL)
	shows = data.xpath("//item/includeInApp[text()='True']/ancestor::item")
	for show in shows:
		try:
			title=show.xpath("./title/text()", namespaces=NAMESPACES)[0]
			summary=show.xpath("./ctv:summary/text()", namespaces=NAMESPACES)[0]
			if Client.Platform == 'MacOSX' or Client.Platform == 'Windows' or Client.Platform == 'Linux':
				# header/banner style image
				thumb_url=show.xpath("./ctv:images/ctv:image[1]/url/text()", namespaces=NAMESPACES)[0]
			else:
				# square thumb style image
				thumb_url=show.xpath("./ctv:images/ctv:image[2]/url/text()", namespaces=NAMESPACES)[0]

			showTypeId=show.xpath("./showTypeId/text()")[0]
			oc.add(
				DirectoryObject(
					key=Callback(GetEpisodeList, showTypeId=showTypeId), 
					title=title,
					summary=summary, 
					thumb=Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
		except:
			# no showTypeId means we have no videos for this so let's pass
			pass

	return oc

##########################################################################################
@route("/video/discoveryca/getepisodelist")
def GetEpisodeList(showTypeId):
	oc = ObjectContainer()
	data = XML.ObjectFromURL(FEED_URL)
	shows = data.xpath('//item/ctv:videoType[text()="%s"]/ancestor::item' % showTypeId, namespaces=NAMESPACES)
	for ep in shows:
		try:
			title = ep.xpath("./title/text()")[0]
			clip = ep.xpath("./ctv:clipList/item[1]/ctv:id/text()", namespaces=NAMESPACES)[0]
			url = "http://watch.discoverychannel.ca/#clip"+clip #load the URL with the first clip # (URL service does the rest)
			thumb_url = ep.xpath("./imgUrl/text()")[0]
			summary = ep.xpath("./description/text()")[0]
			originally_available_at = Datetime.ParseDate(ep.xpath("./ctv:startDate/text()", namespaces=NAMESPACES)[0]).date()
			oc.add(VideoClipObject(
				title = title,
				url = url, 
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON), 
				summary = summary, 
				originally_available_at = originally_available_at
				)
			)
		except:
			# some shows don't have clipList items set, in that case they are no good to us
			pass
	if len(oc) < 1:
		return MessageContainer("Sorry", "There aren't any videos currently available for this show.")

	return oc
