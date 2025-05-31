# Moodle PDF Downloader 🚀

This is a Python script that logs into Moodle and navigates course page links recursively to download all available course resources files. If your college uses moodle as their course page and you often find yourself wanting to download all the pdfs from a course but hate doing it manually. Try this out.

## Here is a step by step guide: 📃

### Windows
1. Download the `.exe` and `.bat` file only.
2. Double click the `.bat` file
3. Provide the link to the login screen and the course.
### Linux 
- Run `./download_moodle_pdfs --login-url [LOGIN-URL] --course-url [COURSE-URL]`

### If you don't trust me
- Install python
- Install dependencies `pip install -r requirements.txt`
- Run `python download_moodle_pdfs.py --login-url [LOGIN-URL] --course-url [COURSE-URL]`

The files get downloaded to the directory from where you are running the script.
