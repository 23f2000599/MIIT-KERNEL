# Website Screenshot Automation

This automation tool captures screenshots of ALL pages for ALL user roles in the StudyFocus Learning Companion website.

## What it captures:

### Public Pages (2 pages)
- Landing page
- Login page

### Student Pages (12 pages)
- Dashboard
- Study timers
- Timer sessions (Pomodoro, Deep Focus)
- TA swipe interface
- Student matches
- Live class
- Notes
- Statistics
- Live notes
- Timetable
- Settings

### TA Pages (5 pages)
- TA dashboard
- TA matches
- TA live class
- TA notes
- Settings

### Admin Pages (4 pages)
- Admin dashboard
- User management
- Analytics
- Settings

**Total: ~23 screenshots across all roles**

## Quick Start

### Option 1: Full Automation (Recommended)
```bash
python full_automation.py
```
This will:
1. Install dependencies automatically
2. Start the Flask app
3. Run screenshot automation
4. Clean up when done

### Option 2: Manual Steps
1. Install dependencies:
```bash
pip install selenium webdriver-manager requests
```

2. Start Flask app:
```bash
python app.py
```

3. In another terminal, run screenshots:
```bash
python comprehensive_screenshot_tool.py
```

### Option 3: Windows Batch File
```bash
run_screenshot_automation.bat
```

## Output

Screenshots are saved in a timestamped folder:
```
website_screenshots_YYYYMMDD_HHMMSS/
├── public/
│   ├── 01_landing_page.png
│   └── 02_login_page.png
├── student/
│   ├── 01_student_dashboard.png
│   ├── 02_study_timers.png
│   └── ...
├── ta/
│   ├── 01_ta_dashboard.png
│   └── ...
├── admin/
│   ├── 01_admin_dashboard.png
│   └── ...
└── screenshot_report.txt
```

## Requirements

- Python 3.7+
- Chrome browser (ChromeDriver auto-installed)
- Flask app running on localhost:5000

## Notes

- The tool automatically creates test accounts for each role
- Screenshots are taken at 1920x1080 resolution
- Each page loads for 3 seconds before screenshot
- A summary report is generated with all captured pages