# 使用nest_asyncio确保异步稳定性
import nest_asyncio
nest_asyncio.apply()
from mermaid import Mermaid
import json
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs import *
from database import *
from server.prompt_api import *
from server.embedding_api import *

client = OpenAI()
def get_completion(
    prompt: str,
    system_message: str = "You are a helpful assistant.",
    model: str = MODEL,
    temperature: float = 0.3,
    json_mode: bool = False,
):
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        top_p=1,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

# 定义传递的信息结构
from typing import TypedDict, Optional
class State(TypedDict):
    hero_story: str
    story_idea: str
    hero_story_out1: Optional[str] = None
    reflection: Optional[str] = None
    hero_story_out2: Optional[str] = None
    satisfied: Optional[bool] = None

# 创建一个工作流对象
workflow = StateGraph(State)

# 定义获取故事想法的节点
def get_story_idea(state):
    # story_idea = input("请输入新的故事想法: ")
    story_idea = state.get("story_idea")
    return { "story_idea": story_idea }

# 定义故事创作的初始节点
def initial_story(state):
    hero_story = state.get("hero_story")
    story_idea = state.get("story_idea")

    system_message = f"你是一位优秀的故事创作家，专门从事为简单的故事编织更复杂情节的工作"
    prompt = f"""
    你是一位优秀的故事创作家，专门从事为简单的故事编织更复杂情节的工作。请根据以下故事情节和故事想法，创作一个更复杂的故事情节：
    故事想法：{story_idea}
    故事情节：{hero_story}
    """

    hero_story_out1 = get_completion(prompt, system_message=system_message)

    print("[初次创作结果]: \n", hero_story_out1)

    return { "hero_story_out1": hero_story_out1 }

# 定义反思节点
def reflect_on_story(state):
    hero_story = state.get("hero_story")
    story_idea = state.get("story_idea")
    hero_story_out1 = state.get("hero_story_out1")

    system_message = f"你是一位优秀的故事创作家，专门从事为简单的故事编织更复杂情节的工作。你将收到一份故事创作作品，你的目标是改进这一份故事创作。"

    prompt = f"""你的任务是仔细阅读一段创作的故事情节，并提出建设性的意见和建议，以改进这个故事情节。

故事想法：{story_idea}
初次创作的故事情节：{hero_story_out1}

请根据故事想法和初次创作的故事情节，提出改进建议。请关注以下几点：
(i) 故事情节的复杂性和连贯性，
(ii) 人物的深度和发展，
(iii) 叙事风格和语调，
(iv) 故事的整体吸引力。

请仅输出具体的、帮助改进故事的建议。"""

    reflection = get_completion(prompt, system_message=system_message)

    print("[反思和建议]: \n", reflection)

    return { "reflection": reflection }

# 定义改进故事的节点
def improve_story(state):
    hero_story = state.get("hero_story")
    story_idea = state.get("story_idea")
    hero_story_out1 = state.get("hero_story_out1")
    reflection = state.get("reflection")

    system_message = f"你是一位优秀的故事创作家，专门从事为简单的故事编织更复杂情节的工作。"

    prompt = f"""你的任务是仔细阅读一段创作的故事情节及其改进建议，然后对故事进行编辑和改进。

故事想法：{story_idea}
初次创作的故事情节：{hero_story_out1}
改进建议：{reflection}

请根据改进建议和故事想法，对初次创作的故事情节进行编辑和改进。请确保：

(i) 提高故事的复杂性和连贯性，
(ii) 丰富人物的深度和发展，
(iii) 优化叙事风格和语调，
(iv) 提高故事的整体吸引力。

请输出改进后的故事情节。"""

    hero_story_out2 = get_completion(prompt, system_message)

    print("[改进后的故事情节]: \n", hero_story_out2)

    return { "hero_story_out2": hero_story_out2 }

# 定义检查满意度的节点
def check_satisfaction(state):
    hero_story_out2 = state.get("hero_story_out2")

    system_message = "你是一位严谨的编辑，负责审查故事情节的质量。"
    prompt = f"""请仔细阅读以下改进后的故事情节，并回答你是否满意这次创作。如果满意，请回答'yes'，如果不满意，请回答'no'。

改进后的故事情节：{hero_story_out2}

你是否满意这次创作？"""

    satisfaction = get_completion(prompt, system_message=system_message).strip().lower()
    satisfied = satisfaction == "yes"

    print("[满意度检查]: \n", satisfied)

    return { "satisfied": satisfied }

