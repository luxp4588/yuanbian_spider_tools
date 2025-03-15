# -*- coding=utf-8 -*-
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.firefox import GeckoDriverManager   
from selenium.webdriver.common.by import By


try:
    options = Options()
    options.add_argument("--disable-web-security")  # 禁用同源策略
    options.add_argument("--allow-running-insecure-content")  # 允许不安全内容
    options.add_argument("--ignore-certificate-errors")  # 忽略证书错误
    service = Service(GeckoDriverManager().install(), options=options)
except Exception:
    print("无法下载浏览器驱动")

class BrowserAutomation(QThread):
    # 通过信号传递浏览器获取的结果
    result_ready = pyqtSignal(str)
    driver = None
    def __init__(self, url=None, hook_js=None):
        super().__init__()
        self.url = url
        self.hook_js = hook_js
        if self.driver is None:
            self.driver = webdriver.Firefox(service=service)

    def set_status(self, status="close"):
        self.status = status

    def run(self):
        # 使用 Selenium 打开浏览器并执行脚本
    
        if self.url is None:
            return
        
        self.driver.get(self.url)
        self.driver.execute_script(self.hook_js)

        time.sleep(3)

        while self.driver.window_handles:
            time.sleep(5)
        self.driver.quit()
        print("浏览器已经关闭")

    def xpath_crawler(self, xpath, target="href"):
        data = self.driver.find_elements(By.XPATH, xpath)
        for item in data:
            try:
                self.result_ready.emit(item.get_attribute(target))
            except:
                try:
                    links = item.find_elements(By.TAG_NAME, "a")
                    if links:
                        for link in links:
                            print(link)
                            self.result_ready.emit(link.get_attribute(target))
                except:
                    pass

    def __del__(self):
        self.driver.close()
