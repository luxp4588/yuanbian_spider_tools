# -*- coding=utf-8 -*-
import os
import sys
import time
import asyncio
from threading import Thread
import time
import json

os.environ['WDM_LOCAL'] = '1'
os.environ['QT_LOGGING_RULES'] = '*.debug=false'

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, \
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QLineEdit, QListWidget, QMessageBox, QSplitter, \
    QMainWindow, QSpacerItem, QSizePolicy, QTextEdit, \
    QTextBrowser, QDialog, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from BrowerDriver import BrowserAutomation
from SpiderConfig import SpiderConfigWindow
from YuanbianWidgets import YuanbianTextEdit
from PyQt5.QtGui import QFont, QIcon


class BrowserApp(QMainWindow):
    result_ready = pyqtSignal(str)



    hook_js = """(function() {
    window.xpaths = [];
    var rect = {};
    window.mouseIsDown = false;
    window.end_select = false;
    window.copyTextToClipboard = function (xpath) {
        // e.stopPropagation();
        try {
            navigator.clipboard.writeText(xpath);
            console.log('Text copied to clipboard');
        } catch (err) {
            console.error('Could not copy text: ', err);
        }
    }
    window.resetSelect = function() {
        window.mouseIsDown = false;
        window.end_select = false;
        selectionDiv.style.width = "0px"
        selectionDiv.style.height = "0px"
        selectionDiv.innerHTML = ""
        console.log("重新选择")
    }
    function createSelectionDiv() {
        var selectionDiv = document.getElementById("crawler-area")
        if (!selectionDiv) {
            var selectionDiv = document.createElement('div');
            selectionDiv.id = "crawler-area"
            selectionDiv.style.border = "3px dashed #0099FF";
            selectionDiv.style.position = "absolute";
            selectionDiv.style.background = "#ffffff";
            selectionDiv.style.opacity = 0.7;
            selectionDiv.style.pointerEvents = "none";
            selectionDiv.style.zIndex = "1000";
            selectionDiv.style.color = "#000";
            selectionDiv.style.fontWeight = "Bold"
            selectionDiv.style.pointerEvents = "auto"
            document.body.appendChild(selectionDiv);
        }
        return selectionDiv;
    }
    var selectionDiv = createSelectionDiv();
    document.addEventListener('mousedown', function(e) {
        if (window.end_select || window.mouseIsDown ) return;
        window.mouseIsDown = true;
        rect.startX = e.pageX;
        rect.startY = e.pageY;
        console.log(e.pageX, e.pageY, e.clientX, e.clientY);
        selectionDiv.style.left = e.pageX + 'px';
        selectionDiv.style.top = e.pageY + 'px';
        selectionDiv.innerText = selectionDiv.style.left + " " + selectionDiv.style.top + " " + rect.startX + " " +rect.startY ;
    });
    document.addEventListener('mousemove', function(e) {
        if (window.end_select || !window.mouseIsDown ) return;
        var x = Math.min(e.pageX, rect.startX);
        var y = Math.min(e.pageY, rect.startY);
        var w = Math.abs(e.pageX - rect.startX);
        var h = Math.abs(e.pageY - rect.startY);
        selectionDiv.style.left = x + 'px';
        selectionDiv.style.top = y + 'px';
        selectionDiv.style.width = w + 'px';
        selectionDiv.style.height = h + 'px';
    });
    document.addEventListener('mouseup', function(e) {
        if (window.end_select || !window.mouseIsDown ) return;
        if (parseInt(selectionDiv.style.width) < 100 ||
            parseInt(selectionDiv.style.height) < 80 ) return;
        window.mouseIsDown = false
        window.end_select = true
        // Find elements within the selected region
        var current_center_x = e.clientX - (e.pageX - rect.startX) / 2;
        var current_center_y = e.clientY - (e.pageY - rect.startY) / 2;
        var elements = document.elementsFromPoint(current_center_x, current_center_y) ;
        console.log(elements);
        // elements.forEach(function(element) {
        var xpath = getXPathForElement(elements[1]);
        window.xpath = xpath;
        // });
        selectionDiv.innerHTML = `
          请复制下面xpath至客户端: </br>${window.xpath}
          <div><button onclick="copyTextToClipboard('${window.xpath}')">复制</button>&nbsp;&nbsp;&nbsp;&nbsp;
          <button onclick="resetSelect()">重选</button></div>
        `
    });
    function getXPathForElement(element) {
        var idx, path = '';
        for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode) {
            idx = Array.from(element.parentNode.childNodes).filter(node => node.nodeName == element.nodeName).indexOf(element) + 1;
            idx = (idx > 1) ? `[${idx}]` : '';
            path = '/' + element.nodeName.toLowerCase() + idx + path;
        }
        return path;
    }
})();"""

    def __init__(self):
        super().__init__()
        self.driver = None
        self.rule_window = None
        self.browser_thread = None
        self.setWindowTitle("猿变实验室爬虫客户端")
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
        # bug修复：将self.layout改为layout
        self.setLayout(layout)

    def create_left_menu(self):
        options = [("设置爬虫", self.set_crawler_rule),
                   ("开始爬取", self.start_spider),
                   ("JSON格式化", self.format_json),
                   ("header格式化", self.format_header),
                   ("cookie格式化", self.format_cookie),
                   ("加解密", self.encrypt_decrypt),
                   ]

        for menu in options:
            btn = QPushButton(menu[0])
            if menu[1]:
                btn.clicked.connect(menu[1])
            self.left_layout.addWidget(btn)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.left_layout.addItem(spacer)
        self.splitter.addWidget(self.left_widget)

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
        self.code_editor = QTextBrowser()
        self.code_editor.setPlaceholderText(
            "即将开始爬取"
        )
        self.right_layout.addWidget(self.code_editor)

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
        self.rule_window.setWindowFlags(self.rule_window.windowFlags() | Qt.WindowStaysOnTopHint)
        self.rule_window.show()

    def crawler_run(self, rule, target):
        if self.browser_thread:
            self.browser_thread.xpath_crawler(rule, target)

    def closeEvent(self, a0):
        print("窗口已经关闭", a0)
        if self.browser_thread:
            self.browser_thread.driver.close()

    def start_spider(self):
        print(self.right_widget)


    def show_main_interface(self):
        self.json_widget.hide()
        self.right_widget.show()

    def format_json(self):
        if not hasattr(self, 'json_widget'):
            # 创建上下分区的布局
            self.json_layout = QVBoxLayout()
            self.json_widget = QWidget()
            self.json_widget.setLayout(self.json_layout)
            
            # 上部：JSON输入框
            self.json_input = YuanbianTextEdit()
          
            self.json_input.setPlaceholderText("请输入JSON字符串")
            self.json_layout.addWidget(self.json_input)
            
            # 下部：格式化显示区域
            self.json_output = QTextBrowser()
            self.json_output.setPlaceholderText("格式化后的JSON将显示在这里")
            self.json_layout.addWidget(self.json_output)
            
            # 格式化按钮
            self.format_button = QPushButton("格式化JSON")
            self.format_button.clicked.connect(self._format_json)
            self.json_layout.addWidget(self.format_button)
            
            # 将JSON布局设置到右侧
            self.right_widget.hide()
            self.right_layout.addWidget(self.json_widget)

        # 添加返回按钮
            self.return_button = QPushButton('可视化爬虫')
            self.return_button.clicked.connect(self.show_main_interface)
            self.json_layout.addWidget(self.return_button)
        else:
            self.json_widget.show()
        

   

    def _format_json(self):
        try:
            json_str = self.json_input.toPlainText()
            json_str = json_str.strip()  # 去除前后空白
            json_data = json.loads(json_str)
            formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
            self.json_output.setText(formatted_json)
        except Exception as e:
            QMessageBox.warning(self, "JSON格式错误", f"无效的JSON格式: {str(e)}")

    def format_header(self):
        # TODO: 实现header格式化功能
        pass

    def format_cookie(self):
        # TODO: 实现cookie格式化功能
        pass

    def encrypt_decrypt(self):
        # TODO: 实现加解密功能
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BrowserApp()
    window.show()

    sys.exit(app.exec_())
