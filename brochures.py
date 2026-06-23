import os
import re
import time
import requests

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def download_brochure(url):

    print("starting brochure extraction")
    # Create folder
    os.makedirs("Brochures", exist_ok=True)

    # Open browser
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.get(url)

    # Wait for page to load
    time.sleep(5)

    page_source = driver.page_source

    driver.quit()

    # Find full PDF URLs
    pdf_links = re.findall(
        r'https?://[^"\'>\s]+\.pdf',
        page_source,
        re.IGNORECASE
    )
    # print(pdf_links)

       # Find relative PDF URLs
    pdf_links += re.findall(
        r'/content/[^"\'>\s]+\.pdf',
        page_source,
        re.IGNORECASE
    )

    # Remove duplicates
    pdf_links = list(set(pdf_links))

    brochure_found = False

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for pdf_url in pdf_links:

        # Download only brochure PDFs
        if (
            "brochure" not in pdf_url.lower()
            and
            "catalog" not in pdf_url.lower()
             or
            "accessories" in pdf_url.lower()
        ):
            continue

        # Convert relative URL to full URL
        full_pdf_url = urljoin(url, pdf_url)

        print("\nBrochure Found:")
        print(full_pdf_url)

        file_name = full_pdf_url.split("/")[-1]

        try:

            response = requests.get(
                full_pdf_url,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:

                with open(
                    os.path.join("Brochures", file_name),
                    "wb"
                ) as f:
                    f.write(response.content)

                print("Downloaded:", file_name)

                brochure_found = True

            else:

                print(
                    "Failed:",
                    file_name,
                    "Status Code:",
                    response.status_code
                )

        except Exception as e:

            print(
                "Failed:",
                file_name
            )

            print(e)

    print("Ending brochure extraction")
    if not brochure_found:
        brochure_found = False
        print("No brochure PDF found.")

    return brochure_found
# download_brochure("https://www.kia.com/in/our-vehicles/carnival/specs.html")






