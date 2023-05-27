"""
Most SVG to Gif online generators are using magick's command
this was not sufficent for my use case due to the outputs not formatting correctly 
and scalability
"""


import glob
import contextlib
import re
import os 
import shutil
import sys

from PIL import Image
from bs4 import BeautifulSoup
from math import ceil
from selenium import webdriver


########################################################
# Constants
########################################################
if len(sys.argv) == 2:
	FILE_NAME = sys.argv[1]
	ABSOLUTE_FILE_PATH = os.getcwd()
elif len(sys.argv) == 1:
	ABSOLUTE_FILE_PATH = os.getcwd()
	FILE_NAME = "examples/test.svg"
else:
	raise Exception("Usage: python svg2gif.py <SVG_file>")
SCREENSHOTS_PER_SECOND = 11 # This arbitrary number worked but is not perfect

########################################################
# Helper functions
########################################################

def _clean_time_element(time):
	"""
	takes time paramter in an svg and converts it to seconds

	Args:
		time (str): time format from SVG i.e. 10s = 10 seconds
	Returns:
		(float): cleaned time
	"""
	if type(time) != str:
		raise Exception("did not pass str")
	elif "s" in time:
		return float(time.replace("s",""))
	elif "m" in time:
		return float(time.replace("m","")) * 60
	else:
		raise Exception("Time was not in seconds or minutes")


########################################################
# Beautiful soup parse to find total duration of SVG
########################################################

svg_file = open(FILE_NAME, 'r+')
soup = BeautifulSoup(svg_file,features="html.parser")



animation_timers = [_clean_time_element(time_element.get("dur"))
		 for time_element in soup.findAll('animate')]

total_time_animated = ceil(max(animation_timers)) 


########################################################
#                Create Temporary File
# Useful to provide more files to smooth the gif
########################################################
USE_TMP_PATH = False

if total_time_animated < 20:
	USE_TMP_PATH = True 

	file_text = (open(FILE_NAME).read())
	for animation_timer in animation_timers:
		if animation_timer % 1 == 0:
			file_text = file_text.replace(f"{int(animation_timer)}s",f"{int(animation_timer * 2)}s")
		else:
			file_text = file_text.replace(f"{animation_timer}s",f"{animation_timer * 2}s")

	with open(f"TMP_{FILE_NAME}", "w") as text_file:
		print(file_text, file=text_file)


########################################################
# Use Selenium to play the SVG file to play the file
# and capture screenshots of the SVG

## currently Magick doesn't support this conversion:
## https://github.com/ImageMagick/ImageMagick/discussions/2391
########################################################
if not os.path.exists("_screenshots"):
	os.makedirs("_screenshots")


driver = webdriver.Firefox()

# In Selenium you need the prefix file:/// to open a local file
if USE_TMP_PATH:
	driver.get(f"file:///{ABSOLUTE_FILE_PATH}/TMP_{FILE_NAME}")
else:
	driver.get(f"file:///{ABSOLUTE_FILE_PATH}/{FILE_NAME}")

if USE_TMP_PATH:
	total_screenshots = int(SCREENSHOTS_PER_SECOND * (total_time_animated *2))
else:
	total_screenshots = int(SCREENSHOTS_PER_SECOND * total_time_animated)
for i in range(total_screenshots):
	driver.get_screenshot_as_file(f"_screenshots/{i}.png")

driver.close()
driver.quit()


########################################################
# use PIL to combine the save PNG's to a GIF
########################################################


# filepaths
fp_in = "_screenshots/*.png"
fp_out = f'{FILE_NAME.replace(".svg",".gif")}'

# use exit stack to automatically close opened images
with contextlib.ExitStack() as stack:

    files = glob.glob(fp_in)
    files.sort(key=lambda f: int(re.sub('\D', '', f))) 

    # lazily load images
    imgs = (stack.enter_context(Image.open(f))
            for f in files)

    img = next(imgs)


    # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
    img.save(fp=fp_out, format='GIF', append_images=imgs,
             save_all=True,
             duration=(total_time_animated * 1000)/len(files) - 20, # the math here feels off because the resulting gif is too slow thus -10 is implemented
              loop=0)


########################################################
# Remove temporary directories
########################################################
if USE_TMP_PATH:
	os.remove(f"TMP_{FILE_NAME}")
shutil.rmtree("_screenshots")

#Optional delete of selenium logs
os.remove(f"geckodriver.log")
