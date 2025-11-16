import os
import json
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from backend.app.PROMPT.planprompt import planprompt
from backend.app.PROMPT.filecode_generate import filecode_generate
from backend.app.PROMPT.summaryprompt import summary_prompt
from backend.app.PROMPT.textprompt import text_prompt
from langchain_core.prompts import ChatPromptTemplate
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.app.services.base import CodeGenerationState
import fitz
from openai import OpenAI

def call_project_plan_llm(text_description: str):
    model = ChatOpenAI(
        model="qwen3-max",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    agent = create_agent(model)
    resp = agent.invoke({"messages":[{"role":"user","content":planprompt.format(text_information=text_description)}]})
    return json.loads(resp["messages"][-1].content)

def call_generate_code_llm(state : CodeGenerationState):
    if not state["current_file"]:
        return state

    def generate_file(file_info):
        context = ""
        if "api_summaries" in state:
            for dep_file in file_info.get("dependencies", []):
                if dep_file in state["api_summaries"]:
                    context += f"文件: {dep_file}\n"
                    for api in state["api_summaries"][dep_file]:
                        context += f"- 函数: {api['func_name']}\n"
                        context += f"  参数: {api['params']}\n"
                        context += f"  返回: {api['returns']}\n"
                        context += f"  说明: {api['description']}\n\n"

        prompt = ChatPromptTemplate([
            ("system", "你是一个资深软件架构师，负责根据需求设计项目结构。"),
            ("user", filecode_generate)
        ])
        model = ChatOpenAI(
            model="qwen3-max",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        chain = prompt | model
        response = chain.invoke({
            "project_description": state["project_description"],
            "file_path": file_info["path"],
            "file_purpose": file_info["purpose"],
            "dependencies": ", ".join(file_info.get("dependencies", [])),
            "context": context if context else "无依赖"
        })
        return file_info["path"], response.text

    # 使用多线程并行生成
    generated_codes = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(generate_file, file_info) for file_info in state["current_file"]]
        for future in as_completed(futures):
            file_path, code = future.result()
            generated_codes[file_path] = code

    if "generated_codes" not in state or state["generated_code"] is None:
        state["generated_code"] = {}
    # 更新状态
    for file_path, code in generated_codes.items():
        state["generated_code"][file_path] = code
    state["files_to_process"] = list(generated_codes.keys())  # 标记需要处理的文件
    return state


def call_api_summary_llm(state : CodeGenerationState) -> List[Dict[str, str]]:
    """从代码中提取API摘要"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个API文档专家，负责从代码中提取关键接口信息。"),
        ("human", summary_prompt)
    ])
    model = ChatOpenAI(
        model="qwen3-max",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    chain = prompt | model
    file_path = state["current_file"]
    code = state["generated_code"]
    response = chain.invoke({"file_path": file_path, "code": code}).text
    try:
        api_summary = json.loads(response)
    except Exception:
        # 如果模型返回多余内容（常见），做容错
        try:
            response_text = response.strip().strip("```json").strip("```")
            api_summary = json.loads(response_text)
        except Exception as e:
            raise ValueError("LLM API summary JSON 解析失败: ", e)

    return api_summary


def call_pdf_reader_llm(file,image_information):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    prompt = text_prompt.format(
        image_information = image_information
    )
    # doc = fitz.open(pdf_path)
    doc = fitz.open(stream=file.read(), filetype="pdf")
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()

    response = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "text", "text": pdf_text}
            ]}
        ]
    )
    text = response.choices[0].message.content
    return text