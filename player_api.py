import os
import json
from volcenginesdkarkruntime import Ark
from openai import OpenAI


# 玩家操作
def player_action():
    print("玩家正在思考")
    # load rule
    with open('rule/player_system.json', 'r', encoding='utf-8') as f:
        rule = f.read()
    rule = json.loads(rule)
    player1_rule = rule["player1"]
    json_rule = rule["json_rule"]
    example = rule["example"]

    # load messages
    with open('log.json', 'r', encoding='utf-8') as f:
        messages = f.read()
    messages = json.loads(messages)

    # 玩家信息
    player1_message = messages["id1"][0]
    player2_message = messages["id2"][0]
    player3_message = messages["id3"][0]
    # 公共信息
    public_messages = messages["public_messages"]
    # 本轮玩家
    next_player_id = messages["next_player_id"]
    # 可用操作
    remark_and_available_operations = messages["remark_and_available_operations"]

    if next_player_id == "1":

        # Deepseek

        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": player1_rule + json_rule + example},
                {"role": "user",
                 "content": f"你的信息：{player1_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
            ],
            response_format={
                'type': 'json_object'
            }
        )

        results = response.choices[0].message.content

    elif next_player_id == "2":

        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        response = client.chat.completions.create(
            model="qwen3-max",
            messages=[
                {"role": "system", "content": player1_rule + json_rule + example},
                {"role": "user",
                 "content": f"你的信息：{player2_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
            ],
            response_format={"type": "json_object"}
        )

        results = response.choices[0].message.content


    else:
        #Doubao

        client = Ark(
            # 从环境变量中读取您的方舟API Key
            api_key=os.environ.get("DOUBAO_API_KEY"),
            # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
            timeout=1800,
            )
        response = client.chat.completions.create(
            # 替换 <Model> 为您的Model ID
            model="doubao-seed-1.6-250615",
            messages=[
                {"role": "system", "content": player1_rule + json_rule + example},
                {"role": "user", "content": f"你的信息：{player3_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
            ],
             thinking={
                 "type": "disabled" # 不使用深度思考能力,
                 # "type": "enabled" # 使用深度思考能力
                 # "type": "auto" # 模型自行判断是否使用深度思考能力
             },
            response_format={'type': 'json_object'}
        )

        results = response.choices[0].message.content

    return results
action_results = json.loads(player_action())
print(action_results["action"])
# action_results = json.loads(player_action())
# player_action = action_results["action"]