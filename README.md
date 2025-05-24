# Moodle PDF Downloader

This is a Python script that logs into a Moodle course page and downloads all available PDF files. If your college uses moodle as their coursepage and you often find yourself wanting to download all the pdfs from a course but hate doing it manually. Try this out. 

## Here is a step by step guide:

### Windows
1. Download the .exe and .bat file only.
2. Double click the .bat file
3. Provide the link to the login screen and the course.
### Linux 
- Run "./download_moodle_pdfs --login-url [LOGIN-URL] --course-url [COURSE-URL]"

### Python developers
- Run "python download_moodle_pdfs.py --login-url [LOGIN-URL] --course-url [COURSE-URL]"

## 🚀 Features

- Securely prompts for Moodle credentials
- Logs in via session handling
- Parses course page to find all PDF links
- Downloads PDFs to a local `pdfs/` folder
- Uses a virtual environment for clean dependency management

---

## 📁 Project Structure

