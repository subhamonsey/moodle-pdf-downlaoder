import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlunparse, parse_qs, urlencode, urlparse
import getpass
import argparse
import re
import logging

logging.basicConfig(
    filename='moodle_downloader.log',
    filemode='a',  # append to existing logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO  # or DEBUG for more verbosity
)

def login_to_moodle(session, login_url, username, password):
    # Get the login page to find the login token
    response = session.get(login_url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find logintoken if it exists
    token_input = soup.find('input', attrs={'name': 'logintoken'})
    login_token = token_input['value'] if token_input else ''

    login_data = {
        'username': username,
        'password': password,
        'logintoken': login_token
    }

    # Post the login form
    login_response = session.post(login_url, data=login_data)

    # Check if login was successful
    if "login" in login_response.url.lower():
        raise Exception("Login failed. Please check your credentials.")
    return session

def clean_url(url):
    """Remove fragment and unnecessary query parameters."""
    parsed = urlparse(url)
    allowed_params = ['id']
    query = parse_qs(parsed.query)
    filtered_query = {k: v for k, v in query.items() if k in allowed_params}
    cleaned_query = urlencode(filtered_query, doseq=True)

    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', cleaned_query, ''))

def should_skip_url(url):
    """Skip URLs that point to non-content modules."""
    skip_keywords = ['forum', 'comment']
    return any(k in url for k in skip_keywords)

def get_resource_links(session, course_url, visited=None, depth=0, max_depth=2, base_folder='resources'):
    page_type = 0
    if visited is None:
        visited = set()
    course_url = clean_url(course_url)
    if course_url in visited or depth > max_depth or should_skip_url(course_url):
        return []
    print(f"{'📂 ' + '  ' * depth}Crawling: {course_url}")
    logging.info(f"{'📂 ' + '  ' * depth}Crawling: {course_url}")
    visited.add(course_url)
    
    response = session.get(course_url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    parsed = urlparse(course_url)
    path_part = parsed.path
    query_part = parsed.query.replace('=', '_').replace('&', '_')[:40]
    safe_folder_name = f"{path_part}_{query_part}" if query_part else path_part
    title = soup.title.string.strip() if soup.title else safe_folder_name
    target_folder_name = re.sub(r'[^\w\-_.]', '_', title)
    target_folder = os.path.join(base_folder, target_folder_name) if depth != 0 else base_folder
    
    resource_files = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(course_url, href)

        if any(keyword in full_url for keyword in ['mod', 'pdf']):
            try:
                head = session.head(full_url, allow_redirects=True)
                content_type = head.headers.get('Content-Type', '')

                if 'application' in content_type:
                    # Try to get filename from Content-Disposition header
                    cd = head.headers.get('Content-Disposition', '')
                    filename_match = re.search(r'filename[^;=\n]*=["\']?([^"\';\n]*)', cd)
                    if filename_match:
                        filename = filename_match.group(1)
                    else:
                        # Fallback: extract filename from url path
                        path=urlparse(full_url).path
                        filename = re.search(r'[^/]+$', path).group()
                    
                    resource_files.append((full_url, filename, target_folder))
                elif 'text/html' in content_type and 'moodle' in full_url:
                    clean_full_url = clean_url(full_url)
                    if (clean_full_url not in visited) and not should_skip_url(clean_full_url):
                        resource_files.extend(get_resource_links(session, clean_full_url, visited, depth + 1, max_depth, base_folder))
            except Exception as e:
                print(f"⚠️ Skipping {full_url} due to error: {e}")
                logging.warning(f"⚠️ Skipping {full_url} due to error: {e}", exc_info=True)

    return resource_files

def download_resources(session, resource_files):
    for url, filename, folder in resource_files:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        print(f"📥 Downloading {url} -> {path}")
        logging.info((f"📥 Downloading {url} -> {path}"))
        try:
            response = session.get(url)
            with open(path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            logging.error(f"❌ Failed to download {url}: {e}",exc_info=True)
            print(f"❌ Failed to download {url}: {e}")
    print(f"✅ Downloaded {len(resource_files)} resources.")
    logging.info(f"✅ Downloaded {len(resource_files)} resources.")
    
def main():
    parser = argparse.ArgumentParser(
        description="Download all resources from a Moodle course page after logging in."
    )
    parser.add_argument(
        '--login-url', required=True, help='The Moodle login URL (e.g., https://moodle.example.com/login/index.php)'
    )
    parser.add_argument(
        '--course-url', required=True, help='The Moodle course URL (e.g., https://moodle.example.com/course/view.php?id=123)'
    )
    args = parser.parse_args()

    print("Enter your Moodle credentials:")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    with requests.Session() as session:
        try:
            login_to_moodle(session, args.login_url, username, password)
            print("✅ Logged in successfully.")
            logging.info("✅ Logged in successfully.")

            course_page_response = session.get(args.course_url, timeout=20)
            course_page_soup = BeautifulSoup(course_page_response.text, 'html.parser')
            title = course_page_soup.title.string.strip() if course_page_soup.title else "course"
            safe_title = re.sub(r'[^\w\-_.]', '_', title)
            course_folder = os.path.join(os.getcwd(), safe_title)
            resource_files = get_resource_links(session, args.course_url, base_folder=course_folder)
            if not resource_files:
                print("⚠️ No resource files found on the course page.")
                logging.warning("⚠️ No resource files found on the course page.")
                return

            print(f"Found {len(resource_files)} resource files.")
            logging.info(f"Found {len(resource_files)} resource files.")
            download_resources(session, resource_files)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.error(f"❌ Error: {e}",exc_info=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ An unexpected error occurred. See 'moodle_downloader.log' for details.")
        logging.exception("❌ Unhandled exception occurred:")
