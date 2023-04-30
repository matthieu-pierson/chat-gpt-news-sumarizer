import os
import json
import time
import uuid

class JsonCreator:
    def __init__(self):
        timestr = time.strftime("%Y%m%d")
        self.filepath_json = "cache/"+timestr+"posts.json"
        self.data_json = ''

    def create_json(self,article,summarizer):
        text_fr = article.get_summary_FR()
        text_en = article.get_summary_EN()
        tags_fr = article.hashtags_FR
        tags_en = article.hashtags_EN
        image_path = article.img_path
        image_url = article.img_url
        article_url = article.url
        summarizer_type = summarizer.current_summarizer
        publish_date = article.publish_date
        uuid4 = str(uuid.uuid4())
        data = {
                    'posts' : [
                        {
                            'text_en' : text_en,
                            'text_fr' : text_fr,
                            'summarizer' : summarizer_type,
                            'tags_en' : tags_en,
                            'tags_fr' : tags_fr,
                            'image_path' : image_path,
                            'image_url' : image_url,
                            'source' : article_url,
                            'publish_date' : publish_date,
                            'uuid' : uuid4,
                            'is_posted' : "false"
                        }
                    ]
                }
        return data
    
    def read_json(self):
        self.dummy_json()
        with open(self.filepath_json, 'r', encoding="utf-8") as infile:
            self.data_json = json.load(infile)
        return self.data_json

    def dict_compare(d1, d2):
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        added = d1_keys - d2_keys
        removed = d2_keys - d1_keys
        modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
        same = set(o for o in shared_keys if d1[o] == d2[o])
        return added, removed, modified, same

    def dummy_json(self):
        if(os.path.exists(self.filepath_json) == False or os.stat(self.filepath_json).st_size == 0):
            dummy = {
                        'posts' : [
                        ]
                    }
            with open(self.filepath_json, 'w+', encoding="utf-8") as outfile:
                outfile.write(json.dumps(dummy, sort_keys=True, ensure_ascii=False))
    
    def append_post_if_not_there(self,data, json_object_to_append):
        self.dummy_json()
        current_traduced_articles = self.list_articles_already_traduced()
        if(isinstance(data, dict)):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        if(isinstance(json_object_to_append, dict)):
            json_object_to_append_str = json.dumps(json_object_to_append['posts'][0], sort_keys=True, ensure_ascii=False)
        """print(data_str)
        print(json_object_to_append_str)"""
        data_parsed_json = json.loads(data_str)
        object_to_append_json = json.loads(json_object_to_append_str)
        to_append = True
        for post in data_parsed_json['posts']:
            post = str(post).replace("\'","\"")
            """print(post,"post")
            print(json_object_to_append_str,"json_object_to_append_str")"""
            if(object_to_append_json['source'] in current_traduced_articles):
                print('Object already in json database')
                to_append = False
                break

        if(to_append == True):
            data["posts"].append(json_object_to_append["posts"][0])
            print('Appending post to json database\n',json_object_to_append["posts"][0])
            #print('Appending post to json database\n',data)

        json_string = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
        with open(self.filepath_json, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)

    def list_articles_already_traduced(self):
        list_traduced = []
        if(self.data_json ==""):
            data_json = self.read_json()
        else:
            data_json = self.data_json
        if(isinstance(data_json, dict)):
            data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
        data_parsed_json = json.loads(data_str)
        for post in data_parsed_json["posts"]:
            if(post['source']!="none"):
                list_traduced.append(post['source'])
        return list_traduced

    def list_articles_not_posted(self):
        list_not_posted = []
        if(self.data_json ==""):
            data_json = self.read_json()
        else:
            data_json = self.data_json
        if(isinstance(data_json, dict)):
            data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
        data_parsed_json = json.loads(data_str)
        try:
            for post in data_parsed_json["posts"]:
                if(post['is_posted']=="false"):
                    list_not_posted.append(post['source'])
        except Exception as e:
            print(e)
        return list_not_posted

    def is_article_in_json(self):
        list_traduced = []
        if(self.data_json ==""):
            data_json = self.read_json()
        else:
            data_json = self.data_json
        if(isinstance(data_json, dict)):
            data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
        data_parsed_json = json.loads(data_str)
        for post in data_parsed_json["posts"]:
            if(post['source']!="none"):
                list_traduced.append(post['source'])
        return list_traduced

    def get_json_data(self,article_url,data_type):
        entries = ["image_path","image_url","is_posted","publish_date","source","summarizer","tags_en","tags_fr","text_en","text_fr","uuid"]
        if(data_type in entries):
            if(self.data_json ==""):
                data_json = self.read_json()
            else:
                data_json = self.data_json
            if(isinstance(data_json, dict)):
                data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
            data_parsed_json = json.loads(data_str)
            for post in data_parsed_json["posts"]:
                if(post['source']==article_url):
                    return post[data_type]
        else:
            print("Bad entry key selection, accepted entries :", entries)
            print("Current entry :", data_type)
            return False

    def set_article_to_is_posted(self,article_url):
        data = []
        flag = False
        if(self.data_json ==""):
            data_json = self.read_json()
        else:
            data_json = self.data_json
        if(isinstance(data_json, dict)):
            data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
        data_parsed_json = json.loads(data_str)
        for post in data_parsed_json["posts"]:
            if(post['source']==article_url and post['is_posted']!="true"):
                post['is_posted']="true"
                flag = True
            data.append(post)
        if(flag==True):
            data = {'posts':data}
            json_string = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
            with open(self.filepath_json, 'w', encoding="utf-8") as outfile:
                outfile.write(json_string)
                self.read_json()
            print("Article",article_url,"set to posted !")
        else:
            print("Article",article_url,"already set to posted or not found!")

    def load_json_to_article(self,article_url):
        article = Article()
        entries = ["image_path","image_url","is_posted","publish_date","source","summarizer","tags_en","tags_fr","text_en","text_fr","uuid"]
        article.set_img_path(self.get_json_data(article_url,entries[0]))
        article.set_img_url(self.get_json_data(article_url,entries[1]))
        article.set_is_posted(self.get_json_data(article_url,entries[2]))
        article.set_publish_date(self.get_json_data(article_url,entries[3]))
        article.set_source(self.get_json_data(article_url,entries[4]))
        article.set_hashtags_EN(self.get_json_data(article_url,entries[6]))
        article.set_hashtags_FR(self.get_json_data(article_url,entries[7]))
        article.set_summary_EN(self.get_json_data(article_url,entries[8]))
        article.set_summary_FR(self.get_json_data(article_url,entries[9]))
        article.set_uuid(self.get_json_data(article_url,entries[10]))
        return article

    def set_key_to(self,uuid,key,value):
        data = []
        flag = False
        if(self.data_json ==""):
            data_json = self.read_json()
        else:
            data_json = self.data_json
        if(isinstance(data_json, dict)):
            data_str = json.dumps(data_json, sort_keys=True, ensure_ascii=False)
        data_parsed_json = json.loads(data_str)
        for post in data_parsed_json["posts"]:
            if(post['uuid']==uuid and key not in post):
                post[key]=value
                flag = True
            elif(post['uuid']==uuid and post[key]!=value):
                post[key]=value
                flag = True
            data.append(post)
        if(flag==True):
            data = {'posts':data}
            json_string = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
            with open(self.filepath_json, 'w', encoding="utf-8") as outfile:
                outfile.write(json_string)
                self.read_json()
            print("Article",uuid,"key",key,"set to",value)
        else:
            print("Article",uuid,"key",key,"already set to",value)

