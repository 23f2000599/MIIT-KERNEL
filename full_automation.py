import subprocess
import time
import os
import sys
import requests
from threading import Thread

class FullAutomationRunner:
    def __init__(self):
        self.flask_process = None
        self.base_url = "http://localhost:5000"
        
    def install_dependencies(self):
        print("📦 Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "selenium==4.15.2", "webdriver-manager==4.0.1", "requests"])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def start_flask_app(self):
        print("🚀 Starting Flask application...")
        try:
            # Start Flask app in background
            self.flask_process = subprocess.Popen([sys.executable, "app.py"], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
            
            # Wait for Flask to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(self.base_url, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Flask app is running at {self.base_url}")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"⏳ Waiting for Flask to start... ({i+1}/30)")
                
            print("❌ Flask app failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Flask app: {e}")
            return False
            
    def run_screenshot_automation(self):
        print("📸 Starting screenshot automation...")
        try:
            # Import and run the screenshot tool
            from comprehensive_screenshot_tool import ComprehensiveWebsiteScreenshotter
            screenshotter = ComprehensiveWebsiteScreenshotter()
            screenshotter.run_all_screenshots()
            return True
        except Exception as e:
            print(f"❌ Screenshot automation failed: {e}")
            return False
            
    def cleanup(self):
        if self.flask_process:
            print("🔚 Stopping Flask application...")
            self.flask_process.terminate()
            self.flask_process.wait()
            
    def run_complete_automation(self):
        print("🌐 Complete Website Screenshot Automation")
        print("=" * 60)
        print("This will:")
        print("1. Install required dependencies")
        print("2. Start the Flask application")
        print("3. Capture screenshots of ALL pages for ALL roles")
        print("4. Generate a summary report")
        print("\nPress Enter to continue or Ctrl+C to cancel...")
        
        try:
            input()
            
            # Step 1: Install dependencies
            if not self.install_dependencies():
                return
                
            # Step 2: Start Flask app
            if not self.start_flask_app():
                return
                
            # Step 3: Run screenshot automation
            self.run_screenshot_automation()
            
        except KeyboardInterrupt:
            print("\n❌ Automation cancelled by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    runner = FullAutomationRunner()
    runner.run_complete_automation()