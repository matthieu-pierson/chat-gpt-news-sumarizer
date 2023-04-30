import os
import os.path
import json
import requests
import base64
from requests_oauthlib import OAuth1Session
from libs.Article import *
from libs.Twitter import *
from libs.Instagram import *
from libs.JsonCreator import *

class PostManager:
    def __init__(self):
        self.jsoncreator = JsonCreator()
        self.instagram = "none"
        self.twitter = "none"
        self.articles_not_posted = []
        self.articles = []
        self.twitter_consumer_key = "dKM0rf12QKHEQoW5BWayjiJBB"
        self.twitter_consumer_secret = "njLI53JixiHTmPX8j454hKQ7S5GPBIoiMAurXWvYmqp1A0X01D"
        self.twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAAFHIlQEAAAAAtyMqBrVrtges5RZ%2BOLPEZq%2FAN04%3Dfpci9PgEtu77FxRSJlqttGFq8XwyDzRdxt9uf7twpvzCj2NhxW"

    def set_list_articles_to_post(self,quantity_of_posts):
        self.articles_not_posted = self.jsoncreator.list_articles_not_posted()
        articles = []
        for i,article_url in enumerate(self.articles_not_posted):
            article = self.jsoncreator.load_json_to_article(article_url)
            articles.append(article)
            if(i == quantity_of_posts-1):
                break
        self.articles = articles
        return True

    def post_instagram(self):
        self.instagram = Instagram()
        if(self.articles != []):
            images_to_post = []
            hastags_to_post = []
            for i,article in enumerate(self.articles):
                current_uuid = article.get_uuid()
                for dirpath, dirnames, filenames in os.walk("F:\\ai_news\\template\\img"):
                    for filename in [f for f in filenames if f.endswith(".jpg")]:
                        if(current_uuid in filename and 'en' in dirpath):
                            img_post_path = os.path.join(dirpath, filename).replace('\\','/')
                            hastags_to_post.append(article.get_hashtags_EN().split(' ')[0])
                            images_to_post.append(img_post_path)
                if(i==3):
                    break
            
            if(len(images_to_post)==1):
                hastags_to_post = article.get_hashtags_EN()
            if(self.instagram.post_picture(path=images_to_post,caption=hastags_to_post) == True):
                return True
            print("End post Instagram")
            return False
        else:
            print("Instagram posting aborted, no articles to post !")
            return False
    
    def post_twitter(self):
        self.twitter = Twitter()
        abort = False
        if(self.articles != []):
            images_to_post = []
            hastags_to_post = []
            uuid = []
            for i,article in enumerate(self.articles):
                current_uuid = article.get_uuid()
                for dirpath, dirnames, filenames in os.walk("F:\\ai_news\\template\\img"):
                    for filename in [f for f in filenames if f.endswith(".jpg")]:
                        if(current_uuid in filename and 'en' in dirpath):
                            img_post_path = os.path.join(dirpath, filename).replace('\\','/')
                            hastags_to_post.append(article.get_hashtags_EN().split(' ')[0])
                            images_to_post.append(img_post_path)
                            uuid.append(article.get_uuid())
                if(i==3):
                    break
            
            media_id_list = []
            for img_post_path in images_to_post:
                media_id = self.twitter.upload_image_twitter(img_post_path,uuid)
                if(media_id == False):
                    abort = True
                    break
                media_id_list.append(str(self.twitter.upload_image_twitter(img_post_path,uuid)))
            if(abort != True):
                if(len(media_id_list)==1):
                    hastags_to_post = article.get_hashtags_EN()
                    payload = {"text": hastags_to_post, "media": {"media_ids": media_id_list}}
                else:
                    payload = {"text": " ".join(hastags_to_post), "media": {"media_ids": media_id_list}}
                if(self.twitter.post_picture(payload)==True):
                    return True
                else:
                    return False
            else:
                return False
        else:
            print("Instagram posting aborted, no articles to post !")
            return False

    def post_all_platform(self):
        for article in self.articles:
                print(article.get_source())
        if(self.post_instagram() == True):
            for article in self.articles:
                self.jsoncreator.set_key_to(article.get_uuid(),"is_posted_instagram","true")
        if(self.post_twitter() == True):
            for article in self.articles:
                self.jsoncreator.set_key_to(article.get_uuid(),"is_posted_twitter","true")

if __name__ == '__main__':
    postmanager = PostManager()
    postmanager.set_list_articles_to_post(quantity_of_posts = 1)
    postmanager.post_all_platform()
