#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/11/1 13:32
# @Author : liangchunhua
# @Desc   : ui自动化元素结果校验
import time
from typing import Dict, Text, Any, List

import jmespath
import requests
from jmespath.exceptions import JMESPathError
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from autorunner import exceptions
from autorunner.exceptions import ValidationFailure, ParamsError, FunctionNotFound
from autorunner.models import VariablesMapping, Validators, FunctionsMapping, TUiLocation
from autorunner.parser import parse_data, parse_string_value, get_mapping_function
from autorunner.uicore.driver import AutoDriver
from autorunner.uicore.web_action import Action


def get_uniform_comparator(comparator: Text):
    """
    convert comparator alias to uniform name
    """
    if comparator in ["eq", "equals", "equal"]:
        return "equal"
    elif comparator in ["lt", "less_than"]:
        return "less_than"
    elif comparator in ["le", "less_or_equals"]:
        return "less_or_equals"
    elif comparator in ["gt", "greater_than"]:
        return "greater_than"
    elif comparator in ["ge", "greater_or_equals"]:
        return "greater_or_equals"
    elif comparator in ["ne", "not_equal"]:
        return "not_equal"
    elif comparator in ["str_eq", "string_equals"]:
        return "string_equals"
    elif comparator in ["len_eq", "length_equal"]:
        return "length_equal"
    elif comparator in [
        "len_gt",
        "length_greater_than",
    ]:
        return "length_greater_than"
    elif comparator in [
        "len_ge",
        "length_greater_or_equals",
    ]:
        return "length_greater_or_equals"
    elif comparator in ["len_lt", "length_less_than"]:
        return "length_less_than"
    elif comparator in [
        "len_le",
        "length_less_or_equals",
    ]:
        return "length_less_or_equals"
    elif comparator in [
        "cont",
        "contains",
    ]:
        # 包含 expect_value
        return "contains"
    elif comparator in [
        "cont_by",
        "contained_by",
    ]:
        # expect_value 包含check_value
        return "contained_by"
    elif comparator in [
        "startswith",
    ]:
        return "startswith"
    elif comparator in [
        "endswith",
    ]:
        return "endswith"
    elif comparator in [
        "regex_match",
    ]:
        return "regex_match"
    else:
        return comparator


