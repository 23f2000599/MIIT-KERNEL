from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime

class WebsiteScreenshotter:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.screenshots_dir = "screenshots"
        self.setup_driver()
        self.create_directories()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def create_directories(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screenshots_dir = f"screenshots_{timestamp}"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        for role in ["public", "student", "ta", "admin"]:
            os.makedirs(f"{self.screenshots_dir}/{role}", exist_ok=True)
            
    def take_screenshot(self, page_name, role="public"):
        filename = f"{self.screenshots_dir}/{role}/{page_name}.png"
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
        
    def login_as_role(self, role):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Create test users if they don't exist
        test_users = {
            "student": {"email": "student@test.com", "password": "password123", "name": "Test Student"},
            "ta": {"email": "ta@test.com", "password": "password123", "name": "Test TA"},
            "admin": {"email": "admin@test.com", "password": "password123", "name": "Test Admin"}
        }
        
        user = test_users[role]
        
        # Try to login first
        try:
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(user["email"])
            password_field.clear()
            password_field.send_keys(user["password"])
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]")
            login_button.click()
            time.sleep(3)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url:
                return True
                
        except Exception as e:
            print(f"Login failed, trying to create account: {e}")
            
        # If login failed, try to create account
        try:
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            # Look for signup form or toggle
            signup_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Create Account')]")
            if signup_elements:
                signup_elements[0].click()
                time.sleep(1)
            
            # Fill signup form
            name_field = self.driver.find_element(By.NAME, "name")
            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")
            role_field = self.driver.find_element(By.NAME, "role")
            
            name_field.send_keys(user["name"])
            email_field.send_keys(user["email"])
            password_field.send_keys(user["password"])
            
            # Select role
            from selenium.webdriver.support.ui import Select
            select = Select(role_field)
            select.select_by_value(role)
            
            signup_button = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Sign Up')]")
            signup_button.click()
            time.sleep(3)
            
            return "dashboard" in self.driver.current_url
            
        except Exception as e:
            print(f"Account creation failed: {e}")
            return False
            
    def capture_public_pages(self):
        print("Capturing public pages...")
        
        # Landing page
        self.driver.get(self.base_url)
        time.sleep(3)
        self.take_screenshot("01_landing", "public")
        
        # Login page
        self.driver.get(f"{self.base_url}/login")
        time.sleep(3)
        self.take_screenshot("02_login", "public")
        
    def capture_student_pages(self):
        print("Capturing student pages...")
        
        if not self.login_as_role("student"):
            print("Failed to login as student")
            return
            
        student_urls = [
            ("/student/dashboard", "01_dashboard"),
            ("/student/timers", "02_timers"),
            ("/student/timer/Pomodoro Timer", "03_timer_session"),
            ("/student/swipe", "04_swipe"),
            ("/student/matches", "05_matches"),
            ("/student/live-class", "06_live_class"),
            ("/student/notes", "07_notes"),
            ("/student/stats", "08_stats"),
            ("/student/live-notes", "09_live_notes"),
            ("/student/timetable", "10_timetable"),
            ("/settings", "11_settings")
        ]
        
        for url, filename in student_urls:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "student")
            except Exception as e:
                print(f"Error capturing {url}: {e}")
                
        self.logout()
        
    def capture_ta_pages(self):
        print("Capturing TA pages...")
        
        if not self.login_as_role("ta"):
            print("Failed to login as TA")
            return
            
        ta_urls = [
            ("/ta/dashboard", "01_dashboard"),
            ("/ta/matches", "02_matches"),
            ("/ta/live-class", "03_live_class"),
            ("/ta/notes", "04_notes"),
            ("/settings", "05_settings")
        ]
        
        for url, filename in ta_urls:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "ta")
            except Exception as e:
                print(f"Error capturing {url}: {e}")
                
        self.logout()
        
    def capture_admin_pages(self):
        print("Capturing admin pages...")
        
        if not self.login_as_role("admin"):
            print("Failed to login as admin")
            return
            
        admin_urls = [
            ("/admin/dashboard", "01_dashboard"),
            ("/admin/users", "02_users"),
            ("/admin/analytics", "03_analytics"),
            ("/settings", "04_settings")
        ]
        
        for url, filename in admin_urls:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "admin")
            except Exception as e:
                print(f"Error capturing {url}: {e}")
                
        self.logout()
        
    def logout(self):
        try:
            self.driver.get(f"{self.base_url}/logout")
            time.sleep(2)
        except:
            pass
            
    def run_all_screenshots(self):
        print("Starting comprehensive website screenshot capture...")
        
        try:
            self.capture_public_pages()
            self.capture_student_pages()
            self.capture_ta_pages()
            self.capture_admin_pages()
            
            print(f"\nAll screenshots completed! Check the '{self.screenshots_dir}' directory.")
            print(f"Total pages captured:")
            for role in ["public", "student", "ta", "admin"]:
                count = len([f for f in os.listdir(f"{self.screenshots_dir}/{role}") if f.endswith('.png')])
                print(f"  {role.capitalize()}: {count} pages")
                
        except Exception as e:
            print(f"Error during screenshot capture: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    print("Website Screenshot Automation")
    print("=" * 50)
    print("Make sure the Flask app is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    screenshotter = WebsiteScreenshotter()
    screenshotter.run_all_screenshots()