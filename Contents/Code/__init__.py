TITLE = 'Discovery Channel Canada'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
NAMESPACES = {'ctv': 'http://www.ctv.ca'}

# iOS app video feed, must be parsed manually
# They say: "This bin contains all the videos that will be picked up by the iOS Discovery app. Show specific clips will be filtered using video/clip title field."
FEED_URL = 'http://www.discovery.ca/feeds/videos.aspx'

# show listings as served for the iOS app (and assuming other things on their site)
SHOWS_URL = 'http://www.discovery.ca/feeds/shows.aspx'

##########################################################################################
def Start():

	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = TITLE
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR

##########################################################################################
@handler('/video/discoveryca', TITLE, art=ART, thumb=ICON)
def MainMenu():

	return GetShowList()

##########################################################################################
@route("/video/discoveryca/getshowlist")
def GetShowList():

	oc = ObjectContainer()
	data = XML.ObjectFromURL(SHOWS_URL)
	shows = data.xpath("//item/includeInApp[text()='True']/ancestor::item")

	for show in shows:
		try:
			title = show.xpath("./title/text()", namespaces=NAMESPACES)[0]
			summary = show.xpath("./ctv:summary/text()", namespaces=NAMESPACES)[0]

			if Client.Platform == 'MacOSX' or Client.Platform == 'Windows' or Client.Platform == 'Linux':
				# header/banner style image
				thumb_url = show.xpath("./ctv:images/ctv:image[1]/url/text()", namespaces=NAMESPACES)[0]
			else:
				# square thumb style image
				thumb_url = show.xpath("./ctv:images/ctv:image[2]/url/text()", namespaces=NAMESPACES)[0]

			showTypeId = show.xpath("./showTypeId/text()")[0]

			oc.add(DirectoryObject(
				key = Callback(GetEpisodeList, title=title, showTypeId=showTypeId),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
			))
		except:
			# no showTypeId means we have no videos for this so let's pass
			pass

	return oc

##########################################################################################
@route("/video/discoveryca/getepisodelist")
def GetEpisodeList(title, showTypeId):

	oc = ObjectContainer(title2=title)
	data = XML.ObjectFromURL(FEED_URL)
	shows = data.xpath('//item/ctv:videoType[text()="%s"]/ancestor::item' % showTypeId, namespaces=NAMESPACES)

	for ep in shows:
		try:
			title = ep.xpath("./title/text()")[0]
			clip = ep.xpath("./ctv:clipList/item[1]/ctv:id/text()", namespaces=NAMESPACES)[0]
			url = "http://watch.discoverychannel.ca/#clip"+clip # load the URL with the first clip # (URL service does the rest)
			thumb_url = ep.xpath("./imgUrl/text()")[0]
			summary = ep.xpath("./description/text()")[0]
			originally_available_at = Datetime.ParseDate(ep.xpath("./ctv:startDate/text()", namespaces=NAMESPACES)[0]).date()

			oc.add(VideoClipObject(
				title = title,
				url = url, 
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON), 
				summary = summary, 
				originally_available_at = originally_available_at
			))
		except:
			# some shows don't have clipList items set, in that case they are no good to us
			pass

	if len(oc) < 1:
		return ObjectContainer(header="Sorry", message="There aren't any videos currently available for this show.")

	return oc
