# coding=utf-8
import urllib.request
from bs4 import BeautifulSoup
#import bs4
import time
import re
import json

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')



root_url="http://www.xf4hs.com/skin/skin001/NewsList.php?searchtext=&news_class_id=123&page_index="

print("输入起止页面编号 以一个半角空格隔开")

x,y=input().split()

print("输入爬取条数 若输入0则全部爬取")

num=int(input())
ccnt=0

Newurl=set()

def addurl(url):
    if url is None:
        return
    global ccnt
    if url not in Newurl and (ccnt<num or num==0):
        Newurl.add(url)
        ccnt+=1


print("输入排序方式")
print("1. 时间从近到远")
print("2. 时间从远到近")
print("3. 标题字典序")
print("4. 点击量降序")
print("5. 点击量升序")

z=int(input())
for i in range(int(x),int(y)+1):
    header={"User-Agent":"Mozilla/5.0"}
    url=root_url+str(i)                            #url表示地址
    print(url)
    response=urllib.request.urlopen(url).read()
    #print(response.getcode())
    #response=response.decode('utf-8')
    soup=BeautifulSoup(response,'html.parser')
    link=soup.find_all('a',href=re.compile(r"news_id="))
    for l in link:
        #print(l.get('href'))
        #addurl(l.get('href'))
        if l.get('href').find('2072') == -1:    #不要页脚
            addurl(l.get('href'))               #存储链接
            #print(l.get('href'))
    time.sleep(0.1)

Urls=[]                                         #Urls表示下载好的网页列表+具体信息
while len(Newurl)!=0:
    Url={}
    url="http://www.xf4hs.com/"+Newurl.pop()
    response=urllib.request.urlopen(url).read()
    soup=BeautifulSoup(response,'html.parser')
    Url['url']=url
    title=soup.find('title')
    Url['title']=title.get_text()
    #print(Url['title'])
    Date=soup.find_all('li',string=re.compile(r"-"))
    for date in Date:
        #print(date.get_text())
        Url['date']=date.get_text()
    Author=soup.find_all('li',string=re.compile(r"发布者"))
    for author in Author:
        Url['author']=author.get_text()
    Cnt=soup.find_all('li',string=re.compile(r"点击"))
    for cnt in Cnt:
        Url['cnt']=cnt.get_text()[3:]
    content=soup.find_all('p')
    Url['content']=""
    for p in content:
        Url['content']+=p.get_text()
    x=0
    flag=0
    urllist=list(Url['content'])

    #处理特殊内容如表格
    for i in urllist:
        if i == '\n':
            urllist[x]='\\'
            urllist.insert(x+1,'n')
        elif i =='\"' and flag == 0:
            urllist[x]='\\'
            x=x+1
            urllist.insert(x,'\"')
            flag=1
            continue
        elif i =='\'' and flag == 0:
            urllist[x]='\\'
            x=x+1
            urllist.insert(x,'\'')
            flag=1
            continue
        x=x+1
        flag=0

    Url['content']="".join(urllist)
    #Url['content'].encode('raw_unicode_escape')
    #Url['content'].decode()
    Urls.append(Url)

print()
def cmp1(a):
    return a['date']
def cmp2(a):
    return a['title']
def cmp3(a):
    return int(a['cnt'])

ss=time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
fout = open('crawl-%s.json'%ss,'w',encoding='utf-8')

Json={}

Json['name']="襄阳四中校园资讯"

if z == 1:
    Urls.sort(key=cmp1,reverse=True)
    Json['order']='date1'
elif z == 2:
    Urls.sort(key=cmp1)
    Json['order']='date2'
elif z == 3:
    Urls.sort(key=cmp2)
    Json['order']='title'
elif z == 4:
    Urls.sort(key=cmp3,reverse=True)
    Json['order']='counter1'
else:
    Urls.sort(key=cmp3)
    Json['order']='counter2'

s=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

Json['generated_at']=s
Json['data']=[]


one = 0
for urlS in Urls:
    urlS['author']=urlS['author'][4:]
    urlS['date']=urlS['date']+"T08:00:00"
    Json['data'].append(urlS)
    #fout可能要存到服务器上去 
fout.write(json.dumps(Json,indent=4).encode('utf-8').decode('unicode_escape'))
fout.close()
