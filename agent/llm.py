from dotenv import load_dotenv,find_dotenv
import os
from langchain.chat_models import init_chat_model

# 加载配置文件
# find_dotenv() 确保找到 .env文件 递归查询当前项目文件夹
load_dotenv(find_dotenv())

model = init_chat_model(
    model=os.getenv("LLM_QWEN_MAX"),
    model_provider="openai"
)