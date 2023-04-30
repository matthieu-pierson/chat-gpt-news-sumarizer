import os
import time
import newspaper
import requests
import spacy
from datetime import date
from collections import Counter
from string import punctuation
from bs4 import BeautifulSoup as bs
from PIL import Image
import re
from better_profanity import profanity
from urllib.parse import urlparse

class Article:
    def __init__(self, url='https://www.ladepeche.fr/2022/12/06/norman-thavaud-accuse-de-viol-la-garde-a-vue-du-youtubeur-levee-10851329.php'):
        self.start_time = time.time()
        self.url = url
        self.article = 'none'
        self.article_str= 'none'
        self.article_FR = 'none'
        self.article_EN = 'none'
        self.img_path = 'none'
        self.img_url = 'none'
        self.summary_FR = 'none'
        self.summary_EN = 'none'
        self.hashtags_FR = 'none'
        self.hashtags_EN = 'none'
        self.domain = 'none'
        self.publish_date = 'none'
        self.title_FR = 'none'
        self.title_EN = 'none'
        self.topic_FR = 'none'
        self.topic_EN = 'none'
        self.uuid = 'none'
        self.is_posted = 'none'
    
    def convert_url_to_domain_name(self):
        domain = urlparse(self.url).netloc
        self.domain = domain

    def get_article_web(self):
        self.convert_url_to_domain_name()
        print("Downloading article from", self.domain, "-->", self.url)
        if (self.domain == "www.ladepeche.fr"):
            self.article_FR = self.get_article_web_depeche()
            return self.article_FR
        elif (self.domain == "www.lemonde.fr"):
            self.article_FR = self.get_article_web_lemonde()
            return self.article_FR
        else:
            print("Impossible to get the article")
    
    def get_article_web_base(self):
        self.article = newspaper.Article(self.url)
        self.article .download()
        self.article .parse()
        article_final = self.article.text
        article_final = " ".join(article_final.split())
        self.article_str = article_final
        print(article_final)
        self.get_images()
        self.crop_to_1_to_1()
        return article_final

    def get_article_web_depeche(self):
        self.article = newspaper.Article(self.url)
        self.article .download()
        self.article .parse()
        soup = bs(self.article .html,'html.parser')
        div = soup.find("div", {"class": "article-full__body-content"})
        article_final = ''
        for match in div.find_all('span'):
            match.replace_with('')
        for match in div.find_all("p"):
            article_final += " "+ match.get_text()
        article_final = " ".join(article_final.split())
        self.article_str= article_final
        #print(article_final
        self.get_images()
        self.crop_to_1_to_1()
        self.publish_date = self.article.publish_date.strftime("%m/%d/%Y")
        return article_final

    def get_article_web_lemonde(self):
        self.article = newspaper.Article(self.url)
        self.article .download()
        self.article .parse()
        soup = bs(self.article .html,'html.parser')
        article_final = ''
        div = soup.select_one(".article__content")
        if (div.find('h2')):
            for match in div.find_all('h2'):
                match.replace_with('')
        if (div.find('h3')):
            for match in div.find_all('h3'):
                match.replace_with('')
        if (div.find('article')):
            for match in div.find_all('article'):
                match.replace_with('')
        if (div.find('a', href=True)):
            for match in div.find_all('a', href=True):
                match.replace_with('')
        if (div.find('div',class_='twitter-tweet')):
            for match in div.find_all('div',class_='twitter-tweet'):
                print("found")
                match.replace_with('')
        if (div.find('blockquote')):
            for match in div.find_all('blockquote'):
                match.replace_with('')
        if (div.find('section')):
            for match in div.find_all('section'):
                match.replace_with('')
        if (div.find('figcaption')):
            for match in div.find_all('figcaption'):
                match.replace_with('')
        if (div.find('span')):
            for match in div.find_all('span'):
                match.replace_with('')
        if (div.find('strong')):
            for match in div.find_all('strong'):
                match.replace_with('')
        if (div.find('p')):
            for match in div.find_all("p"):
                article_final += " "+ match.get_text()
        article_final = re.sub(r"\S*https?:\S*", "", article_final) #removes hyperlinks
        article_final = " ".join(article_final.split())
        self.title_FR = self.article.title + ". "
        self.article_str = article_final
        self.get_images()
        self.crop_to_1_to_1()
        self.crop_to_16_to_9()
        self.publish_date = self.article.publish_date.strftime("%m/%d/%Y")
        return article_final

    def get_images(self):
        article = newspaper.Article(url=self.url)
        article.download()
        article.parse()
        top_image = article.top_image
        self.img_url = top_image
        print(top_image)
        r = requests.get(top_image, allow_redirects=True)
        print(r.headers.get('content-type'))
        path = "cache/img/"+str(date.today())+"/"
        self.img_path = "cache/img/"+str(date.today())+"/"+self.img_url.split("/")[-1].split(".")[0]+".jpg"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        open(self.img_path, 'wb').write(r.content)

    def crop_to_1_to_1(self):
        im = Image.open(self.img_path)
        im = im.convert('RGB')
        width, height = im.size
        new_width = height
        new_height = height
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2
        im = im.crop((left, top, right, bottom))
        im.save("cache/img/"+str(date.today())+"/"+self.img_url.split("/")[-1].split(".")[0]+"1x1.jpg")

    def crop_to_16_to_9(self):
        img = Image.open(self.img_path)
        img = img.convert('RGB')
        original_size = img.size
        if self.is16to9(img):
            cropped_img = img
        else:
            width = original_size[0]
            height = original_size[0] * 9 / 16
            upper = (original_size[1] - height) / 2
            box = (0, upper, width, upper + height)
            cropped_img = img.crop(box)
        cropped_img.save("cache/img/"+str(date.today())+"/"+self.img_url.split("/")[-1].split(".")[0]+"16x9.jpg")

    def is16to9(self,img):
        img.size
        return img.size[0] * 9 == img.size[1] * 16

    def get_hotwords(self,language):
        if(language == "en"):
            if(self.get_article_EN()!='none'):
                result_en = []
                pos_tag = ['PROPN', 'ADJ', 'NOUN'] # 1
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(self.get_article_EN().lower()) # 2
                for token in doc:
                    # 3
                    if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
                        continue
                    # 4
                    if(token.pos_ in pos_tag):
                        result_en.append(token.text)
                return result_en# 5
            else:
                print("No article_EN found")
                return False
        else:
            if(self.get_article_FR()!='none'):
                result_fr =[]
                pos_tag = ['PROPN', 'ADJ', 'NOUN'] # 1
                nlp = spacy.load("fr_core_news_sm")
                doc = nlp(self.get_article_FR().lower()) # 2
                for token in doc:
                    # 3
                    if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
                        continue
                    # 4
                    if(token.pos_ in pos_tag):
                        result_fr.append(token.text)
                return result_fr# 5
            else:
                print("No article_FR found")
                return False        

    def get_nlp_summary(self):
        self.article.nlp()
        result = ''
        for sentence in self.parse_text(self.article.summary):
            result += sentence+" "
        return result

    def set_hashtags(self,language):
        hotwords = self.get_hotwords(language)
        result = ''
        for i in range(len(hotwords)):
            if(profanity.contains_profanity(hotwords[i])!=True):
                result = result + "#"+hotwords[i]+" "
            if(i==5):
                break
        if(language =='en'):
            self.hashtags_EN = result
        else:
            self.hashtags_FR = result

    def parse_text(self,text):
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        digits = "([0-9])"

        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
        if "..." in text: text = text.replace("...","<prd><prd><prd>")
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences

    def corr(self,s):
        return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', s))

    def get_source(self):
        return self.article.authors

    def get_article(self):
        return self.article

    def set_article(self, article):
        self.article_str = article

    def get_article_FR(self):
        return self.article_FR

    def set_article_FR(self, article_FR):
        self.article_FR = article_FR

    def get_article_EN(self):
        return self.article_EN

    def set_article_EN(self, article_EN):
        self.article_EN = article_EN

    def get_summary_FR(self):
        return self.summary_FR

    def set_summary_FR(self, summary_FR):
        self.summary_FR = summary_FR

    def get_summary_EN(self):
        return self.summary_EN

    def set_summary_EN(self, summary_EN):
        self.summary_EN = summary_EN

    def get_img_path(self):
        return self.img_path

    def set_img_path(self, img_path):
        self.img_path = img_path

    def get_img_url(self):
        return self.img_url

    def set_img_url(self, img_url):
        self.img_url = img_url

    def get_publish_date(self):
        return self.publish_date

    def set_publish_date(self, publish_date):
        self.publish_date = publish_date

    def get_source(self):
        return self.url

    def set_source(self, url):
        self.url = url

    def get_hashtags_FR(self):
        return self.hashtags_FR

    def set_hashtags_FR(self, hashtags_FR):
        self.hashtags_FR = hashtags_FR

    def get_hashtags_EN(self):
        return self.hashtags_EN

    def set_hashtags_EN(self, hashtags_EN):
        self.hashtags_EN = hashtags_EN

    def get_uuid(self):
        return self.uuid

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_is_posted(self):
        return self.is_posted

    def set_is_posted(self, is_posted):
        self.is_posted = is_posted


