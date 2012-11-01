####################################################################################################
TITLE = "Discovery Channel Canada"
ART = 'art-discovery.jpg'
ICON = 'icon-discovery.png'
CLIP_LOOKUP	= 'http://watch.discoverychannel.ca/AJAX/ClipLookup.aspx?episodeid=%s'
###################################################################################################
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

	#HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():
	oc = ObjectContainer()
	data = HTML.ElementFromURL("http://watch.discoverychannel.ca/AJAX/VideoLibraryWithFrame.aspx")

	for show in data.xpath("//a"):
		title = show.xpath("./text()")[0].strip()
		url = show.xpath("./@href")[0]
		oc.add(DirectoryObject(key=Callback(GetVideoList,url=url,title2=title), title=title, thumb=R(ICON)))
	return oc

####################################################################################################
def GetVideoList(url, title2 = "Shows"):
	oc = ObjectContainer(title2 = title2)
	data = HTML.ElementFromURL(url)
	found = False
	
	# first try for directly playable clips - ("//a[@title='Play'][contains(@href,'#clip')]/@href")
	# this will be handled before here and by URL service
# 	try:
# 		if data.xpath("//a[@title='Play'][contains(@href,'#clip')]"):
# 			title = show.xpath("./text()")
# 			url = show.xpath("./@href")
# 			oc.add(DirectoryObject(key=Callback(GetVideoList,url=url), title=title))
# 			
# 	except: pass
	
	# then try for episode titles
	try:
		for show in data.xpath("//a[@class='EpisodeTitle']/ancestor::li"):
			title = show.xpath(".//a[@class='EpisodeTitle']/text()")[0].strip()
			url = show.xpath(".//a[@class='EpisodeTitle']/@href")[0]
			try:
				description = show.xpath(".//dd[@class='Description']/text()")[0]
			except:
				description = ""
			try:
				thumb_url = show.xpath(".//dd[@class='Thumbnail']//img/@src")[0].split(".jpg")[0]+".jpg" # this is the nicest way to filter out all of their extra stuff for resizing which can be different at times
			except:
				thumb_url = ""
				
			oc.add(
				VideoClipObject(
					url=url, 
					title=title,
					summary=description, 
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
			found = True
		Log.Debug("Found Episode Titles")

	except: 
		Log.Debug("No Episode Titles, found, passing")
		pass
	
	# then try for Season links
	if not found:
		Log.Debug("Looking for Seasons")
		try:
			for show in data.xpath("//div[@id='Level2']//li/a"):
				title = show.xpath("./text()")[0].strip()
				url = show.xpath("./@href")[0]
				oc.add(DirectoryObject(key=Callback(GetVideoList,url=url,title2=title2+" : "+title), title=title, thumb=R(ICON)))
				found = True
		
		except: pass	
	
	# if we land here we got nothin'
	
	
	return oc