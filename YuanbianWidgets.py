from PyQt5.QtWidgets import QTextEdit


class YuanbianTextEdit(QTextEdit):
    """
    自定义文本编辑控件，继承自QTextEdit
    """
    def paste(self):
        """
        重写粘贴方法，在粘贴后执行自定义操作
        """
        super().paste()

    def insertFromMimeData(self, source):
        if source and source.hasText():
            self.insertPlainText(source.text())

