import os
import os.path
import json
import requests
import base64
from bs4 import BeautifulSoup as bs
from requests_oauthlib import OAuth1Session
import chromedriver_autoinstaller
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

class Twitter:
    def __init__(self):
        self.jsoncreator = JsonCreator()
        self.twitter_consumer_key = "dKM0rf12QKHEQoW5BWayjiJBB"
        self.twitter_consumer_secret = "njLI53JixiHTmPX8j454hKQ7S5GPBIoiMAurXWvYmqp1A0X01D"
        self.twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAAFHIlQEAAAAAtyMqBrVrtges5RZ%2BOLPEZq%2FAN04%3Dfpci9PgEtu77FxRSJlqttGFq8XwyDzRdxt9uf7twpvzCj2NhxW"

    def post_picture(self,payload):
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        consumer_key = self.twitter_consumer_key
        consumer_secret = self.twitter_consumer_secret
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        # verifier = input("Paste the PIN here: ")
        verifier = self.get_pin(authorization_url)
        print("PIN = "+verifier)

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        #temporary fix 503 error is a bug 
        if response.status_code != 201 and response.status_code != 503 :
            return False
        print("Response code: {}".format(response.status_code))
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return True
        
    
    def upload_image_twitter(self,img_post_path,uuid):
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        consumer_key = self.twitter_consumer_key
        consumer_secret = self.twitter_consumer_secret
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        # self.get_pin(authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        # verifier = input("Paste the PIN here: ")
        verifier = self.get_pin(authorization_url)
        print("PIN = "+verifier)

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        with open(img_post_path, "rb") as image_file:
            image_data = image_file.read()
            image_data = base64.b64encode(image_data)

        payload = {"media_data": image_data}

        # Making the request
        response = oauth.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            data=payload,
        )

        if response.status_code == 200:
            media_id = json.loads(response.text)["media_id"]
            self.jsoncreator.set_key_to(uuid,"twitter_media_id",media_id)
            print("Image téléchargée avec succès. ID de média : ", media_id)
            return media_id
        else:
            print("Erreur lors du téléchargement de l'image : ", response.text)
            return False

    def get_pin(self,authorization_url):
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(authorization_url)
        try:
            email_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="username_or_email"]')))
            email_field.send_keys("cleartimes.ai@protonmail.com")
            password_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
            password_field.send_keys("A85Xgsisn#%8Y$")
            allow_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="allow"]')))
            allow_field.click()
            try:
                sing_in_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')))
                sing_in_field.send_keys("cleartimes.ai@protonmail.com")
                next_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')))
                next_button.click()
                username_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')))
                username_field.send_keys("ClearTimesAI")
                next2_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div')))
                next2_button.click()
                password2_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')))
                password2_field.send_keys("A85Xgsisn#%8Y$")
                log_in_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div')))
                log_in_button.click()
                allow_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="allow"]')))
                allow_field.click()
            except:
                print("No challenge")
            pin_code = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="oauth_pin"]/p/kbd/code')))
            pin = pin_code.text
        finally:
            driver.quit()
        return pin

if __name__ == '__main__':
    twitter = Twitter()
    media_id_list = [1619692241823453184,1619692269963018242]
    twitter.get_pin_test("EO9wbAAAAAABlchRAAABhf5GDUg")
    #twitter.post_picture(payload={"text":"blabla", "media": {"media_ids": list(map(str, media_id_list))}})
else:
    from libs.JsonCreator import *