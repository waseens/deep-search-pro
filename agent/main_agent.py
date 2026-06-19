from agent.subagents.knowledge_base_agent import knowledge_base_agent
from agent.subagents.database_query_agent import database_query_agent
from agent.subagents.network_search_agent import network_search_agent
from langgraph.checkpoint.memory import InMemorySaver

# main_agent tool导入
from tools.markdown_tools import generate_markdown
from tools.pdf_tools import convert_md_to_pdf
from tools.upload_file_read_tool import read_file_content

from deepagents import create_deep_agent

from agent.llm import model
from agent.prompts import main_agent_content

from api.monitor import monitor
import asyncio
import uuid
import shutil
from pathlib import Path

from api.context import set_session_context, reset_session_context, set_thread_context

from langchain_core.messages import AIMessage

main_agent = create_deep_agent(
   model = model,
   system_prompt=main_agent_content['system_prompt'],
   tools= [generate_markdown,convert_md_to_pdf,read_file_content],
   checkpointer=InMemorySaver(),
   subagents=[
       database_query_agent,
       network_search_agent,
       knowledge_base_agent
   ]
)

# 执行
"""
  1. 执行主智能体 一定选异步，原因：对应多个客户端
  2. 什么时候触发我们智能体的调用或者执行？？？
  3. 客户端 -》 api/task -> fastapi 接口 -》 异步执行 -》 main_agent的运行 （异步方法）
  4. main_agent执行stream流式处理 -》 调用工具 -》 已经埋好了点  
                                   调用子智能体 -》 结果解析 -》 name = task -> monitor -> 发送子智能体
                                   调用最终结果 -》 结果 -》 monitor -> 发送结果的方法
                                   开启调用以后 -》 当前会话 -》 文件夹地址 -》 推送到前端
"""



project_root_path = Path(__file__).parents[1].resolve() # 绝对 解析路径标识以及软连接
# project_root_path = Path(__file__).parents[1].absolute() # 绝对
# main_agent.invoke()
# main_agent.stream()
# main_agent.astream() [选他]
async def run_deep_agent(task_query,session_id):
    """
    定义流式+异步执行主智能体！！
    执行过程中，返回  会话文件化返回  调用子智能体  调用最终结果 （monitor）
    task_query: 前端提问的问题
    session_id: 每个前端会话对应的标识 （1.存储session_id ContextVars 2.session_id 给他创建对应的output输出地址）
    """
    print(f"当前会话的main_agent开始执行了！ 会话id:{session_id}")
    # 准备工作 【1. session_dir（前端） 2. relative_session_dir (大模型) 3. 上传的文件拼接上传文件专属提示词】
    # project_root_path / output / session_session_id(uuid)
    # 当前会话存储生成文件的专属文件夹
    session_dir = project_root_path / "output" / f"session_{session_id}"
    # 文件夹可能没有，第一次请求要创建
    session_dir.mkdir(parents=True, exist_ok=True)
    # \  \n \t -> /
    session_dir_str = str(session_dir).replace("\\","/")
    # 获取相对文件夹
    # session_dir : project_root_path / output / session_session_id(uuid)
    # project_root_path : project_root_path
    # relative_session_dir_str: / output / session_session_id(uuid)
    relative_session_dir_str = str(session_dir.relative_to(project_root_path)).replace("\\","/")

    #处理上传文件 （updated / session_session_id）
    updated_dir_path = project_root_path / "updated" / f"session_{session_id}"
    updated_info_prompt = "" # 有上传文件，拼接上传文件专属解析位置的提示词
    if updated_dir_path.exists():
        # 有
        files = [ f.name  for f in updated_dir_path.iterdir()  if f.is_file()]
        # 将上传文件统一赋值到 output_dir 方便前端统一读取 session_dir
        if files:
            for filename in files:
                # 将原文件 -》 复制 -》 目标文件中  （copy2 保留原文件修改时间和权限等元数据）
                shutil.copy2(updated_dir_path / filename, session_dir / filename)
            # 构建提示词！告诉大模型，有上传文件，你要读取上传文件！！
            updated_info_prompt = (f"\n    [已上传文件] 已加载到工作目录:\n" +
                             "\n".join([f"    - {f}" for f in files]) +
                             "\n    请优先使用工具（read_file_content）读取并参考这些文件。")

    # 继续准备 1. 当前会话的对应的session_id session_dir 存储到contextVars [后续工具获取，socket -> 推送消息] 2.调用monitor给前端推送session_dir信息
    session_dir_token = set_session_context(session_dir_str)  # 存储的当前会话对应的文件夹地址
    session_id_token = set_thread_context(session_id)  #获取当前会话的session_id对应socket

    monitor.report_session_dir(session_dir_str)  # 当前会话对应的文件夹地址推送给起前端！

    # 执行main_agent
    config = {
        "configurable":{
            "thread_id":session_id
        }
    }

    # 构建提示词
    path_instruction = f"""
    【工作环境指令】
    工作目录: {relative_session_dir_str}
    {updated_info_prompt}

    规则：
    1. 新生成文件必须保存到工作目录：'{relative_session_dir_str}/filename'
    2. 读取已上传的文件时，请直接将文件名（例如：'开篇.txt'）作为 filename 参数传入（read_file_content）读取工具，不要带上任何目录前缀。
    3. 使用相对路径，禁止使用绝对路径
    4. 若存在上传文件，请先分析内容
    """
    # 反馈结果
    try:
        # 执行
        async for chunk in main_agent.astream({
            "messages":[
                {
                    "role":"user","content":task_query+path_instruction
                }
            ]
        },config=config):
            # {"model [大模型决定调用工具 子智能体  最终结果] / tools" : {messages:[xxx...]}}
            for node_name,state in chunk.items():
                if not state or "messages" not in state: continue
                messages = state["messages"]
                if messages and isinstance(messages,list):
                    last_msg = messages[-1]
                    if node_name == 'model':
                        if last_msg.tool_calls:
                            # 工具和子智能体
                            for tool_call in last_msg.tool_calls:
                                """
                                  tool_call = {
                                      name: task
                                      args:{
                                          subagent_type:子智能体的名字
                                          description:子智能体的描述
                                      }
                                  }                                
                                """
                                if tool_call['name'] == 'task':
                                    # 调用某个子智能体
                                    monitor.report_assistant(tool_call['args']['subagent_type'],{'description':tool_call['args']['description']})
                        elif last_msg.content:
                            # 最终结果
                            print(f"主智能体执行结果，最终结果：{last_msg.content[:100]}")
                            monitor.report_task_result(last_msg.content)

    except Exception as e :
        # 报错推送错误信息给前端
        monitor._emit("error",f"执行主智能发生异常信息：{str(e)}")
    finally:
        # 释放存储的地址和session_id
        reset_session_context(session_dir_token, session_id_token)

