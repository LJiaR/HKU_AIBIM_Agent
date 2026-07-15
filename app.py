import streamlit as st
import pandas as pd
import os
from checker import run_compliance_check
from agent import get_ai_advisor_report, ask_ai_assistant

# 1. 网页标题和说明
st.set_page_config(page_title="HKU AI+BIM 智能合规审查工具", layout="wide")
st.title("🏗️ HKU AI+BIM 智能合规与合理性审查 Agent")
st.markdown("---")

# 2. 侧边栏：模型载入与设置
with st.sidebar:
    st.header("⚙️ 模型载入与设置")
    st.info("💡 **操作指引**：您可以直接一键体验示例，或上传您自己的 JSON 简化建筑模型。")

    # 选项 A：一键载入示例
    run_sample_btn = st.button("🚀 一键使用示例模型检查", type="primary", use_container_width=True)
    st.markdown("<div style='text-align: center; color: gray; margin: 10px 0;'>— 或 —</div>", unsafe_allow_html=True)

    # 选项 B：文件上传区 (Day 3 新增)
    uploaded_file = st.file_uploader("📂 独立上传 JSON 模型文件", type=["json"])

    st.markdown("---")
    st.markdown("### 🌟 系统亮点 (Day 3 升级版)")
    st.markdown(
        "1. **前端自动化**：秒级几何与属性合规审查\n2. **AI Agent 赋能**：自动溯源建筑防火规范\n3. **智能闭环**：生成 JSON 一键整改补丁\n4. **动态驱动**：支持本地模型即时上传与对话")

# 3. 数据加载逻辑判断
model_path_to_check = None

if run_sample_btn:
    model_path_to_check = "data/sample_model.json"
    st.session_state["current_mode"] = "示例模型"
elif uploaded_file is not None:
    # 将上传的文件临时存入 data 文件夹以便检测
    os.makedirs("data", exist_ok=True)
    temp_path = "data/temp_uploaded_model.json"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    model_path_to_check = temp_path
    st.session_state["current_mode"] = f"自定义文件: {uploaded_file.name}"

# 4. 主界面：多标签页布局 (Day 3 高级 UI 改造)
tab1, tab2 = st.tabs(["📊 合规审查与修复补丁", "💬 AI 建筑专家实时咨询 (Chat Assistant)"])

# === Tab 1: 自动化审查与报告 ===
with tab1:
    if model_path_to_check:
        st.caption(f"当前正在审查的模型源：`{st.session_state.get('current_mode', '未知')}`")

        # 步骤 1：传统规则引擎审查
        st.subheader("1. 规则引擎合规性扫描 (Rule-Engine Checking)")
        with st.spinner("规则引擎正在解析 BIM 模型几何与信息字段..."):
            results = run_compliance_check(model_path_to_check)
            st.session_state["last_results"] = results  # 存入 session 供问答使用

            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                st.error(f"⚠️ 扫描结束！共发现 {len(results)} 处规范违规，请见上方清单。")
            else:
                st.success("🎉 恭喜！模型构件各项指标全部合规！")

        st.markdown("---")

        # 步骤 2：AI 深度建议与补丁
        st.subheader("2. AI 建筑专家深度解析与智能修复 (Agent Advisory)")
        with st.spinner("AI 专家正在引经据典，生成整改方案与代码补丁..."):
            ai_report = get_ai_advisor_report(results)
            with st.container():
                st.markdown(ai_report)
                st.success("💡 提示：您可以直接复制上方代码框中的 JSON Patch，在建模软件或数据库中一键覆盖原属性。")
    else:
        st.info("👈 请从左侧侧边栏点击 **「一键使用示例模型检查」**，或者 **「上传本地 JSON 模型」** 开始体验系统。")

# === Tab 2: AI 实时咨询问答室 ===
with tab2:
    st.subheader("🤖 BIM 与建筑防火规范在线咨询")
    st.caption("您可以围绕当前 BIM 审查结果、疏散门宽设置、消防分区耐火极限等相关专业问题，向智能审查官提问。")

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "您好！我是 HKU AI+BIM 智能合规助理。请问有任何关于本次检测报告或建筑防火规范的疑问可以帮您解答吗？"}
        ]

    # 显示历史对话
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 接收用户新提问
    if prompt := st.chat_input("例如：请问商场疏散门的净宽度最低要求是多少？为什么？"):
        # 显示用户的提问
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # AI 思考并回答
        with st.chat_message("assistant"):
            with st.spinner("AI 审查官正在翻阅建筑规范知识库..."):
                context_data = st.session_state.get("last_results", None)
                reply = ask_ai_assistant(prompt, context_issues=context_data)
                st.markdown(reply)
        st.session_state["messages"].append({"role": "assistant", "content": reply})