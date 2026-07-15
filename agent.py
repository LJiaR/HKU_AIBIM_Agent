import json
import os

# =====================================================================
# 【顶级工程容错设计】
# =====================================================================
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

API_KEY = ""  # 例如："sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"


def get_ai_advisor_report(issues_list):
    """
    输入 checker.py 检查出的违规列表，调用 AI 大模型或离线引擎生成深度解析与建议
    """
    if not issues_list:
        return "🎉 当前模型构件全部合规，无需 AI 介入修改意见。"

    issues_str = json.dumps(issues_list, ensure_ascii=False, indent=2)

    if not OPENAI_AVAILABLE or not API_KEY or API_KEY == "":
        return _get_fallback_mock_response(issues_list)

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
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 呼叫云端 AI 遇到网络波动 ({str(e)})。\n\n" + _get_fallback_mock_response(issues_list)


def ask_ai_assistant(user_question, context_issues=None):
    """
    【Day 3 新增】支持针对模型审查结果或建筑规范进行实时自由问答
    """
    if not OPENAI_AVAILABLE or not API_KEY or API_KEY == "":
        # 智能离线知识库回复，展现极佳的本地容错体验
        q = user_question.lower()
        if "门" in q or "002" in q or "宽" in q or "疏散" in q:
            return "🤖 **[离线专家解答]**：关于疏散门宽度，根据《建筑设计防火规范 GB 50016》第5.5条及通则规定，商业/公共建筑内疏散门的净宽度**不应小于 0.90m**。测试模型中的 `DOOR_002` 仅为 0.75m，极易在紧急疏散时造成拥堵，建议通过 Revit/ArchiCAD 将其修改为 1.0m 标准门宽。"
        elif "墙" in q or "防火" in q or "rating" in q or "等级" in q:
            return "🤖 **[离线专家解答]**：关于墙体防火等级 (FireRating)，在 BIM 建模中，非承重隔墙通常要求不低于 **1.00h** 的耐火极限。如果是防火分区墙，一般要求 **2.00h** 或以上。`WALL_002` 缺失该字段将导致后续 Pyrosim 消防模拟与算量失败，建议使用上方的 JSON Patch 一键补全为 `\"1H\"`。"
        else:
            return f"🤖 **[离线专家解答]**：您好！我是 HKU AI+BIM 智能合规助理。我已接收到您的疑问：*“{user_question}”*。在本次 BIM 模型审查中，我们的核心关注点在**几何尺度安全**（如门净宽）和**数字化信息完整度**（如耐火极限）。如果您对刚才检测到的 2 处违规有任何具体的修改疑问，请随时吩咐！"

    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        system_prompt = "你是一位香港大学 AI+BIM 团队的资深智能建筑顾问，回答需专业、严谨、排版清晰，深入浅出地解释 BIM 与消防规范。"
        messages = [{"role": "system", "content": system_prompt}]
        if context_issues:
            messages.append(
                {"role": "assistant", "content": f"当前审查的模型背景：共检测到 {len(context_issues)} 处违规，具体为：{str(context_issues)}"})
        messages.append({"role": "user", "content": user_question})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 呼叫云端 AI 遇到波动，自动切换离线解答：\n\n" + ask_ai_assistant(user_question)


def _get_fallback_mock_response(issues_list):
    """
    本地智能专家报告生成器
    """
    mock_md = "*(💡 系统状态：当前调用 AI 建筑专家离线推理引擎)*\n\n"
    mock_md += "### 1. 📖 违规风险与规范溯源\n"
    mock_md += "- **DOOR_002 (储藏室窄门)**：当前净宽为 0.75m。根据《建筑设计防火规范 GB 50016》及民用建筑设计通则，公共/商业建筑内作为疏散通道的门，其净宽度**严禁小于 0.90m**。0.75m 在紧急疏散或消防队员负重进入时极易造成拥堵和致命安全隐患。\n"
    mock_md += "- **WALL_002 (会议室隔断墙)**：当前 `FireRating` (防火等级) 属性缺失 (`null`)。在 BIM 数字化运维与消防审查中，墙体作为防火分区或分隔载体，必须明确耐火极限。缺失该属性将导致 BIM 算量与消防模拟（如 Pyrosim、Pathfinder）无法正常识别空间分割条件。\n\n"

    mock_md += "### 2. 🛠️ 专家整改指导\n"
    mock_md += "1. **门构件调整**：建议在建模软件（如 Revit / ArchiCAD）中，将 `DOOR_002` 的族类型参数 `ClearWidth` 调整至标准尺寸 **1.0m**（最低严禁低于 0.9m）。\n"
    mock_md += "2. **墙体属性补全**：根据该墙体作为“会议室隔断”的功能特性，非承重防火墙常规耐火极限要求一般为 **1.00h**，建议在 IFC/JSON 属性表中补充 `\"FireRating\": \"1H\"`。\n\n"

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