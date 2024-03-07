import requests
from bs4 import BeautifulSoup
from pyzotero import zotero
import pickle
import time

#获取期刊信息的文本内容
def get_Publication_info(url):
    try:
        response = requests.get(url, headers = Useragent, timeout = 10)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all('li', 'js-article-list-item article-item u-padding-xs-top u-margin-l-bottom')
        #pdf_links = soup.find_all("a", "anchor pdf-download u-margin-l-right text-s anchor-default anchor-icon-left")
        #print(pdf_links)
        #print(articles)
    except Exception as e:
        print(f"获取期刊信息时出错：{e}")
    return articles


#解析文本内容，并打包成zotero的item模板
def parse_Publication_info(articals):
    templates = []
#下面加一个报错
    for article in articles:
        try:
            Paper_doi = article.find("div", hidden = True).get_text()
            Paper_title = article.find('span', 'js-article-title').get_text()
            Paper_link ="https://www.sciencedirect.com"+ article.find('a', 'anchor article-content-title u-margin-xs-top u-margin-s-bottom anchor-default').get('href')
            Paper_authors = article.find('div', 'text-s u-clr-grey8 js-article__item__authors').get_text(strip = True)
            Paper_author = Paper_authors.split(',')[0].strip()
            response = requests.get(Paper_link, headers = Useragent)
            time.sleep(0.5)
            Soup = BeautifulSoup(response.text, "html.parser")
            # abstractNote
            Highlights = Soup.find_all("li", "react-xocs-list-item")
            Paper_Highlight = ""
            for Highlight in Highlights:
                Paper_Highlight = Paper_Highlight + Highlight.get_text() + "\n"
            #print("Paper_Highlight:" + "\n" + Paper_Highlight)
            abstract = Soup.find("div", "abstract author").find("p").get_text()
            #print(abstract)

            template = zot.item_template('journalArticle')
            template['creators'] = [{
                "creatorType": "author",
                "firstName": "",
                "lastName": ""
            }]
            template['title'] = Paper_title
            template['DOI'] = Paper_doi
            template['url'] = Paper_link
            template['abstractNote'] = "HighLights:"+"\n"+Paper_Highlight+"\n"+"Abstract:"+"\n"+abstract
            templates.append(template)
        except Exception as e:
            print(f"解析文献:{Paper_title}时出错：{e}")
    return templates

# 通过templates解析出文章对应的url
"""def get_Paper_links(templates):
    Paper_links = []
    for template in templates:
        Paper_links.append(template['url'])
    return Paper_links"""
#判断条目是否已经存在于zotero中,并将条目添加到zotero指定collection中
def is_item_exist(templates):
    i = 0
    for template in templates:
        try:
            if template['DOI'] in DOIs:
                print(f"条目{template['title']}:{template['DOI']}已经存在于zotero中")
            else:
                try:
                    print(f"条目{template['title']}:{template['DOI']}不在zotero中")
                    item_key = zot.create_items([template])['successful']["0"]["key"]
                    zot.addto_collection("RCVLGRJ9", zot.item(item_key))  # 将文献信息添加到抓取最新文献的集合中
                    DOIs.add(template['DOI'])
                    with open("scripts/DOIs.pickle", "wb") as file:
                        pickle.dump(DOIs, file)
                    i = i + 1
                    print(f"条目{template['title']}(DOI:{template['DOI']})成功添加到zotero中")
                except Exception as e:
                    print(f"添加条目{template['title']}(DOI:{template['DOI']})时出错：{e}")
            # 添加条目到zotero中
        except Exception as e:
            print(f"添加条目{template['title']}(DOI:{template['DOI']})时出错：{e}")
    print(f"共添加{i}条文献到zotero中")


Useragent = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}
#文献信息库
with open("scripts/DOIs.pickle", "rb") as file:
    DOIs = pickle.load(file)

Urls = ["https://www.sciencedirect.com/journal/geoscience-frontiers/vol/1000/issue/20","https://www.sciencedirect.com/journal/lithos/vol/10000/suppl/C","https://www.sciencedirect.com/journal/geochimica-et-cosmochimica-acta/vol/10000/suppl/C","https://www.sciencedirect.com/journal/chemical-geology/vol/10000/suppl/C","https://www.sciencedirect.com/journal/earth-and-planetary-science-letters/vol/10000/suppl/C","https://www.sciencedirect.com/journal/earth-science-reviews/vol/10000/suppl/C"]  #
#爱斯维尔期刊链接当期刊版数超过最新的，自动定位为最新期刊，因此将改为vol/10000即可
zot = zotero.Zotero("5342248", "group", "SAjnkNkrQiPHCToY5Tdfi4jI")

for url in Urls:
    articles = get_Publication_info(url)
    templates = parse_Publication_info(articles)
    is_item_exist(templates)
