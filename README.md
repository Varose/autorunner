# autorunner

创建venv虚拟环境并激活，最后安装依赖
```
$ python -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

--startproject: 创建一个新的项目

--startcase: 创建一个新的测试用例

--dot-env: 指定环境变量文件

--failfast: 出现失败时即即停止测试

--html: 生成 HTML 报告

--json-report: 生成 JSON 报告

--log-level: 设置日志级别

--no-html-report: 不生成 HTML 报告

--no-json-report: 不生成 JSON 报告

--output-file: 指定输出文件

--report-dir: 指定报告目录

--testcase: 运行单个测试用例

--testsuite: 运行测试套件

hrun =httprunner run，用于运行 YAML/JSON/pytest 测试用例

hmake =httprunner make，用于将 YAML/JSON 测试用例转换为 pytest 文件

har2case =httprunner har2case，用于将 HAR 转换为 YAML/JSON 测试用例
