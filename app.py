import streamlit as st
import pandas as pd
from checker import run_compliance_check
from agent import get_ai_advisor_report

# 网页标题和说明
st.set_page_config(page_title="HKU AI+BIM 智能合规审查工具", layout="wide")
st.title("🏗️ HKU AI+BIM 智能合规与合理性审查 Agent")
st.markdown("---")

# 侧边栏：操作区
with st.sidebar:
    st.header("⚙️ 模型载入与设置")
    st.info("当前模式：简便测试模式 (JSON 简化格式)")
    run_btn = st.button("🚀 一键载入示例模型并开始检查", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("### 💡 系统特色")
    st.markdown("1. **前端自动化**：秒级几何与属性合规审查\n2. **AI Agent 赋能**：自动溯源建筑防火规范\n3. **智能闭环**：生成 JSON 一键整改补丁")

# 主界面：结果展示区
if run_btn:
    # 1. 传统规则引擎审查
    st.subheader("📊 1. 合规性审查结果 (Rule-Engine Checking)")
    with st.spinner("规则引擎正在解析 BIM 模型结构..."):
        results = run_compliance_check("data/sample_model.json")

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.error(f"⚠️ 审查结束！共发现 {len(results)} 处规范问题，请参阅上表。")
        else:
            st.success("🎉 恭喜！模型构件全部合规！")

    st.markdown("---")

    # 2. AI Agent 深度分析与建议
    st.subheader("🤖 2. AI 建筑专家深度解析与智能修复 (Agent Advisory)")
    with st.spinner("AI 专家正在引经据典，生成整改方案与代码补丁..."):
        ai_report = get_ai_advisor_report(results)
        # 用 Streamlit 的容器将 AI 报告框起来，提升高级感
        with st.container():
            st.markdown(ai_report)
            st.success("💡 提示：您可以直接复制上方代码框中的 JSON Patch，在建模软件或数据库中一键覆盖原属性。")

else:
    st.info("👈 请点击左侧侧边栏的 **「一键载入示例模型并开始检查」** 按钮体验系统。")