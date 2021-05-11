import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import json
import time
import os


def get_content(mail, mail_info):
    content_type = mail.get_content_type()
    if content_type == "text/plain":
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)
        mail_info[content_type] = body

    elif content_type == "text/html":
        content_charset = mail.get_content_charset()
        body = mail.get_payload(decode=True).decode(content_charset)

        html = BeautifulSoup(body, "lxml").find("body")

        mail_info[content_type] = str(html).replace('"', '\"')
        mail_info["preview"] = html.text
    else:
        pass


username = ""
password = ""

data_full = {}
id_num = 0

imap = imaplib.IMAP4_SSL('imap.yandex.ru')
imap.login(username, password)


for folder in imap.list()[1]:
    folder = folder.decode().split(' "|" ')
    folder = folder[1]
    status, messages = imap.select(folder)
    data_full[folder] = []
    for i in range(int(messages[0]), 0, -1):
        mail_info = {}
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                id_num += 1
                """ GET SUBJECT """
                try:
                    subject = decode_header(msg["Subject"])[0][0]
                except TypeError:
                    subject = msg["Subject"]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode()
                    except UnicodeDecodeError:
                        subject = ""

                """ GET NAME / EMAIL """
                from_ = msg.get("From")
                from_decode = []
                try:
                    from_ = decode_header(from_)
                    for elem in range(len(from_)):
                        if isinstance(from_[elem][0], bytes):
                            from_decode.append(from_[elem][0].decode())
                except:
                    from_decode = from_

                """ GET DATE """
                date = msg.get("Date")

                message_ID = msg["Message-ID"]
                in_reply_to = msg["In-Reply-To"]

                mail_info["id"] = id_num
                mail_info["date"] = date
                mail_info["subject"] = subject
                mail_info["from"] = from_decode
                mail_info["message-id"] = message_ID
                mail_info["in-reply-to"] = in_reply_to

                """GET EMAIL BODY"""
                if msg.is_multipart():
                    for part in msg.walk():
                        get_content(part, mail_info)
                else:
                    get_content(msg, mail_info)
        data_full[folder].append(mail_info)
print(data_full)
# with open("data.json", "w", encoding='utf8') as outfile:
#     json.dump(data_full, outfile, ensure_ascii=False)
imap.close()
imap.logout()