if __name__ == '__main__':
    article = Article(url="https://www.lemonde.fr/sport/article/2022/12/29/mort-de-pele-les-ambiguites-politiques-du-roi-du-football-loin-des-terrains_6156025_3242.html")
    #article = Article(url="https://www.lemonde.fr/international/live/2023/01/02/guerre-en-ukraine-en-direct-des-coupures-de-courant-a-kiev-apres-de-nouveaux-bombardements-russes_6156281_3210.html")
    #article.get_article_web()
    article.get_article_web()
    
    article.set_article_EN("""Pelé in Copenhagen, on the occasion of a meeting of the International Olympic Committee, October 1, 2009. FRANCK FIFE / AFP Pelé, "king" of football, but also of controversy. Celebrated around the world for his exceptional sports performances, the football star has also been the target of intense criticism in Brazil. At issue: controversial positions held during and after his playing career. Between passivity, slippages, conservatism and indifference to the major issues of society in his country. The main grievance concerns the period of the military dictatorship (1964-1985). Come
in power in 1969, General Emilio Garrastazu Médici accentuated the repression on a Brazil where freedoms were suspended and the torture of opponents generalized. To hide its crimes, the junta needs a resounding international success. Victory at the 1970 Mexican World Cup became his priority. At almost 30 years old, Pelé is at the top of his game. “He was the most famous human figure in the world. For Médici, it was crucial to appropriate his image, ”recalls Euclides de Freitas Couto, specialist in the links between football and politics. As the tournament approached, the dictatorship affixed the figure of the "king" of football to its propaganda posters, accompanied by nationalist slogans ("Love Brazil or leave it", "Nobody can remember this country ! "…). Pelé does not protest and becomes without flinching the radiant face of a sinister dictatorship. Back home after his victory against Italy, the young "king" went straight to Brasilia, to win the Jules-Rimet Cup with a smile alongside General Medici. We will never hear him utter a word of support for political prisoners. "Brazilians don't know how to vote", he will go so far as to let go, suspicious of democracy. Courted by all the presidents "Pelé was not strictly speaking a supporter of the dictatorship", however nuance Ademir Takara, librarian at the Sao Paulo Football Museum. The player did not always maintain good relations with the generals and even, for a time, suffered the wrath of the regime because of his refusal to participate in the 1974 World Cup. Criticized, threatened, "Pelé then goes from status of puppet to that of “traitor to the fatherland”, continues the researcher. “I have always opened the doors to those in power who were looking for me,” Pelé put it into perspective. Over the course of his victories, the star was actually received and courted by all the successive presidents, democrats and dictators, on the right, but also on the left. Among them, the founder of Brasilia, Juscelino Kubitschek, the Labor Joao Goulart, or, later, the former "metalworker" Lula. “He maintained an apolitical posture” and “received the blessing of all governments”, sums up Ademir Takara. You have 61.95% of this article left to read. The following is for subscribers only.""")
    print(article.get_article_EN())
    print("\n")
    print(article.get_nlp_summary())
    print("\n")
    print(article.get_article_FR())
    print(article.set_hashtags('en'))
    