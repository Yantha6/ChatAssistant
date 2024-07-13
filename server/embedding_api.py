import os
import json
import faiss
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

# 设置嵌入模型路径
EMBEDDING_MODEL_PATH = 'bge-large-zh'
INDEX_PATH = './database/faiss_index.bin'
DATA_PATH = './database/heroinfo'
TEXTS_PATH = './database/texts.json'

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
def build_index():
    texts = []
    filenames = os.listdir(DATA_PATH)
    for filename in filenames:
        with open(os.path.join(DATA_PATH, filename), 'r', encoding='gbk') as file:
            text = file.read()
            chunks = split_text_into_chunks(text)  # 分割文本
            texts.extend(chunks)  # 添加所有分段
    embeddings = embedding_model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().detach().numpy()

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    with open(TEXTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=4)

# 载入索引
def load_index():
    if not os.path.exists(INDEX_PATH):
        build_index()

    index = faiss.read_index(INDEX_PATH)
    with open(TEXTS_PATH, 'r', encoding='utf-8') as f:
        texts = json.load(f)
    
    return index, texts

index, texts = load_index()

# 嵌入数据的函数
def embed_texts(new_texts):
    new_chunks = []
    for text in new_texts:
        new_chunks.extend(split_text_into_chunks(text))
    
    embeddings = embedding_model.encode(new_chunks, convert_to_tensor=True)
    embeddings = embeddings.cpu().detach().numpy()

    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    
    with open(TEXTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(texts + new_chunks, f, ensure_ascii=False, indent=4)

def search_texts(query, top_k=2):
    query_embedding = embedding_model.encode([query], convert_to_tensor=True)
    query_embedding = query_embedding.cpu().detach().numpy()

    D, I = index.search(query_embedding, top_k)
    results = [texts[i] for i in I[0]]
     
    # 将 D 的元素转换为浮点数并打印
    print("相关性分数（D）:", D[0].astype(float))
    return results

# 测试功能
# if __name__ == "__main__":
#     build_index()
#     query = "孙尚香如何出装"
#     results = search_texts(query)
#     for reult in results:
#         print(reult, "\n")
