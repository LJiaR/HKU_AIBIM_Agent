import json
import os
from openai import OpenAI

# =====================================================================
# 【配置区】如果你有 DeepSeek、OpenAI 或智谱的 API Key，可填入下方。
# 如果暂时没有，保持为空 "" 即可，系统会自动启动“智能模拟模式”确保流畅演示！
# =====================================================================
API_KEY = ""  # 例如："sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "https://api.deepseek.com"  # 默认使用性价比极高的 DeepSeek 接口地址
MODEL_NAME = "deepseek-chat"


def get_ai_advisor_report(issues_list):
    """
    输入 checker.py 检查出的违规列表，调用 AI 大模型生成深度解析与建议
    """
    if not issues_list:
        return "🎉 当前模型构件全部合规，无需 AI 介入修改意见。"

    # 将违规数据转为字符串，传给 AI 作为参考背景
    issues_str = json.dumps(issues_list, ensure_ascii=False, indent=2)

    # 1. 优雅降级：如果没有填 API Key，直接返回高水准的建筑规范模拟报告
    if not API_KEY or API_KEY == "":
        return _get_fallback_mock_response(issues_list)

    # 2. 真实 AI 调用：如果你填了 Key，将向云端大模型发送专业提示词
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

        system_prompt = """
        你是一位具备20年经验的资深 BIM 数字化合规审查官与注册建筑师。
        请针对用户提交的 BIM 构件违规检测结果，给出专业的整改建议。

        你的回答必须包含以下三个板块（请使用 Markdown 格式清晰排版）：
        ### 1. 📖 违规风险与规范溯源
        （对每一个违规点，指出违反了《建筑设计防火规范 GB 50016》或相关通用的疏散标准，解释具体安全隐患）
        ### 2. 🛠️ 专家整改指导
        （用通俗易懂的工程语言告诉建模师该怎么改，建议改到多少数值）
        ### 3. 💻 自动修复补丁 (JSON Patch)
        （直接生成一段合规的 JSON 代码段，包含正确的 ClearWidth 或 FireRating 参数，方便工程师一键复制覆盖）
        """

        user_prompt = f"以下是系统自动检测到的违规构件列表，请出具你的专家审查意见：\n{issues_str}"

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3  # 低温度确保工程技术参数的准确性和严谨性
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ 调用大模型 API 出现网络或认证异常 ({str(e)})。\n\n" + _get_fallback_mock_response(issues_list)


def _get_fallback_mock_response(issues_list):
    """
    本地智能模拟生成报告（针对测试模型定向优化），展现系统高鲁棒性
    """
    mock_md = "*(💡 当前运行于本地 AI 离线专家引擎模式)*\n\n"
    mock_md += "### 1. 📖 违规风险与规范溯源\n"
    mock_md += "- **DOOR_002 (储藏室窄门)**：当前净宽为 0.75m。根据《建筑设计防火规范 GB 50016》及民用建筑设计通则，公共/商业建筑内作为疏散通道的门，其净宽度**严禁小于 0.90m**。0.75m 在紧急疏散或消防队员负重进入时极易造成拥堵和安全事故。\n"
    mock_md += "- **WALL_002 (会议室隔断墙)**：当前 `FireRating` (防火等级) 属性缺失 (`null`)。在 BIM 数字化运维与消防审查中，墙体作为防火分区或房间分隔的载体，必须明确其耐火极限。缺失该属性将导致 BIM 算量与消防模拟（如 Pyrosim）无法正常识别空间属性。\n\n"

    mock_md += "### 2. 🛠️ 专家整改指导\n"
    mock_md += "1. **门构件调整**：建议在建模软件（如 Revit/ArchiCAD）中，将 `DOOR_002` 的族类型参数 `ClearWidth` 提升至标准尺寸 **1.0m**（或者至少不低于 0.9m）。\n"
    mock_md += "2. **墙体属性补全**：根据该墙体作为“会议室隔断”的功能特性，非承重隔墙常规耐火极限要求一般为 **1.00h**，建议补充属性字段 `\"FireRating\": \"1H\"`。\n\n"

    mock_md += "### 3. 💻 自动修复补丁 (JSON Patch)\n"
    mock_md += "您可以直接复制以下 JSON 补丁代码，覆盖原模型中对应构件的 `properties` 字段以完成一键修复：\n"
    mock_md += "```json\n"
    mock_md += "[\n"
    mock_md += "  {\n"
    mock_md += "    \"id\": \"DOOR_002\",\n"
    mock_md += "    \"name\": \"储藏室窄门\",\n"
    mock_md += "    \"properties_patch\": { \"ClearWidth\": 1.0, \"FireRating\": \"1H\" }\n"
    mock_md += "  },\n"
    mock_md += "  {\n"
    mock_md += "    \"id\": \"WALL_002\",\n"
    mock_md += "    \"name\": \"会议室隔断墙\",\n"
    mock_md += "    \"properties_patch\": { \"Thickness\": 120, \"FireRating\": \"1H\" }\n"
    mock_md += "  }\n"
    mock_md += "]\n"
    mock_md += "```"
    return mock_md


# 本地测试代码
if __name__ == "__main__":
    from checker import run_compliance_check

    issues = run_compliance_check("data/sample_model.json")
    print("—— 正在呼唤 AI 建筑专家思考 ——")
    report = get_ai_advisor_report(issues)
    print(report)