import streamlit as st
import pandas as pd
from checker import run_compliance_check

# 网页标题和说明
st.set_page_config(page_title="HKU AI+BIM 智能合规审查工具", layout="wide")
st.title("🏗️ HKU AI+BIM 智能合规与合理性审查 Agent")
st.markdown("---")

# 侧边栏：操作区
with st.sidebar:
    st.header("⚙️ 模型载入与设置")
    st.info("当前模式：简便测试模式 (JSON 简化格式)")
    run_btn = st.button("🚀 一键载入示例模型并开始检查", type="primary", use_container_width=True)

# 主界面：结果展示区
if run_btn:
    st.subheader("📊 合规性审查结果")
    with st.spinner("AI 与规则引擎正在解析 BIM 模型结构..."):
        # 调用我们在 checker.py 写好的函数
        results = run_compliance_check("data/sample_model.json")

        if results:
            # 用 pandas 转成表格，在网页上漂亮地展示出来
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.error(f"⚠️ 审查结束！共发现 {len(results)} 处规范问题，请参阅上表。")
        else:
            st.success("🎉 恭喜！模型构件全部合规！")
else:
    st.info("👈 请点击左侧侧边栏的 **「一键载入示例模型并开始检查」** 按钮体验系统。")