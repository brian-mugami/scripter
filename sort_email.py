import email
import imaplib
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

links = []


def click_link(link):
    try:
        resp = requests.get(link)
        if resp.status_code == 200:
            print("Successfully Visited", link)
        else:
            print("Failed to visit", link, "error code", resp.status_code)

    except Exception as e:
        print("Error with", link, str(e))


def connect_to_mail(user_mail, pwd):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_mail, pwd)
        mail.select("inbox")
        return mail
    except Exception as e:
        print(str(e))
        return None


def extract_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    extracted_links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
    return extracted_links


def search_for_emails():
    mail = connect_to_mail(username, password)
    if not mail:
        print("Failed to connect to email.")
        return []

    try:
        time = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
        search_criteria = f'SINCE {time} BODY "unsubscribe"'
        _, search_data = mail.search(None, search_criteria)
        email_ids = search_data[0].split()

        for num in email_ids:
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode()
                        links.extend(extract_links_from_html(html_content))
            else:
                content_type = msg.get_content_type()
                if content_type == "text/html":
                    content = msg.get_payload(decode=True).decode()
                    links.extend(extract_links_from_html(content))
    except Exception as e:
        print(f"Error while searching emails: {str(e)}")
    finally:
        mail.logout()

    return links


def save_links(links):
    with open("links.txt", "w") as f:
        f.write("\n".join(links))


# links_list = search_for_emails()
# for link in links_list:
#     click_link(link)
#
# save_links(links_list)

def list_folders(mail):
    """
    Lists all folders in the email account.
    """
    try:
        _, folders = mail.list()
        print("Available folders:")
        for folder in folders:
            print(folder.decode())
    except Exception as e:
        print(f"Failed to list folders: {e}")


def delete_emails(mail, label):
    """
    Deletes emails from a specific folder.
    """
    try:
        # Select the label (folder)
        status, _ = mail.select(label)
        if status != "OK":
            print(f"Failed to select folder: {label}")
            return

        # Search for all emails in the folder
        _, data = mail.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print(f"No emails found in {label}.")
            return

        # Mark each email for deletion
        for email_id in email_ids:
            mail.store(email_id, "+FLAGS", "\\Deleted")

        # Permanently delete the marked emails
        mail.expunge()
        print(f"All emails in {label} have been deleted.")
    except Exception as e:
        print(f"Failed to delete emails in {label}: {e}")


def main():
    mail = connect_to_mail(username, password)
    if not mail:
        return

    try:
        # List folders to ensure proper label names
        list_folders(mail)

        # Delete emails from 'Social' and 'Promotions'
        delete_emails(mail, "INBOX/Categories")  # Adjust this based on the folder name
        # delete_emails(mail, "[Gmail]/Spam")  # Adjust this based on the folder name
    finally:
        mail.logout()

main()