#!/usr/bin/python

import os
import sys
import subprocess
import fileinput
import shutil

imgHeight = 500
thbHeight = 50
imgExts = [".jpg", ".JPG", ".png"]
thbSuffix = "_thumb"
resizeCmd = "convert -resize x%s %s %s"
thbCmd = "convert -thumbnail x%s %s %s"
identifyCmd = "identify %s"

indexPageAlbum = "index.html.album"
indexPageAbout = "index.html.about"
indexPage = "index.html"
about = "about"
aboutContent = "about.txt"
ignoreDirs = ["wp-content", "wp-includes", "images", "img", "."]
ignoreImg = ["logo.png", "me.jpg"]

imgsTemplate = '''
<div id="holder" style="width:%spx">
	%s
</div>
'''

imgTemplate = '''
<div class="singleitem">
	<img src="%s" width="%s" height="%s">
	<div class="imglink show"></div>
	<div class="postlink">
		<div class="imgexcerpt"><h6>Red</h6>Red</div>
	</div>
</div>
'''

thbTemplate = '''
<img src="%s" width="%s" height="%s">
'''

menuTemplate = '''
<li id="menu-item-70" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-70"><a href="../%s/index.html">%s</a></li>
'''

aboutTemplate='''
<p>%s</p>
'''

imagesToken = "IMAGES_TOKEN"

thumbsToken = "THUMBS_TOKEN"

menuToken = "MENU_TOKEN"

aboutToken = "ABOUT_TOKEN"

def width(img):
	cmd = identifyCmd % (img)
	res = subprocess.check_output(cmd, shell=True)
	size = res.split()[2]
	width = size.split('x')[0]
	return width
	
def processAlbum(img):
	# Thumbnail
	parts = os.path.splitext(img)
	thb = "%s%s%s" % (parts[0], thbSuffix, parts[1])
	cmd = thbCmd % (thbHeight, img, thb)
	res = subprocess.check_output(cmd, shell=True)

	# Resize
	cmd = resizeCmd % (imgHeight, img, img)
	res = subprocess.check_output(cmd, shell=True)

	widths = (int(width(img)), int(width(thb)))
	
	print "%s - %sx%s" % (img, widths[0], imgHeight)
	print "%s - %sx%s" % (thb, widths[1], thbHeight)

	return widths

def processAbout(menuTag):
		pagePath = os.path.join(about, indexPage)
		shutil.copyfile(indexPageAbout, pagePath)

		file = open(aboutContent)
		aboutTag = ""
		for para in file.readlines():
			aboutTag += aboutTemplate % para
		file.close()
		
		for line in fileinput.FileInput(pagePath,  inplace = 1):
		   line = line.replace(menuToken, menuTag)
		   line = line.replace(aboutToken, aboutTag)
		   print line

def processDir(dir):
	albums = []

	# Page is each subdir
	for root, subFolders, files in os.walk(dir):
		name = os.path.split(root)[-1]
		imgs = []
		
		# About page has no images and is processed specially
		if name == about:
			continue

		if name in ignoreDirs:
			continue

		# All imgs in the subdir is the content
		for file in files:
			if file in ignoreImg:
				continue
			ext = os.path.splitext(file)[1]
			if ext in imgExts:
				img = os.path.join(root,file)
				if thbSuffix not in img:
					imgs.append(img)

		# Ignore current directory
		if len(imgs) > 0 and not os.getcwd() == root:
			albums.append((name, imgs))
			
	# Generate menu first
	menuTag = ""
	for album in albums:
		menuTag += menuTemplate % (album[0], album[0][0].upper() + album[0][1:])

	# Process about page
	processAbout(menuTag)

	# Process albums
	for album in albums:

		imgWidths = 0
		thbWidths = 0

		imgTag = ""
		thbTag = ""

		print album[0]
		for img in album[1]:
			imgWidth, thbWidth = processAlbum(img)
			imgWidths += imgWidth
			thbWidths += thbWidth

			img = os.path.split(img)[-1]
			imgTag += imgTemplate % (img, imgWidth, imgHeight)

			parts = os.path.splitext(img)
			thb = "%s%s%s" % (parts[0], thbSuffix, parts[1])
			thbTag += thbTemplate % (thb, thbWidth, thbHeight)

		imgTag = imgsTemplate % (imgWidths, imgTag)

		pagePath = os.path.join(album[0], indexPage)
		shutil.copyfile(indexPageAlbum, pagePath)
		
		for line in fileinput.FileInput(pagePath,  inplace = 1):
		   line = line.replace(menuToken, menuTag)
		   line = line.replace(imagesToken, imgTag)
		   line = line.replace(thumbsToken, thbTag)
		   print line

		print thbWidths
		
processDir(os.getcwd())