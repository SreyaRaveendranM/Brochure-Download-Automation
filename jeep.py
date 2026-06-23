import os
import time
import requests
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# Save folder
# -----------------------------
DOWNLOAD_DIR = str(Path.cwd() / "Jeep_Brochures")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -----------------------------
# Start page
# -----------------------------
START_URL = "https://www.jeep-india.com/new-compass/specifications.html"

# -----------------------------
# Common form data
# -----------------------------
FIRST_NAME = "Sreya"
LAST_NAME = "Raveendran"
EMAIL = "yourmail@example.com"
PHONE = "9876543210"
PINCODE = "682001"
SALUTATION = "Ms."


# -------------------------------------------------
# Step 1: open specs page -> click BROCHURE
# -------------------------------------------------
def open_brochure_page(driver, wait):
    driver.get(START_URL)
    time.sleep(5)
    print("Specifications page opened")

    # cookie popup
    try:
        cookie_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept All')]"))
        )
        cookie_btn.click()
        print("Cookie popup accepted")
    except:
        print("Cookie popup not found")

    # click BROCHURE link
    brochure_btn = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "BROCHURE"))
    )
    driver.execute_script("arguments[0].click();", brochure_btn)
    print("BROCHURE clicked")
    time.sleep(5)

    # if brochure page opens in new tab, switch
    all_tabs = driver.window_handles
    if len(all_tabs) > 1:
        driver.switch_to.window(all_tabs[-1])

    print("Reached brochure page:", driver.current_url)


# -------------------------------------------------
# Step 2: get all model checkboxes dynamically
# -------------------------------------------------
def get_all_model_cards(driver):
    model_elements = driver.find_elements(
        By.XPATH,
        "//input[starts-with(@id,'brochureCardCheckbox')]"
    )

    models = []

    for element in model_elements:
        model_id = element.get_attribute("id")

        # try to get a readable model name from nearby text
        model_name = model_id   # fallback name

        try:
            # go to parent card and get visible text
            card = element.find_element(By.XPATH, "./ancestor::*[self::label or self::div][1]")
            text = card.text.strip()

            if text:
                model_name = text.replace("\n", " ").strip()

        except:
            pass

        # clean file name friendly text
        safe_name = (
            model_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )

        models.append({
            "id": model_id,
            "name": safe_name
        })

    return models


# -------------------------------------------------
# Step 3: fill form and download one brochure
# -------------------------------------------------
def fill_form_and_download(driver, wait, model_id, model_name):
    print(f"\nStarting brochure for: {model_name}")

    # -----------------------------
    # select model checkbox
    # -----------------------------
    model_checkbox = wait.until(
        EC.presence_of_element_located((By.ID, model_id))
    )
    driver.execute_script("arguments[0].click();", model_checkbox)
    print(f"Selected model checkbox: {model_id}")
    time.sleep(2)

    # -----------------------------
    # select salutation
    # -----------------------------
    salutation = driver.find_element(By.ID, "salutation_dropdown")
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, salutation, SALUTATION)

    print("Salutation selected")
    time.sleep(1)

    # -----------------------------
    # fill form fields
    # -----------------------------
    driver.find_element(By.ID, "first_name").clear()
    driver.find_element(By.ID, "first_name").send_keys(FIRST_NAME)

    driver.find_element(By.ID, "last_name").clear()
    driver.find_element(By.ID, "last_name").send_keys(LAST_NAME)

    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(EMAIL)

    driver.find_element(By.ID, "phone").clear()
    driver.find_element(By.ID, "phone").send_keys(PHONE)

    driver.find_element(By.ID, "zip_code").clear()
    driver.find_element(By.ID, "zip_code").send_keys(PINCODE)

    print("Form filled")
    time.sleep(1)

    # -----------------------------
    # privacy checkbox
    # -----------------------------
    privacy_checkbox = driver.find_element(By.ID, "privacy_checkbox")
    driver.execute_script("arguments[0].click();", privacy_checkbox)
    print("Privacy checkbox selected")
    time.sleep(1)

    # -----------------------------
    # submit form
    # -----------------------------
    submit_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_btn.click()
    print("Submit clicked")
    time.sleep(5)

    # -----------------------------
    # click DOWNLOAD BROCHURE
    # -----------------------------
    download_btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'DOWNLOAD BROCHURE')]"
            )
        )
    )
    driver.execute_script("arguments[0].click();", download_btn)
    print("Download brochure clicked")
    time.sleep(5)

    # -----------------------------
    # switch to brochure tab if needed
    # -----------------------------
    all_tabs = driver.window_handles
    if len(all_tabs) > 1:
        driver.switch_to.window(all_tabs[-1])

    brochure_url = driver.current_url
    print("Brochure URL:", brochure_url)

    # -----------------------------
    # save PDF
    # -----------------------------
    file_path = os.path.join(DOWNLOAD_DIR, f"{model_name}_brochure.pdf")

    response = requests.get(brochure_url)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("Brochure downloaded successfully:", file_path)
    else:
        print("Failed to download brochure. Status code:", response.status_code)


# -------------------------------------------------
# Step 4: get list of models first
# -------------------------------------------------
def get_available_models():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        open_brochure_page(driver, wait)
        models = get_all_model_cards(driver)

        print("\nModels found on brochure page:")
        for m in models:
            print(m)

        return models

    finally:
        driver.quit()


# -------------------------------------------------
# Step 5: loop through each model one by one
# -------------------------------------------------
all_models = get_available_models()

for model in all_models:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        open_brochure_page(driver, wait)
        fill_form_and_download(driver, wait, model["id"], model["name"])
    except Exception as e:
        print(f"Error for {model['name']}: {e}")
    finally:
        driver.quit()