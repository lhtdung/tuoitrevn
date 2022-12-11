import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from tuoitre.items import TuoitreItem
import re
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client
import urllib
import os

import requests # request img from web
import shutil # save img locally
from PIL import Image
from os.path import splitext
output_dir = '/images'
wp = Client('http://localhost/wordpress/xmlrpc.php', 'user', 'mfOd Ol6M rLFS QLYK Y7JL KoTA')
wp.call(GetPosts())
wp.call(GetUserInfo())
def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1
def strip_value(value):
    m = re.search("http[^\s]+(\s)*h?(http[^\s>]+)(\s)*", value)
    if m:
        return m.group(2)
    else:
        return value
class BaoDauTuSpider(CrawlSpider):
    name = "tuoitre"
    allowed_domains = ['tuoitre.vn']
    start_urls = [
            'https://tuoitre.vn/thoi-su.htm',
            'https://tuoitre.vn/the-gioi.htm',
            'https://baodautu.vn/thoi-su-d1/',
            'https://tuoitre.vn/phap-luat.htm',
    ]       
    rules = (
        Rule(LinkExtractor(allow='',
                           deny=['/abc/'],
                           process_value=strip_value,
                           restrict_xpaths=["//a[@class='btn-readmore']"]), follow=True, process_links=None),

        Rule(LinkExtractor(allow='',
                           deny=['/abc/'],
                           process_value=strip_value,
                           restrict_xpaths=["//h3[@class='title-news']/a | //h3[@class='title-name']/a | //a[@class='focus-middle-title'] | //a[@class='focus-top-box-relation-title fl'] | //a[@class='focus-top-title'] "]), 
                           follow=False, callback='parse_item', process_links=None)
    )
    def parse_item(self, response):
        item = TuoitreItem()
        item['title'] = response.xpath("//h1[@class='article-title']/text()").get().strip() 
        item['image'] = response.xpath("//div[@class='VCSortableInPreviewMode active']//@src").get()
        item['category'] = response.xpath("//div[@class='bread-crumbs fl']/ul/li[@class='fl'][1]/a/text()").get().strip()
        list_p = response.xpath("//div[@id='main-detail-body']/p").getall()
        item['content'] = listToString(list_p)
        item['url'] = response.request.url
        post = WordPressPost()
        post.title = item['title']
        post.content = item['content']
        post.post_status = 'publish'
        post.terms_names = {
            'post_tag': ['baotuoitre'],
            'category': [item['category']]
        }
        r = requests.get(item['image'])
        with open(f"{item['title']}.png",'wb') as f:
             f.write(r.content)
        filename = f"D:\\GitHUB\\scrapy\\tuoitre\\{item['title']}.png"
        data = {    
            'name': f'{item["title"]}.jpg',
            'type': 'image/jpeg', 
        }
        with open(filename, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())
        response = wp.call(media.UploadFile(data))
        attachment_id = response['id']
        post.thumbnail = attachment_id
        os.remove(f"{item['title']}.png")
        wp.call(NewPost(post))
        return item