# -*- coding=utf-8 -*-
import os
import sys
import re
import time
import tempfile
import subprocess
import asyncio
from threading import Thread
import time
import json
import urllib

os.environ['WDM_LOCAL'] = '1'
os.environ['QT_LOGGING_RULES'] = '*.debug=false'

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, \
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QLineEdit, QListWidget, QMessageBox, QSplitter, \
    QMainWindow, QSpacerItem, QSizePolicy, QTextEdit, \
    QTextBrowser, QDialog, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from .BrowerDriver import BrowserAutomation
from .SpiderConfig import SpiderConfigWindow
from .YuanbianWidgets import YuanbianTextEdit
from .hook_js import hook_js


class BrowserApp(QMainWindow):
    result_ready = pyqtSignal(str)

    hook_js = hook_js

    

    def __init__(self):
        super().__init__()
        self.driver = None
        self.rule_window = None
        self.browser_thread = None
        self.setWindowTitle("猿变实验室爬虫工具-YuanbianSpiderTools")
        self.setGeometry(100, 100, 900, 800)
        self.create_main_layout()
        # 主窗口布局
        # 创建主布局
    def create_main_layout(self):
        # bug修复：将self.layout改为QHBoxLayout实例，避免调用function的属性
        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.splitter = QSplitter()
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet("background: #efefef")
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.create_left_menu()
        self.create_right_layout()
        self.setCentralWidget(self.splitter)
        # 删除self.setLayout(layout)
        self.setLayout(layout)

    def create_left_menu(self):
        options = [("可视化爬虫", self.show_main_interface),
                   ("JSON格式化", self.format_json),
                   ("CURL格式化", self.format_header),
                   ("Cookie格式化", self.format_cookie),
                   ("算法探针", self.encrypt_decrypt),
                   ("URL编码", self.url_encode),
                   ("URL解码", self.url_decode),
                   ("Unicode解码", self.unicode_decode),
                   ("网页测试", self.show_web_test),
                   ("Python运行环境", self.show_python_env),
                   ("Node.js运行环境", self.show_nodejs_env),
                   ("RPC服务器", self.show_nodejs_env),
                   ("WebSocket服务器", self.show_nodejs_env),
                   ("WebSocket客户端", self.show_nodejs_env),
                   ("爬虫知识库", self.show_nodejs_env),
                   ]

        for menu in options:
            btn = QPushButton(menu[0])
            if menu[1]:
                btn.clicked.connect(menu[1])
            self.left_layout.addWidget(btn)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.left_layout.addItem(spacer)
        self.splitter.addWidget(self.left_widget)

    def show_web_test(self):
        self.clear_right_layout()
        self.web_test_layout = QHBoxLayout()
        self.web_test_widget = QWidget()
        self.web_test_widget.setLayout(self.web_test_layout)

        # 网页显示区域
        self.web_output = QWebEngineView()
        self.web_output.setUrl(QUrl("https://www.python-xp.com/run_code/html#"))
        self.web_test_layout.addWidget(self.web_output)

        self.right_layout.addWidget(self.web_test_widget)

       

    def create_right_layout(self):
        # 右边的布局
        # 右侧功能区域（初始为空）
        self.right_layout = QVBoxLayout()
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("background: #fefefe")
        # self.layout.addWidget(self.right_widget, stretch=4)
        self.right_widget.setLayout(self.right_layout)

        self.top_right_widget = QWidget()
        self.top_right_layout = QHBoxLayout()
        self.top_right_widget.setLayout(self.top_right_layout)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入网址")
        self.url_input.setText("https://www.python-xp.com")
        self.start_button = QPushButton("打开网站")
        self.start_button.clicked.connect(self.open_browser)
        self.top_right_layout.addWidget(self.url_input)
        self.top_right_layout.addWidget(self.start_button)
        self.right_layout.addWidget(self.top_right_widget)
        self.code_editor = YuanbianTextEdit()
        self.code_editor.setPlaceholderText(
            "即将开始爬取"
        )
        self.right_layout.addWidget(self.code_editor)
        self.set_crawler_button = QPushButton("设置爬虫")
        self.set_crawler_button.clicked.connect(self.set_crawler_rule)
        self.start_spider_button = QPushButton("开始爬取")
        self.start_spider_button.clicked.connect(self.start_spider)
        self.right_layout.addWidget(self.set_crawler_button)
        self.right_layout.addWidget(self.start_spider_button)

        self.splitter.addWidget(self.right_widget)

        # self.websocket_server = WebSocketServer()
        # self.websocket_server.received_message.connect(self.on_received_message)

        # self.start_websocket_server()

    #
    def open_browser(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "输入错误", "请输入一个有效的网址")
            return
        self.browser_thread = BrowserAutomation(url, self.hook_js)
        self.browser_thread.result_ready.connect(self.handle_result)
        self.browser_thread.start()

    # def get_xpath(self):
    #     xpath = self.driver.execute_script("return window.xpath")
    #     print(xpath)
    def handle_result(self, data):
        if data == "fail":
            QMessageBox.warning(self, "下载驱动失败", "浏览器驱动无法下载，请稍后尝试")
            return
        self.code_editor.append(data)

    def flush(self):
        time.sleep(5)
        for i in range(1000):
            self.code_editor.append("hello")
            time.sleep(0.1)

    def start_websocket_server(self):
        self.websocket_server.start()

    def on_received_message(self, message):
        print("recived message:", message)

    def set_crawler_rule(self):
        if self.rule_window is None:
            self.rule_window = SpiderConfigWindow(self)
        # Bug修复：将Qt.WindowStaysOnTopHint替换为Qt.WindowStaysOnTop
        self.rule_window.setWindowFlags(self.rule_window.windowFlags() | Qt.WindowStaysOnTopHint)
        self.rule_window.show()

    def crawler_run(self, rule, target):
        if self.browser_thread:
            self.browser_thread.xpath_crawler(rule, target)

    def closeEvent(self, a0):
        print("窗口已经关闭", a0)
        if self.browser_thread and self.browser_thread.driver:
            self.browser_thread.driver.close()

    def start_spider(self):
        print(self.right_widget)


    def clear_right_layout(self):
        # 清空右侧布局
        for i in reversed(range(self.right_layout.count())): 
            widget = self.right_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def show_main_interface(self):
        self.clear_right_layout()
        # 创建主界面布局
        self.create_right_layout()

    def format_json(self):
        self.clear_right_layout()
        # 创建JSON格式化布局
        self.json_layout = QVBoxLayout()
        self.json_widget = QWidget()
        self.json_widget.setLayout(self.json_layout)
        
        # 左侧：JSON输入框
        self.json_input = YuanbianTextEdit()
        self.json_input.setPlaceholderText("请输入JSON字符串")
        self.json_layout.addWidget(self.json_input)
        
        # 格式化按钮
        self.format_button = QPushButton("格式化JSON")
        self.format_button.clicked.connect(self._format_json)
        self.json_layout.addWidget(self.format_button)
        
        # 右侧：格式化显示区域
        self.json_output = QTextBrowser()
        self.json_output.setPlaceholderText("格式化后的JSON将显示在这里")
        self.json_layout.addWidget(self.json_output)
        
        # 显示布局
        self.right_layout.addWidget(self.json_widget)

    def _format_json(self):
        try:
            json_str = self.json_input.toPlainText()
            json_str = json_str.strip()  # 去除前后空白
            json_str = json_str.strip("\"")
            json_str = json_str.strip("'")
            json_data = json.loads(json_str)
            formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
            self.json_output.setText(formatted_json)
        except Exception as e:
            QMessageBox.warning(self, "JSON格式错误", f"无效的JSON格式: {str(e)}")
    
    def _run_header_code(self):
        self._run_code(self.code_output, self.result_output)
    def _run_cookie_code(self):
        self._run_code(self.cookie_code_output, self.cookie_result_output)
    def _run_code(self, code_editor, result_output=None):
        if result_output is None:
            result_output = self.result_output
        try:
            # 获取代码内容
            code = code_editor.toPlainText()
            if not code:
                return

            # 创建临时文件执行代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # 在子进程中执行代码
            process = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            # 删除临时文件
            os.unlink(temp_file)

            # 显示执行结果
            if stderr:
                result_output.setText(stderr.decode('utf-8'))
            else:
                result_output.setText(stdout.decode('utf-8'))

        except Exception as e:
            result_output.setText(f"代码执行出错: {str(e)}")

    def _format_header(self):
        try:
            header_text = self.header_input.toPlainText().strip()
            if not header_text:
                return
            
            # 解析curl格式的header和url
            headers = {}
            url = ''
            for line in header_text.split('\n'):
                if line.strip().startswith('-H'):
                    # 提取-H后的内容
                    header = line.split('-H', 1)[1].strip()
                    # 去除引号
                    header = header.replace("\\", "")
                    header = header.strip(" ")
                    header = header.strip("\"")
                    header = header.strip("'")
                    
                    # 分割key和value
                    if ':' in header:
                        key, value = header.split(':', 1)
                        headers[key.strip()] = value.strip()
                elif line.strip().startswith('curl'):
                    # 提取url
                    url = line.split(' ')[1].strip()
                    url = url.strip("\"")
                    url = url.strip("'")
            
            # 生成输出
            output = "```python\n"
            output += "import requests\n\n"
            output += "url = '" + url + "'\n\n"
            output += "headers = " + json.dumps(headers, indent=4) + "\n\n"
            output += "response = requests.get(url, headers=headers)\n"
            output += "print(response.text)\n"
            output += "```"
            
            self.dict_output.setText(json.dumps(headers, indent=4, ensure_ascii=False))
            # self.code_output.setText(output)
            self.code_output.setMarkdown(output)
            self.code_output.show()
        except Exception as e:
            self.output_text.setText(f"格式化失败: {str(e)}")

    def format_header(self):
        self.clear_right_layout()
        # 创建header格式化布局
        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout()
        self.header_widget.setLayout(self.header_layout)
        
        # 添加header输入框
        self.header_input = YuanbianTextEdit()
        self.header_input.setPlaceholderText("请粘贴从浏览器开发者工具复制的curl请求头数据")
        self.header_layout.addWidget(self.header_input)
        
        # 添加格式化按钮
        self.format_header_button = QPushButton("格式化header")
        self.format_header_button.clicked.connect(self._format_header)
        self.header_layout.addWidget(self.format_header_button)
        
        # 添加输出区域
        self.dict_output = QTextBrowser()
        self.dict_output.setPlaceholderText("转换后的header字典将显示在这里")
        self.header_layout.addWidget(self.dict_output)

        self.code_output = YuanbianTextEdit()
        self.code_output.setPlaceholderText("requests使用示例将显示在这里")
        self.header_layout.addWidget(self.code_output)

        # 添加运行按钮
        self.run_button = QPushButton("运行代码")
        self.run_button.clicked.connect(self._run_header_code)
        self.header_layout.addWidget(self.run_button)

        # 添加结果显示区域
        self.result_output = QTextBrowser()
        self.result_output.setPlaceholderText("代码执行结果将显示在这里")
        self.header_layout.addWidget(self.result_output)
        
        # 显示布局
        self.right_layout.addWidget(self.header_widget)

    def format_cookie(self):
        self.clear_right_layout()
        # 创建cookie格式化布局
        self.cookie_widget = QWidget()
        self.cookie_layout = QVBoxLayout()
        self.cookie_widget.setLayout(self.cookie_layout)
        
        # 添加cookie输入框
        self.cookie_input = YuanbianTextEdit()
        self.cookie_input.setPlaceholderText("请输入cookie字符串（格式如：key1=val1; key2=val2）")
        self.cookie_layout.addWidget(self.cookie_input)
        
        # 添加格式化按钮
        self.format_cookie_button = QPushButton("格式化cookie")
        self.format_cookie_button.clicked.connect(self._format_cookie)
        self.cookie_layout.addWidget(self.format_cookie_button)
        
        # 添加字典输出区域
        self.cookie_dict_output = QTextBrowser()
        self.cookie_dict_output.setPlaceholderText("格式化后的Cookie字典将显示在这里")
        self.cookie_layout.addWidget(self.cookie_dict_output)
        
        # 添加代码示例区域
        self.cookie_code_output = YuanbianTextEdit()
        self.cookie_code_output.setPlaceholderText("requests使用示例将显示在这里")
        self.cookie_layout.addWidget(self.cookie_code_output)
        # 添加运行按钮
        self.run_cookie_button = QPushButton("运行代码")
        self.run_cookie_button.clicked.connect(self._run_cookie_code)
        self.cookie_layout.addWidget(self.run_cookie_button)
        
        # 添加结果显示区域
        self.cookie_result_output = QTextBrowser()
        self.cookie_result_output.setPlaceholderText("代码执行结果将显示在这里")
        self.cookie_layout.addWidget(self.cookie_result_output)
        
        # 显示布局
        self.right_layout.addWidget(self.cookie_widget)

    def _format_cookie(self):
        try:
            cookie_str = self.cookie_input.toPlainText().strip()
            if not cookie_str:
                return
            
            # 将Cookie字符串转换为字典
            cookie_dict = {}
            for item in cookie_str.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookie_dict[key.strip()] = value.strip()
            
            # 显示格式化结果
            self.cookie_dict_output.setText(json.dumps(cookie_dict, indent=4, ensure_ascii=False))
            
            # 生成requests使用示例
            code_example = "```python\n"
            code_example += "import requests\n\n"
            code_example += "cookies = " + json.dumps(cookie_dict, indent=4) + "\n\n"
            code_example += "response = requests.get('https://example.com', cookies=cookies)\n"
            code_example += "print(response.text)\n"
            code_example += "```"
            self.cookie_code_output.setMarkdown(code_example)
        except Exception as e:
            QMessageBox.warning(self, "Cookie格式错误", f"无效的Cookie格式: {str(e)}")

    def encrypt_decrypt(self):
        self.clear_right_layout()
        # 创建加解密布局
        self.encrypt_widget = QWidget()
        self.encrypt_layout = QVBoxLayout()
        self.encrypt_widget.setLayout(self.encrypt_layout)
        
        # 添加输入框
        self.encrypt_input = YuanbianTextEdit()
        self.encrypt_input.setPlaceholderText("请输入待加密明文文本")
        self.encrypt_layout.addWidget(self.encrypt_input)

        self.decrypt_input = YuanbianTextEdit()
        self.decrypt_input.setPlaceholderText("请输入加密后的密文")
        self.encrypt_layout.addWidget(self.decrypt_input)

        self.encrypt_button = QPushButton("算法探测")
        self.encrypt_button.clicked.connect(self._encrypt)
        self.encrypt_layout.addWidget(self.encrypt_button)

        self.result_output = QTextBrowser()
        self.result_output.setPlaceholderText("算法验证结果将显示在这里")
        self.encrypt_layout.addWidget(self.result_output)

        # 显示布局
        self.right_layout.addWidget(self.encrypt_widget)

    def _encrypt(self):
        try:
            from hashlib import md5, sha1, sha256, sha512, sha3_512, sha3_384, sha3_256, sha3_224, new
            import base64, codecs, hmac

            text = self.encrypt_input.toPlainText()
            if not text:
                return

            results = []
            user_cipher = self.decrypt_input.toPlainText()
            # MD5
            md5_result = md5(text.encode()).hexdigest()
            md5_style = 'color: red;' if md5_result == user_cipher else ''
            results.append(f"<span style='{md5_style}'>MD5: {md5_result}</span>")
            # SHA系列
            sha1_result = sha1(text.encode()).hexdigest()
            sha1_style = 'color: red;' if sha1_result == user_cipher else ''
            results.append(f"<span style='{sha1_style}'>SHA1: {sha1_result}</span>")
            sha256_result = sha256(text.encode()).hexdigest()
            sha256_style = 'color: red;' if sha256_result == user_cipher else ''
            results.append(f"<span style='{sha256_style}'>SHA256: {sha256_result}</span>")
            sha512_result = sha512(text.encode()).hexdigest()
            sha512_style = 'color: red;' if sha512_result == user_cipher else ''
            results.append(f"<span style='{sha512_style}'>SHA512: {sha512_result}</span>")
            sha3_512_result = sha3_512(text.encode()).hexdigest()
            sha3_512_style = 'color: red;' if sha3_512_result == user_cipher else ''
            results.append(f"<span style='{sha3_512_style}'>SHA3-512: {sha3_512_result}</span>")
            sha3_384_result = sha3_384(text.encode()).hexdigest()
            sha3_384_style = 'color: red;' if sha3_384_result == user_cipher else ''
            results.append(f"<span style='{sha3_384_style}'>SHA3-384: {sha3_384_result}</span>")
            sha3_256_result = sha3_256(text.encode()).hexdigest()
            sha3_256_style = 'color: red;' if sha3_256_result == user_cipher else ''
            results.append(f"<span style='{sha3_256_style}'>SHA3-256: {sha3_256_result}</span>")
            sha3_224_result = sha3_224(text.encode()).hexdigest()
            sha3_224_style = 'color: red;' if sha3_224_result == user_cipher else ''
            results.append(f"<span style='{sha3_224_style}'>SHA3-224: {sha3_224_result}</span>")
            # Base64
            base64_result = base64.b64encode(text.encode()).decode()
            base64_style = 'color: red;' if base64_result == user_cipher else ''
            results.append(f"<span style='{base64_style}'>Base64: {base64_result}</span>")
            # Hex
            hex_result = text.encode().hex()
            hex_style = 'color: red;' if hex_result == user_cipher else ''
            results.append(f"<span style='{hex_style}'>Hex: {hex_result}</span>")
            # UTF-8/16
            results.append(f"UTF-8: {text.encode('utf-8').decode('utf-8')}")
            results.append(f"UTF-16: {text.encode('utf-16').decode('utf-16')}")
            # 显示结果
            self.result_output.setText("<br>".join(results))

        except Exception as e:
            QMessageBox.warning(self, "加密错误", f"加密过程中出现错误: {str(e)}")

    def _decrypt(self):
        try:
            import base64, codecs

            ciphertext = self.decrypt_input.toPlainText()
            if not ciphertext:
                return

            results = []
            # Base64
            try:
                results.append(f"Base64: {base64.b64decode(ciphertext).decode()}")
            except:
                pass
            # Hex
            try:
                results.append(f"Hex: {bytes.fromhex(ciphertext).decode()}")
            except:
                pass
            # 显示结果
            self.result_output.setText("\n".join(results))

        except Exception as e:
            QMessageBox.warning(self, "解密错误", f"解密过程中出现错误: {str(e)}")

        # 显示布局
        self.right_layout.addWidget(self.encrypt_widget)

    def url_encode(self):
        self.clear_right_layout()
        # 创建URL编码布局
        self.url_encode_widget = QWidget()
        self.url_encode_layout = QVBoxLayout()
        self.url_encode_widget.setLayout(self.url_encode_layout)
        
        # 添加URL输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入URL")
        self.url_encode_layout.addWidget(self.url_input)
        
        # 添加编码按钮
        self.encode_button = QPushButton("URL编码")
        self.encode_button.clicked.connect(self._url_encode)
        self.url_encode_layout.addWidget(self.encode_button)
        
        # 添加结果显示区域
        self.url_output = QTextBrowser()
        self.url_output.setPlaceholderText("编码结果将显示在这里")
        self.url_encode_layout.addWidget(self.url_output)
        
        # 显示布局
        self.right_layout.addWidget(self.url_encode_widget)

    def _url_encode(self):
        try:
            text = self.url_input.text().strip()
            if not text:
                return
            encoded_text = urllib.parse.quote(text)
            self.url_output.setText(encoded_text)
        except Exception as e:
            QMessageBox.warning(self, "URL编码错误", f"编码失败: {str(e)}")

    def url_decode(self):
        self.clear_right_layout()
        # 创建URL解码布局
        self.url_decode_widget = QWidget()
        self.url_decode_layout = QVBoxLayout()
        self.url_decode_widget.setLayout(self.url_decode_layout)
        
        # 添加URL输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入URL")
        self.url_decode_layout.addWidget(self.url_input)
        
        # 添加解码按钮
        self.decode_button = QPushButton("URL解码")
        self.decode_button.clicked.connect(self._url_decode)
        self.url_decode_layout.addWidget(self.decode_button)
        
        # 添加结果显示区域
        self.url_output = QTextBrowser()
        self.url_output.setPlaceholderText("解码结果将显示在这里")
        self.url_decode_layout.addWidget(self.url_output)
        
        # 显示布局
        self.right_layout.addWidget(self.url_decode_widget)

    def _url_decode(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "输入错误", "请输入一个有效的URL")
            return
        try:
            decoded = urllib.parse.unquote(url)
            self.url_output.setText(decoded)
        except Exception as e:
            QMessageBox.warning(self, "解码错误", f"解码失败: {str(e)}")

    def unicode_decode(self):
        self.clear_right_layout()
        # 创建Unicode解码布局
        self.unicode_decode_widget = QWidget()
        self.unicode_decode_layout = QVBoxLayout()
        self.unicode_decode_widget.setLayout(self.unicode_decode_layout)
        
        # 添加Unicode输入框
        self.unicode_input = QLineEdit()
        self.unicode_input.setPlaceholderText("请输入Unicode字符串")
        self.unicode_decode_layout.addWidget(self.unicode_input)
        
        # 添加解码按钮
        self.decode_button = QPushButton("解码Unicode")
        self.decode_button.clicked.connect(self._unicode_decode)
        self.unicode_decode_layout.addWidget(self.decode_button)
        
        # 添加结果显示区域
        self.unicode_output = QTextBrowser()
        self.unicode_output.setPlaceholderText("解码结果将显示在这里")
        self.unicode_decode_layout.addWidget(self.unicode_output)
        
        # 显示布局
        self.right_layout.addWidget(self.unicode_decode_widget)

    def _unicode_decode(self):
        unicode_str = self.unicode_input.text()
        if not unicode_str:
            QMessageBox.warning(self, "输入错误", "请输入有效的Unicode字符串")
            return
        try:
            decoded = unicode_str.encode('utf-8').decode('unicode_escape')
            self.unicode_output.setText(decoded)
        except Exception as e:
            QMessageBox.warning(self, "解码错误", f"Unicode解码失败: {str(e)}")

    def show_python_env(self):
        self.clear_right_layout()
        self.python_env_layout = QVBoxLayout()
        self.python_env_widget = QWidget()
        self.python_env_widget.setLayout(self.python_env_layout)

        self.python_editor = YuanbianTextEdit()
        self.python_editor.setPlaceholderText("请输入Python代码")
        self.python_env_layout.addWidget(self.python_editor)

        self.run_python_button = QPushButton("运行")
        self.run_python_button.clicked.connect(self._run_python_code)
        self.python_env_layout.addWidget(self.run_python_button)

        self.python_output = QTextBrowser()
        self.python_output.setPlaceholderText("运行结果将显示在这里")
        self.python_env_layout.addWidget(self.python_output)

        self.right_layout.addWidget(self.python_env_widget)

    def _run_python_code(self):
        code = self.python_editor.toPlainText()
        if not code:
            return
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            process = subprocess.Popen([sys.executable, temp_file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            os.unlink(temp_file)
            if stderr:
                self.python_output.setText(stderr.decode('utf-8'))
            else:
                self.python_output.setText(stdout.decode('utf-8'))
        except Exception as e:
            self.python_output.setText(f"代码执行出错: {str(e)}")

    def show_nodejs_env(self):
        self.clear_right_layout()
        self.nodejs_env_layout = QVBoxLayout()
        self.nodejs_env_widget = QWidget()
        self.nodejs_env_widget.setLayout(self.nodejs_env_layout)

        self.nodejs_editor = YuanbianTextEdit()
        self.nodejs_editor.setPlaceholderText("请输入Node.js代码")
        self.nodejs_env_layout.addWidget(self.nodejs_editor)

        self.run_nodejs_button = QPushButton("运行")
        self.run_nodejs_button.clicked.connect(self._run_nodejs_code)
        self.nodejs_env_layout.addWidget(self.run_nodejs_button)

        self.nodejs_output = QTextBrowser()
        self.nodejs_output.setPlaceholderText("运行结果将显示在这里")
        self.nodejs_env_layout.addWidget(self.nodejs_output)

        self.right_layout.addWidget(self.nodejs_env_widget)

    def _run_nodejs_code(self):
        code = self.nodejs_editor.toPlainText()
        if not code:
            return
        try:
            process = subprocess.Popen(['node', '-e', code],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                self.nodejs_output.setText(stderr.decode('utf-8'))
            else:
                self.nodejs_output.setText(stdout.decode('utf-8'))
        except Exception as e:
            self.nodejs_output.setText(f"代码执行出错: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BrowserApp()
    window.show()

    sys.exit(app.exec_())
