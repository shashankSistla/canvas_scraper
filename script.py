# Import necessary libraries
from __future__ import unicode_literals
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import youtube_dl
import os
import time
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from tqdm.auto import tqdm
import colorama

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--log-level=3')


username = input("Enter your Canvas username: ")
password = getpass("Enter your Canvas password: ")

# Enter the course code for the lectures you want to download
course_code = input("Enter the course code: ")

driver = webdriver.Chrome(options=chrome_options)
# Navigate to Canvas login page
driver.get("https://canvas.ucsd.edu/")

# Wait for page to load
wait = WebDriverWait(driver, 30)

# Enter username and password
username_input = wait.until(EC.presence_of_element_located((By.ID, "ssousername")))
username_input.send_keys(username)

password_input = wait.until(EC.presence_of_element_located((By.ID, "ssopassword")))
password_input.send_keys(password)

print("Please keep your phone ready for Duo 2FA!")

# Click login button
login_button = driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Wait for 2FA page to load
wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))


# Switch to 2FA iframe
driver.switch_to.frame("duo_iframe")

# Click "Send Me a Push" button
push_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Send Me a Push ']")))
push_button.click()
current_url = driver.current_url
# Wait for 60 seconds for user to grant access from phone
WebDriverWait(driver, 60).until(EC.url_changes(current_url))

print("2FA Granted!")

# Go to course page
driver.get(f"https://canvas.ucsd.edu/courses/{course_code}/external_tools/82")

print("Accessing lectures...")

iframe = WebDriverWait(driver, 10).until(
EC.presence_of_element_located((By.ID, "tool_content")))
driver.switch_to.frame(iframe)
thumbs =  driver.find_elements(By.CLASS_NAME, "thumb_wrapper")

media_tab = driver.find_element(By.ID, "media-tab")
media_tab.click()


last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load the page.
    time.sleep(2)

    # Calculate new scroll height and compare with last scroll height.
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:

        break

    last_height = new_height
    
#we have scrolled down fully

video_urls = []

item_info = []

gallery = driver.find_element(By.ID, "gallery")
galleryItems = driver.find_elements(By.CLASS_NAME, "galleryItem")
for galleryItem in galleryItems:
    thumbnail = galleryItem.find_element(By.CLASS_NAME, "thumbnail")
    thumb_wrapper = thumbnail.find_element(By.CLASS_NAME, "thumb_wrapper")
    title = thumb_wrapper.get_attribute("title")
    item_link = thumb_wrapper.find_element(By.CLASS_NAME, "item_link")
    link = item_link.get_attribute("href")
    obj = {
        'title': title,
        'link': link
    }
    item_info.append(obj)
    
    
for item in tqdm(item_info, desc ="Collecting metadata: "):
    thumb_url = item['link']
    try:
        driver.get(thumb_url)
        player_iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kplayer_ifp")))
        driver.switch_to.frame(player_iframe)
        # Parse the response
        # Press the play button
        driver.find_element(By.CLASS_NAME, "icon-play").click()
    except:
        print("err")
        continue
    
    time.sleep(2)
    JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
    network_requests = driver.execute_script(JS_get_network_requests)
    for n in network_requests:
        if "index.m3u8" in n["name"]:       
            item['url'] = n["name"]
driver.close()

colorama.init()

def show_progress_bar(d):
    if d['status'] == 'downloading':
        print(f'Downloading {d["filename"]}: {int(d["_percent_str"][:-1])}% complete')

def my_hook(d):
    if d['status'] == 'downloading':
        progress = round(float(d['downloaded_bytes'])/float(d['total_bytes'])*100,1)
        progress_str = f'downloading {progress}%'
        print(colorama.ansi.clear_line() + colorama.ansi.cursor_left() + progress_str)
    if d['status'] == 'finished':
        filename=d['filename']
        print(filename)



def download_videos(course_code, videos_list):
    for video in videos_list:
        if 'url' in video:
            url = video['url']
            title = video['title']
            file_path = f'{course_code}/{title}.mp4'

            # Check if the file already exists in the specified path
            if os.path.exists(file_path):
                print(f'Skipping {title} as it already exists')
                continue

            ydl_opts = {
            'outtmpl': file_path,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [my_hook],
            'no_warnings': True,
            "external_downloader_args": ['-loglevel', 'panic']
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

download_videos(str(course_code), item_info)
colorama.deinit()

# print(video_urls)
