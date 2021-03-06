import requests
from bs4 import BeautifulSoup
import time

# 爬取数据的字段名
field_name = ['position_id', 'position_salary', 'position_name', 'position_url', 'position_city', 'position_area',
              'position_publishtime', 'work_year', 'education', 'position_desc', 'position_tags', 'hr_id',
              'company_name', 'company_id', 'company_url', 'company_desc']
# 爬取的职位信息列表
job_info_list = []


def get_job_index(index_url):
    """
    爬取职位总览：通过拉勾首页获取各职位的分类标签，职位名称，以及对应链接。例如：
    ['技术', '后端开发', 'Python', 'https://www.lagou.com/zhaopin/Python/']

    """
    job_index_list = []  # 初始化列表，保存各职位总览数据
    r = requests.get(index_url)  # 请求首页链接
    soup_index = BeautifulSoup(r.text, 'lxml')  # 创建解析对象

    # '#'号开头的是通过html的id名查找，例如：#sidebar；直接写div是通过html的标签查找；'.'开头的是通过类名查找，例如：.menu_box。
    for each_first in soup_index.select('#sidebar > div > .menu_box'):
        first_name = each_first.select_one('h2').get_text().strip(' \n')  # 第一分类名称
        for each_second in each_first.select('div.menu_sub.dn > dl'):
            second_name = each_second.select_one('dt > span').get_text()  # 第二分类名称
            for each_third in each_second.select('dd > a'):
                third_name = each_third.get_text()  # 职位名称
                third_url = each_third['href']  # 职位url
                job_index_list.append([first_name, second_name, third_name, third_url])
    return job_index_list


def parse_position_page(html_page):
    bs_obj = BeautifulSoup(html_page, 'lxml')
    for each_position in bs_obj.select('#s_position_list > ul > li'):
        position_id = each_position['data-positionid']  # 职位id
        position_salary = each_position['data-salary']  # 薪资
        position_name = each_position['data-positionname'].strip().replace(',', '，')  # 职位名称
        position_url = each_position.select_one('.position_link')['href']  # 职位url
        position_location = each_position.select_one('.add > em').get_text()  # 工作地点
        position_publishtime = each_position.select_one('.format-time').get_text()  # 发布时间
        position_requ = \
            each_position.select_one('div.position > div.p_bot > div.li_b_l').get_text().split('\n')[-2]  # 职位要求
        position_desc = each_position.select_one('div.li_b_r').get_text().replace(',', '，')  # 职位描述
        position_tags = each_position.select_one('div.list_item_bot > div.li_b_l').get_text('/')  # 职位tags

        hr_id = each_position['data-hrid']  # HRid
        company_name = each_position['data-company']  # 供职公司
        company_id = each_position['data-companyid']  # 公司id
        company_url = each_position.select_one('.company_name > a')['href']  # 公司url
        company_desc = each_position.select_one('div.industry').get_text().strip().replace(',', '，')  # 公司行业描述
        try:
            position_city = position_location.split('·')[0]
            position_area = position_location.split('·')[1]
            work_year = position_requ.split('/')[0].strip()
            education = position_requ.split('/')[1].strip()
        except IndexError as err:
            print(err)
            print(each_position)
            position_city = position_location
            position_area = ""
            work_year = position_requ
            education = ""
        job_info_list.append(
            [position_id, position_salary, position_name, position_url, position_city, position_area,
             position_publishtime,
             work_year, education, position_desc, position_tags, hr_id, company_name, company_id, company_url,
             company_desc])
    print(len(job_info_list))


def download_position_page(url_prefix, page_num):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.75 Safari/537.36 '
    }

    s = requests.Session()
    s.headers.update(headers)  # 需要设置headers信息，否则返回登陆页面
    s.get('http://www.lagou.com')  # 第一步先访问首页，获得cookies
    time.sleep(1)
    r = s.get(url_prefix + str(page_num) + '/')  # 循环进行翻页访问
    print(url_prefix + str(page_num) + '/')
    print(len(r.text))
    return r.text


def save_data(file_name, job_data):
    with open(file_name, 'w') as fo:
        out = ','.join(field_name).replace('\n', '') + '\n'
        fo.write(out)
        for job in job_data:
            print(job)
            out = ','.join(job).replace('\n', '') + '\n'
            try:
                fo.write(out)
            except UnicodeEncodeError as err:
                print(err)


if __name__ == '__main__':
    job_index_list = get_job_index("http://www.lagou.com")
    for i in job_index_list:
        print(i)
    for i in range(1, 31):
        html_page = download_position_page("https://www.lagou.com/zhaopin/Python/", i)
        parse_position_page(html_page)
    save_data("out.csv", job_info_list)
