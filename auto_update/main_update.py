"""
@Author : SakuraFox
@Time: 2025-01-22 21:38
@File : main_update.py
@Description : 基于Git Actions的客户端更新
"""
import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QVBoxLayout, QApplication, QMainWindow, QPushButton

import subInterFace
import version

currentVersion = version.version


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.init_ui()

    def detectUpdateBtnClick(self):
        # 弹出窗口
        self.winUpdate = subInterFace.updateUI()
        self.winUpdate.show()

    def init_ui(self):
        self.resize(400, 300)
        self.setWindowTitle(f"自动更新的程序演示")
        self.show()
        # 创建容器
        self.main_widget = QWidget()

        self.detectUpdateBtn = QPushButton(self.main_widget)
        self.detectUpdateBtn.clicked.connect(self.detectUpdateBtnClick)
        self.detectUpdateBtn.resize(160, 100)
        self.detectUpdateBtn.setText(f'检查更新')
        self.detectUpdateBtn.show()

        self.label = QLabel(self.main_widget)
        self.label.setText(f'当前版本:{currentVersion}')
        self.label.resize(160, 100)
        self.label.show()

        self.label2 = QLabel(self.main_widget)
        self.label2.setText(f'最新版本:查询中')
        self.label2.resize(160, 100)
        self.label2.show()

        # 编辑框
        self.textEdit = QTextEdit(self.main_widget)
        self.textEdit.resize(400, 150)
        self.textEdit.show()

        # 创建布局容器并应用
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.addWidget(self.detectUpdateBtn)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.textEdit, 1)
        self.setCentralWidget(self.main_widget)


def fileRunPath():
    """ PyInstaller 单文件的运行目录  """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        return sys.path[0]


def updateInit():
    # 构建时测试运行是否正常的
    inputParam = sys.argv
    if len(inputParam) == 2:
        inputParam1 = inputParam[1]
        if inputParam1 == "test":
            print("app run success")
            # 写出文件
            with open(fileRunPath() + "/test.txt", "w") as f:
                f.write("app run success")
            sys.exit(0)


if __name__ == '__main__':
    updateInit()
    # app = QApplication(sys.argv)
    # win = Main()
    # sys.exit(app.exec())