# 规划执行任务
## 节点（node）注册
workflow.add_node("get_story_idea", get_story_idea)
workflow.add_node("initial_story", initial_story)
workflow.add_node("reflect_on_story", reflect_on_story)
workflow.add_node("improve_story", improve_story)
workflow.add_node("check_satisfaction", check_satisfaction)
## 连接节点
workflow.set_entry_point("get_story_idea")
workflow.add_edge("get_story_idea", "initial_story")
workflow.add_edge("initial_story", "reflect_on_story")
workflow.add_edge("reflect_on_story", "improve_story")
workflow.add_edge("improve_story", "check_satisfaction")
workflow.add_conditional_edges(
    source="check_satisfaction",
    path=lambda state: "get_story_idea" if not state["satisfied"] else END,
    path_map={False: "get_story_idea", True: END}
)

# 开始执行
def run_storyflow(hero_story, story_idea):
    app = workflow.compile()
    mermaid_code = app.get_graph().draw_mermaid()
    # print(f"meramid code: \n{mermaid_code}")
    Mermaid(mermaid_code)
    result = app.invoke({
        "hero_story": hero_story,
        "story_idea": story_idea
    })
    print(result)
    return result

# 测试功能
# run_storyflow(
#     hero_story="""
#     刘邦的故事
#     英雄故事
#     云梦泽，东方最神秘的地域之一。大河缓行穿过，沿途残留着森林，沼泽和遗迹。这里依旧传承着对太古当权者的信仰，而诠释这些信仰的权力，掌握在阴阳家们的手中。他们凭借这种权力，以及所握有的“奇迹”，统治着这片土地。
#     星移斗转，再虔诚的地方，最终也将产生腐朽和堕落。阴阳家们逐渐老朽，已不再适应时代，原本严谨的秩序开始逐渐瓦解，很快，有投机取巧的家伙瞅准机会，试图从中渔利。
#     刘邦，就是其中一位。虔诚的大河子民中，他那样另类：既无视信仰，又热衷利益，更不择手段。凭借煞费苦心的钻营，谋取小小的官职，但很快发现付出和收获不成正比——大人们利用他，也防范他。他可不愿白白装作傻子，一个胆大妄为的想法产生了，关于那由阴阳家们掌握的，唯一非实体，需要借助仪式来展现的太古奥秘。如果自己得到“奇迹”，是否可以代替阴阳家们成为这片土地的王者？这个想法令他激动不已。
#     他敢于如此妄想，多亏了天才的友人张良。掌握言灵之力的张良因不通俗事频频惹出大麻烦，甚至不得不为下一餐饭发愁。刘邦替他解围，并得到了他的信任，不费吹灰之力便说服他带领自己走入通往阴阳家们祭祀“奇迹”的大泽。张良自己，也对所谓“奇迹”产生了好奇。
#     借助言灵之力，他们成功迷惑守卫，目睹了神秘的仪式。“奇迹”璀璨的光芒笼罩着九位呢喃着咒语的阴阳家，以及窥视的两人。张良以言灵与“奇迹”对话。他都听说了些什么？师父姜子牙的话得到印证，还有更多……更多……关于大魔神王的命运……
#     至于刘邦，却为惊人的发现而兴奋着……当仪式中的阴阳家们揭开神秘的面具……啊，原来统治云梦泽的，竟然是这样一群……一群怪物！阴阳家们的真面目！那瞬间，他的脑海中涌现出更加激动人心的计划。
#     他偷偷拔出护身剑。仪式完成，阴阳家们一个接一个结束膜拜。待最后一名阴阳家落单的瞬间，发动了无耻的偷袭。那高高在上的统治者，哀嚎着露出真容——蛇的面孔。张良也加入了战局，言灵的枷锁缠绕着他，让他无法动弹。只听见哀嚎回荡，阴阳家“礼魂”就这样不明不白化为灰烬，那无处安放的力量，尽数进入刘邦的身躯。
#     张良心情复杂望着眼前欣喜若狂的男人。出手的那刻，便是决定追随于他。命运又开始了轮回，而身为姜子牙的弟子，他必须作出选择。
#     需要一个家伙去斩断这可怕的宿命。
#     哪怕，他是如此野心勃勃。
#     “不客观的说，我是个好人！”
#     """,
#     story_idea="续写这个故事"
# )