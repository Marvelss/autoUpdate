"""
@Author : SakuraFox
@Time: 2025-01-23 15:18
@File : run_write_version.py
@Description : file description
"""
# -*- coding: utf-8 -*-
import os


version = os.environ.get('version')
print("version:", version)
# 获取运行目录
# print("run dir:", os.getcwd())
# 获取文件目录
fileDir = os.path.dirname(__file__)
print("file dir:", os.path.dirname(__file__))
versionFilePath = os.path.join(fileDir, "version.py")
print(f"edit file {versionFilePath} output: version = {version}")
# 覆盖写出文件 version.py 中
# with open(versionFilePath, 'w') as f:
#     f.write(f'version = "{version}"')
exit()