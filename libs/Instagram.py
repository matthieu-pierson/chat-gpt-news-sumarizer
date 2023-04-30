from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
import random
import imaplib
import email
import re

class Instagram:
    def __init__(self):
        self.cl = Client()
        self.cl.challenge_code_handler = self.challenge_code_handler("clear.times.ai", "EMAIL")
        self.cl.login("clear.times.ai", "VmgQ%a#5k7DjxR")

    def post_picture(self,path,caption):
        if(len(path)!=1):
            try:
                print("Posting on Instagram... images :", path, "with caption :", caption)
                media = self.cl.album_upload(
                    path,
                    caption,
                    extra_data={
                        "custom_accessibility_caption": caption,
                        "like_and_view_counts_disabled": 0,
                        "disable_comments": 0,
                    }
                )
                print("Posting on Instagram successful")
                return True
            except Exception as e:
                print(e)
                print("Posting on Instagram failled")
                return False
        else:
            try:
                path = path[0]
                print("Posting on Instagram... images :", path, "with caption :", caption)
                media = self.cl.photo_upload(
                    path,
                    caption,
                    extra_data={
                        "custom_accessibility_caption": caption,
                        "like_and_view_counts_disabled": 0,
                        "disable_comments": 0,
                    }
                )
                print("Posting on Instagram successful")
                return True
            except Exception as e:
                print(e)
                print("Posting on Instagram failled")
                return False
            
    def change_password_handler(self):
        chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
        password = "".join(random.sample(chars, 8))
        return password
    
    def challenge_code_handler(self,username, choice):
        if choice == ChallengeChoice.EMAIL:
            return self.get_code_from_email(username)
        return False
    
    def get_code_from_email(self,username):
        mail = imaplib.IMAP4_SSL("imap.protonmail.com")
        mail.login("newsaipy@protonmail.com", "newsaipy")
        mail.select("inbox")
        result, data = mail.search(None, "(UNSEEN)")
        assert result == "OK", "Error1 during get_code_from_email: %s" % result
        ids = data.pop().split()
        for num in reversed(ids):
            mail.store(num, "+FLAGS", "\\Seen")  # mark as read
            result, data = mail.fetch(num, "(RFC822)")
            assert result == "OK", "Error2 during get_code_from_email: %s" % result
            msg = email.message_from_string(data[0][1].decode())
            payloads = msg.get_payload()
            if not isinstance(payloads, list):
                payloads = [msg]
            code = None
            for payload in payloads:
                body = payload.get_payload(decode=True).decode()
                if "<div" not in body:
                    continue
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
                if not match:
                    continue
                print("Match from email:", match.group(1))
                match = re.search(r">(\d{6})<", body)
                if not match:
                    print('Skip this email, "code" not found')
                    continue
                code = match.group(1)
                if code:
                    return code
        return False

if __name__ == '__main__':
    instagram = Instagram()
    instagram.post_picture(path="F:/ai_news/template/img/20230121/en/2caada9d-db66-4e47-8b3e-0bdab5cb0629.png",caption="test")
    print("v2")
    instagram.cl.photo_upload(path="F:/ai_news/template/img/20230121/en/2caada9d-db66-4e47-8b3e-0bdab5cb0629.png",caption="test")