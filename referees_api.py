import os
import json
from volcenginesdkarkruntime import Ark
from pydantic import BaseModel  # 用于定义响应解析模型




def getfile(file):
    with open(file, 'r', encoding='utf-8') as f:
        results = f.read()
    return results


#Doubao 裁判

def referees(logfile = 'poker_log.txt'):
    print('荷官正在整理牌桌')

    # 定义分步解析模型（对应业务场景的结构化响应）
    class ID(BaseModel):
        name: str  # 玩家名称
        hind_chips: str    # 玩家剩余筹码
        hind_cards: str    # 玩家手牌


    class MathResponse(BaseModel):
        id1: list[ID]       # 玩家信息列表
        id2: list[ID]
        id3: list[ID]
        public_messages: str   # 公共信息
        next_player_id: str   # 当前玩家名称
        remark_and_available_operations: str   #可用操作

    client = Ark(
        # 从环境变量中读取您的方舟API Key
        api_key=os.environ.get("DOUBAO_API_KEY"),
        # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
        timeout=1800,
        )
    completion = client.beta.chat.completions.parse(
        # 替换 <Model> 为您的Model ID
        model="doubao-seed-1.6-250615",
        messages=[
            {"role": "system", "content": "你是一名德州扑克游戏的裁判，你需要分析附件的游戏日志，将日志提取为公开信息和每名玩家隐藏信息，公开信息为公共牌，底池与边池，每名玩家每轮状态，玩家筹码明细，不能包含玩家手牌。玩家隐藏信息为玩家手牌及剩余筹码，并将当前玩家及可选操作列出，输出为json"},
            {"role": "user", "content": getfile(logfile)}
        ],
        response_format=MathResponse,  # 指定响应解析模型
        extra_body={
            "thinking": {
                "type": "disabled"  # 不使用深度思考能力
                # "type": "enabled" # 使用深度思考能力
            }
        }
    )
    resp = completion.choices[0].message.parsed

    with open('log.json', 'w', encoding='utf-8') as f:
        f.write(resp.model_dump_json(indent=2))
