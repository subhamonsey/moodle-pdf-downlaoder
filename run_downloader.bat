@echo off
echo ==== Moodle PDF Downloader ====
set /p LOGIN_URL=Enter Moodle login URL:
set /p COURSE_URL=Enter course URL:

download_moodle_resources.exe --login-url %LOGIN_URL% --course-url %COURSE_URL%

pause
