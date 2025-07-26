🚖 Ola Fare Scraper Setup & Execution Manual (for Windows)

⸻

🧰 1. Prerequisites (Installations)

✅ 1.1 Install Python 3.10+
	•	Download: https://www.python.org/downloads/windows/
	•	During installation:
	•	✅ Check “Add Python to PATH”
	•	Click “Install Now”

✅ 1.2 Install Java Development Kit (JDK)
	•	Download JDK 11: https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html
	•	Install and then:
	•	Add JAVA_HOME to Environment Variables
	•	Path: C:\Program Files\Java\jdk-11.x.x
	•	Also add JAVA_HOME\bin to system Path

✅ 1.3 Install Android Studio (with Emulator)
	•	Download: https://developer.android.com/studio
	•	During setup:
	•	Install SDK tools and Emulator
	•	Create an emulator for Android version ≥ 10

✅ 1.4 Install Appium Server
	•	Download Appium Desktop (v1.22+): https://github.com/appium/appium-desktop/releases
	•	Run Appium → Start the server manually

✅ 1.5 Install Appium Inspector
	•	Download: https://github.com/appium/appium-inspector/releases
	•	Use it to inspect Ola app’s elements.

✅ 1.6 Install Node.js (for Appium)
	•	Download: https://nodejs.org/
	•	Install LTS version.

⸻

💻 2. Python Environment Setup

✅ 2.1 Create Virtual Environment

python -m venv venv
venv\Scripts\activate

✅ 2.2 Install Required Python Packages

pip install -r requirements.txt

Your requirements.txt should include:

Appium-Python-Client==2.11.1
requests
Pillow

etc


⸻

📲 3. Install Ola App on Emulator

✅ 3.1 Download Ola APK

Use a site like: https://apkpure.com or https://apkmirror.com

✅ 3.2 Install APK on Emulator

adb install path/to/ola.apk


⸻

🔍 4. Inspect Ola App with Appium Inspector

✅ 4.1 Connect Appium Inspector
	•	Start emulator
	•	Start Appium Desktop (port 4723)
	•	In Appium Inspector:
	•	Desired capabilities:

{
  "platformName": "Android",
  "deviceName": "emulator-5554",
  "appPackage": "com.olacabs.customer",
  "appActivity": "com.olacabs.customer.ui.SplashActivity",
  "noReset": true
}

	•	Click Start Session

✅ 4.2 Note UI Elements

Using Inspector, inspect and note resource IDs / xpaths for:
	•	Pickup location input
	•	Drop location input
	•	Ride types (Auto, Prime, Mini)
	•	Fare values
	•	Scroll containers (if needed)

⸻

🔧 5. Reconfigure Your Python Automation Script

✅ 5.1 Create a Selector Config

Create a Python file: ola_selectors.py

OLA_SELECTORS = {
    "pickup_input": "com.olacabs.customer:id/pickup_textbox",
    "drop_input": "com.olacabs.customer:id/drop_textbox",
    "search_result": "com.olacabs.customer:id/search_result_title",
    "fare_text": "com.olacabs.customer:id/fare_value",
    "ride_type_container": "com.olacabs.customer:id/ride_type_card",
    # Add more as inspected
}

✅ 5.2 Use It in Your Automation Script

In ola_scraper.py:

from ola_selectors import OLA_SELECTORS

driver.find_element(By.ID, OLA_SELECTORS["pickup_input"]).click()
# etc.


⸻

🛠 6. Run the Scraper

✅ 6.1 Start Appium Server

Manually or via command:

appium

✅ 6.2 Run the Script

python ola_scraper.py


⸻

🔁 7. Optional: Run Every 2 Minutes

✅ 7.1 Create a Loop in Script

In main.py:

import time
from ola_scraper import run_scraper

while True:
    run_scraper()
    time.sleep(120)

Or use Task Scheduler (Windows) to run main.py every 2 minutes.
