import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from transformers import pipeline
from string import punctuation
from heapq import nlargest
import re
import os
import openai
import torchtext

class Summarizer:
    def __init__(self):
        self.current_summarizer = "none"

    def BasicSummarize(self,text, per):
        nlp = spacy.load("en_core_web_sm")
        doc= nlp(text)
        tokens=[token.text for token in doc]
        word_frequencies={}
        for word in doc:
            if word.text.lower() not in list(STOP_WORDS):
                if word.text.lower() not in punctuation:
                    if word.text not in word_frequencies.keys():
                        word_frequencies[word.text] = 1
                    else:
                        word_frequencies[word.text] += 1
        max_frequency=max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word]=word_frequencies[word]/max_frequency
        sentence_tokens= [sent for sent in doc.sents]
        sentence_scores = {}
        for sent in sentence_tokens:
            for word in sent:
                if word.text.lower() in word_frequencies.keys():
                    if sent not in sentence_scores.keys():                            
                        sentence_scores[sent]=word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent]+=word_frequencies[word.text.lower()]
        select_length=int(len(sentence_tokens)*per)
        summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
        final_summary=[word.text for word in summary]
        summary=''.join(final_summary)
        return summary

    def AvgSentenceLenght(self,text):
        sentences = text.split(".") #split the text into a list of sentences.
        words = text.split(" ") #split the input text into a list of separate words
        if(sentences[len(sentences)-1]==""): #if the last value in sentences is an empty string
            actual_average_sentence_length = len(words) / len(sentences)-1
        else:
            actual_average_sentence_length = len(words) / len(sentences)
        return actual_average_sentence_length #returning avg length of sentence
    
    def count_words(self,sentence):
        words = sentence.split()
        return len(words)

    def count_tokens(self,text):
        tokenizer = torchtext.data.utils.get_tokenizer("basic_english")
        tokens = tokenizer(text)
        return len(tokens)

    def final_summarize(self,article,eco):
        article_final = article.get_article_EN()
        if(eco==True):
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            ratio = 0.9
            final_sum = 'none'
            has_failled = False
            if(article_final != 'none' and len(article_final)>512):
                while ratio > 0:
                    try:
                        if(self.count_tokens(article_final)>1024 or has_failled == True):
                            print("Trying sumup with ratio : "+"%0.1f"%ratio)
                            sumup = self.BasicSummarize(article_final, ratio)
                            result = ''
                            for sentence in self.parse_text(sumup):
                                result += sentence+" "
                            sumup = result
                        else:
                            sumup = article_final
                        """print("Shorten article :\n",sumup)
                        print(len(sumup))"""
                        final_sum = summarizer(sumup, max_length=256, min_length=64, do_sample=False)[0]['summary_text']
                        print("Text shortener successful !")
                        break
                    except Exception as e:
                        print("Failling :", e)
                        ratio = ratio - 0.1
                        if(has_failled == False):
                            has_failled = True
            self.current_summarizer = "BART + spacy"
        else:
            final_sum= self.openAI_summarizer(article_final)
            self.current_summarizer = "openAI"
        print("Shorten article :\n",final_sum)
        return(final_sum)

    def openAI_summarizer(self,article_final):
        openai.api_key = "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"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Summarize the following text in formal language, no contracted words in at least two sentence and no more than 128 characters : \n\n"+article_final,
            #Summarize the following text in formal language, no contracted words in at least two sentence and no more than 256 characters :
            #Summarize the following text in formal language with no more than 128 characters and no contracted words :
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        #print(response)
        final_sum = str(response["choices"][0]["text"]).replace("\n\n","")
        if(len(final_sum)>410):
            final_sum = self.cut_text_under_410(final_sum)
        return(final_sum)

    def cut_text_under_410(self,text):
        print("Text longer than 410 characters, start shrinking")
        sentences = self.parse_text(text)
        for i in range(len(sentences)):
            print("Sentence removed :", sentences[-1])
            sentences = sentences[:-1]
            current_text_size = sum(len(i) for i in sentences)
            if(current_text_size<=410):
                print("End shrink")
                break
        result = ''
        for sentence in sentences:
            result += sentence+" "
        print('Final characters count :', len(result))
        return result
            

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
    summarizer = Summarizer()
    print(summarizer.cut_text_under_410("""The use of Pegasus spy software against journalists and human rights defenders is the focus of three videos. One video looks at the case of Mexico in 2014, where it is proven that former judge Tomas Zeron attempted to sabotage the investigation of a mass crime. NSO customers in Mexico were two intelligence agencies, and the Office of the Public Prosecutor of the Republic used the software to spy on 15,000 people from 2014-2017. Mr. Zeron was responsible for shedding light on the disappearance of 43 students from Ayotzinapa Normal School."""))