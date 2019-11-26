# coding: utf-8
import yaml
import os
import pycurl
import time
import io
# from StringIO import StringIO
from prometheus_client.core import CollectorRegistry
from prometheus_client import Gauge, generate_latest
from flask import Flask, Response


def get_config(filename):
    with open(filename, "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def get_site_status(url):
    data = {'namelookup_time': 0, 'connect_time': 0, 'pretransfer_time': 0,
            'starttransfer_time': 0, 'total_time': 0, 'http_code': 444,
            'size_download': 0, 'header_size': 0, 'speed_download': 0}
    html = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    # 请求连接的等待时间
    c.setopt(pycurl.CONNECTTIMEOUT, 5)
    # 请求超时时间
    c.setopt(pycurl.TIMEOUT, 5)
    # 屏蔽下载进度条
    c.setopt(pycurl.NOPROGRESS, 1)
    # 完成交互后强制断开连接，不重用
    c.setopt(pycurl.FORBID_REUSE, 1)
    # 指定 HTTP 重定向的最大数为 1
    c.setopt(pycurl.MAXREDIRS, 1)
    # 设置保存 DNS 信息的时间为 10 秒
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 10)
    # 设置是否返回请求头
    # c.setopt(pycurl.HEADER, True)
    # 设置是否返回请求体
    # c.setopt(pycurl.NOBODY, True)
    # 设置是否验证HTTP证书
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    # 把 response body 存在 html 变量里，不输出到终端
    c.setopt(pycurl.WRITEFUNCTION, html.write)
    try:
        c.perform()
        # 变量含义，参考文档：https://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
        # 获取 DNS 解析时间，单位 秒(s)
        namelookup_time = c.getinfo(c.NAMELOOKUP_TIME)
        # 获取建立连接时间，单位 秒(s)
        connect_time = c.getinfo(c.CONNECT_TIME)
        # 获取从建立连接到准备传输所消耗的时间，单位 秒(s)
        pretransfer_time = c.getinfo(c.PRETRANSFER_TIME)
        # 获取从建立连接到传输开始消耗的时间，单位 秒(s)
        starttransfer_time = c.getinfo(c.STARTTRANSFER_TIME)
        # 获取传输的总时间，单位 秒(s)
        total_time = c.getinfo(c.TOTAL_TIME)
        # 获取 HTTP 状态码
        http_code = c.getinfo(c.HTTP_CODE)
        # 获取下载数据包大小，单位 bytes
        size_download = c.getinfo(c.SIZE_DOWNLOAD)
        # 获取 HTTP 头部大小，单位 byte
        header_size = c.getinfo(c.HEADER_SIZE)
        # 获取平均下载速度，单位 bytes/s
        speed_download = c.getinfo(c.SPEED_DOWNLOAD)
        c.close()
        data = dict(namelookup_time=namelookup_time * 1000, connect_time=connect_time * 1000,
                    pretransfer_time=pretransfer_time * 1000, starttransfer_time=starttransfer_time * 1000,
                    total_time=total_time * 1000, http_code=http_code,
                    size_download=size_download, header_size=header_size,
                    speed_download=speed_download)
    # 如果站点无法访问，捕获异常，并使用前面初始化的字典 data 的值
    except Exception as e:
        print("{} connection error: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(e)))
        c.close()
    return data


# 设置 metrics
registry = CollectorRegistry(auto_describe=False)
namelookup_time = Gauge('namelookup_time', 'namelookup time', ['url'], registry=registry)
connect_time = Gauge('connect_time', 'connect time', ['url'], registry=registry)
pretransfer_time = Gauge('pretransfer_time', 'pretransfer time time', ['url'], registry=registry)
starttransfer_time = Gauge('starttransfer_time', 'starttransfertime time', ['url'], registry=registry)
total_time = Gauge('total_time', 'total time', ['url'], registry=registry)
size_download = Gauge('size_download', 'size download', ['url'], registry=registry)
header_size = Gauge('header_size', 'header size', ['url'], registry=registry)
speed_download = Gauge('speed_download', 'speed download', ['url'], registry=registry)
http_code = Gauge('http_code', 'http code', ['url'], registry=registry)

app = Flask(__name__)


@app.route("/metrics")
def main():
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    res = get_config(filename)
    for url in res['urls']:
        data = get_site_status(url)
        print(data)
        for key, value in data.items():
            if key == 'namelookup_time':
                namelookup_time.labels(url=url).set(float(value))
            elif key == 'connect_time':
                connect_time.labels(url=url).set(float(value))
            elif key == 'pretransfer_time':
                pretransfer_time.labels(url=url).set(float(value))
            elif key == 'starttransfer_time':
                starttransfer_time.labels(url=url).set(float(value))
            elif key == 'total_time':
                total_time.labels(url=url).set(float(value))
            elif key == 'size_download':
                size_download.labels(url=url).set(float(value))
            elif key == 'header_size':
                header_size.labels(url=url).set(float(value))
            elif key == 'speed_download':
                speed_download.labels(url=url).set(float(value))
            elif key == 'http_code':
                http_code.labels(url=url).set(float(value))
    return Response(generate_latest(registry), mimetype="text/plain")
