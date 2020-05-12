
from sys import argv
from os import mkdir
from re import search,compile,match
from pathlib import Path
from operator import attrgetter
import requests
from bs4 import BeautifulSoup,NavigableString

nytimes_com = '''
This New Liquid Is Magnetic, and Mesmerizing
 
Scientists have created “soft” magnets that can flow 
and change shape, and that could be a boon to medicine 
and robotics. (Source: New York Times)
 
 
Most Wikipedia Profiles Are of Men. This Scientist Is Changing That.
 
Jessica Wade has added nearly 700 Wikipedia biographies for
 important female and minority scientists in less than two 
 years.
 
'''

bloomberg_com = '''
The Space Race: From Apollo 11 to Elon Musk
 
It's 50 years since the world was gripped by historic images
 of Apollo 11, and Neil Armstrong -- the first man to walk 
 on the moon. It was the height of the Cold War, and the charts
 were filled with David Bowie's Space Oddity, and Creedence's 
 Bad Moon Rising. The world is a very different place than 
 it was 5 decades ago. But how has the space race changed since
 the summer of '69? (Source: Bloomberg)
 
 
Twitter CEO Jack Dorsey Gives Talk at Apple Headquarters
 
Twitter and Square Chief Executive Officer Jack Dorsey 
 addressed Apple Inc. employees at the iPhone maker’s headquarters
 Tuesday, a signal of the strong ties between the Silicon Valley giants.
'''

class InvalidPageException(Exception):
    pass

class Parser:
    def __init__(self,html_string):
        self.soup=BeautifulSoup(html_string,"html.parser")

    def __isblock(self,tag):
        return tag.name in ["li","p","ul","ol"] or tag.name.startswith("h")

    def __is_valid_tag(self,tag):
        """
        return true if tag is not empty and not content of a script tag
        """
        not_empty = not (match(r"\s+",tag) or tag == "\n")
        return not tag.parent.name in ["script"] and not_empty

    def __parser(self,root):
        """
        traverse the tree
            base case: if tag is string return if not empty
            append  a new line to the response  if tag is block element
        """
        response=""
        for tag in root.contents:
            if isinstance(tag,NavigableString):
                if self.__is_valid_tag(tag) and not match(r"\s+",tag.string):
                    response += tag.string

            elif self.__isblock(tag):
                response += "\n" + self.__parser(tag)
            else:
                response += self.__parser(tag)

        return response

    def to_string(self):
        """
        return html without tag
        """
        return self.__parser(self.soup.body)


class History:
    def __init__(self):
        self.history=[]
        self.current=""

    def update_current(self,new_item):
        if self.current:
            self.history.append(self.current)
        self.current=new_item

    def back(self):
        self.current= self.history.pop()
        return self.current


class Pages:
    url_pattern=r"https?://[^.]+\.[^.]+\.[^.](/.*)?"
    available=["bloomberg","nytimes"]
    def __init__(self,path):
        self.path=path

    @staticmethod
    def is_valid_url(path):
        # return search(Pages.url_pattern,path)
        return not path.find(".") == -1

    @staticmethod
    def  name_from_url(url):
        """
        extract name from url
        """
        id = url.find(".")
        return url[:id]

    def available(self):
        """
        available pages are save in folder './path'
        return list of available page
        """
        folder=Path(self.path)
        return list(map(attrgetter("name"), folder.iterdir()))

    def get(self,page):
         """
            return a a string or error
         """
         if self.is_available(page):
             name_file= f"{self.path}/{page}"
             with open(name_file,"r") as file:
                 data=file.read()
                 return data,page

         elif not Pages.is_valid_url(page):
                raise InvalidPageException()
         else:
             name_page=Pages.name_from_url(page)
             data= self.request_page(page)
             if   data=="error":
                 raise InvalidPageException()
             name_file= f"{self.path}/{name_page}"
             with open(name_file,"w") as file:
                    parser=Parser(data)
                    data_string=parser.to_string()
                    file.write(data_string)
                    return data_string,name_page

    
    def request_page(self,page):
        """
        get page from an url or  by name
        for url append https:// if prefix is not at the begining
        """

        # data=""
        # if page == "bloomberg":
        #      data = bloomberg_com
        # elif page == "nytimes":
        #      data = nytimes_com
        #
        # else:
        if not page.startswith("https://"):
                page = "https://" + page
        response=requests.get(page)
        if response.status_code == 200:
                data= response.content
        else:
                data= "error"
        return data

    def is_available(self,page):
        return page in self.available()




class Browser:
    """
    method start : launch the brower and wait command
        exit quit browser
        back show previous page
        to get a page type url with pattern aaaa.aaaa

    """
    def __init__(self,directory=""):
        self.pages=Pages(directory)
        self.history=History()

    def start(self):

        while True:
            choice=input()
            if choice=="exit":
                break
            elif choice=="back":
                choice=self.history.back()
            try:
                data,name=self.pages.get(choice)
                self.history.update_current(name)
                print(data)
            except InvalidPageException :
                print("error")



if __name__=="__main__":

    path=argv[1]
    if not Path(path).is_dir():
        mkdir(path)

    browser=Browser(path)
    browser.start()

