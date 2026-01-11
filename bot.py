import re
from os import system
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# Import tambahan untuk Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

class Bot:

    def __init__(self):
        system("cls || clear")

        self._print_banner()
        self.driver = self._init_driver()
        self.services = self._init_services()

    def start(self):
        self.driver.get("https://zefoy.com")
        self._solve_captcha()

        # Page refresh 1
        sleep(2)
        self.driver.refresh()

        # Page refresh 2
        sleep(2)
        self.driver.refresh()

        self._check_services_status()
        self.driver.minimize_window()
        self._print_services_list()
        service = self._choose_service()
        video_url = self._choose_video_url()
        self._start_service(service, video_url)

    def _print_banner(self):
        print("+--------------------------------------------------------+")
        print("|                                                        |")
        print("|   Made by : Simon Farah                                |")
        print("|   Github  : https://github.com/simonfarah/tiktok-bot   |")
        print("|                                                        |")
        print("+--------------------------------------------------------+")
        print("\n")

    def _init_driver(self):
        try:
            print("[~] Loading Chrome driver, please wait...")

            options = ChromeOptions()
            # Menghilangkan deteksi bot otomatis (agar lebih aman di Zefoy)
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Pengaturan ukuran jendela
            options.add_argument("--window-size=800,700")

            # Otomatis download & setup chromedriver yang sesuai dengan versi Chrome Anda
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(options=options, service=service)

            print("[+] Chrome driver loaded successfully")
            print("\n")
            return driver
        except Exception as e:
            print("[x] Error loading driver: {}".format(e))
            exit(1)

    def _init_services(self):
        return {
            "followers": {"title": "Followers", "selector": "t-followers-button", "status": None},
            "hearts": {"title": "Hearts", "selector": "t-hearts-button", "status": None},
            "comments_hearts": {"title": "Comments Hearts", "selector": "t-chearts-button", "status": None},
            "views": {"title": "Views", "selector": "t-views-button", "status": None},
            "shares": {"title": "Shares", "selector": "t-shares-button", "status": None},
            "favorites": {"title": "Favorites", "selector": "t-favorites-button", "status": None},
            "live_stream": {"title": "Live Stream [VS+LIKES]", "selector": "t-livesteam-button", "status": None},
        }

    def _solve_captcha(self):
        self._wait_for_element(By.TAG_NAME, "input")
        print("[~] Please complete the captcha")
        # Menunggu sampai input captcha hilang atau halaman berganti (ditandai adanya link Youtube)
        self._wait_for_element(By.LINK_TEXT, "Youtube")
        print("[+] Captcha completed successfully\n")

    def _check_services_status(self):
        for service in self.services:
            selector = self.services[service]["selector"]
            try:
                element = self.driver.find_element(By.CLASS_NAME, selector)
                if element.is_enabled():
                    self.services[service]["status"] = "[WORKING]"
                else:
                    self.services[service]["status"] = "[OFFLINE]"
            except NoSuchElementException:
                self.services[service]["status"] = "[OFFLINE]"

    def _print_services_list(self):
        for index, service in enumerate(self.services):
            title = self.services[service]["title"]
            status = self.services[service]["status"]
            print("[{}] {}".format(str(index + 1), title).ljust(30), status)
        print("\n")

    def _choose_service(self):
        while True:
            try:
                choice = int(input("[~] Choose an option : "))
            except ValueError:
                print("[!] Invalid input format.\n")
                continue

            if choice in range(1, 8):
                key = list(self.services.keys())[choice - 1]
                if self.services[key]["status"] == "[OFFLINE]":
                    print("[!] Service is offline. Choose another...\n")
                    continue
                print("[+] You have chosen {}\n".format(self.services[key]["title"]))
                break
            else:
                print("[!] No service found with this number\n")
        return key

    def _choose_video_url(self):
        video_url = input("[~] Video URL : ")
        print("\n")
        return video_url

    def _start_service(self, service, video_url):
        self._wait_for_element(By.CLASS_NAME, self.services[service]["selector"]).click()

        container = self._wait_for_element(By.CSS_SELECTOR, "div.col-sm-5.col-xs-12.p-1.container:not(.nonec)")

        input_element = container.find_element(By.TAG_NAME, "input")
        input_element.clear()
        input_element.send_keys(video_url)

        while True:
            container.find_element(By.CSS_SELECTOR, "button.btn.btn-primary").click()
            sleep(3)

            try:
                container.find_element(By.CSS_SELECTOR, "button.btn.btn-dark").click()
                print("[~] {} sent successfully".format(self.services[service]["title"]))
            except NoSuchElementException:
                pass

            sleep(3)
            remaining_time = self._compute_remaining_time(container)

            if remaining_time is not None:
                minutes = remaining_time // 60
                seconds = remaining_time - minutes * 60
                print("[~] Sleeping for {} minutes {} seconds".format(minutes, seconds))
                sleep(remaining_time)
            print("\n")

    def _compute_remaining_time(self, container):
        try:
            element = container.find_element(By.CSS_SELECTOR, "span.br")
            text = element.text
            if "Please wait" in text:
                nums = re.findall(r"\d+", text)
                if len(nums) == 2:
                    return int(nums[0]) * 60 + int(nums[1]) + 5
                elif len(nums) == 1:
                    return int(nums[0]) + 5
            return None
        except NoSuchElementException:
            return None

    def _wait_for_element(self, by, value):
        while True:
            try:
                element = self.driver.find_element(by, value)
                return element
            except NoSuchElementException:
                sleep(1)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
