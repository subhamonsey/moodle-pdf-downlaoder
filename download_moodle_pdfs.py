import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import getpass
import argparse

def login_to_moodle(session, login_url, username, password):
    # Get the login page to find the login token
    response = session.get(login_url)
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

def get_pdf_links(session, course_url):
    response = session.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links that end with .pdf
    pdf_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '.pdf' in href.lower():
            full_url = urljoin(course_url, href)
            pdf_links.append(full_url)
    return pdf_links

def download_pdfs(session, pdf_links, folder='pdfs'):
    os.makedirs(folder, exist_ok=True)
    for url in pdf_links:
        filename = os.path.join(folder, url.split('/')[-1])
        print(f"Downloading {url} -> {filename}")
        response = session.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
    print(f"✅ Downloaded {len(pdf_links)} PDFs to '{folder}'")

def main():
    parser = argparse.ArgumentParser(
        description="Download all PDFs from a Moodle course page after logging in."
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

            pdf_links = get_pdf_links(session, args.course_url)
            if not pdf_links:
                print("⚠️ No PDF files found on the course page.")
                return

            print(f"Found {len(pdf_links)} PDF files.")
            download_pdfs(session, pdf_links)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()