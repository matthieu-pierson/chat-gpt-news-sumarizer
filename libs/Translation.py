from googletrans import Translator
import requests
import deepl
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time
from rake_nltk import Rake
import re
from google_trans_new import google_translator
from libs.Article import *

class Translation:
    def __init__(self, auth_key = "c588265f-3408-7672-c98d-36f15eb49be7:fx"):
        self.translator = Translator(service_urls=[
            'translate.google.com',
            'translate.google.fr',
        ])
        self.auth_key = auth_key
        self.is_deepl_ko = False

    def traduce_google(self,text,dest="en",src="auto"):
        result = ''
        for sentence in self.parse_text(text):
            result += self.translator.translate(sentence,dest,src).text+" "
        return result

    def traduce_deepl(self,text,dest="en",src="fr"):
        if(dest == "en"):
            dest = dest+"-US"
        translator = deepl.Translator(self.auth_key)
        result = translator.translate_text(text, source_lang=src, target_lang=dest)
        return result.text

    def traduce_deepl_free(self,text,dest="en",src="fr"):
        url = "https://www2.deepl.com/jsonrpc?method=LMT_handle_jobs"
        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "LMT_handle_jobs",
        "params": {
            "jobs": [
            {
                "kind": "default",
                "sentences": [
                {
                    "text": text,
                    "id": 0,
                    "prefix": ""
                }
                ],
                "raw_en_context_before": [],
                "raw_en_context_after": [],
                "preferred_num_beams": 4,
                "quality": "fast"
            }
            ],
            "lang": {
            "preference": {
                "weight": {
                "DE": 0.29472,
                "EN": 1.56956,
                "ES": 0.39514,
                "FR": 9.06557,
                "IT": 0.4715,
                "JA": 0.11421,
                "NL": 1.34979,
                "PL": 0.3278,
                "PT": 0.36332,
                "RU": 0.11043,
                "ZH": 0.09739,
                "BG": 0.08241,
                "CS": 0.33156,
                "DA": 0.43522,
                "EL": 0.08123,
                "ET": 0.35525,
                "FI": 0.2337,
                "HU": 0.16786,
                "ID": 0.20169,
                "LV": 0.08526,
                "LT": 0.31333,
                "RO": 0.21008,
                "SK": 0.38899,
                "SL": 0.22984,
                "SV": 0.31588,
                "TR": 0.1577,
                "UK": 0.09376
                },
                "default": "default"
            },
            "source_lang_user_selected": src.upper(),
            "target_lang": dest.upper()
            },
            "priority": -1,
            "commonJobParams": {
            "regionalVariant": "en-US",
            "mode": "translate",
            "browserType": 1,
            "formality": None
            },
            "timestamp": 12124
        },
        "id": 743465
        })
        headers = {
        'authority': 'www2.deepl.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,de;q=0.5,no;q=0.4',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': self.get_deepl_cookies(),
        'origin': 'https://www.deepl.com',
        'pragma': 'no-cache',
        'referer': 'https://www.deepl.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print("Status Code", response.status_code)
        print("JSON Response ", response.json())
        json_str = json.dumps(response.json())
        resp = json.loads(json_str)
        traduced_text = resp['result']['translations'][0]['beams'][0]["sentences"][0]["text"]
        return traduced_text

    def get_deepl_cookies(self):
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.deepl.com/translator")
        time.sleep(2)
        cookies = driver.get_cookies()
        print(cookies)
        cookie_header = ''
        for cookie in cookies:
            cookie_header = cookie_header + cookie['name'] + "=" + cookie['value'] + ";"
        cookie_header += "LMTBID=v2|0bdbff88-445a-4188-8536-0782505cae19|e8fc4c9cad429c87b62142b646ca6192; dl_logoutReason=%7B%22loggedOutReason%22%3A%22USER_REQUEST%22%7D;"
        cookie_header += "LMTBID=v2|9a5aa2ff-63ac-412b-be5f-afeb4c6336fa|9eac7ebdcf0acc0afbaca2bb135661fe"
        time.sleep(2)
        return cookie_header

    def get_translation(self,article,eco,summary=False,dest="en",src="fr"):
        if(summary == False):
            if(dest=="en" and src=="fr"):
                text = article.get_article_FR()
            else:
                text = article.get_article_EN()
        else:
            if(dest=="en" and src=="fr"):
                text = article.get_summary_FR()
            else:
                text = article.get_summary_EN()
        traduction = "none"
        if(eco == True):
            try:
                traduction = self.traduce_google(text,dest,src)
                article.title_EN = self.traduce_google(article.title_FR,dest,src)
                print("Translation done with Google Translation")
            except Exception as e:
                print(e)
                print("Translation failled with Google Translation")
        else:
            try:
                if(self.is_deepl_ko == False):
                    traduction = self.traduce_deepl(text,dest,src)
                    article.title_EN = self.traduce_deepl(article.title_FR,dest,src)
                    print("Translation done with DeepL API")
                else:
                    raise Exception('message', 'Skip DeepL translation')
            except Exception as e:
                print(e)
                self.is_deepl_ko = True
                print("Translation failled with DeepL API")
                try:
                    traduction = self.traduce_google(text,dest,src)
                    article.title_EN = self.traduce_google(article.title_FR,dest,src)
                    print("Translation done with Google Translation")
                except Exception as e:
                    print(e)
                    print("Translation failled with Google Translation")
        return traduction


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

if __name__ == '__main__':
    translation = Translation()
    src = """La garde à vue du Youtubeur Norman Thavaud pour viol et corruption de mineur a été levée mardi soir "pour poursuite d'enquête", sans poursuites à ce stade, a indiqué le parquet de Paris à l'AFP. L'animateur de la chaîne "Norman fait des vidéos" aux douze millions d'abonnés avait été placé en garde à vue lundi dans le cadre d'une enquête préliminaire confiée à la Brigade de protection des mineurs (BPM), ouverte en janvier 2022. Six jeunes femmes ont porté plainte contre le youtubeur, selon le ministère public. Plusieurs sources indiquaient depuis lundi à l'AFP que la garde à vue de Norman ne déboucherait pas forcément sur des poursuites, en l'état du dossier. Selon le journal Libération, cinq des plaignantes accuseraient Norman Thavaud de viol et deux étaient mineures au moment des faits. En 2020, une fan québécoise, Maggie D., avait publiquement accusé Norman Thavaud de l'avoir manipulée pour obtenir des photos et vidéos à caractère sexuel, alors qu'elle avait selon elle 16 ans à ce moment-là. Elle avait indiqué avoir porté plainte au Canada. Dans le cadre d'une enquête québéco-française publiée par le média Urbania en avril 2021, d'autres femmes avaient formulé des accusations comparables à l'encontre du youtubeur pour des faits qui se seraient produits alors que certaines étaient encore mineures. Interrogée par l'AFP, Maggie D. a confirmé être en France pour être confrontée ce mardi à Norman Thavaud devant les enquêteurs, comme l'a indiqué Libération. Norman, troisième youtubeur français en nombre d'abonnés, fait figure d'ancien, après avoir fait ses débuts en 2011 sur la plateforme. Ses vidéos, selon un décompte officiel, ont été vues plus de 2,7 milliards de fois. Porte-drapeau d'une nouvelle génération d'humoristes nés sur les réseaux sociaux, ce monteur de 
formation s'est fait connaître au début des années 2010 avec des séquences inspirées de sa vie quotidienne ("Avoir un chat", "Les toilettes") ou des jeux vidéo ("Luigi clash Mario"). Passionné de stand-up, il est monté sur scène pour deux spectacles en solo entre 2015 et 2020, en plus de quelques apparitions au cinéma ("Mon roi") et à la télévision ("Dix pour cent"). En 2018, le youtubeur français numéro un, Squeezie (17,6 million d'abonnés) avait dénoncé sur Twitter "les YouTubers (y compris ceux qui crient sur tous les toits qu'ils sont féministes) qui profitent de la vulnérabilité psychologique de jeunes abonnées pour obtenir des rapports sexuels". Son tweet avait été énormément rediffusé dans le cadre du mouvement #balancetonyoutubeur. Certains témoignages avaient visé Norman. Squeezie a assuré par la suite que cela ne visait "pas du tout" Norman. Lundi, le groupe Webedia (AlloCiné, PurePeople...) a annoncé suspendre sa collaboration avec l'icône de 35 ans, qui a séduit toute une génération en parodiant la vie quotidienne depuis sa coloc' de Montreuil (Seine-Saint-Denis)."""
    src="""The ban on disposable dishes in fast food for meals taken on site came into force on January 1. Large fast food brands, which serve around 6 billion meals per year in 40,000 establishments, are particularly targeted by law - which also applies to collective catering."""
    result = translation.get_translation(src,eco=True)
    print(result)
    result = translation.get_translation(result,dest='fr',src="en",eco=True)
    print(result)
