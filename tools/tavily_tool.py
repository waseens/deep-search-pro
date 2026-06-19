# 定义一个网络搜索的工具！
# ======================== 导入核心依赖 ========================
# 类型注解：增强代码提示和静态检查能力
from typing import  Literal
# LangChain 工具装饰器：将普通函数转为 Agent 可调用的工具
from langchain_core.tools import tool
# Tavily 官方客户端：实现网络搜索核心功能
from tavily import TavilyClient

# 系统/第三方依赖
import os  # 系统路径/环境变量处理
from dotenv import load_dotenv  # 加载 .env 文件中的环境变量

# 自定义模块：工具调用埋点监控（需确保 api 模块可导入）
from api.monitor import monitor

# ======================== 初始化配置 ========================
# 加载项目根目录的 .env 文件，读取环境变量（如 TAVILY_API_KEY）
load_dotenv()


# 步骤1： 定义一个TavilyClient对象
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# 步骤2： 定义一个网络搜索工具
@tool
def internet_search(
        query: str,
        topic: Literal[ "news",  "finance",  "general"] = "general",
        max_results: int = 5,
        include_raw_content: bool = False
):
    """
    根据用户问题，进行网络信息收！ 
    注意：主要搜索公开的网络信息！如果指定查询数据库或者rag不能使用此工具！
    :param query: 用户的查询信息
    :param topic: 查询的类型
    :param max_results: 返回的最大条数 
    :param include_raw_content: 是否返回原内容 False 精简 True 详细
    :return: 
    """
    # 每次调用工具，都都会向前端推进调用进度！
    # 参数1： 工具的名字  参数2： 就是调用工具的参数信息
    monitor.report_tool(tool_name="网络搜索工具",
                        args={"query": query, "topic": topic, "max_results": max_results,
                              "include_raw_content": include_raw_content})

    return tavily_client.search(query = query, topic =  topic,
                                max_results = max_results, include_raw_content = include_raw_content)