if __name__ == '__main__':
    from Article import *
    jsoncreator = JsonCreator()
    #jsoncreator.create_json(text='none',tags='none',image_path='none',image_url='none',article_url='none')
    jsoncreator.read_json()
    """data_to_append = {
                        "posts": [
                            {
                                "image_path": "cache/img/2023-01-12/010be87_1673552082509-000-336x9c2.jpg",
                                "image_url": "https://img.lemde.fr/2023/01/12/0/0/7936/5291/1440/960/60/0/010be87_1673552082509-000-336x9c2.jpg",
                                "publish_date": "01/12/2023",
                                "source": "https://www.lemonde.fr/international/article/2023/01/12/en-argentine-une-inflation-record-de-presque-95-pour-2022_6157646_3210.html",
                                "summarizer": "openAI",
                                "tags_en": "#record #figure #argentina #inflation #year #rate ",
                                "tags_fr": "#chiffre #record #argentine #inflation #année #taux ",
                                "text_en": "Argentina's inflation rate is 94. 8% in 2022, the highest in 32yrs. Relative deceleration in recent months, with 2021 expected to reach 50. 9% and gov't aiming for 60% by 2023. ",
                                "text_fr": "Le taux d'inflation de l'Argentine est de 94. 8 % en 2022, soit le taux le plus élevé depuis 32 ans. Décélération relative au cours des derniers mois, l'inflation devrait atteindre 50,9% en 2021. 9% en 2021 et le gouvernement vise 60% en 2023. ",
                                "uuid": "77857bab-2201-4cf2-8b37-448547138242",
                                'is_posted' : "false"
                            }
                        ]
                    }
    jsoncreator.append_post_if_not_there(jsoncreator.data_json,data_to_append)
    jsoncreator.list_articles_already_traduced()
    myarticle = jsoncreator.load_json_to_article("https://www.lemonde.fr/culture/article/2023/01/17/kamala-harris-une-ambition-americaine-et-une-enigme-sur-arte_6158258_3246.html")
    jsoncreator.set_article_to_is_posted("https://www.lemonde.fr/international/article/2023/01/17/qatargate-pier-antonio-panzeri-pret-a-collaborer-avec-la-justice-belge_6158251_3210.html")"""
    jsoncreator.set_key_to("0237e6d5-dd21-4c2d-a982-495f4bd281a6","twitter_media_id","1618950216715063296")
else :
    from libs.Article import *