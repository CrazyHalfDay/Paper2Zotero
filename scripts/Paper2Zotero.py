import requests
from bs4 import BeautifulSoup
from pyzotero import zotero
import pickle

#获取期刊信息的文本内容
def get_Publication_info(url):
    response = requests.get(url, headers = Useragent)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all('li', 'js-article-list-item article-item u-padding-xs-top u-margin-l-bottom')
    pdf_links = soup.find_all("a", "anchor pdf-download u-margin-l-right text-s anchor-default anchor-icon-left")
    #print(pdf_links)
    #print(articles)
    return articles


#解析文本内容，并打包成zotero的item模板
def parse_Publication_info(articals):
    templates = []
#下面加一个报错
    for article in articles:
            Paper_doi = article.find("div", hidden = True).get_text()
            Paper_title = article.find('span', 'js-article-title').get_text()
            Paper_link ="https://www.sciencedirect.com"+ article.find('a', 'anchor article-content-title u-margin-xs-top u-margin-s-bottom anchor-default').get('href')
            Paper_authors = article.find('div', 'text-s u-clr-grey8 js-article__item__authors').get_text(strip = True)
            Paper_author = Paper_authors.split(',')[0].strip()
            template = zot.item_template('journalArticle')
            template['creators'] = [{
                "creatorType": "author",
                "firstName": "",
                "lastName": ""
            }]
            template['title'] = Paper_title
            template['DOI'] = Paper_doi
            template['url'] = Paper_link
            templates.append(template)
    return templates

#判断条目是否已经存在于zotero中,并将条目添加到zotero指定collection中
def is_item_exist(templates):
    for template in templates:
        if template['DOI'] in DOIs:
            print(f"条目{template['title']}:{template['DOI']}已经存在于zotero中")
        else:
            try:
                item_key = zot.create_items([template])['successful']["0"]["key"]
                zot.addto_collection("RCVLGRJ9", zot.item(item_key))  # 将文献信息添加到抓取最新文献的集合中
                DOIs.add(template['DOI'])
                with open("DOIs.pickle", "wb") as file:
                    pickle.dump(DOIs, file)
                print(f"条目{template['title']}:{template['DOI']}不存在于zotero中")
            except Exception as e:
                print(f"添加文献时出错：{e}")
            # 添加条目到zotero中


Useragent = {
    "user-agent":"Mozlila/5.0"
}
#文献信息库
with open("DOIs.pickle", "rb") as file:
    DOIs = pickle.load(file)

Urls = ["https://www.sciencedirect.com/journal/lithos/vol/472/suppl/C","https://www.sciencedirect.com/journal/geochimica-et-cosmochimica-acta/vol/370/suppl/C","https://www.sciencedirect.com/journal/chemical-geology/vol/651/suppl/C","https://www.sciencedirect.com/journal/earth-and-planetary-science-letters/vol/631/suppl/C"]  #
response = requests.get("https://www.sciencedirect.com/journal/lithos/vol/472/suppl/C", headers = Useragent)
zot = zotero.Zotero("5342248", "group", "SAjnkNkrQiPHCToY5Tdfi4jI")

for url in Urls:
    articles = get_Publication_info(url)
    templates = parse_Publication_info(articles)
    is_item_exist(templates)
