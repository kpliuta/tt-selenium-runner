from __future__ import annotations

import os
import platform
import sys
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


class TermuxGeckoDriverManager(GeckoDriverManager):
    """Corrects OS type detection for Termux on aarch64 devices and emulators."""

    def get_os_type(self) -> str:
        if platform.machine() == "aarch64":
            return "linux-aarch64"

        # fall back to linux64 when os_type contains None (emulator)
        os_type = super().get_os_type()
        if not os_type or "None" in str(os_type):
            return "linux64"
        return os_type


def main() -> None:
    target_url = os.environ.get("TARGET_URL", "https://example.com")
    mnt_output_dir = os.environ.get("MNT_OUTPUT_DIR")
    if not mnt_output_dir:
        print("Error: MNT_OUTPUT_DIR environment variable is not set", file=sys.stderr)
        sys.exit(1)
    output_dir = Path(mnt_output_dir)
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    firefox_options = Options()
    firefox_options.add_argument("--headless")

    try:
        driver = webdriver.Firefox(
            options=firefox_options,
            service=FirefoxService(TermuxGeckoDriverManager().install()),
        )
    except Exception as e:
        print(f"Failed to create driver: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        driver.get(target_url)

        current_url = driver.current_url
        print(f"Loaded: {current_url}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshots_dir / f"{timestamp}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")

        print(f"Page title: {driver.title}")
        print(f"Page loaded successfully: {target_url}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        driver.quit()
        sys.exit(1)

    driver.quit()

    sys.exit(0)


if __name__ == "__main__":
    main()
