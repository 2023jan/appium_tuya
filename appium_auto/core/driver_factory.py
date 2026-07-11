from appium import webdriver
from appium.options.android import UiAutomator2Options

from appium_auto.core.environment import EnvironmentConfig


def create_android_driver(
    server_url: str, environment: EnvironmentConfig
) -> webdriver.Remote:
    phone = environment.phone
    options = UiAutomator2Options()
    options.load_capabilities(
        {
            "platformName": phone.platform_name,
            "appium:automationName": phone.automation_name,
            "appium:udid": phone.udid,
            "appium:noReset": True,
            "appium:fullReset": False,
            "appium:newCommandTimeout": 600,
            "appium:skipDeviceInitialization": phone.skip_device_initialization,
            "appium:skipServerInstallation": phone.skip_server_installation,
            "appium:disableWindowAnimation": False,
        }
    )
    return webdriver.Remote(server_url, options=options)
