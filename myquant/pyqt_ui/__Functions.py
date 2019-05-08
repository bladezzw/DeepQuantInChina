"""读取函数"""
import os
import json
import traceback

def FilePath(filename):
    """
    文件路径
    :return:
    """
    filePath = os.path.join(os.getcwd(), filename)
    if os.path.isfile(filePath):#如果当前路径下有filePath,就运行
        return filePath
    # else:
    #     moduleFolder = os.path.abspath(os.path.dirname(moduleFile))
    #     moduleJsonPath = os.path.join(moduleFolder, '.', name)
    #     jsonPathDict[name] = moduleJsonPath
    #     return moduleJsonPath

def Json_loading(filename):
    """
    读取json文件
    :return:
    """
    ctplogin = {}

    try:
        with open(filename, 'r') as f:
            ctplogin = f.read()
            if type(ctplogin) is not str:
                setting = str(ctplogin, encoding='utf8')
            setting = json.loads(ctplogin)
    except:
        traceback.print_exc()

    return setting









if __name__ == "__main__":
    filename = 'CTPLogin.json'
    filePath = os.path.join(os.getcwd(), filename)