import json
import pyminizip
import os
import imaplib
import email
from email.header import decode_header
from tkinter import *
from tkinter.ttk import Progressbar
from bs4 import BeautifulSoup


def main_window():
    global root
    root = Tk()
    root.title("Login")
    root.geometry("400x400")
    Label(root, text="Please enter details below to login").pack()
    Label(root, text="").pack()

    global login
    global password

    login = StringVar()
    password = StringVar()

    Label(root, text="Username * ").pack()
    Entry(root, textvariable=login).pack()
    Label(root, text="").pack()
    Label(root, text="Password * ").pack()
    Entry(root, textvariable=password, show='*').pack()
    Label(root, text="").pack()
    Button(root, text="Login", width=10, height=1, command=login_verification).pack()

    root.mainloop()


def delete_frame():
    invalid_password_screen.destroy()


def raise_invalid_pass():
    global invalid_password_screen
    invalid_password_screen = Toplevel(root)
    invalid_password_screen.title("Success")
    invalid_password_screen.geometry("400x300")
    Label(invalid_password_screen, text="").pack()
    Label(invalid_password_screen, text="Invalid Password or Login").pack()
    Button(invalid_password_screen, text="OK", command=delete_frame).pack()


def get_content(mail, mail_info):
    content_type = mail.get_content_type()
    if content_type == "text/plain":
        try:
            content_charset = mail.get_content_charset()
            body = mail.get_payload(decode=True).decode(content_charset)
            mail_info[content_type] = body
        except:
            mail_info[content_type] = ""

    elif content_type == "text/html":
        try:
            content_charset = mail.get_content_charset()
            body = mail.get_payload(decode=True).decode(content_charset)
            html = BeautifulSoup(body, "lxml").find("body")

            mail_info[content_type] = str(html).replace('"', '\"')
            mail_info["preview"] = html.text
        except:
            mail_info[content_type] = ""
            mail_info["preview"] = ""
    else:
        pass


def login_verification():
    data_full = {}
    id_num = 0
    imap = imaplib.IMAP4_SSL('imap.yandex.ru')
    try:
        imap.login(login.get(), password.get())
        folders = imap.list()[1]
        text = Label(root, text='')
        progress = Progressbar(root, orient=HORIZONTAL,
                               length=150, mode='determinate')
        text.pack()
        progress.pack(pady=10)
        root.update_idletasks()
        for folder in folders:
            folder = folder.decode().split(' "|" ')
            text['text'] = folder[0][folder[0].rfind("\\")+1:-1]
            folder = folder[1]
            status, messages = imap.select(folder)
            data_full[folder] = []
            progress['value'] = 0
            root.update_idletasks()
            for i in range(int(messages[0]), 0, -1):
                mail_info = {}
                res, msg = imap.fetch(str(i), "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        # print(id_num)
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
                            from_decode = ['','']

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
                progress['value'] += 150 / int(messages[0])
                root.update_idletasks()
        imap.close()
        imap.logout()
        with open("data.json", "w", encoding='utf8') as outfile:
            json.dump(data_full, outfile, ensure_ascii=False)
        p = 'p1s$wr0te'
        pyminizip.compress("data.json", '', "data.mlds", p, 0)
        os.remove("data.json")
        Label(root, text="ALL DONE! \n YOU CAN CLOSE THIS WINDOW").pack()
    except imaplib.IMAP4.error:
        raise_invalid_pass()


main_window()
