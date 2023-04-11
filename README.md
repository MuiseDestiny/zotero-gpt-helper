# zotero-gpt-helper

> 本项目用于开启一个本地的 `127.0.0.1:5000` 服务，用于 `Zotero GPT` 插件向PDF提问。

此服务无需进行任何配置，api和apiKey从插件获取，只需要在zotero-gpt插件配置好即可  

## 一键运行
首先下载或克隆本仓库代码，然后  
* `Windows`用户可以直接双击运行 `start.bat` 文件  
* `Linux`或`Mac`用户可以直接运行 `start.sh` 文件

## 手动运行
```
git clone https://github.com/MuiseDestiny/zotero-gpt-helper.git
cd zotero-gpt-helper
pip install -r requirements.txt
python main.py
```
