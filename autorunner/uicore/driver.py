#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/29 16:18
# @Author : liangchunhua
# @Desc   :
import os
from enum import Enum

from pydantic import Field
from pydantic.v1 import HttpUrl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager_zh.chrome import ChromeDriverManager
from webdriver_manager_zh.core.driver_cache import DriverCacheManager


class BrowserTypeEnum(str, Enum):
    """浏览器类型"""
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    EDGE = "Edge"
    IE = "IE"


class AutoDriver:
    def __init__(
            self,
            remote_url: HttpUrl = "http://127.0.0.1:4444/wb/hub",
            browser: BrowserTypeEnum = BrowserTypeEnum.CHROME,
            headless: bool = False,
            snapshot: bool = Field(True, description="截图路径"),
            # 页面闪烁超时
            page_load_timeout: int = 30,
            # 元素等待超时
            implicitly_wait_time: int = 3
    ):
        self.page_load_timeout = page_load_timeout
        self.implicitly_wait_time = implicitly_wait_time
        if browser == BrowserTypeEnum.CHROME:
            options = Options()
            options.add_argument("--start-maximized")
            # 添加浏览器缓存
            user_directory_path = os.path.expanduser('~')
            options.add_argument(f'--disk-cache-dir={user_directory_path}\chromeUiCache')
            # options.add_argument('--disable-gpu')
            # options.add_argument("--no-sandbox") # linux无头模式以root用户运行，开启可能会报错
            # options.add_argument('--ignore-certificate-errors')
            # options.add_experimental_option("excludeSwitches",
            #                                 ['load-extension', 'enable-automation', 'enable-logging'])
            if not headless:
                """本地执行"""

                # drivers = webdriver.Chrome(service=ChromeService(
                #     ChromeDriverManager(url=url, latest_release_url=latest_release_url).install()))
                # self.drivers = webdriver.Chrome(executable_path=setting.executable_path, options=options)
                driver_path = ChromeDriverManager(url=url, latest_release_url=latest_release_url).install()
                self.driver = webdriver.Chrome(options, service=webdriver.ChromeService(driver_path))
            else:
                """远程执行"""
                # 默认vnc密码：secret
                desired_capabilities = {
                    "browserName": "chrome",  # 浏览器名称
                    "version": "",  # 操作系统版本
                    "platform": "ANY",  # 平台，这里可以是windows、linux、andriod等等
                    "javascriptEnabled": True,  # 是否启用js
                }
                options.add_argument("--headless")
                self.driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            raise Exception(f"暂不支持其他浏览器: {browser}")
        # 元素等待超时时间
        self.driver.implicitly_wait(implicitly_wait_time)  # seconds
        # 页面刷新超时时间
        self.driver.set_page_load_timeout(page_load_timeout)  # seconds
        # self.drivers.maximize_window()

    def open(self, url):
        self.driver.get(url)
        return self.driver

    def get_session_variables(self):
        """获取session变量"""
        return self._session_variables

    def quit(self):
        """退出"""
        self.driver.quit()

    def get_driver_session_id(self):
        """获取session_id"""
        return self.driver.session_id

    def get_screenshot(self, screenshot_type="base64", file_path=None):
        """截图"""
        if screenshot_type == "base64":
            """方法得到图片的base64编码"""
            return self.driver.get_screenshot_as_base64()
        elif screenshot_type == "png":
            """方法得到图片的二进制数据"""
            return self.driver.get_screenshot_as_png()
        elif screenshot_type == "file":
            """方法得到图片的二进制数据"""
            if not file_path:
                raise Exception("截图路径不能为空")
            return self.driver.get_screenshot_as_file(file_path)
        else:
            raise Exception(f"不支持的截图类型: {screenshot_type}")


def browser_type(bw_type, open_url):
    if bw_type == "Chrome":
        pass

    elif bw_type == "Edge":
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager_zh.microsoft import EdgeChromiumDriverManager
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
        driver.get(open_url)

    elif bw_type == "Firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager_zh.firefox import GeckoDriverManager
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get(open_url)

    elif bw_type == "IE":
        from selenium.webdriver.ie.service import Service as IEService
        from webdriver_manager_zh.microsoft import IEDriverManager
        driver = webdriver.Ie(service=IEService(IEDriverManager().install()))
        driver.get(open_url)


def test():
    from webdriver_manager_zh.chrome import ChromeDriverManager
    from webdriver_manager_zh.core.os_manager import OperationSystemManager
    from webdriver_manager_zh.core.file_manager import FileManager
    from webdriver_manager_zh.core.driver_cache import DriverCacheManager

    # https://registry.npmmirror.com/-/binary/chrome-for-testing

    # 配置操作系统管理器
    os_manager = OperationSystemManager(os_type="win64")

    # 配置文件管理器
    file_manager = FileManager(os_system_manager=os_manager)

    # 配置驱动缓存管理器
    cache_manager = DriverCacheManager(file_manager=file_manager)

    # 配置 Chrome 驱动管理器
    chrome_manager = ChromeDriverManager(cache_manager=cache_manager)
    chrome_manager.install()

    # OperationSystemManager: 操作系统管理器，用于配置操作系统的类型。
    # FileManager: 文件管理器，用于管理文件操作。
    # DriverCacheManager: 驱动缓存管理器，用于管理驱动的缓存。
    # ChromeDriverManager: Chrome


if __name__ == '__main__':
    a = AutoDriver().open('https://www.baidu.com/')
