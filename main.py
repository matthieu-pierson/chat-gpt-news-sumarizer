import sys
import time
from libs.Rss import *
from libs.Article import *
#from libs.Instagram import *
from libs.Summarizer import *
from libs.Translation import *
from libs.JsonCreator import *
from libs.Template import *

start_time = time.time()
original_stdout = sys.stdout

jsoncreator = JsonCreator()
translation = Translation()
summarizer = Summarizer()
template = Template(jsoncreator)
#instagram = Instagram()
rss = Rss(filepath_rss="config/rss_feeds")
"""i = 0"""
eco = False
articles_already_traduced = jsoncreator.list_articles_already_traduced()
articles_of_the_day = rss.articles_of_the_day()
total_articles = len(articles_of_the_day)
for i,article_url in enumerate(articles_of_the_day):
    if(article_url not in articles_already_traduced):
        article = Article(url=article_url)
        article.set_article_FR(article.get_article_web())
        article.set_article_EN(translation.get_translation(article,eco,summary=False,dest="en",src="fr"))
        print("Article FR:\n", article.title_FR + article.get_article_FR())
        print("Article EN:\n", article.title_EN + article.get_article_EN())
        article.set_summary_EN(article.corr(summarizer.final_summarize(article,eco)))
        article.set_hashtags('en')
        article.set_summary_FR(article.corr(translation.get_translation(article,eco,summary=True,dest="fr",src="en")))
        article.set_hashtags('fr')
        #summarizer.current_summarizer = "base"
        #article.set_summary_FR(article.corr(article.get_nlp_summary()))
        #article.set_summary_EN(article.corr(translation.get_translation(article,eco,summary=True,dest="en",src="fr")))
        print("Summary FR:\n", article.title_FR + article.get_summary_FR())
        print("Summary EN:\n", article.title_EN + article.get_summary_EN())
        json_post = jsoncreator.create_json(article,summarizer)
        jsoncreator.append_post_if_not_there(jsoncreator.read_json(),json_post)
        #instagram.post_picture(path="cache/thumbnail_crop.jpg",caption=article.get_summary_FR()+"\n"+article.get_hashtags())
        print(i,"/",total_articles," --- %s seconds ---" % (time.time() - start_time))
        """i+=1
        if(i==1):
            break"""
    else:
        print("Already in json", article_url)

template.generate_all_posts()