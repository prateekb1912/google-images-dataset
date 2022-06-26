import hashlib
import io
import os
import requests
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from PIL import Image

options = Options()
options.add_argument('-profile')
options.add_argument('/home/marvin/snap/firefox/common/.mozilla/firefox')

def fetch_image_urls(query, max_links, driver, sleep_time = 1):
    def scroll_to_end(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_time)
    
    # Build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    driver.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links:
        scroll_to_end(driver)


        # Get all thumbanil images
        thumbnail_res = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')

        num_results = len(thumbnail_res)

        print(f"Found: {num_results} search results. Extracting links from {results_start}:{num_results}")

        for img in thumbnail_res[results_start:num_results]:
            try:
                img.click()
                time.sleep(sleep_time)
            except Exception:
                continue
            
            actual_images = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')

            for actual_img in actual_images:
                if actual_img.get_attribute('src') and 'http' in actual_img.get_attribute('src'):
                    image_urls.add(actual_img.get_attribute('src'))

            image_count = len(image_urls)
            if len(image_urls) >= max_links:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        
        results_start = len(thumbnail_res)
    
    return image_urls


def persist_image(folder_path, url):
    try:
        image_content =requests.get(url).content
    
    except Exception as e:
        print(f"Error - could not download image - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10]+'.jpg')

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        
        print(f"SUCCESS - saved image as {file_path}")
    
    except Exception as e:
        print(f"Error - could not save image - {e}")


def search_and_download(search_term, dataset_path = './dataset', number_images = 5000):
    dataset_folder = os.path.join(dataset_path, "_".join(search_term.lower().split(' ')))

    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    with webdriver.Firefox(options=options) as driver:
        res = fetch_image_urls(search_term, number_images, driver, 0.1)

    for elem in res:
        persist_image(dataset_folder, elem)


time_bef = time.time()
search_and_download('toad', number_images=1000)
time_aft = time.time()

print("Total time to download 1000 images = ", str(time_aft-time_bef), " secs.")