# -*- coding=utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
    QPushButton, QSpacerItem, \
    QSizePolicy, QLineEdit,\
    QComboBox, QLabel, QWidget


class SpiderConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("爬取规则设计器")
        self.setGeometry(100, 100, 500, 300)

        # 创建一个垂直布局
        self.layout = QVBoxLayout()
        self.add_rule_button = QPushButton("添加爬取规则")
        self.add_rule_button.clicked.connect(self.add_crawler_rule)
        self.add_finish_button = QPushButton("完成爬取规则设置")
        self.add_finish_button.clicked.connect(lambda: self.hide())
        # Add button to layout
        self.layout.addWidget(self.add_rule_button)
        self.layout.addWidget(self.add_finish_button)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        # 应用垂直布局
        self.setLayout(self.layout)

    def add_crawler_rule(self):
        # Create input field and '测试爬取' button
        input_field = QLineEdit()
        target_type = QComboBox()
        target_type.addItems(["text", "href", "src"])
        test_crawl_button = QPushButton("测试爬取")

        # Create a container for input and button
        container_layout = QHBoxLayout()
        container_layout.addWidget(QLabel("输入规则: "))
        container_layout.addWidget(input_field)
        container_layout.addWidget(target_type)
        container_layout.addWidget(test_crawl_button)
        container_widget = QWidget()
        container_widget.setLayout(container_layout)
        self.layout.insertWidget(self.layout.count() - 2, container_widget)
        test_crawl_button.clicked.connect(lambda: self.test_crawl(input_field.text(),
                                                                  target_type.currentText()
                                                                  ))

    def test_crawl(self, text, target):
        # Call the parent's crawler_run method with the input text
        self.parent().crawler_run(text, target)

