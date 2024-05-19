from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import torch
from transformers import AutoModel, AutoTokenizer
from langchain_openai import ChatOpenAI
from openai import OpenAI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs import *
from database import *
from server.prompt_api import *
from server.embedding_api import *

# 初始化 FastAPI 应用
app = FastAPI()

# 加载 ChatGLM-6B 模型和 tokenizer
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, device='cuda')
model.eval()

# 定义请求和响应模型
class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int
    temperature: float
    top_p: float = 1.0
    history: list = []

class QueryResponse(BaseModel):
    response: str

class ChatCompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int
    temperature: float
    top_p: float = 1.0
    history: list = []

class ChatCompletionResponse(BaseModel):
    # id: str
    # object: str
    # created: int
    # model: str
    # choices: list
    # usage: dict
    response: str

class SearchRequest(BaseModel):
    query: str
    top_k: int

class SearchResponse(BaseModel):
    results: list

@app.post("/generate", response_model=QueryResponse)
async def generate_text(query: QueryRequest):
    try:
        """单次调用
        inputs = tokenizer(query.prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_tokens=query.max_tokens,
                temperature=query.temperature,
                do_sample=True
            )
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        """

        """流式调用
        response_text = ""
        history, past_key_values = query.history, None
        for response, history, past_key_values in model.stream_chat(
            tokenizer, 
            query.prompt, 
            history=[], 
            past_key_values=None, 
            max_tokens=query.max_tokens, 
            top_p=query.top_p, 
            temperature=query.temperature,
            return_past_key_values=True
        ):
            response_text += response
        print("response:", response)
        print("response_text:", response_text)
        """

        history = []
        response, history = model.chat(
            tokenizer, 
            query.prompt, 
            history=history, 
            max_length=query.max_tokens, 
            top_p=query.top_p, 
            temperature=query.temperature
        )
        # print("response:", response)
        return QueryResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/openai_generate", response_model=QueryResponse)
async def openai_generate_text(query: QueryRequest):
    try:
        # message = get_chat_prompt(history=query.history, query=query.prompt)
        message = chatprompt.format(query=query.prompt)
        openai = ChatOpenAI(temperature=query.temperature,
                         max_tokens=query.max_tokens,
                         model=MODEL)
        response = openai.invoke(message)
        # print("\nresponse:", response.content)
        final_response = response.content.replace("System: ", "")
        return QueryResponse(response=final_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    if request.model == "ChatGLM3":
        try:
            search_results = search_texts(request.prompt)
            context = "\n".join(search_results)
            message = datachatprompt.format(context=context, query=request.prompt)
            """
            history, past_key_values = request.history, None
            response_text = ""
            for response, history, past_key_values in model.stream_chat(
                tokenizer, 
                message, 
                history=history, 
                past_key_values=past_key_values, 
                max_tokens=request.max_tokens, 
                top_p=request.top_p, 
                temperature=request.temperature,
                return_past_key_values=True
            ):
                response_text += response
            print("response:", response)
            print("response_text:", response_text)
            """
            history = []
            response, history = model.chat(
                tokenizer, 
                message, 
                history, 
                max_length=request.max_tokens, 
                top_p=request.top_p, 
                temperature=request.temperature
            )
            # print("response:", response)
            return ChatCompletionResponse(response=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    elif request.model == "OpenAI":
        try:
            search_results = search_texts(request.prompt)
            context = "\n".join(search_results)
            message = datachatprompt.format(context=context, query=request.prompt)
            openai = ChatOpenAI(temperature=request.temperature,
                            max_tokens=request.max_tokens,
                            model=MODEL)
            response = openai.invoke(message)
            final_response = response.content.replace("System: ", "")
            return ChatCompletionResponse(response=final_response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Unsupported model")

@app.get("/crawl")
async def crawl_data():
    try:
        result = perform_data_crawl()
        if result:
            return {"status": "success", "message": "数据爬取成功！"}
        else:
            raise HTTPException(status_code=500, detail="数据爬取失败！")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed", response_model=dict)
async def embed_data():
    try:
        build_index()
        return {"status": "success", "message": "数据嵌入成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_data(query: SearchRequest):
    try:
        results = search_texts(query.query, query.top_k)
        return SearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
