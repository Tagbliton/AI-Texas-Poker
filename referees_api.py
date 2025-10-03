import os
from google import genai
from pydantic import BaseModel  # 用于定义响应解析模型




def getfile(file):
    with open(file, 'r', encoding='utf-8') as f:
        results = f.read()
    return results


#Gemini 裁判

def referees(logfile = 'poker_log.txt', croupier = '乌丑'):

    print(f'{croupier}正在整理牌桌')

    # 定义分步解析模型（对应业务场景的结构化响应）
    class ID(BaseModel):
        name: str  # 玩家名称
        hind_chips: str    # 玩家剩余筹码
        hind_cards: str    # 玩家手牌


    class MathResponse(BaseModel):
        id1: list[ID]       # 玩家1信息列表
        id2: list[ID]       # 玩家2信息列表
        id3: list[ID]       # 玩家3信息列表
        public_messages: str   # 公共信息
        next_player_id: str   # 当前玩家名称
        remark_and_available_operations: str   #可用操作

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),   # 从环境变量中读取您的API Key
    )
    completion = client.models.generate_content(
        # 替换 <Model> 为您的Model ID
        model="gemini-2.5-flash",
        contents=f"{getfile("./rule/referees.txt")}\n以下内容为游戏日志：\n{getfile(logfile)}",
        # contents=[
        #     types.Content(
        #         role="system",
        #         parts=[
        #             types.Part.from_text(text=getfile("./rule/referees.txt")),
        #         ],
        #     ),
        #     types.Content(
        #         role="user",
        #         parts=[
        #             types.Part.from_text(text=getfile(logfile)),
        #         ],
        #     ),
        # ],
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[MathResponse],
        },      # 指定响应解析模型
    )
    resp = completion.text

    print(resp)
    with open('log.json', 'w', encoding='utf-8') as f:
        f.write(resp)


