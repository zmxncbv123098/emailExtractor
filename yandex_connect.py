import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import time
import os


def get_sent_content(mail):
    content_type = mail.get_content_type()
    if content_type == "text/plain":
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)
        # print(body)

    elif content_type == "text/html":
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)
        if "<blockquote" in body:

            main_body = BeautifulSoup(body[:body.find("<blockquote")], "lxml")
            main_div_body = main_body.find_all("div")
            if len(main_div_body) == 0:
                print(main_body.text)
            else:
                print("Response from:", main_div_body[-1].text)
                print("MAIN TEXT")
                for div in main_div_body[:-1]:
                    print(div.text)

            print("RESPONSE")
            blockquotes = BeautifulSoup(body, "lxml").find_all("blockquote")
            print(blockquotes[0].text)
            # if len(blockquotes) > 1:
            #     index1 = body.find("<blockquote>")
            #     index2 = body.find("<blockquote", index1 + 1)
            #     response_body = body[index1: index2].replace("<blockquote>", "")
            #     first_block = BeautifulSoup(response_body, "lxml").find_all("div")
            #
            #     if len(blockquotes) == 2:
            #         for div in first_block[1:-1]:
            #             print(div.text)
            #     else:
            #         for div in first_block[:-1]:
            #             print(div.text)
            #     # print(blockquotes[0].text.replace(blockquotes[1].text, ""))
            # else:
            #     print(blockquotes[0].text)
        else:
            print("MAIN TEXT NO BLOCKS")
            body_html = BeautifulSoup(body, "lxml")
            div_boxes = body_html.find_all("div")
            if len(div_boxes) == 0:
                print(body_html.text)
            else:
                print("DIV")
                for div in div_boxes:
                    print(div.text)
        pass
    else:
        pass


# username = "alexandraivv@yandex.ru"
# password = "weare6789"
username = "zmxncbv12309@yandex.ru"
password = "mike2112"

id_num = 0

imap = imaplib.IMAP4_SSL('imap.yandex.ru')
imap.login(username, password)
print(imap.list())
status, messages = imap.select("Sent")
if status == "NO":
    status, messages = imap.select("&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-")

# messages = [253]

for i in range(int(messages[0]), 0, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")
    # print(i)
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])

            """GET SUBJECT / NAME / EMAIL / DATE"""
            try:
                subject = decode_header(msg["Subject"])[0][0]
            except TypeError:
                subject = msg["Subject"]
            from_ = msg.get("From")
            name, user_mail = decode_header(from_)
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
    # time.sleep(2)
imap.close()
imap.logout()
