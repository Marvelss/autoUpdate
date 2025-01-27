"""
@Author : SakuraFox
@Time: 2025-01-23 21:12
@File : subInterFace.py
@Description : file description
"""
import time
from PyQt5.QtCore import QThread, pyqtSignal

import webbrowser

from PyQt5.QtWidgets import QDialog
from urllib3.exceptions import NewConnectionError

import ui_winUpdate
import requests
import version
import re

import os
import platform
import shutil
import sys

projectName = "Marvelss/autoUpdate"
applicationName = "main_update"
currentVersion = version.version
projectURL = "https://github.com/Marvelss/autoUpdate"


class updateUI(QDialog):
    icClosed = False

    def __init__(self):
        super(updateUI, self).__init__()
        self.ui = ui_winUpdate.Ui_Form()
        self.ui.setupUi(self)
        self.initFunc()
        self.setWindowTitle('软件更新')
        self.resize(620, 380)

        # 绑定按钮事件
        self.ui.pushButton_azgx.clicked.connect(self.install)
        self.ui.pushButton_tgbb.clicked.connect(self.close)

        # 隐藏更新进度条和状态编辑框
        self.ui.progressBar.hide()
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 100)
        self.ui.label_zt.hide()
        self.ui.pushButton_azgx.setEnabled(False)
        self.ui.pushButton_tgbb.setEnabled(False)
        # textEdit 禁止编辑
        self.ui.textEdit.setReadOnly(True)
        self.ui.textEdit.setText("正在检查更新...")

        self.applicationName = applicationName
        self.currentVersion = currentVersion
        self.projectURL = projectURL
        self.downloadDir = os.path.expanduser('~/Downloads')
        if isWindows():
            self.rarPath = os.path.abspath(self.downloadDir + f"/{self.applicationName}.exe")
        print('开始检查')
        self.detectUpdateThread = detectUpdateThread(projectName, self.detectUpdateRecallData)
        self.detectUpdateThread.start()

    def initFunc(self):
        # 如果在window系统中存在旧的文件则自动删除
        backFile = windowsPath() + ".old.bak"
        if os.path.exists(backFile):
            # 删除文件
            os.remove(backFile)

    def closeEvent(self, event):
        # self.detectUpdateThread.quit()
        self.hide()
        if self.icClosed is False:
            event.ignore()

    def detectUpdateRecallData(self, updateContent):
        print("数据", updateContent)
        if updateContent is None:
            return
        newVersion = updateContent['versionNum']
        self.ui.textEdit.setHtml(updateContent['updateContent'])
        self.downloadExe = updateContent['downloadExe']

        if newVersion == self.currentVersion or newVersion == "":
            self.ui.pushButton_azgx.hide()
            self.ui.pushButton_tgbb.hide()
            return

        self.ui.pushButton_azgx.setEnabled(True)
        self.ui.pushButton_tgbb.setEnabled(True)

    def install(self):
        print('install')
        self.ui.progressBar.show()
        self.ui.label_zt.show()
        self.ui.label_zt.setText('更新中...')
        self.ui.pushButton_azgx.setEnabled(False)
        self.ui.pushButton_tgbb.setEnabled(False)
        print('downloadExe', self.downloadExe)

        if isWindows():
            if self.downloadExe == "":
                self.ui.label_zt.setText("没有找到 windows 系统软件下载地址")
                return
            print('install win', self.downloadExe, self.rarPath)
            try:
                self.fileDownloadThread = downloadFileThread(
                    downloadURL=self.downloadExe,
                    savedFilePath=self.rarPath,
                    uiForm=self,
                    editLabel=self.ui.label_zt,
                    progressBar=self.ui.progressBar,
                    applicationName=self.applicationName,
                    recallData=self.downloadFinish
                )
                self.fileDownloadThread.start()
            except BaseException as e:
                print(e)

    def downloadFinish(self, downloadResult, savedFilePath):
        if not downloadResult:
            self.ui.label_zt.setText("下载更新失败")
            return

        if isWindows():
            print('覆盖原有软件')
            coverSoftware(savedFilePath)

    def openProjectURL(self):
        # 浏览器打开网址
        print('projectURL', self.projectURL)
        webbrowser.open(self.projectURL)


