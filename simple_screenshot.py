from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime
import requests

class SimpleScreenshotter:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.setup_driver()
        self.create_directories()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Chrome setup failed: {e}")
            print("Please ensure Chrome is installed and ChromeDriver is in PATH")
            raise
            
        self.wait = WebDriverWait(self.driver, 10)
        
    def create_directories(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screenshots_dir = f"screenshots_{timestamp}"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        for role in ["public", "student", "ta", "admin"]:
            os.makedirs(f"{self.screenshots_dir}/{role}", exist_ok=True)
            
    def take_screenshot(self, page_name, role="public"):
        time.sleep(2)
        filename = f"{self.screenshots_dir}/{role}/{page_name}.png"
        self.driver.save_screenshot(filename)
        print(f"✓ {role}/{page_name}.png")
        
    def create_user(self, role):
        users = {
            "student": {"email": "student@test.com", "password": "test123", "name": "Test Student"},
            "ta": {"email": "ta@test.com", "password": "test123", "name": "Test TA"},
            "admin": {"email": "admin@test.com", "password": "test123", "name": "Test Admin"}
        }
        
        user = users[role]
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        try:
            # Fill form
            self.driver.find_element(By.NAME, "name").send_keys(user["name"])
            self.driver.find_element(By.NAME, "email").send_keys(user["email"])
            self.driver.find_element(By.NAME, "password").send_keys(user["password"])
            Select(self.driver.find_element(By.NAME, "role")).select_by_value(role)
            
            # Submit
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(3)
            return "dashboard" in self.driver.current_url
        except:
            return False
            
    def login(self, role):
        users = {
            "student": {"email": "student@test.com", "password": "test123"},
            "ta": {"email": "ta@test.com", "password": "test123"},
            "admin": {"email": "admin@test.com", "password": "test123"}
        }
        
        user = users[role]
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        try:
            self.driver.find_element(By.NAME, "email").send_keys(user["email"])
            self.driver.find_element(By.NAME, "password").send_keys(user["password"])
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
            time.sleep(3)
            
            if "dashboard" in self.driver.current_url:
                return True
            else:
                return self.create_user(role)
        except:
            return self.create_user(role)
            
    def capture_all(self):
        print("📸 Capturing all pages...")
        
        # Public pages
        self.driver.get(self.base_url)
        self.take_screenshot("01_landing", "public")
        
        self.driver.get(f"{self.base_url}/login")
        self.take_screenshot("02_login", "public")
        
        # Student pages
        if self.login("student"):
            pages = [
                ("/student/dashboard", "01_dashboard"),
                ("/student/timers", "02_timers"),
                ("/student/swipe", "03_swipe"),
                ("/student/matches", "04_matches"),
                ("/student/notes", "05_notes"),
                ("/student/stats", "06_stats"),
                ("/settings", "07_settings")
            ]
            
            for url, name in pages:
                try:
                    self.driver.get(f"{self.base_url}{url}")
                    self.take_screenshot(name, "student")
                except:
                    pass
                    
        # TA pages
        if self.login("ta"):
            pages = [
                ("/ta/dashboard", "01_dashboard"),
                ("/ta/matches", "02_matches"),
                ("/ta/notes", "03_notes"),
                ("/settings", "04_settings")
            ]
            
            for url, name in pages:
                try:
                    self.driver.get(f"{self.base_url}{url}")
                    self.take_screenshot(name, "ta")
                except:
                    pass
                    
        # Admin pages
        if self.login("admin"):
            pages = [
                ("/admin/dashboard", "01_dashboard"),
                ("/admin/users", "02_users"),
                ("/admin/analytics", "03_analytics"),
                ("/settings", "04_settings")
            ]
            
            for url, name in pages:
                try:
                    self.driver.get(f"{self.base_url}{url}")
                    self.take_screenshot(name, "admin")
                except:
                    pass
                    
        print(f"\n✅ Screenshots saved in: {self.screenshots_dir}")
        self.driver.quit()

if __name__ == "__main__":
    try:
        screenshotter = SimpleScreenshotter()
        screenshotter.capture_all()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry installing ChromeDriver manually:")
        print("1. Download from: https://chromedriver.chromium.org/")
        print("2. Add to PATH or place in project folder")