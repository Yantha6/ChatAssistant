from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

# 设置 ChatGLM-6B 模型和 tokenizer 路径
MODEL_PATH = "chatglm3-6b"
TOKENIZER_PATH = MODEL_PATH
EMBEDDING_MODEL_PATH = 'bge-large-zh'

# MODEL = "gpt-3.5-turbo"
MODEL = "gpt-4"