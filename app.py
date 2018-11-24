from bs4 import BeautifulSoup
import requests
import os
import shutil
from PIL import Image
import sys

#"https://mangakakalot.com/chapter/komisan_wa_komyushou_desu/chapter_"

link = sys.argv[2]
name = sys.argv[1]

#Current Chapter
try:
	current_chapter = int(open("stats.txt", "r").read())
except:
	with open("stats.txt", "w") as out:
		out.write("1")
	current_chapter = 1


#Directory
if not os.path.exists("manga"):
	os.mkdir("manga")

#Manga
manga = name

if not os.path.exists("manga/"+manga):
	os.mkdir("manga/"+manga)

#Getting Scans
for i in range(current_chapter, 173):
	url = link+str(i)
	
	trying = True
	while trying:
		try:
			req = requests.get(url, timeout=5)
			trying = False
		except:
			trying = True
	content = BeautifulSoup(req.content, 'html.parser')
	
	imgs = content.find("div", id="vungdoc")
	imgs = imgs.find_all("img")
	
	#Chapter Folder
	if not os.path.exists("manga/"+manga+"/chapter"+str(i)):
		os.mkdir("manga/"+manga+"/chapter"+str(i))
		
	print "Downloading Chapter "+str(i)
	
	index = 1
	img_list = []
	for img in imgs:
		img_link = img.get("src")
		
		#Download Image
		trying = True
		while trying:
			try:
				req = requests.get(img_link, stream=True, timeout=5)
				trying = False
			except:
				trying = True
		with open("manga/"+manga+"/chapter"+str(i)+"/"+str(index)+".jpg", "wb") as out:
			shutil.copyfileobj(req.raw, out)
			img_list.append("manga/"+manga+"/chapter"+str(i)+"/"+str(index)+".jpg")
		print "Downloaded scan "+str(index)
		
		index += 1
	print "Downloaded Chapter "+str(i)
	print "Concatenating all scans"
	
	#Calculate 
	max_height = 0
	max_width  = 0
	for img in img_list:
		im = Image.open(img)
		w, h = im.size
		if max_width <= w :
			max_width = w
			
	for img in img_list:
		im = Image.open(img)
		w, h = im.size
		ratio = max_width/float(w)
		h = int((float(h)*float(ratio)))
		max_height += h
	#Creating the image with width and height
	print max_height
	final_image = Image.new("RGB", (max_width, max_height))
	y = 0
	for img in img_list:
		im = Image.open(img)
		w,h = im.size
		
		ratio = max_width/float(w)
		h = int((float(h)*float(ratio)))
		
		im = im.resize((max_width,h), Image.ANTIALIAS)
		final_image.paste(im, (0, y))
		#os.remove(img)
		y += h
	#os.rmdir("manga/"+manga+"/chapter"+str(i))
	final_image.save("manga/"+manga+"/chapter"+str(i)+".jpg")
		
	current_chapter += 1
	with open("stats.txt", "w") as out:
		out.write(str(current_chapter))
	
	#break