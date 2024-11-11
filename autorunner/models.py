import os
import typing
from enum import Enum
from typing import Any
from typing import Dict, Text, Union, Callable
from typing import List

from pydantic import BaseModel, Field, field_validator, ValidationError
from pydantic import HttpUrl

Name = Text
Url = Text
BaseUrl = Union[HttpUrl, Text]
VariablesMapping = Dict[Text, Any]
FunctionsMapping = Dict[Text, Callable]
Headers = Dict[Text, Text]
Cookies = Dict[Text, Text]
Verify = bool
Hooks = List[Union[Text, Dict[Text, Text]]]
Export = List[Text]
Validators = List[Dict]
Env = Dict[Text, Any]


class MethodEnum(Text, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


class StepTypeEnum(str, Enum):
    """步骤类型枚举"""
    API = "API"
    SQL = "SQL"
    UI = "UI"


class TConfig(BaseModel):
    name: Name
    verify: Verify = False
    base_url: BaseUrl = ""
    # Text: prepare variables in debugtalk.py, ${gen_variables()}
    variables: Union[VariablesMapping, Text] = {}
    parameters: Union[VariablesMapping, Text] = {}
    # setup_hooks: Hooks = []
    # teardown_hooks: Hooks = []
    export: Export = []
    path: Text = None
    weight: int = 1
    datasource: str = None


class TRequest(BaseModel):
    """requests.Request model"""

    method: MethodEnum
    url: Url
    params: Dict[Text, Text] = {}
    headers: Headers = {}
    req_json: Union[Dict, List, Text] = Field(None, alias="json")
    data: Union[Text, Dict[Text, Any]] = None
    cookies: Cookies = {}
    timeout: float = 120
    allow_redirects: bool = True
    verify: Verify = False
    upload: Dict = {}  # used for upload files


class TUiLocation(BaseModel):
    """ui模型"""
    action: str = Field(None, description="动作")
    data: Union[Dict, List, Text, int] = Field({}, description="输入数据")
    by: typing.Literal[
        'ID', 'XPATH', 'LINK_TEXT', 'PARTIAL_LINK_TEXT', 'NAME', 'TAG_NAME', 'CLASS_NAME', 'CSS_SELECTOR'] = Field(None, description="定位器")
    value: str = Field(None, description="定位值")
    sleep: int = Field(0, ge=0, description="睡眠时间")
    desc: str = Field(None, description="描述")
    time: int = Field(0, ge=0, description="等待元素时间")
    # @field_validator('action')
    # def check_action_func_name(cls,v):
    #     """
    #     校验action的传参,需要匹配Action的静态方法
    #     :param v:
    #     :return:
    #     """
    #     from autorunner.uicore.web_action import Action
    #     if '$' in v or v is None:
    #         return v
    #     funcs = [w for w in dir(Action) if callable(getattr(Action, w)) and not w.startswith("__")]
    #     if v not in funcs:
    #         raise ValueError(f'action: {v}, 操作方法不存在以下列表中:{funcs}')
    #     return v


class SqlData(BaseModel):
    """sql数据"""
    datasource: str = Field(None, description="数据源")
    dml: List[str] = Field([], description="sql语句")

    @field_validator('dml')
    def check_dml_content(cls, v):
        for i in v:
            if '*' in i:
                raise ValidationError(f'{i},不能使用*查询,请查询具体字段！')
        return v


class TStep(BaseModel):
    name: Name
    request: Union[TRequest, None] = None
    testcase: Union[Text, Callable, None] = None
    variables: VariablesMapping = {}
    setup_hooks: Hooks = []
    teardown_hooks: Hooks = []
    # used to extract request's response field
    extract: VariablesMapping = {}
    # used to export session variables from referenced testcase
    export: Export = []
    validators: Validators = Field([], alias="validate")
    validate_script: List[Text] = []
    skip: Text = None
    step_type: StepTypeEnum = Field(StepTypeEnum.API, description="步骤类型 api sql ui", alias="type")
    location: Union[List[TUiLocation], None] = None
    sql: Union[List[SqlData], None] = None


class TestCase(BaseModel):
    config: TConfig
    teststeps: List[TStep]


class ProjectMeta(BaseModel):
    debugtalk_py: Text = ""  # debugtalk.py file content
    debugtalk_path: Text = ""  # debugtalk.py file path
    dot_env_path: Text = ""  # .env file path
    functions: FunctionsMapping = {}  # functions defined in debugtalk.py
    env: Env = {}
    RootDir: Text = os.getcwd()  # project root directory (ensure absolute), the path debugtalk.py located


class TestsMapping(BaseModel):
    project_meta: ProjectMeta
    testcases: List[TestCase]


class TestCaseTime(BaseModel):
    """用例时间"""
    start_at: float = 0
    start_at_iso_format: Text = ""  # 开始系统时间
    duration: float = 0


class TestCaseInOut(BaseModel):
    """用例输入输出"""
    config_vars: VariablesMapping = {}
    export_vars: Dict = {}


class RequestStat(BaseModel):
    """请求统计"""
    content_size: float = 0  # 响应内容大小
    response_time_ms: float = 0  # 响应时间 毫秒
    elapsed_ms: float = 0  # 过程时间


class AddressData(BaseModel):
    """地址信息"""
    client_ip: Text = "N/A"
    client_port: int = 0
    server_ip: Text = "N/A"
    server_port: int = 0


class RequestData(BaseModel):
    method: MethodEnum = MethodEnum.GET
    url: Url
    headers: Headers = {}
    cookies: Cookies = {}
    body: Union[Text, bytes, List, Dict, None] = {}


class ResponseData(BaseModel):
    status_code: int
    headers: Dict
    cookies: Cookies
    encoding: Union[Text, None] = None
    content_type: Text
    body: Union[Text, bytes, List, Dict, None]


class ReqRespData(BaseModel):
    request: RequestData
    response: ResponseData


class SessionData(BaseModel):
    """ 请求会话数据 request session data, including request, response, validators and stat data"""

    success: bool = False
    # in most cases, req_resps only contains one request & response
    # while when 30X redirect occurs, req_resps will contain multiple request & response
    req_resps: List[ReqRespData] = []
    stat: RequestStat = RequestStat()
    address: AddressData = AddressData()
    validators: Dict = {}


class StepData(BaseModel):
    """teststep data, each step maybe corresponding to one request or one testcase"""

    success: bool = False
    name: Text = ""  # teststep name
    data: Union[SessionData, List['StepData']] = None
    export_vars: VariablesMapping = {}


StepData.update_forward_refs()


class TestCaseSummary(BaseModel):
    """用例汇总数据"""
    name: Text
    success: bool
    case_id: Text
    time: TestCaseTime
    in_out: TestCaseInOut = {}
    log: Text = ""
    step_datas: List[StepData] = []
    # ------------------- 20241029
    # run_count: int  # 运行数量
    # actual_run_count: int  # 实际执行数量
    # run_success_count: int  # 运行成功数
    # run_fail_count: int  # 运行错误数
    # run_skip_count: int  # 运行跳过数
    # run_err_count: int  # 运行错误数
    # start_time_iso_format: str  # 运行时间系统时间
    # # message 记录错误信息
    # message: str


class PlatformInfo(BaseModel):
    autorunner_version: Text
    python_version: Text
    platform: Text


class TestCaseRef(BaseModel):
    name: Text
    base_url: Text = ""
    testcase: Text
    variables: VariablesMapping = {}


class TestSuite(BaseModel):
    config: TConfig
    testcases: List[TestCaseRef]


class Stat(BaseModel):
    """统计数据"""
    total: int = 0
    success: int = 0
    fail: int = 0


class TestSuiteSummary(BaseModel):
    """测试套件汇总数据"""
    success: bool = False
    stat: Stat = Stat()
    time: TestCaseTime = TestCaseTime()
    platform: PlatformInfo
    testcases: List[TestCaseSummary]
