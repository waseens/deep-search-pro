# 目标加载yml中的数据，供创建主和子智能体使用
import yaml # yaml配置文件读取
from pathlib import Path

# 定义一个加载函数，配置文件yaml加载成字典
def load_yaml(file_path):
    """
    加载指定位置的yaml配置文件
    :param file_path:  加载的文件的地址
    :return:  返回的加载结果 本质就是字典
    """
    with open(file_path, 'r', encoding='utf-8') as f :
        # safe_load 只会加载，不会触发！
        # load 加载过程中可能无意执行内部的嵌入函数！！ 可能发生注入脚本攻击
        return yaml.safe_load(f)

# 尝试读取主和子智能体的配置文件和数据（供后续使用）
# 项目的根地址
# project_root_path  = Path(__file__).parent.parent
project_root_path  = Path(__file__).parents[1] # prompts -> parents -> [agent , deep_search_pro]
yaml_file_path = project_root_path / "prompt" / "prompts.yml"

prompt_yaml_content = load_yaml(yaml_file_path)


# main_agent_content
main_agent_content = prompt_yaml_content["main_agent"]
print(main_agent_content)
# sub_agents_content
sub_agents_content = prompt_yaml_content["sub_agents"]

print(sub_agents_content)