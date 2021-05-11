import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import time
import os


def get_sent_content(mail):
    content_type = mail.get_content_type()
    print(content_type)
    if content_type == "text/plain":
        # print(content_type)
        # print("###")
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)
        print(body)
        # print("###")
        pass

    elif content_type == "text/html":
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)

        html = BeautifulSoup(body, "lxml")
        print(html.text)
        if "<blockquote" in body:

            main_body = BeautifulSoup(body[:body.find("<blockquote")], "lxml")
            main_div_body = main_body.find_all("div")
            if len(main_div_body) == 0:
                print(main_body.text)
            else:
                print("Response from:", main_div_body[-1].text)
                print("MAIN TEXT")
                print(main_div_body[0].text)

            print("RESPONSE")
            blockquotes = BeautifulSoup(body, "lxml").find_all("blockquote")
            print(blockquotes[0].text)
        else:
            print("MAIN TEXT NO BLOCKS")
            body_html = BeautifulSoup(body, "lxml")
            div_boxes = body_html.find_all("div")
            if len(div_boxes) == 0:
                print(body_html.text)
            else:
                print(div_boxes[0].text)
    else:
        pass



username = ""
password = ""

id_num = 0

imap = imaplib.IMAP4_SSL('imap.yandex.ru')
imap.login(username, password)
print(imap.list())
status, messages = imap.select("INBOX")
print(messages)
# if status == "NO":
#     status, messages = imap.select("&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-")


for i in range(int(messages[0]), int(messages[0])-2, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")
    # print(i)
    for response in msg:
        if isinstance(response, tuple):
            id_num += 1
            msg = email.message_from_bytes(response[1])
            """GET SUBJECT / NAME / EMAIL / DATE"""
            try:
                subject = decode_header(msg["Subject"])[0][0]
            except TypeError:
                subject = msg["Subject"]

            from_ = msg.get("From")
            try:
                name, user_mail = decode_header(from_)
            except ValueError:
                name, user_mail = from_.split()

            date = msg.get("Date")
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode()
                except UnicodeDecodeError:
                    subject = ""
            if isinstance(name[0], bytes):
                try:
                    name = name[0].decode()
                except UnicodeDecodeError:
                    name = ""
            if isinstance(user_mail[0], bytes):
                user_mail = user_mail[0].decode()

            print("ID", id_num)
            print("Date:", date)
            print("Subject:", subject)
            print("From:", name, user_mail)

            """GET EMAIL BODY"""
            if msg.is_multipart():
                print("!! MULTI !!")
                for part in msg.walk():
                    get_sent_content(part)
            else:
                get_sent_content(msg)
            print("=" * 100)
imap.close()
imap.logout()
