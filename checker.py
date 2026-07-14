import json

def run_compliance_check(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    report = []

    # 遍历模型中的每个构件
    for el in data.get('elements', []):
        props = el.get('properties', {})
        el_id = el.get('id')
        el_name = el.get('name')

        # 规则 1：疏散门净宽检查（最低要求 0.9m）
        if el.get('type') == 'IfcDoor':
            width = props.get('ClearWidth', 0)
            if width < 0.9:
                report.append({
                    "构件ID": el_id,
                    "构件名称": el_name,
                    "检查类型": "几何尺寸违规",
                    "当前状态": f"净宽 {width}m",
                    "合规要求": "≥ 0.9m (疏散规范)",
                    "风险等级": "🔴 严重违规"
                })

        # 规则 2：防火等级 (FireRating) 属性完善度检查
        if props.get('FireRating') is None:
            report.append({
                "构件ID": el_id,
                "构件名称": el_name,
                "检查类型": "BIM属性缺失",
                "当前状态": "FireRating 属性为 null",
                "合规要求": "需填入有效防火等级 (如 1H/2H)",
                "风险等级": "🟡 警告/待补全"
            })

    return report

# 本地测试代码：在 PyCharm 里右键运行这个文件，看看下方的终端有没有吐出结果
if __name__ == "__main__":
    results = run_compliance_check("data/sample_model.json")
    print("—— 检查完成！发现以下问题 ——")
    for r in results:
        print(r)