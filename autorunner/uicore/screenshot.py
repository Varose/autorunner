#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/30 9:56
# @Author : liangchunhua
# @Desc   :
import os


def screenshot(driver, file_name):
    """
    截图
    :param driver: 启动浏览器
    :param file_name: 截图文件名
    :return: 返回指定路径的截图文件
    """

    superior_path = os.path.dirname(os.path.dirname(__file__))
    file_path = superior_path + "/report/screenshot/" + file_name
    return driver.get_screenshot_as_file(file_path)
