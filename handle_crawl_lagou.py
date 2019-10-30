import requests
import re
import time
import multiprocessing
import json

class HandleLaGou(object):
    def __init__(self):
        self.lagou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        self.city_list = ""

    #获取全部城市
    def handle_city(self):
        city_url = 'https://www.lagou.com/jobs/allCity.html'
        city_search = re.compile(r'city=(.*?)#filterBox')
        city_result = self.handle_request(method="GET", url=city_url)
        self.city_list = city_search.findall(city_result)
        #清除cookie信息
        self.lagou_session.cookies.clear()

    #获取岗位信息
    def handle_city_job(self, city):
        first_request_url = 'https://www.lagou.com/jobs/list_python?&px=default&city=%s'%city
        first_reponse = self.handle_request(method="GET", url=first_request_url)
        total_page_search = re.compile(r'<span\sclass="span totalNum">(\d+)</span>')
        try:
            total_page = total_page_search.search(first_reponse).group(1)
        except:
            return
        else:
            for i in range(1, int(total_page)+1):
                data = {
                    "pn": i,
                    "kd": "PYTHON"
                }
                page_url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false'%city
                referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city
                self.header['Referer'] = referer_url.encode()
                response = self.handle_request(method="POST", url=page_url, data=data, info=city)
                lagou_data = json.loads(response)
                job_list = lagou_data['content']['positionResult']['result']
                for job in job_list:
                    print(job)

    #请求方法
    def handle_request(self, method, url, data=None, info=None):
        while True:
            if method == "GET":
                response = self.lagou_session.get(url=url, headers=self.header,)
            elif method == "POST":
                response = self.lagou_session.post(url=url, headers=self.header, data=data,)
            response.encoding = 'utf-8'
            if "频繁"in response.text:
                print("频繁获取，请等待")
                # 清除cookie信息
                self.lagou_session.cookies.clear()
                # 重新获取cookie信息
                first_request_url = 'https://www.lagou.com/jobs/list_python?&px=default&city=%s' % info
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)
                continue
            return response.text


if __name__ == '__main__':
        lagou = HandleLaGou()
        lagou.handle_city()
        # pool = multiprocessing.Pool(2)
        print(lagou.city_list)
        for city in lagou.city_list:
            print(city)
            lagou.handle_city_job(city)
        # pool.close()
        # pool.join()



