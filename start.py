import os
import multiprocessing
import uvicorn
import subprocess

def start_combined_api():
    # 获取当前文件的目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 设置工作目录为当前文件的目录
    os.chdir(current_dir)
    # 启动uvicorn，指定完整的模块路径
    uvicorn.run("server.llm_api:app", host="0.0.0.0", port=8000)

def start_web_page():
    # 获取当前文件的目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 设置工作目录为当前文件的目录
    os.chdir(current_dir)
    # 启动Streamlit
    subprocess.run(["streamlit", "run", "webui/web_page.py"])

def main():
    # 启动 combined_api 和 web_page
    p1 = multiprocessing.Process(target=start_combined_api)
    p2 = multiprocessing.Process(target=start_web_page)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()
