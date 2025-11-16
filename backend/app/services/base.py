from typing import List, Dict, Any, TypedDict, Optional
from pydantic import BaseModel, Field

# 文件计划模型
class FileInfo(BaseModel):
    path: str = Field(description="文件路径")
    purpose: str = Field(description="文件用途")
    dependencies: List[str] = Field(default_factory=list, description="依赖的文件列表")

# API摘要模型
class APISummary(BaseModel):
    func_name: str = Field(description="函数名")
    params: str = Field(description="参数描述")
    returns: str = Field(description="返回值描述")
    description: str = Field(description="功能描述")

# 状态模式
class CodeGenerationState(TypedDict,total=False):
    project_description: str  # 项目需求描述
    file_plan: List[Dict]  # 计划生成的文件列表
    completed_files: List[str]  # 已完成的文件路径
    api_summaries: List[Dict]  # API摘要库: {文件路径: [API摘要]}
    current_file: List[Dict]  # 当前正在处理的文件
    generated_code: Dict[str, str]  # 当前生成的代码
    files_to_process: List[str]  # 需要处理的文件列表
    error: Optional[str]  # 错误信息