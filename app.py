from bs4 import BeautifulSoup
import requests
import os
import shutil
from PIL import Image
import threading
from proxy import Proxy
import sys

#Args:
#url
#file name
#starting chapter
#number of threads

#Proxies
proxy = Proxy()

#Args
#Url exemple "https://manganelo.com/chapter/read_nanatsu_no_taizai_manga_online_free/chapter_"
MANGA  = sys.argv[2]
URL = sys.argv[1]

# Thread Paramters
NMBR = sys.argv[4]
CHAPTERS = sys.argv[3]
INC = CHAPTERS/NMBR

def main(th):
	print "Started Thread " + str(th)

	#Current Chapter
	'''
	try:
		current_chapter = int(open("stats.txt", "r").read())
	except:
		with open("stats.txt", "w") as out:
			out.write("1")
		current_chapter = 1
	'''


	#Directory
	if not os.path.exists("manga"):
		os.mkdir("manga")

	#Manga
	manga = MANGA

	if not os.path.exists("manga/"+manga):
		os.mkdir("manga/"+manga)

	#Getting Scans
	for i in range(th*INC + 196, th*INC + INC + 1):
		#Check if already exists
		if os.path.isfile("manga/"+manga+"/chapter"+str(i)+".jpg"):
			continue
		url = URL+str(i)
		trying = True
		while trying:
			try:
				req = requests.get(url)
				trying = False
			except:
				trying = True
		content = BeautifulSoup(req.content, 'html.parser')
		
		imgs = content.find("div", id="vungdoc")
		imgs = imgs.find_all("img")
		
		#Chapter Folder
		if not os.path.exists("manga/"+manga+"/chapter"+str(i)):
			os.mkdir("manga/"+manga+"/chapter"+str(i))
			
		#print "Downloading Chapter "+str(i)
		
		index = 1
		img_list = []
		for img in imgs:
			img_link = img.get("src")
			
			#Download Image
			trying = True
			while trying:
				try:
					req = requests.get(img_link, stream=True)
					trying = False
				except:
					trying = True
			with open("manga/"+manga+"/chapter"+str(i)+"/"+str(index)+".jpg", "wb") as out:
				shutil.copyfileobj(req.raw, out)
				img_list.append("manga/"+manga+"/chapter"+str(i)+"/"+str(index)+".jpg")
			#print "Downloaded scan "+str(index)
			
			index += 1
		print "Downloaded Chapter "+str(i)
		#print "Concatenating all scans"
		
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
		final_image = Image.new("RGB", (max_width, max_height))
		y = 0
		for img in img_list:
			im = Image.open(img)
			w,h = im.size
			
			ratio = max_width/float(w)
			h = int((float(h)*float(ratio)))
			
			im = im.resize((max_width,h), Image.ANTIALIAS)
			final_image.paste(im, (0, y))
			os.remove(img)
			y += h
		os.rmdir("manga/"+manga+"/chapter"+str(i))
		final_image.save("manga/"+manga+"/chapter"+str(i)+".jpg")
			
		#current_chapter += 1
		#with open("stats.txt", "w") as out:
		#	out.write(str(current_chapter))
		#break

threads = []

for i in range(0, NMBR):
	t = threading.Thread(target=main, args=(i,))
	t.start()
	threads.append(t)
for i in threads:
	i.join()
