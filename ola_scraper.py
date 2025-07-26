from appium import webdriver

desired_caps = {
    "platformName": "Android",
    "deviceName": "emulator-5560",
    "appPackage": "com.olacabs.customer",
    "appActivity": "com.olacabs.customer.ui.SplashActivity",
    "noReset": True,
    "automationName": "UiAutomator2"
}

driver = webdriver.Remote("http://localhost:4724/wd/hub", desired_caps)

# Perform your automation like setting pickup/drop, scraping fare, etc.