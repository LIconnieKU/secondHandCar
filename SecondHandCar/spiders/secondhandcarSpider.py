# -*- coding: utf-8 -*-
import requests

import scrapy
from scrapy import Request
from scrapy import Selector

from pytesser1 import pytesser

import time

import json

class SecondHandCarSpider(scrapy.Spider):

    name = "SHCSpider"

    pre_url = "https://www.che168.com"

    post_url = "/guangzhou/a0_0ms1dgscncgpi1ltocsp1exe10b1x0/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    }

    def start_requests(self):
        yield Request(url="https://www.che168.com/guangzhou/a0_0ms1dgscncgpi1ltocsp1exe10b1x0/",headers=self.headers,callback=self.page_parse)

    def page_parse(self,response):
        body = response.body.decode("gbk")      #
        select = Selector(text=body)
        if u"下一页" in body:
            page_url_select = select.xpath("//div[@id='listpagination']//a[@class='page-item-next']/@href")
            page_url = self.pre_url + page_url_select.extract()[0]
            yield Request(url=page_url, headers=self.headers, callback=self.page_parse)

        url_select = select.xpath("//ul[@id='viewlist_ul']//li[@class='']/a/@href").extract()
        for lo in url_select[:2]:
            temp_url = self.pre_url + lo
            print temp_url
            yield Request(url=temp_url,headers=self.headers)



    def parse(self, response):
        body = response.body.decode("gbk")
        select = Selector(text=body)

        try:
            title_select = select.xpath("/html/body/div[6]/div[2]/div[1]/h2").xpath("string(.)").extract()[0]
            price_select = select.xpath("/html/body/div[6]/div[2]/div[2]/div/*")[0].xpath("string(.)").extract()[0] \
                           + select.xpath("/html/body/div[6]/div[2]/div[2]/div/*")[1].xpath("string(.)").extract()[0]
            mileage_select = select.xpath("//div[@class='car-info']/div[@class='details']//span")[0].xpath("string(.)").extract()[0]
            first_license_select = select.xpath("//div[@class='car-info']/div[@class='details']//span")[1].xpath("string(.)").extract()[0]
            shift_displace_select = select.xpath("//div[@class='car-info']/div[@class='details']//span")[2].xpath("string(.)").extract()[0]
            shift = shift_displace_select.split(u'／')[0]
            displacement = shift_displace_select.split(u'／')[1]
            locate_select = select.xpath("//div[@class='car-info']/div[@class='details']//span")[3].xpath("string(.)").extract()[0]
            meeting_select = select.xpath(u"//div[contains(text(),'看车地点')]/text()").extract()       #
            m_place = meeting_select[0].split(u': ')[1]
            p_time = meeting_select[1].split(u': ')[1]
        except:
            print response.url,"detail error"
            return

        try:
            phone_select = select.xpath("//a[@class='btn btn-iphone3']")
            if len(phone_select)!=0:
                image_url = self.pre_url + phone_select.xpath(".//img/@src").extract()[0]
                pic = requests.get(image_url)
                pic_name = "phoneNum/" + str(int(round(1000 * time.time()))) + ".png"
                fp = open(pic_name, 'wb')
                fp.write(pic.content)
                fp.close()
                phone = pytesser.image_file_to_string(pic_name).replace("\n","").replace(" ","")
            else:
                phone = ""
        except:
            print response.url,"phone error"
            return

        data = {"title":title_select, "price":price_select, "mileage":mileage_select, "first_l":first_license_select, "shift":shift, "displacement":displacement, "location":locate_select, "m_place":m_place, "p_time":p_time, "phone":phone}
        jjson = json.dumps(data) + "\n"
        fp = open("info.txt", 'a')
        fp.write(jjson)
        fp.close()
