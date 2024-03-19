import os
import csv
import uvicorn
import json
from datetime import datetime
from fastapi import Body, FastAPI
from pydantic import BaseModel

class Msg(BaseModel):
    id: int # 消息id
    ts: int # timestamp时间戳
    sign: str # signature 信息签名，用于验证信息的完整性或者身份验证
    type: int # 信息类型
    xml: str # 信息xml部分
    sender: str # 消息发送人
    roomid: str # 信息所属的群id
    content: str # 信息内容
    thumb: str # 视频或者图片信息的略缩图路径
    extra: str # 视频或者图片信息的路径
    is_at: bool # 是否@自己的信息
    is_self: bool # 是否自己说的话
    is_group: bool # 是否群聊信息

def load_sender_names():
    # 加载配置文件中的 sender id 到名称的映射
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)["sender_to_name"]

sender_to_name = load_sender_names()

def save_message_to_csv(message):
    # 检查消息的 sender id，如果在配置文件中且符合特定条件，保存到 CSV 文件中
    if message.sender in sender_to_name:
        sender_name = sender_to_name[message.sender]
        today_date = datetime.now().strftime("%Y%m%d")
        folder_name = sender_name.replace(" ", "_")
        file_name = f"{sender_name}_{today_date}.csv"
        file_path = os.path.join(folder_name, file_name)
        os.makedirs(folder_name, exist_ok=True)
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=message.dict().keys())
            if os.stat(file_path).st_size == 0:
                writer.writeheader()
            writer.writerow(message.dict())

def msg_cb(msg: Msg = Body(description="微信消息")):
    """示例回调方法，简单打印消息"""
    print(f"收到消息：{msg}")
    save_message_to_csv(msg)
    return {"status": 0, "message": "成功"}

if __name__ == "__main__":
    app = FastAPI()
    app.add_api_route("/callback", msg_cb, methods=["POST"])
    uvicorn.run(app, host="127.0.0.1", port=8001)
