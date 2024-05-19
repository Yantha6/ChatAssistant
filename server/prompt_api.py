from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage

chatprompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "你是一位聪明的AI助手，你的任务是根据用户的提问给出详细的回复"),
        HumanMessagePromptTemplate.from_template(
            "{query}"),
    ]
)

datachatprompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """你是一位经验丰富游戏数据分析师，你的任务是根据下述给定的已知信息回答用户问题，要求如下：
            1.如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
            2.请注意，提取已知信息中和问题最关键的部分给出答案，不要长篇大论。
            3.请用中文回答用户问题。
            4.如果用户问装备信息，只需要返回装备信息，不要返回英雄关系等其他信息
            5.如果用户问技能信息，只需要返回技能信息，不要返回装备关系等其他信息
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

def get_history(history):
    historys = []
    for entry in history:
        if entry.startswith("用户: "):
            content = entry[3:].strip()
            historys.append(HumanMessage(content=content))
        elif entry.starstwith("模型: "):
            content = entry[3:].strip()
            historys.append(AIMessage(content=content))
    print("historys:\n" + historys)
    return historys

humanmessageprompt = HumanMessagePromptTemplate.from_template("{query}")
chathistoryprompt = ChatPromptTemplate.from_messages(
    [MessagesPlaceholder(variable_name="historys_chat"),humanmessageprompt]
)

def get_chat_prompt(history, query):
    historys = get_history(history)
    messages = chathistoryprompt.format_prompt(
        historys_chat=historys,query=query
    )
    return messages