#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/31 16:50
# @Author : liangchunhua
# @Desc   :
import copy
import os
import re
import time
from typing import Dict

from autorunner.uicore.web_action import Action

def merge_variables(
    variables: Dict, variables_to_be_overridden: Dict
) :
    """ merge two variables mapping, the first variables have higher priority
    """
    step_new_variables = {}
    for key, value in variables.items():
        if f"${key}" == value or "${" + key + "}" == value:
            # e.g. {"base_url": "$base_url"}
            # or {"base_url": "${base_url}"}
            continue

        step_new_variables[key] = value

    merged_variables = copy.copy(variables_to_be_overridden)
    merged_variables.update(step_new_variables)
    return merged_variables

if __name__ == '__main__':
    variables = {}
    variables_to_be_overridden = {'code':'123'}
    print(merge_variables(variables, variables_to_be_overridden))
