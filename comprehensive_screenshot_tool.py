from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
import requests

class ComprehensiveWebsiteScreenshotter:
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
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        
    def create_directories(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screenshots_dir = f"website_screenshots_{timestamp}"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        for role in ["public", "student", "ta", "admin"]:
            os.makedirs(f"{self.screenshots_dir}/{role}", exist_ok=True)
            
    def check_server_running(self):
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def take_screenshot(self, page_name, role="public"):
        # Scroll to top and wait for page to load
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        filename = f"{self.screenshots_dir}/{role}/{page_name}.png"
        self.driver.save_screenshot(filename)
        print(f"✓ Screenshot saved: {role}/{page_name}.png")
        
    def create_test_account(self, role):
        test_users = {
            "student": {"email": "student@test.com", "password": "password123", "name": "Test Student"},
            "ta": {"email": "ta@test.com", "password": "password123", "name": "Test TA"},
            "admin": {"email": "admin@test.com", "password": "password123", "name": "Test Admin"}
        }
        
        user = test_users[role]
        
        try:
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            # Fill signup form (assuming it's on the same page or accessible)
            name_field = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")
            role_field = self.driver.find_element(By.NAME, "role")
            
            name_field.clear()
            name_field.send_keys(user["name"])
            email_field.clear()
            email_field.send_keys(user["email"])
            password_field.clear()
            password_field.send_keys(user["password"])
            
            # Select role
            select = Select(role_field)
            select.select_by_value(role)
            
            # Submit signup form
            signup_button = self.driver.find_element(By.XPATH, "//button[contains(@type, 'submit')]")
            signup_button.click()
            time.sleep(3)
            
            return "dashboard" in self.driver.current_url
            
        except Exception as e:
            print(f"Account creation failed for {role}: {e}")
            return False
            
    def login_as_role(self, role):
        test_users = {
            "student": {"email": "student@test.com", "password": "password123"},
            "ta": {"email": "ta@test.com", "password": "password123"},
            "admin": {"email": "admin@test.com", "password": "password123"}
        }
        
        user = test_users[role]
        
        try:
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(user["email"])
            password_field.clear()
            password_field.send_keys(user["password"])
            
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or @type='submit']")
            login_button.click()
            time.sleep(3)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url:
                return True
            else:
                # Try to create account if login failed
                return self.create_test_account(role)
                
        except Exception as e:
            print(f"Login failed for {role}: {e}")
            return self.create_test_account(role)
            
    def capture_public_pages(self):
        print("\n📸 Capturing public pages...")
        
        public_pages = [
            ("/", "01_landing_page"),
            ("/login", "02_login_page")
        ]
        
        for url, filename in public_pages:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "public")
            except Exception as e:
                print(f"❌ Error capturing {url}: {e}")
                
    def capture_student_pages(self):
        print("\n📸 Capturing student pages...")
        
        if not self.login_as_role("student"):
            print("❌ Failed to login as student")
            return
            
        student_pages = [
            ("/student/dashboard", "01_student_dashboard"),
            ("/student/timers", "02_study_timers"),
            ("/student/timer/Pomodoro%20Timer", "03_pomodoro_timer"),
            ("/student/timer/Deep%20Focus%20Timer", "04_deep_focus_timer"),
            ("/student/swipe", "05_ta_swipe"),
            ("/student/matches", "06_student_matches"),
            ("/student/live-class", "07_live_class"),
            ("/student/notes", "08_student_notes"),
            ("/student/stats", "09_student_stats"),
            ("/student/live-notes", "10_live_notes"),
            ("/student/timetable", "11_timetable"),
            ("/settings", "12_settings")
        ]
        
        for url, filename in student_pages:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "student")
            except Exception as e:
                print(f"❌ Error capturing {url}: {e}")
                
        self.logout()
        
    def capture_ta_pages(self):
        print("\n📸 Capturing TA pages...")
        
        if not self.login_as_role("ta"):
            print("❌ Failed to login as TA")
            return
            
        ta_pages = [
            ("/ta/dashboard", "01_ta_dashboard"),
            ("/ta/matches", "02_ta_matches"),
            ("/ta/live-class", "03_ta_live_class"),
            ("/ta/notes", "04_ta_notes"),
            ("/settings", "05_ta_settings")
        ]
        
        for url, filename in ta_pages:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "ta")
            except Exception as e:
                print(f"❌ Error capturing {url}: {e}")
                
        self.logout()
        
    def capture_admin_pages(self):
        print("\n📸 Capturing admin pages...")
        
        if not self.login_as_role("admin"):
            print("❌ Failed to login as admin")
            return
            
        admin_pages = [
            ("/admin/dashboard", "01_admin_dashboard"),
            ("/admin/users", "02_admin_users"),
            ("/admin/analytics", "03_admin_analytics"),
            ("/settings", "04_admin_settings")
        ]
        
        for url, filename in admin_pages:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(3)
                self.take_screenshot(filename, "admin")
            except Exception as e:
                print(f"❌ Error capturing {url}: {e}")
                
        self.logout()
        
    def logout(self):
        try:
            self.driver.get(f"{self.base_url}/logout")
            time.sleep(2)
        except:
            pass
            
    def generate_summary_report(self):
        report_path = f"{self.screenshots_dir}/screenshot_report.txt"
        with open(report_path, 'w') as f:
            f.write("Website Screenshot Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base URL: {self.base_url}\n\n")
            
            total_screenshots = 0
            for role in ["public", "student", "ta", "admin"]:
                role_dir = f"{self.screenshots_dir}/{role}"
                if os.path.exists(role_dir):
                    count = len([f for f in os.listdir(role_dir) if f.endswith('.png')])
                    total_screenshots += count
                    f.write(f"{role.capitalize()} Pages: {count}\n")
                    
                    # List all screenshots
                    screenshots = sorted([f for f in os.listdir(role_dir) if f.endswith('.png')])
                    for screenshot in screenshots:
                        f.write(f"  - {screenshot}\n")
                    f.write("\n")
            
            f.write(f"Total Screenshots: {total_screenshots}\n")
            
        print(f"\n📋 Summary report generated: {report_path}")
            
    def run_all_screenshots(self):
        print("🚀 Starting Comprehensive Website Screenshot Capture")
        print("=" * 60)
        
        # Check if server is running
        if not self.check_server_running():
            print(f"❌ Server is not running at {self.base_url}")
            print("Please start the Flask application first:")
            print("  python app.py")
            return
            
        print(f"✅ Server is running at {self.base_url}")
        
        try:
            self.capture_public_pages()
            self.capture_student_pages()
            self.capture_ta_pages()
            self.capture_admin_pages()
            
            self.generate_summary_report()
            
            print(f"\n🎉 All screenshots completed successfully!")
            print(f"📁 Screenshots saved in: {self.screenshots_dir}")
            
            # Count total screenshots
            total_count = 0
            for role in ["public", "student", "ta", "admin"]:
                role_dir = f"{self.screenshots_dir}/{role}"
                if os.path.exists(role_dir):
                    count = len([f for f in os.listdir(role_dir) if f.endswith('.png')])
                    total_count += count
                    print(f"   {role.capitalize()}: {count} pages")
            
            print(f"\n📊 Total: {total_count} screenshots captured")
                
        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
        finally:
            self.driver.quit()
            print("\n🔚 Browser closed. Screenshot capture complete!")

if __name__ == "__main__":
    print("🌐 Website Screenshot Automation Tool")
    print("=" * 50)
    print("This tool will capture screenshots of ALL pages for ALL roles:")
    print("  • Public pages (landing, login)")
    print("  • Student pages (dashboard, timers, swipe, matches, etc.)")
    print("  • TA pages (dashboard, matches, notes, etc.)")
    print("  • Admin pages (dashboard, users, analytics, etc.)")
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
        screenshotter = ComprehensiveWebsiteScreenshotter()
        screenshotter.run_all_screenshots()
    except KeyboardInterrupt:
        print("\n❌ Screenshot capture cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")