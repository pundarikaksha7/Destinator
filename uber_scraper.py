from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import re 
import pytesseract
from PIL import Image
import cv2




def tap_by_adb(x, y):
    os.system(f"adb -s emulator-5554 shell input tap {x} {y}")

def swipe_up():
    os.system("adb -s emulator-5554 shell input swipe 500 1600 500 600 600")

def extract_uber_go_fare(driver):
    seen_texts = set()
    
    for _ in range(3):  # scroll 3 times to ensure all are loaded
        text_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        texts = [(el.text.strip(), el.get_attribute("bounds")) for el in text_elements if el.text.strip()]
        
        for idx, (text, bounds) in enumerate(texts):
            if text in seen_texts:
                continue
            seen_texts.add(text)
            
            # Match price text like ₹85.87
            if re.match(r"₹\s?\d+\.\d{2}", text):
                # Look 1–3 elements before for ride type
                for offset in range(1, 4):
                    if idx - offset >= 0:
                        name_candidate = texts[idx - offset][0].lower()
                        if "uber go" in name_candidate:
                            print("[INFO] Uber Go fare found:", text)
                            return text  # Only return this price
                        
        swipe_up()
        time.sleep(2)

    print("[WARN] Uber Go fare not found.")
    return None

def get_uber_fares(pickup_location: str, drop_location: str):
    caps = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "emulator-5554",
        "appium:appPackage": "com.ubercab",
        "appium:appActivity": "com.ubercab.presidio.app.core.root.RootActivity",
        "appium:noReset": True,
    }

    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote("http://localhost:4723", options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print("[STEP] Waiting for app to load...")
        # time.sleep(10)
        wait.until(EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "Enter pickup location")
        ))
        driver.save_screenshot("step1_loaded.png")

        # Click "Enter pickup location"
        pickup_button = wait.until(EC.element_to_be_clickable((
            AppiumBy.ACCESSIBILITY_ID, "Enter pickup location"
        )))
        pickup_button.click()
        # time.sleep(2)
        wait.until(EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Search in a different city")')
        ))
        driver.save_screenshot("step2_pickup_clicked.png")

        # Click "Search in a different city"
        different_city = wait.until(EC.element_to_be_clickable((
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("Search in a different city")'
        )))
        different_city.click()
        time.sleep(2)
        driver.save_screenshot("step3_different_city.png")

        # Tap on "Delhi NCR" using ADB
        time.sleep(2)
        tap_by_adb(540, 1447)
        driver.save_screenshot("step4_tapped_delhi_ncr.png")
        time.sleep(3)

        # Enter pickup location
        pickup_edit = wait.until(EC.element_to_be_clickable((
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("com.ubercab:id/ub__location_edit_search_pickup_edit")'
        )))
        pickup_edit.click()
        pickup_edit.clear()
        time.sleep(1)

        try:
            pickup_edit.send_keys(pickup_location)
        except:
            for ch in pickup_location:
                pickup_edit.send_keys(ch)
                time.sleep(0.2)

        time.sleep(3)
        tap_by_adb(600, 1230)  # Tap first pickup suggestion
        driver.save_screenshot("step5_pickup_selected.png")
        time.sleep(3)

        # Enter drop location (already focused — no click!)
        drop_edit = wait.until(EC.presence_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("com.ubercab:id/ub__location_edit_search_destination_edit")'
        )))
        drop_edit.clear()
        time.sleep(1)

        try:
            drop_edit.send_keys(drop_location)
        except:
            for ch in drop_location:
                drop_edit.send_keys(ch)
                time.sleep(0.2)

        time.sleep(3)
        tap_by_adb(600, 1230)  # Tap first drop suggestion
        driver.save_screenshot("step6_drop_selected.png")
        time.sleep(3)

        # Wait for fare options
        print("[STEP] Waiting for fare options to load...")
        time.sleep(6)
        driver.save_screenshot("step7_fares_visible.png")

        print("[STEP] Waiting for fare options to load and scrolling...")
        time.sleep(3)

        ride_fare=extract_uber_go_fare(driver)

        return ride_fare,None

    except TimeoutException as e:
        return [], f"[Timeout] UI element not found: {e}"
    except Exception as e:
        return [], f"[ERROR] Failed to complete workflow: {e}"
    finally:
        try:
            driver.terminate_app("com.ubercab")
            print(" Uber app closed successfully.")
        except Exception as e:
            print(f" Failed to close Uber app: {e}")
        finally:
            driver.quit()

# Example use
if __name__ == "__main__":
    pickup = "AIIMS Delhi"
    drop = "Connaught Place"

    fares,err= get_uber_fares(pickup, drop)
    if err:
        print(err)
    else:
        print("Fares found:", fares)