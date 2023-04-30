import sys
import os
import time
from html2image import Html2Image
from unidecode import unidecode
from PIL import Image
from libs.JsonCreator import *

class Template:
    def __init__(self,jsoncreator):
        self.root = "template"
        self.lang = ['fr','en']
        self.jsoncreator = jsoncreator
        self.hti = Html2Image()
        timestr = time.strftime("%Y%m%d")
        abspath = os.path.abspath(__file__)
        self.abs_root =  os.path.dirname(os.path.dirname(abspath)).replace("\\","/")
        print(self.abs_root)

    def generate_post(self,page_name,html_str,css_str):
        if(not os.path.exists(self.root)):
            print("Creating folder")
            os.mkdir(self.root)
            print ("Created",self.root,"folder")
        print("Creating "+page_name+".html, style.css, script.js")
        index_html_path = self.root + "/"+page_name+".html"
        style_css_path = self.root + "/style.css"
        script_js_path = self.root + "/script.js"
        indexHtml = open(index_html_path, "w+", encoding="utf-8")
        styleCSS = open(style_css_path, "w+", encoding="utf-8")
        scriptJS = open(script_js_path, "w+", encoding="utf-8")

        indexHtml.write(html_str)
        styleCSS.write(css_str)
        scriptJS.write('')

        indexHtml.close()
        styleCSS.close()
        scriptJS.close()
        return index_html_path,style_css_path,script_js_path


    def generate_all_posts(self):
        data_json = self.jsoncreator.read_json()
        for lang in self.lang:
          for post in data_json['posts']:
              img_path = post["image_path"]
              publish_date = post["publish_date"]
              if (lang == "fr"):
                  temp_txt = post["text_fr"].split('.', 1)
                  first_text = temp_txt[0]+". "
              else:
                  temp_txt = post["text_en"].split('.', 1)
                  first_text = temp_txt[0]+". "
              text = temp_txt[1]
              uuid4 = post["uuid"]
              html_str = '''
              <!DOCTYPE html>
              <html lang="en" dir="ltr">
                  <head>
                      <meta charset="utf-8">
                      <title>Home Page</title>
                      <link rel="stylesheet" href="./style.css">
                      <link rel="preconnect" href="https://fonts.googleapis.com">
                      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap" rel="stylesheet"><link href='https://fonts.googleapis.com/css?family=Playfair Display' rel='stylesheet'>
                      <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap" rel="stylesheet">
                  </head>
                  <body>
                      <div id="rectangle">
                          <div class="banner">
                              <div id="name" class="left-column">
                                  Clear Times
                              </div>
                              <div class="right-column">
                                  <hr id="hr1">
                              </div>
                              <div id="logo-column" class="right-column-logo">
                                  <img id="logo" src = "'''+self.abs_root+'''/config/logo_close_orange.png">
                              </div>
                          </div>
                          
                          <img id = "thumbnail" src = "'''+self.abs_root+"/"+img_path+'''" />
                          <p id="text">
                              <span id="first-text">
                                  '''+first_text+'''
                              </span>
                              '''+text+'''
                          </p>
                          <div class="footer">
                              <div class="left-column-footer">
                                  <hr id="hr2">
                              </div>
                              <div id="name" class="right-column-footer">
                                  '''+publish_date+'''
                              </div>
                          </div>
                      </div>
                  <script src="./script.js" charset="utf-8"></script>
                  </body>
              </html>
              '''
              css_str='''
              * {
                  margin: 0;
                  padding: 0;
                }
                body { 
                  background: #111;
                  overflow:hidden;
                }

              body {
                  margin: 0;
                  width: 1080px;
                  height: 1080px;
                  padding-right: 300;
              }

              .myCanvas{
                width: 1080px;
                height: 1080px;
              }

              #rectangle{
                position:relative;
                width: 1080px;
                height: 1080px;
                background: rgb(212, 211, 207);
                z-index: 1;
                overflow: hidden;
                /*box-shadow: rgba(0, 0, 0, 0.25) 0px 14px 28px, rgba(0, 0, 0, 0.22) 0px 10px 10px;*/
                box-shadow: rgba(0, 0, 0, 0.25) 0px 14px 28px, rgba(0, 0, 0, 0.22) 0px 10px 10px;
                display: flex;
                flex-direction: column;
                justify-content: start;
                margin-bottom: auto;
              }

              .banner {
                display: flex;
              }

              .left-column {
                width: fit-content;
                margin-left: 40px;
                font-weight: bolder;
              }

              .right-column {
                flex: 1;
              }

              .footer {
                display: flex;
                margin-top: auto;
              }

              .left-column-footer {
                flex: 1;
              }

              .right-column-footer {
                
                width: fit-content;
                margin-right: 40px;
                font-weight: bolder;
              }

              #text {
                font-family: 'Poppins', sans-serif;
                font-size: 2rem;
                color: rgb(30, 57, 51);
                margin: 20px 40px;
                text-align: justify;
              }

              #thumbnail{
                padding-left: 40px;
                padding-right: 40px;
                height: 50%;
                width: auto;
                filter: saturate(40%);
                object-fit: cover;
              }

              #name{
                font-family: 'Poppins', sans-serif;
                font-size: 50px;
                padding-left: 20px;
                padding-right: 20px;
                background-color: rgb(194, 63, 45);
                color: rgb(212, 211, 207);
                margin-top: 20px;
                margin-bottom: 20px;
                line-height: 37px;
              }

              p > span{
                font-weight: bolder;
                color: rgb(194, 63, 45);
              }

              hr {
                display: block;
                height: 1px;
                border: 0;
                border-top: 3px solid rgb(194, 63, 45);
                margin: 20px 40px;
                padding: 0;
              }

              #hr2 {
                margin-top: 53px;
              }

              .right-column-logo {
                width: fit-content;
                margin-right: 40px;
                font-weight: bolder;
              }

              #logo-column{
                color: rgb(212, 211, 207);
                margin-top: 20px;
                line-height: 37px;
              }

              #logo{
                width: 44px;
              }
          
          '''
              index_html_path,style_css_path,script_js_path = self.generate_post(uuid4,html_str,css_str)
              self.create_post(uuid4,index_html_path,style_css_path,lang)
              if os.path.exists(index_html_path):
                  os.remove(index_html_path)
              else:
                  print("The file does not exist")
        print("End template creation")
        os.remove(style_css_path)
        os.remove(script_js_path)
    
    def remove_special_characters(self,text):
        characters_to_replace = ["<", ">", ":", "“", "/", "\\", "|", "?", "*", ",", "[", "]", "'", "\""]
        for ch in characters_to_replace:
            if ch in text:
                text=text.replace(ch,"")
        return text

    def create_post(self,page_name,index_html_path,style_css_path,lang):
        timestr = time.strftime("%Y%m%d")
        if(lang == "fr"):
            self.hti.output_path = 'F:/ai_news/template/img/'+timestr+"/"+"fr"+"/"
        else:
            self.hti.output_path = 'F:/ai_news/template/img/'+timestr+"/"+"en"+"/"
        if(not os.path.exists(self.root+"/img/"+timestr+"/"+lang+"/")):
            print("Creating folder")
            os.mkdir(self.root+"/img/"+timestr+"/"+lang+"/")
            print ("Created",self.root+"/img/"+timestr+"/"+lang+"/","folder")
        """abspath = os.path.abspath(__file__)
        root = os.path.dirname(os.path.dirname(abspath))
        os.chdir(root+"/template/img/")
        print(root)"""
        path_png = self.hti.screenshot(html_file=index_html_path, css_file=style_css_path, save_as=page_name+".png",size=(1080, 1080))
        path_png = path_png[0]
        im = Image.open(path_png)
        rgb_im = im.convert('RGB')
        path_jpg = self.hti.output_path+"/"+page_name+".jpg"
        rgb_im.save(path_jpg, quality=100)
        print('path_jpg',path_jpg)
        print('path_png',path_png)
        #create jpg files
        return path_jpg,path_png

if __name__ == '__main__':
    template = Template()
    template.generate_all_posts()