class ElementObj:

    def __init__(self, driver: AutoDriver):
        self.__check_item = None
        self.__assert_method = None
        self.driver = driver
        self.validation_results: Dict = {}

    def uniform_validator_element(self, validator):
        if not isinstance(validator, dict):
            raise ParamsError(f"invalid validator: {validator}")

        if len(validator) == 1:
            # format2
            comparator = list(validator.keys())[0]
            compare_values = validator[comparator]

            if not isinstance(compare_values, dict) or len(compare_values) not in [3, 4, 5]:
                raise ParamsError(f"invalid validator: {validator}")
            check_item, expect_value = None, None
            for key, value in compare_values.items():
                if str(key).lower() in ['by', 'value', 'msg', 'action']:
                    continue
                check_item = str(key)
                expect_value = value

            message = "" if 'msg' not in compare_values else compare_values['msg']

            ui_location_obj = TUiLocation.model_validate(compare_values)
            action = 'finds' if not ui_location_obj.action else ui_location_obj.action
            if not hasattr(Action, action):
                funcs = [w for w in dir(Action) if callable(getattr(Action, w)) and not w.startswith("__")]
                logger.error(f'action: {action}, 操作方法不存在以下列表中:{funcs}')
                raise AttributeError(f'action: {action}, 操作方法不存在以下列表中:{funcs}')

            elements = getattr(Action, action)(self.driver, ui_location_obj)
            # logger.info(f'元素定位查询结果：{[vars(element) for element in elements]}')
        else:
            raise ParamsError(f"invalid validator: {validator}")

        # uniform comparator, e.g. lt => less_than, eq => equals
        assert_method = get_uniform_comparator(comparator)
        self.__check_item = check_item
        return {
            "check": check_item,
            "expect": expect_value,
            "assert": assert_method,
            "message": message,
            "elements": elements,
            # make.py中使用
            "compare_values": compare_values,
        }

    def get_element_check_value(self, elements: List[WebElement]):
        if 'len' in self.__check_item:
            return str(len(elements))
        elif 'visible' in self.__check_item:
            # 元素是否存在,true存在，false不存在
            return False if len(elements) == 0 else True
        else:
            if 'val' == str(self.__check_item).lower():
                if len(elements) == 0:
                    return None
                if len(elements) == 1:
                    # 查找当前元素及其所有后代元素的text
                    ele = elements[0]
                    texts = [s.strip() for s in ele.text.split('\n')]
                    return ','.join(texts)
                else:
                    # 数据验证, 获取List每个WebElement的text
                    texts = []
                    for element in elements:
                        # 标签文本内容
                        text = element.text.replace('\n', '').strip()
                        texts.append(text)
                    return ','.join(texts)
            if len(elements) > 0:
                ele = elements[0]
                # 获取属性值 class,id,style,title,src,href,alt,type,value,name,placeholder,disabled,checked,selected,
                # readonly(不会让元素变为灰色),rel,text
                attribute_value = ele.get_attribute(self.__check_item)
                if attribute_value:
                    return attribute_value
            return None

    def validate(
            self,
            validators: Validators,
            variables_mapping: VariablesMapping = None,
            functions_mapping: FunctionsMapping = None,
    ):

        variables_mapping = variables_mapping or {}
        functions_mapping = functions_mapping or {}

        self.validation_results = {}
        if not validators:
            return

        validate_pass = True
        failures = []

        for v in validators:

            if "validate_extractor" not in self.validation_results:
                self.validation_results["validate_extractor"] = []

            u_validator = self.uniform_validator_element(v)

            # check item
            check_item = u_validator["check"]
            elements = list(u_validator["elements"])

            check_value = self.get_element_check_value(elements)

            # comparator
            assert_method = u_validator["assert"]

            assert_func = get_mapping_function(assert_method, functions_mapping)

            # expect item
            expect_item = u_validator["expect"]
            # parse expected value with config/teststep/extracted variables
            expect_value = parse_data(expect_item, variables_mapping, functions_mapping)

            # message
            message = u_validator["message"]
            # parse message with config/teststep/extracted variables
            message = parse_data(message, variables_mapping, functions_mapping)

            validate_msg = f"assert {check_value} {assert_method} {expect_value}({type(expect_value).__name__})"
            validator_dict = {
                "comparator": assert_method,
                "check": check_item,
                "check_value": check_value,
                "expect": expect_item,
                "expect_value": expect_value,
                "message": message,
            }

            try:
                if str(assert_func.__name__).startswith('check_'):
                    assert_func(elements, expect_value, message)
                else:
                    assert_func(check_value, expect_value, message)
                validate_msg += "\t==> pass"
                logger.info(validate_msg)
                validator_dict["check_result"] = "pass"
            except AssertionError as ex:
                validate_pass = False
                validator_dict["check_result"] = "fail"
                validate_msg += "\t==> fail"
                validate_msg += (
                    f"\n"
                    f"check_item: {check_item}\n"
                    f"check_value: {check_value}({type(check_value).__name__})\n"
                    f"assert_method: {assert_method}\n"
                    f"expect_value: {expect_value}({type(expect_value).__name__})\n"
                    f"query_elements_class: "
                )
                for items in v.values():
                    if isinstance(items, dict):
                        validate_msg += f" by={items['by']},value={items['value']}\n"
                if len(elements) == 0:
                    validate_msg += '\t → elements is empty'
                else:
                    for ele in elements:
                        validate_msg += f"\t → {ele.get_attribute('class')}\n"

                message = str(ex)
                if message:
                    validate_msg += f"\nmessage: {message}"

                logger.error(validate_msg)
                failures.append(validate_msg)

            self.validation_results["validate_extractor"].append(validator_dict)

        if not validate_pass:
            failures_string = "\n".join([failure for failure in failures])
            raise ValidationFailure(failures_string)
