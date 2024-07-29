"""
This file is used to define the chat prompt template for the langchain model.
not used in the current version of the code.
"""

from langchain_openai import ChatOpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs import *
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

chatprompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "你是一位AI助手。你的任务是根据用户的提问给出详细的回复"),
        HumanMessagePromptTemplate.from_template(
            "{query}"),
    ]
)

datachatprompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """你是一个问答机器人。你的任务是根据下述给定的已知信息回答用户问题。
            如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
            请不要输出已知信息中不包含的信息或答案。
            请用中文回答用户问题。
            """
        ),
        HumanMessagePromptTemplate.from_template(
            """
            已知信息:
            {context}
            用户问：                                                           
            {query}
            """
        )
    ]
)

def get_message(context,query):
    message = """
    你是一个问答机器人。你的任务是根据下述给定的已知信息回答用户问题。
    如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
    请不要输出已知信息中不包含的信息或答案。
    请用中文回答用户问题。

    已知信息:
    {context}

    用户问：
    {query}
    """
    return message

# llm = ChatOpenAI(model_name="gpt-4",
#                  max_tokens= 1000,
#                  temperature=0.7)
# message = chatprompt.format(query="你是谁")
# print(message)
# response = llm.invoke(message)
# print(response)
# print(response.content)