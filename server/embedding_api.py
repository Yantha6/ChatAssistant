import os
import json
import faiss
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

# 设置嵌入模型路径
EMBEDDING_MODEL_PATH = 'bge-large-zh'
HEROINFO_INDEX_PATH = './database/heroinfo_index.bin'
HEROSTORY_INDEX_PATH = './database/herostory_index.bin'
HEROINFO_TEXTS_PATH = './database/heroinfo_texts.json'
HEROSTORY_TEXTS_PATH = './database/herostory_texts.json'
HEROINFO_PATH = './database/heroinfo'
HEROSTORY_PATH = './database/herostory'

# 加载嵌入模型
embedding_model = SentenceTransformer(EMBEDDING_MODEL_PATH, device='cuda' if torch.cuda.is_available() else 'cpu')

# 长文分割
def split_text_into_chunks(text, max_length=128):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_length):
        chunks.append(" ".join(words[i:i+max_length]))
    return chunks

# 构建和保存索引
def build_index(data_path, index_path, texts_path):
    texts = []

    filenames = os.listdir(data_path)
    for filename in filenames:
        with open(os.path.join(data_path, filename), 'r', encoding='gbk') as file:
            text = file.read()
            chunks = split_text_into_chunks(text)  # 分割文本
            texts.extend(chunks)  # 添加所有分段

    embeddings = embedding_model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().detach().numpy()

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, index_path)

    with open(texts_path, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=4)

# 载入索引
def load_index(index_path, texts_path, data_path):
    if not os.path.exists(index_path):
        build_index(data_path, index_path, texts_path)

    index = faiss.read_index(index_path)
    with open(texts_path, 'r', encoding='utf-8') as f:
        texts = json.load(f)
    
    return index, texts

heroinfo_index, heroinfo_texts = load_index(HEROINFO_INDEX_PATH, HEROINFO_TEXTS_PATH, HEROINFO_PATH)
herostory_index, herostory_texts = load_index(HEROSTORY_INDEX_PATH, HEROSTORY_TEXTS_PATH, HEROSTORY_PATH)

# 嵌入数据的函数
def embed_texts(new_texts, index, texts, index_path, texts_path):
    new_chunks = []
    for text in new_texts:
        new_chunks.extend(split_text_into_chunks(text))
    
    embeddings = embedding_model.encode(new_chunks, convert_to_tensor=True)
    embeddings = embeddings.cpu().detach().numpy()

    index.add(embeddings)
    faiss.write_index(index, index_path)
    
    with open(texts_path, 'w', encoding='utf-8') as f:
        json.dump(texts + new_chunks, f, ensure_ascii=False, indent=4)

def search_texts(query, index, texts, top_k=2):
    query_embedding = embedding_model.encode([query], convert_to_tensor=True)
    query_embedding = query_embedding.cpu().detach().numpy()

    D, I = index.search(query_embedding, top_k)
    results = [texts[i] for i in I[0]]
     
    # 将 D 的元素转换为浮点数并打印
    # print("相关性分数（D）:", D[0].astype(float))
    return results

def search_heroinfo(query, top_k=2):
    return search_texts(query, heroinfo_index, heroinfo_texts, top_k)

def search_stories(query, top_k=2):
    return search_texts(query, herostory_index, herostory_texts, top_k)

# 测试功能
# if __name__ == "__main__":
#     #build_index(HEROINFO_PATH, HEROINFO_INDEX_PATH, HEROINFO_TEXTS_PATH)
#     #build_index(HEROSTORY_PATH, HEROSTORY_INDEX_PATH, HEROSTORY_TEXTS_PATH)
#     query = "孙悟空如何出装"
#     heroinfo_results = search_heroinfo(query)
#     for result in heroinfo_results:
#         print(result, "\n")
    
#     herostory_query = "孙悟空"
#     herostory_results = search_stories(herostory_query)
#     for result in herostory_results:
#         print(result, "\n")
