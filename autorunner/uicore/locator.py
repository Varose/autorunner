#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/30 10:18
# @Author : liangchunhua
# @Desc   : 等待元素，并返回元素类
from time import sleep

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from autorunner.models import TUiLocation
from autorunner.uicore.driver import AutoDriver


def locator(auto_driver: AutoDriver, step: TUiLocation):
    wait = WebDriverWait(auto_driver.driver, auto_driver.implicitly_wait_time)
    if step.by in ('title', 'url', 'current_url'):
        return None
    else:
        try:
            location = wait.until(EC.presence_of_element_located(
                (getattr(By, step.by), step.value)))
        except:
            sleep(5)
            try:
                location = wait.until(EC.presence_of_element_located(
                    (getattr(By, step.by), step.value)))
            except TimeoutException:
                raise TimeoutException(f'定位元素: {step.by}({step.value}) 失败: 超时')
    try:
        if auto_driver.driver.name in ('chrome', 'safari'):
            auto_driver.driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true)", location)
        else:
            auto_driver.driver.execute_script("arguments[0].scrollIntoView(false)", location)
    except:
        pass

    try:
        if step.action.upper() == 'CLICK':
            location = wait.until(EC.element_to_be_clickable(
                (getattr(By, step.by), step.value)))
        else:
            location = wait.until(EC.visibility_of_element_located(
                (getattr(By, step.by), step.value)))
    except:
        pass

    return location
