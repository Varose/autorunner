#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/30 16:18
# @Author : liangchunhua
# @Desc   : 页面元素操作

from time import sleep
from typing import List

from loguru import logger
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from autorunner.models import TUiLocation
from autorunner.uicore.driver import AutoDriver
from autorunner.uicore.locator import locator


class Action:

    @staticmethod
    def open(auto_driver: AutoDriver, step: TUiLocation):
        driver = auto_driver.open(step.data)
        if step.cookie:
            driver.add_cookie(step.cookie)
        sleep(0.5)

    @staticmethod
    def title(auto_driver: AutoDriver):
        """获取页面标题"""
        return auto_driver.driver.title

    @staticmethod
    def current_url(auto_driver: AutoDriver):
        """获取当前页面的url"""
        return auto_driver.driver.current_url

    @staticmethod
    def check(step: TUiLocation, auto_driver: AutoDriver):
        pass

    @staticmethod
    def notcheck(step):
        data = step['data']
        if not data:
            data = step['expected']
        element = step['element']
        # element_location = locator_element(element)

        # if element['by'] == 'title':
        #     assert data['text'] != g.driver.title

    @staticmethod
    def send_keys(auto_driver: AutoDriver, step: TUiLocation):
        element_location = locator(auto_driver, step)
        ActionChains(auto_driver.driver).double_click(element_location).perform()
        element_location.send_keys(step.data)
        return element_location

    @staticmethod
    def switch_to_frame(auto_driver: AutoDriver, step: TUiLocation):
        element_location = locator(auto_driver, step)
        # auto_driver.driver.implicitly_wait(5)
        auto_driver.driver.switch_to.frame(element_location)

    @staticmethod
    def click(auto_driver: AutoDriver, step: TUiLocation):
        element_location = locator(auto_driver, step)
        if element_location:
            try:
                element_location.click()
            except ElementClickInterceptedException:  # 如果元素为不可点击状态，则等待1秒，再重试一次
                sleep(1)
                element_location.click()
        sleep(0.5)
        return element_location

    @staticmethod
    def context_click(auto_driver: AutoDriver, step: TUiLocation):
        """
        右击
        :param auto_driver:
        :param step:
        :return:
        """
        actions = ActionChains(auto_driver.driver)
        element_location = locator(auto_driver, step)
        actions.context_click(element_location)
        actions.perform()
        sleep(0.5)
        return element_location

    @staticmethod
    def finds(auto_driver: AutoDriver, step: TUiLocation) -> List[WebElement]:
        wait = WebDriverWait(auto_driver.driver, 2)
        try:
            return wait.until(expected_conditions.presence_of_all_elements_located(
                    (getattr(By, step.by), step.value)))
        except TimeoutException as e:
            logger.info(f'{step.by}({step.value})调用finds查询超时，返回空数组')
            return []

    @staticmethod
    def find_descendant(auto_driver: AutoDriver, step: TUiLocation):
        """
        查找当前节点的所有后代元素（子、孙等）,不包含当前节点
        :param auto_driver:
        :param step:
        :return:
        """
        element_location = locator(auto_driver, step)
        return element_location.find_elements(By.XPATH, './descendant::*')

    @staticmethod
    def find_descendant_or_self(auto_driver: AutoDriver, step: TUiLocation):
        """
        查找当前节点的所有后代元素（子、孙等）,包含当前节点
        :param auto_driver:
        :param step:
        :return:
        """
        element_location = locator(auto_driver, step)
        return element_location.find_elements(By.XPATH, './descendant-or-self::*')

    @staticmethod
    def find(auto_driver: AutoDriver, step: TUiLocation):
        return Action.finds(auto_driver, step)[0]

    @staticmethod
    def hover(auto_driver: AutoDriver, step: TUiLocation):
        actions = ActionChains(auto_driver.driver)
        element_location = locator(auto_driver, step)
        actions.move_to_element(element_location)
        actions.perform()
        sleep(0.5)
        return element_location

    @staticmethod
    def double_click(auto_driver: AutoDriver, step: TUiLocation):
        actions = ActionChains(auto_driver.driver)
        element_location = locator(auto_driver, step)
        actions.double_click(element_location)
        actions.perform()
        sleep(0.5)
        return element_location

    @staticmethod
    def drag_and_drop(auto_driver: AutoDriver, step: TUiLocation):
        data = step.data
        """拖拽"""
        actions = ActionChains(auto_driver.driver)
        source = locator(auto_driver, data[0])
        target = locator(auto_driver, data[1])
        actions.drag_and_drop(source, target)
        actions.perform()
        sleep(0.5)

    @staticmethod
    def swipe(auto_driver: AutoDriver, step: TUiLocation):
        """滑动"""
        data = step.data
        actions = ActionChains(auto_driver.driver)
        source = locator(auto_driver, step)
        x = data.get('x', 0)
        y = data.get('y', 0)
        actions.drag_and_drop_by_offset(source, x, y)
        actions.perform()
        sleep(0.5)

    @staticmethod
    def script(auto_driver: AutoDriver, step: TUiLocation):
        """执行脚本"""
        auto_driver.driver.execute_script(step.data)

    @staticmethod
    def message(auto_driver: AutoDriver, step: TUiLocation):
        data = step['data']
        text = data.get('text', '')
        element = step['element']
        value = ''  # e.get(element)[1]

        # if value.lower() in ('确认', 'accept'):
        #     g.driver.switch_to_alert().accept()
        # elif value.lower() in ('取消', '关闭', 'cancel', 'close'):
        #     g.driver.switch_to_alert().dismiss()
        # elif value.lower() in ('输入', 'input'):
        #     g.driver.switch_to_alert().send_keys(text)
        #     g.driver.switch_to_alert().accept()
        logger.info('--- Switch Frame: Alert')
        # w.frame = 'Alert'

    @staticmethod
    def upload(auto_driver: AutoDriver, step: TUiLocation):
        """上传文件"""
        import win32com.client

        data = step['data']
        element = step['element']
        element_location = locator(auto_driver, step)
        file_path = data.get('text', '') or data.get('file', '')

        element_location.click()
        sleep(3)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.Sendkeys(file_path)
        sleep(2)
        shell.Sendkeys("{ENTER}")
        sleep(2)

    @staticmethod
    def navigate(auto_driver: AutoDriver, step: TUiLocation):
        """导航"""
        if step.value.lower() in ('刷新', 'refresh'):
            auto_driver.driver.refresh()
        elif step.value.lower() in ('前进', 'forward'):
            auto_driver.driver.forward()
        elif step.value.lower() in ('后退', 'back'):
            auto_driver.driver.back()

    @staticmethod
    def scroll(auto_driver: AutoDriver, step: TUiLocation):
        data = step.data
        """滚动"""
        x = data.get('x', 0)
        y = data.get('y', 0)

        element = step['element']
        if element == '':
            if y:
                auto_driver.driver.execute_script(f"document.documentElement.scrollTop={y}")
            if x:
                auto_driver.driver.execute_script(f"document.documentElement.scrollLeft={x}")
        else:
            element_location = locator(auto_driver, step)

            if y:
                auto_driver.driver.execute_script(f"arguments[0].scrollTop={y}", element_location)
            if x:
                auto_driver.driver.execute_script(f"arguments[0].scrollLeft={x}", element_location)

    @staticmethod
    def wait_page_loaded(auto_driver: AutoDriver):
        pass
