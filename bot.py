import re
from os import system
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# Import khusus Chrome
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

        # Page refresh untuk memastikan elemen termuat
        sleep(2)
        self.driver.refresh()
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
            
            # Perbaikan untuk Error 127 & Masalah Permission
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Agar tidak terdeteksi sebagai bot
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            options.add_argument("--window-size=800,700")

            # Menggunakan ChromeDriverManager untuk otomatisasi
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(options=options, service=service)

            # Bypass deteksi webdriver
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("[+] Chrome driver loaded successfully\n")
            return driver
        except Exception as e:
            print(f"[x] Error loading driver: {e}")
            print("[!] Pastikan Google Chrome sudah terinstal di komputer Anda.")
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
        print("[~] Please complete the captcha in the browser window")
        self._wait_for_element(By.TAG_NAME, "input")
        
        # Menunggu sampai user selesai captcha (halaman berubah dan muncul link Youtube)
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
                if 1 <= choice <= len(self.services):
                    key = list(self.services.keys())[choice - 1]
                    if self.services[key]["status"] == "[OFFLINE]":
                        print("[!] Service offline, pilih yang lain.\n")
                        continue
                    print(f"[+] You have chosen {self.services[key]['title']}\n")
                    break
                else:
                    print("[!] Angka tidak valid.\n")
            except ValueError:
                print("[!] Masukkan angka saja.\n")
        return key

    def _choose_video_url(self):
        url = input("[~] Video URL : ")
        print("\n")
        return url

    def _start_service(self, service, video_url):
        self._wait_for_element(By.CLASS_NAME, self.services[service]["selector"]).click()
        
        # Cari container input yang aktif
        container = self._wait_for_element(By.CSS_SELECTOR, "div.col-sm-5.col-xs-12.p-1.container:not(.nonec)")

        input_element = container.find_element(By.TAG_NAME, "input")
        input_element.clear()
        input_element.send_keys(video_url)

        while True:
            try:
                # Klik tombol cari
                container.find_element(By.CSS_SELECTOR, "button.btn.btn-primary").click()
                sleep(3)

                # Coba klik tombol submit/kirim
                container.find_element(By.CSS_SELECTOR, "button.btn.btn-dark").click()
                print(f"[~] {self.services[service]['title']} sent successfully")
            except NoSuchElementException:
                pass

            sleep(3)
            remaining_time = self._compute_remaining_time(container)

            if remaining_time:
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                print(f"[~] Waiting for {minutes}m {seconds}s...")
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
                return self.driver.find_element(by, value)
            except NoSuchElementException:
                sleep(1)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
