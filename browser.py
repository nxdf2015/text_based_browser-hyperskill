
from sys import argv
from os import mkdir
from re import search,compile
from pathlib import Path
from operator import attrgetter
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
    available=["bloomberg","nytimes"]

    def __init__(self,path):

        self.path=path

    @staticmethod
    def is_valid_url(path):
        return not path.find(".") == -1

    @staticmethod
    def  name_from_url(url):
        id = url.find(".")
        return url[:id]

    def available(self):
        folder=Path(self.path)
        return list(map(attrgetter("name"), folder.iterdir()))

    def get(self,page):
         print("pages",page)
         if self.is_available(page):
             name_file= f"{self.path}/{page}"
             with open(name_file,"r") as file:
                 data=file.read()
                 return data,page
         elif not Pages.is_valid_url(page):
                raise InvalidPageException()
         else:
             name_page=Pages.name_from_url(page)
             data= self.request_page(name_page)
             if   data=="error":
                 raise InvalidPageException()

             name_file= f"{self.path}/{name_page}"
             with open(name_file,"w") as file:
                    file.write(data)
                    return data,name_page




    def request_page(self,page):
        data=""
        if page == "bloomberg":
            data = bloomberg_com
        elif page == "nytimes":
            data = nytimes_com
        else:
            data="error"
        return data

    def is_available(self,page):
        return page in self.available()




class Browser:


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

