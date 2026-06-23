import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By

def download_brochure1(url):
    print("starting parent")
    os.makedirs("brochures", exist_ok=True)

    # go to parent url
    p = urlparse(url)
    parent = f"{p.scheme}://{p.netloc}" + "/".join(p.path.rstrip("/").split("/")[:-1])

    driver = webdriver.Chrome()
    driver.get(parent)

    links = driver.find_elements(By.TAG_NAME, "a")

    for link in links:
        text = link.text.lower()
        href = link.get_attribute("href")

        if href and ".pdf" in href.lower() and "brochure" in text:
            file_name = os.path.basename(urlparse(href).path)
            pdf = requests.get(href)

            with open(f"brochures/{file_name}", "wb") as f:
                f.write(pdf.content)

            print("Downloaded:", file_name)
            driver.quit()
            return

    print("Brochure not found")
    driver.quit()
# download_brochure("https://www.hondacarindia.com/honda-city/tech-specs")