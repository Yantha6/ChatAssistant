import streamlit as st
import requests
import os
import time

# 设置页面布局
st.set_page_config(page_title="ChatAssistant", layout="wide")

# 初始化 session_state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 定义导航栏
st.sidebar.title("导航栏")
mode = st.sidebar.radio("选择对话模式", ["LLM 对话", "知识库问答"], index=1)
model = st.sidebar.radio("选择模型", ["ChatGLM3", "OpenAI"])
max_tokens = st.sidebar.slider("max_tokens", 0, 8192, 4096)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.4)
top_p = st.sidebar.slider("top_p", 0.0, 1.0, 0.7)

# 清除对话历史按钮逻辑
if st.sidebar.button("清除对话历史"):
    st.session_state.chat_history = []
    placeholder = st.empty()
    placeholder.success("清除成功！") 
    time.sleep(1)
    placeholder.empty()
    

# 展开新的对话窗口按钮逻辑
if st.sidebar.button("展开新的对话窗口"):
    st.session_state.chat_history = []
    placeholder = st.empty()
    placeholder.success("清除成功！") 
    time.sleep(1)
    placeholder.empty()
    

# 添加隔离线和项目介绍
st.sidebar.markdown("""
    <div style="text-align: center;">
        <h1>项目介绍</h1>
    </div>
    <div style="padding: 10px;">
        <p>ChatAssistant 是一个基于 LLM 的王者荣耀对战助手。通过此应用，您可以查看各个英雄的详细信息，并且可以选择不同的对话模式与模型进行互动。</p>
        <ul>
            <li><strong>对战策略助手：</strong>利用AI技术，根据玩家的对战记录和英雄特点，为玩家提供个性化的对战策略建议，帮助玩家提高游戏水平。</li>
            <li><strong>英雄搭配推荐：</strong>根据玩家的喜好和游戏风格，结合版本强势英雄，为玩家推荐适合的英雄搭配，做你的私有金牌BP教练。</li>
            <li><strong>游戏数据分析：</strong>利用大数据分析和机器学习技术，为玩家提供游戏数据分析服务，帮助玩家了解自己的游戏表现，找出不足之处，提高游戏水平。</li>
            <li><strong>游戏物品推荐：</strong>根据玩家的游戏进度和英雄特点，为玩家推荐合适的游戏铭文，游戏装备，提高游戏胜率。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 项目标题和信息
st.markdown("""
    <div style='text-align: center;'>
        <h1>ChatAssistant</h1>
        <h2 style="font-size: 20px;">
            <i class="fas fa-envelope"></i>💡一套在线爬取网络数据来训练LLM模型，并部署到网页进行交互的RAG流程🚀
            <a href="https://github.com/Yantha6/ChatAssistant" style="color: #007acc; text-decoration: none;" target="_blank">
                <i class="fab fa-github"></i>项目链接：https://github.com/Yantha6/ChatAssistant
            </a>
        </h2>
    </div>
    """, unsafe_allow_html=True)

# 定义一个函数用于渲染对话历史
def render_chat_history():
    chat_history_html = """
    <div style='height: 700px; overflow-y: auto; background-color: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 10px; padding: 15px;' id='chat-container'>
    """.replace("\n", "")
    for message in st.session_state.chat_history:
        if message.startswith("用户："):
            chat_history_html += f"""
                <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: flex-end;'>
                    <div style='background-color: #e8f0fe; padding: 10px; border-radius: 10px; max-width: 80%;'>
                        {message[3:]}  <!-- 移除 '用户：' 的文本 -->
                    </div>
                    <img src='https://via.placeholder.com/40x40/007acc/ffffff?text=U' alt='用户' style='border-radius: 50%; margin-left: 10px;'/>
                </div>
            """.replace("\n", "")
        else:
            chat_history_html += f"""
                <div style='margin-bottom: 10px; display: flex; align-items: center;'>
                    <img src='https://via.placeholder.com/40x40/005b99/ffffff?text=M' alt='模型' style='border-radius: 50%; margin-right: 10px;'/>
                    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 10px; max-width: 80%;'>
                        {message[3:]}  <!-- 移除 '模型：' 的文本 -->
                    </div>
                </div>
            """.replace("\n", "")
    chat_history_html += "</div>"
    return chat_history_html


# 英雄信息展示窗口
def display_hero_info():
    selected_hero = st.selectbox("选择爬取文件", os.listdir('./database/heroinfo'))
    with open(f'./database/heroinfo/{selected_hero}', 'r', encoding='gbk') as file:
        hero_info = file.read()
    st.text_area("文件信息", hero_info, height=600)
    st.write("——以上数据从最新官网爬取，与最新版本保持一致")

def llm_chat_page():
    # 屏幕布局
    # LLM 对话交互窗口
    with st.container():
        st.subheader("Chat 对话窗口")
        
        # 对话记录展示窗口
        chat_container = st.empty()

        # 初次加载时渲染对话记录
        chat_container.markdown(render_chat_history(), unsafe_allow_html=True)
        
        # 输入框和发送按钮容器
        user_input = st.text_area("输入你的问题")
        send_button = st.button("发送", key='send_button')
        
        # 处理发送按钮的点击事件
        if send_button:
            # 调用 API 进行文本生成
            api_url = "http://localhost:8000/generate" if model == "ChatGLM3" else "http://localhost:8000/openai_generate"
            payload = {
                "prompt": user_input,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "history": st.session_state.chat_history  # 将对话历史包含在请求中
            }
            
            try:
                response = requests.post(api_url, json=payload)
                response_data = response.json()
                response_text = response_data.get("response", "")
                st.session_state.chat_history.append(f"用户：{user_input}\n")
                st.session_state.chat_history.append(f"模型：{response_text}\n")
                
                # 更新对话记录
                chat_container.markdown(render_chat_history(), unsafe_allow_html=True)
            except Exception as e:
                st.write(f"请求失败: {e}")

def data_chat_page():
    # 屏幕布局
    col1, col2 = st.columns([3, 1])
    # LLM 对话交互窗口
    with col1:
        st.subheader("Chat 对话窗口")
        
        # 对话记录展示窗口
        chat_container = st.empty()

        # 初次加载时渲染对话记录
        chat_container.markdown(render_chat_history(), unsafe_allow_html=True)
        
        # 输入框和发送按钮容器
        user_input = st.text_area("输入你的问题")
        send_button = st.button("发送", key='send_button')
        
        # 处理发送按钮的点击事件
        if send_button:
            # 调用 API 进行文本生成
            api_url = "http://localhost:8000/v1/chat/completions"
            payload = {
                "model": model,
                "prompt": user_input,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "history": st.session_state.chat_history  # 将对话历史包含在请求中
            }
            
            try:
                response = requests.post(api_url, json=payload)
                response_data = response.json()
                response_text = response_data.get("response", "")
                st.session_state.chat_history.append(f"用户：{user_input}\n")
                st.session_state.chat_history.append(f"模型：{response_text}\n")
                
                # 更新对话记录
                chat_container.markdown(render_chat_history(), unsafe_allow_html=True)
            except Exception as e:
                st.write(f"请求失败: {e}")

    with col2:
        st.subheader("crawl 信息处理")
        
        # 重新爬取数据按钮
        if st.button("重新爬取数据"):
            # 调用爬取数据的函数或API
            st.write("数据爬取中...")
            try:
                # 假设有一个爬取数据的API
                response = requests.get("http://localhost:8000/crawl")
                if response.status_code == 200:
                    st.success("数据爬取成功！")
                else:
                    st.error("数据爬取失败！")
            except Exception as e:
                st.error(f"爬取数据失败: {e}")
        
        # 将数据灌入 embedding 模型按钮
        if st.button("重构向量数据库"):
            # 调用灌入数据的函数或API
            st.write("数据灌入中...")
            try:
                # 假设有一个灌入数据的API
                response = requests.post("http://localhost:8000/embed")
                if response.status_code == 200:
                    st.success("数据灌入成功！")
                else:
                    st.error("数据灌入失败！")
            except Exception as e:
                st.error(f"灌入数据失败：{e}")
        
        # 显示当前数据量
        display_hero_info()

# 根据选择的模式调用不同的函数
if mode == "LLM 对话":
    llm_chat_page()
else:
    data_chat_page()

# 自定义样式
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff; /* 白色背景 */
        }
        .sidebar .sidebar-content {
            background-color: #e8f0fe; /* 浅蓝色背景 */
            border: 1px solid #b0c4de; /* 浅蓝色边框 */
            text-align: center; /* 居中标题 */
        }
        
        .block-container {
            background-color: #ffffff; /* 白色背景 */
        }
        .css-1q8dd3e {
            color: #007acc; /* 深蓝色文本 */
        }
        .stTextInput, .stTextArea, .stSlider {
            background-color: #e8f0fe; /* 浅蓝色背景 */
            border: 1px solid #b0c4de; /* 浅蓝色边框 */
        }
        .stRadio, .stSelectbox {
            color: #007acc; /* 深蓝色文本 */
        }
        h1 {
            color: #007acc; /* 深蓝色标题 */
            text-align: center;
        }
        h2 {
            color: #005b99; /* 较深的蓝色副标题 */
        }
        a {
            color: #003366; /* 深蓝色链接 */
            text-decoration: none;
        }
        a:hover {
            color: #001f4d; /* 深蓝色链接悬停 */
            text-decoration: underline;
        }
        i.fas, i.fab {
            color: #007acc; /* 深蓝色图标 */
        }
        footer {
            position: fixed;
            left: 250px;
            bottom: 0;
            width: 100%;
            background-color: #ffffff; /* 白色背景 */
            color: #007acc; /* 深蓝色文本 */
            padding: 10px;
        }
        .stButton button {
            width: 100%;
            height: 50px;
            font-size: 16px;
            background-color: #007acc;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .stButton button:hover {
            background-color: #005b99;
        }
    </style>
    """, unsafe_allow_html=True)

# 添加页脚
st.markdown("""
    <footer>
        <p style='text-align: center;'>© yangtianhan01@gmail.com</p>
    </footer>
    """, unsafe_allow_html=True)
