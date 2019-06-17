# /usr/bin/env python
# _*_ coding:utf-8 _*_


import sys
import csv                # 爬下来的数据要写到csv文件中，所以要引入这个模块
from urllib import request, error
from urllib.parse import quote
import string
from lxml import etree    # 元素树用来进行xpath语法解析时，
import random             # 这里我构造了五个浏览器的user-agent，防止被检测出来
 
 
# 1. get_html()这个函数是将给定url和encode方式，返回为html的字符串形式
def get_html(url,encode='gbk'):
    try:
        ua = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        # 创建user-agent集合，模拟浏览器登陆
        url = quote(url, safe=string.printable)
        proxy = request.ProxyHandler({'https': r'qinyf:Abc12345@10.6.5.13:40003'})
        auth = request.HTTPBasicAuthHandler()
        # 构造 opener
        opener = request.build_opener(proxy, auth, request.HTTPHandler)
        opener.addheaders = [('User-Agent', ua)]
        request.install_opener(opener)
        req = request.Request(url)                        # 3.构建爬虫请求对象
        response = request.urlopen(req)                   # 5.发送请求并获取服务器的响应对象response
        # html_str2 = response.read().decode(encode)        # 6.从响应对象中读取网页中的源码（响应正文）
        html_str2 = response.read().decode('gbk','ignore').replace(u'\xb0', u'')        # 6.从响应对象中读取网页中的源码（响应正文）
 
    except error.URLError:            # 抛异常，如果是url错误的话执行这个
        print('url 请求错误: {0}'.format(error.URLError))
    except error.HTTPError:
        print('请求错误: {0}'.format(error.HTTPError))
    except Exception as e:
        print('程序错误:{0}'.format(e))
    return html_str2
 
 
def crawl_onepage(html_str1):           # 这个方法用来将获取到的str格式的html进行xpath解析到rows这个列表中
    html_ = etree.HTML(html_str1)       # 将html字符串结构转换成html文档结构
    html = etree.ElementTree(html_)     # 将html文档结构转换成元素树结构
    # 使用xpath语法进行数据清洗
    div_el = html.xpath('//div[@id="resultList"]/div[@class="el"]')  # 获取id=“resultlist‘ 内所有的class=’el‘的div,div的列表
    rows = list()
    # 通过for循环寻找每一行el数据
    for index, el in enumerate(div_el):  # el数据类型是html文档类型
        el = etree.ElementTree(el)       # 同上：需要将html文档结构再转换成元素树的格式（节点）
        title = el.xpath('/div/p/span/a/@title')               # 职位名
        title = title[0] if title else None
        link = el.xpath('/div/p/span/a/@href')                 # 进入详情页的地址
        link = link[0] if link else None        
        company = el.xpath('/div/span[@class="t2"]/a/@title')  # 公司
        company = company[0] if company else None
        city = el.xpath('/div/span[@class="t3"]/text()')       # 工作地点
        city = city[0] if city else None
        salary = el.xpath('/div/span[@class="t4"]/text()')     # 薪水
        salary = salary[0] if salary else None
        time = el.xpath('/div/span[@class="t5"]/text()')       # 发布时间
        time = time[0] if time else None
        child_str = get_html(link, 'gbk')
        print(child_str)
        child_ = etree.HTML(child_str)
        child = etree.ElementTree(child_)  # 元素树（只有节点才能使用xpath语法）
        # exp = child.xpath('//div[@class="jtag inbox"]/div/span/em[@class="i1"]/parent::span/text()')
        exp = child.xpath('//div[@class="cn"]/p[@class="msg ltype"]/parent::span/text()')
        exp = exp[0] if exp else None
        degree = child.xpath('//div[@class="jtag inbox"]/div/span/em[@class="i2"]/parent::span/text()')
        degree = degree[0] if degree else None
        fuli = child.xpath('//div[@class="jtag inbox"]/p/span/text()')
        fuli = fuli if fuli else None  # 福利就是一个列表，需要将列表转成字符串
        row = (title, company, city, salary, time, exp, degree, fuli)  # 将每一行数据封装到元祖中
        print(row)
        rows.append(row)  # 每次获取到的职位相关信息，放入到空列表中
    return rows
 
 
def csv_write(filename,mode,content):                              # 用于写入csv文件的方法
    with open(filename, mode, newline ="",encoding ='gbk') as job:         # 用指定的mode方式打开filename文件，指定了编码格式
        file = csv.writer(job)
        if mode == 'w':                                # 写的方式，覆盖写
            file.writerow(content)
        if mode == 'a':                                #append方式写，不覆盖
            file.writerows(content)
 
 
def crawl_manypage(keyword,start,end):              # 爬取多页数据，第一个参数表示关键字，第二个是开始页，第三个是结束页
    head = (u'职位', '公司', '工作地点', '薪资', '发布时间', '工作经验', '学历', '福利')   # 第一行数据表头
    csv_write('{}.csv'.format(keyword), 'w', head)                      # 调用刚才的csv_write方法
    for page in range(start, end+1):                                    # page变量是页数
        url1 = 'https://search.51job.com/list/040000,000000,0000,00,9,99,{0},2,{1}.html?' \
               'lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99' \
               '&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=' \
               '&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='.format(keyword,page)
        print(url1)
        html_str = get_html(url1,'gbk')                 # 按照gbk的编码格式获取html字符串
        print(html_str)
        rows = crawl_onepage(html_str)                    # 调用函数爬取一页数据
        csv_write('{}.csv'.format(keyword), 'a', rows)    #  写入到csv文件中


# 51job通过协程实现并发爬虫
crawl_manypage('运维',1,1)
