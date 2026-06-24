
import os
import re
import time
import requests

from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def download_brochure(model_name, url):
    print("Starting brochure extraction...")

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

    # -----------------------------
    # Step 1: Find all PDF links
    # -----------------------------
    pdf_links = re.findall(
    r'https?://[^"\'>\s]+\.pdf',
    page_source,
    re.IGNORECASE
)

    pdf_links += re.findall(
        r'/content/[^"\'>\s]+\.pdf',
        page_source,
        re.IGNORECASE
    )

    # Remove duplicates
    pdf_links = list(set(pdf_links))

    if not pdf_links:
        print("No PDF links found on the page.")
        return False

    # -----------------------------
    # Step 2: Keep only brochure/catalog PDFs
    # -----------------------------
    brochure_links = []

    for pdf_url in pdf_links:
        pdf_lower = pdf_url.lower()

        # keep brochure/catalog only
        if (
            ("brochure" in pdf_lower or "catalog" in pdf_lower)
            and
            ("accessories" not in pdf_lower)
        ):
            brochure_links.append(pdf_url)

    if not brochure_links:
        print("No brochure PDF found.")
        return False

    # -----------------------------
    # Step 3: Filter by model name
    # -----------------------------
    model_name = model_name.lower().strip()

    matched_links = []
    other_links = []

    for pdf_url in brochure_links:
        if model_name in pdf_url.lower():
            matched_links.append(pdf_url)
        else:
            other_links.append(pdf_url)

    # Try model-specific brochure links first
    final_links = matched_links + other_links

    print("\nAll brochure links found:")
    for link in final_links:
        # print(link)

        brochure_found = False
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # -----------------------------
    # Step 4: Download brochure
    # -----------------------------
    for pdf_url in final_links:
        full_pdf_url = urljoin(url, pdf_url)

        print("\nTrying brochure URL:")
        print(full_pdf_url)

        # remove query params from file name if present
        file_name = full_pdf_url.split("/")[-1].split("?")[0]

        try:
            response = requests.get(
                full_pdf_url,
                headers=headers,
                timeout=60,
                stream=True
            )

            if response.status_code == 200:
                file_path = os.path.join("Brochures", file_name)

                with open(file_path, "wb") as f:
                    # for chunk in response.iter_content(chunk_size=8192):
                    #     if chunk:
                            f.write(response.content)

                print("Downloaded:", file_name)
                brochure_found = True
                break

            else:
                print(
                    "Failed:",
                    file_name,
                    "Status Code:",
                    response.status_code
                )

        except Exception as e:
            print("Failed:", file_name)
            print(e)

    print("Ending brochure extraction")

    if not brochure_found:
        print("No brochure PDF downloaded.")

    return brochure_found


# Example usage
download_brochure(
    model_name="comet-ev",
    url="https://www.mgmotor.co.in/vehicles/comet-ev-electric-car-in-india"
)