def isWindows():
    return platform.system().lower() == 'windows'


def onDownloadFile(url, savedFilePath, recallData=None):
    # recallData例子
    #     def 进度(progressRate, 已下载大小, 文件大小, 下载速率, 剩余时间):
    #         信息 = f"进度 {progressRate}% 已下载 {已下载大小}MB 文件大小 {文件大小}MB 下载速率 {下载速率}MB 剩余时间 {剩余时间}秒"
    #         print(f"\r {信息}", end="")
    if recallData:
        start_time = time.time()
    r = requests.get(url, stream=True)
    with open(savedFilePath, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        # 获取百分比 并调用recallData
        for chunk in r.iter_content(chunk_size=10 * 1024):
            if chunk:
                f.write(chunk)
                f.flush()
                if recallData:
                    # 转化为百分比
                    progressRate = int(f.tell() * 100 / total_length)
                    downloadedSize = f.tell() / 1024 / 1024
                    fileSize = total_length / 1024 / 1024
                    downloadSpeed = downloadedSize / (time.time() - start_time)
                    # 获取剩余时间取秒
                    timeRemain = (fileSize - downloadedSize) / downloadSpeed
                    timeRemain = int(timeRemain)
                    # 所有数据保留两位小数
                    downloadSpeed = round(downloadSpeed, 2)
                    fileSize = round(fileSize, 2)
                    downloadedSize = round(downloadedSize, 2)
                    progressRate = round(progressRate, 2)
                    recallData(progressRate, downloadedSize, fileSize, downloadSpeed, timeRemain)
    return True


def windowsPath():
    """
    尝试获取当前可执行文件的路径。
    如果是在PyInstaller打包的环境中，则返回打包后的路径；
    否则，返回命令行参数中的第一个参数（通常是脚本的路径）。
    """
    if hasattr(sys, '_MEIPASS'):
        print(sys.executable[0])
        # PyInstaller打包后的环境
        return sys.executable[0]
    else:
        print(sys.argv[0])
        # 非打包环境，直接返回脚本路径
        return sys.argv[0]


def coverSoftware(exeFilePath):
    try:
        currentWindowsPath = windowsPath()  # 确保这个函数能正确返回路径

        oldFileName = currentWindowsPath + ".old.bak"

        if os.path.exists(oldFileName):
            os.remove(oldFileName)
        os.rename(currentWindowsPath, oldFileName)
        shutil.move(exeFilePath, currentWindowsPath)
        print(f'当前软件路径:{currentWindowsPath}')
        time.sleep(5)
        os.execv(currentWindowsPath, sys.argv)
        # 如果需要，可以在这里添加日志记录或错误处理
    except Exception as e:
        print(f"更新过程中发生错误：{e}")
        return False, str(e)

    return True, "更新成功。"


class downloadFileThread(QThread):
    progressBarSign = pyqtSignal(int, str)  # 进度 提示文本

    def __init__(self, *args, **kwargs):
        super(downloadFileThread, self).__init__()
        print('--downloadFileThread界面--初始化')
        self.uiForm = kwargs.get('uiForm')
        self.downloadURL = kwargs.get('downloadURL')
        self.savedFilePath = kwargs.get('savedFilePath')
        self.editLabel = kwargs.get('editLabel')
        self.progressBar = kwargs.get('progressBar')
        self.applicationName = kwargs.get('applicationName')
        self.recallData = kwargs.get('recallData')
        print(self.uiForm)
        print(self.downloadURL)
        print(self.savedFilePath)
        print(self.editLabel)
        print(self.progressBar)
        print(self.applicationName)
        print(self.recallData)

        self.progressBarSign.connect(self.refreshInterface)

        # 绑定线程开始事件
        self.started.connect(self.ui_start)
        # 绑定线程结束事件
        self.finished.connect(self.ui_end)

    def run(self):
        if self.downloadURL is None:
            print("请传入下载地址")
            return

        def progressInfo(progressRate, downloadedSize, fileSize, downloadSpeed, timeRemain):
            infoT = f"文件大小 {fileSize}MB 速度 {downloadSpeed}MB/s 剩余时间 {timeRemain}秒"
            self.progressBarSign.emit(progressRate, infoT)

        try:
            self.downloadResult = onDownloadFile(self.downloadURL, self.savedFilePath, progressInfo)
        except:
            self.downloadResult = False

    def ui_start(self):
        self.editLabel.setText(f'开始下载')

    def ui_end(self):
        print("下载结果", self.downloadResult)
        print("保存地址", self.savedFilePath)
        self.recallData(self.downloadResult, self.savedFilePath)
        self.editLabel.setText(f"下载完成 {self.savedFilePath}")

    def refreshInterface(self, progressT1, infoT1):
        if self.editLabel:
            self.editLabel.setText(str(infoT1))
        if self.progressBar:
            self.progressBar.setValue(int(progressT1))


class detectUpdateThread(QThread):
    def __init__(self,
                 projectName="Marvelss/autoUpdate",
                 recallData=None):
        super(detectUpdateThread, self).__init__()
        # 绑定线程开始事件
        self.started.connect(self.ui_start)
        # 绑定线程结束事件
        self.finished.connect(self.ui_end)
        self.projectName = projectName
        self.recallData = recallData

    def run(self):
        print('run')
        dataT = getVersionAndURL(self.projectName)
        self.updateData = dataT

    def ui_start(self):
        print("开始检查更新")

    def ui_end(self):
        # data = json.dumps(self.updateData, indent=4, ensure_ascii=False)
        print(f"检查更新结果:{self.updateData}")
        self.recallData(self.updateData)


# def 获取newVersion号和下载地址_需要token(project_name):
#     # 读取github项目中的最新的版本号
#     # pip install PyGithub
#     # 这个代码..尴尬了..在客户端无法跑 应部署在服务器上
#     g = Github("...token...")
#     repo = g.get_repo(project_name)
#     latest_release = repo.get_latest_release()
#     版本号 = latest_release.tag_name
#     body = latest_release.body
#     created_at = latest_release.created_at
#
#     mac下载地址 = ""
#     downloadExe = ""
#     下载地址列表 = []
#     for item in latest_release.get_assets():
#         下载地址 = item.browser_download_url
#         文件名 = item.name
#         下载地址列表.append([
#             文件名, 下载地址
#         ])
#         if 文件名.find('MacOS.zip') != -1:
#             mac下载地址 = 下载地址
#         if 文件名.find('.exe') != -1:
#             downloadExe = 下载地址
#     return {
#         "版本号": 版本号,
#         "下载地址列表": 下载地址列表,
#         "mac下载地址": mac下载地址,
#         "downloadExe": downloadExe,
#         "更新内容": body,
#         "发布时间": str(created_at)
#     }


def getVersionAndURL(project_name):
    # 通过访问最新的页面 获取版本号和下载地址和更新内容
    # https://github.com/duolabmeng6/qtAutoUpdateApp/releases/latest
    # 镜像地址也可以自己造一个 https://quiet-boat-a038.duolabmeng.workers.dev/
    # https://github.com/duolabmeng6/qoq/releases/expanded_assets/v0.1.5
    url = f"https://github.com/{project_name}/releases/latest"

    # url= 'https://github.com/Marvelss/autoUpdate/releases/tag/v0.1.0'
    print(url)
    try:
        jsondata = requests.get(url)
    except NewConnectionError as e:
        # 捕捉并处理NewConnectionError异常
        print(f"链接网址超时,请重试{e}")
        return
    except requests.exceptions.RequestException as e:
        # 捕捉requests库抛出的其他所有异常（可选）
        print(f'无法正常链接Github,错误:{e}')
        return

    # 获取状态码
    status_code = jsondata.status_code
    print(f"Status Code: {status_code}")

    # 获取响应内容（文本形式）
    response_text = jsondata.text
    print(f"Response Text: {response_text[:100]}...")  # 仅打印前100个字符以避免过长输出

    # 如果预期返回的是JSON格式数据，可以使用json()方法
    try:
        response_json = jsondata.json()
        print(f"Response JSON: {response_json}")
    except ValueError:
        print("Response is not in JSON format.")

    # 写出文件
    # with open('test.html', "w", encoding="utf-8") as f:
    #     f.write(jsondata.text)
    # 获取版本号
    return parseURL(jsondata.text, project_name)


def parseURL(urlT, project_name):
    versionT = urlT.find('<span class="ml-1">')
    versionT = urlT[versionT + len('<span class="ml-1">'):]
    versionT = versionT[:versionT.find('</span>')].strip()
    print(f'版本号{versionT}')
    # 获取更新内容
    # <div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3"><h1>自动更新程序</h1>
    # <ul>
    # <li>更新了自动构建</li>
    # <li>自动获取版本</li>
    # <li>自动下载</li>
    # <li>自动替换</li>
    # </ul></div>
    # </div>

    updateContent = urlT.find(
        '<div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3">')
    updateContent = urlT[updateContent + len(
        '<div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3">'):]
    updateContent = updateContent[:updateContent.find('</div>')]
    print(f'更新内容{updateContent}')
    # 获取下载地址列表
    #             <a href="/duolabmeng6/qtAutoUpdateApp/releases/download/0.0.4/my_app_MacOS.zip" rel="nofollow" data-skip-pjax>
    #               <span class="px-1 text-bold">my_app_MacOS.zip</span>
    #
    #             </a>

    downloadExe = ""
    # 重新访问页面
    # https://github.com/duolabmeng6/qoq/releases/expanded_assets/v0.1.5
    url = f"https://github.com/{project_name}/releases/expanded_assets/{versionT}"
    urlAssets = requests.get(url).text

    pattern = re.compile(r'class="Truncate-text text-bold">(.*?)</span>')
    result = pattern.findall(urlAssets)
    # print(result)
    for item in result:
        # print(item)
        downloadURLT = item
        downloadURLT = f"https://github.com/{project_name}/releases/download/{versionT}/{downloadURLT}"
        exeFile = item
        if exeFile.find('Source code') != -1:
            continue
        if exeFile.find('.exe') != -1:
            downloadExe = downloadURLT
            print(downloadExe)
    # print(下载地址列表)

    # 获取发布时间
    # <relative-time datetime="2022-07-22T17:32:41Z" class="no-wrap"></relative-time>
    releaseTime = urlAssets.find('<relative-time datetime="')
    releaseTime = urlAssets[releaseTime + len('<relative-time datetime="'):]
    releaseTime = releaseTime[:releaseTime.find('"')]
    # 去掉 t z
    releaseTime = releaseTime.replace("T", " ").replace("Z", "")
    print(f'发布时间{releaseTime}')
    # 版本号大于20个字符就清空
    if len(versionT) > 20:
        versionT = ""
        releaseTime = ""
        updateContent = ""
    print('-'*20)
    print(f'versionNum:{versionT}')
    print(f'downloadURL:{downloadURLT}')
    print(f'updateContent:{updateContent}')
    print(f'releaseTime:{releaseTime}')
    print(f'downloadExe:{downloadExe}')
    return {
        "versionNum": versionT,
        "downloadURL": downloadURLT,
        "updateContent": updateContent,
        "releaseTime": releaseTime,
        "downloadExe": downloadExe,
    }


# # 测试
# if __name__ == '__main__':
#     data = getVersionAndURL("Marvelss/autoUpdate")
#     print(data)

if __name__ == "__main__":
    # 下载一个大一点的文件
    # urlT = "https://github.com/MCSLTeam/MCSL2/releases/download/v2.2.6.3/MCSL2-2.2.6.3-Linux-x64.zip"  # 你的文件URL
    urlT = "https://epicgames-download1.akamaized.net/Builds/UnrealEngineLauncher/Installers/Win32/EpicInstaller-17.2.0.msi?launcherfilename=EpicInstaller-17.2.0-4ace3595a0144165b3ef0bfe2942a2c2.msi"


    def progressInfo(progressRate, downloadedSize, fileSize, downloadSpeed, timeRemain):
        infoT = f"进度 {progressRate}% 已下载 {downloadedSize}MB 文件大小 {fileSize}MB 下载速率 {downloadSpeed}MB 剩余时间 {timeRemain}秒"
        # 控制台当行输出
        print(f"\r {infoT}", end="")

    # onDownloadFile(urlT,
    #          "QtEsayDesigner_MacOS.zip", progressInfo)
