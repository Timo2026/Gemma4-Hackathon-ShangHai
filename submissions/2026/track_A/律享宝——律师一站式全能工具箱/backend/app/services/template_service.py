"""
律享宝 V1.2 - 模板渲染服务
将用户填写的表单数据与FreeMarker模板结合，生成最终文书
"""
import re
import json
from datetime import datetime
from app.data.template_data import TEMPLATES, get_template_detail, get_template_list, TEMPLATE_CATEGORIES


class TemplateRenderError(Exception):
    """模板渲染异常"""
    pass


def _render_simple_field(template_str: str, field_name: str, value) -> str:
    """渲染简单 ${field_name} 占位符"""
    if value is None:
        value = ""
    if isinstance(value, bool):
        value = "是" if value else "否"
    if isinstance(value, (int, float)):
        value = str(value)
    # 替换 ${field_name} 和 ${field_name!default} 两种格式
    pattern = r'\$\{' + re.escape(field_name) + r'(![^}]*)?\}'
    return re.sub(pattern, str(value), template_str)


def _render_object_field(template_str: str, field_name: str, value: dict) -> str:
    """渲染对象类型字段 ${field_name.sub_field}"""
    if not value or not isinstance(value, dict):
        # 用空字符串替换所有子字段引用
        pattern = r'\$\{' + re.escape(field_name) + r'\.[^}]*\}'
        return re.sub(pattern, "", template_str)
    for sub_key, sub_val in value.items():
        if sub_val is None:
            sub_val = ""
        if isinstance(sub_val, bool):
            sub_val = "是" if sub_val else "否"
        sub_pattern = r'\$\{' + re.escape(field_name) + r'\.' + re.escape(sub_key) + r'(![^}]*)?\}'
        template_str = re.sub(sub_pattern, str(sub_val), template_str)
    return template_str


def _render_array_field(template_str: str, field_name: str, values: list) -> str:
    """渲染数组类型字段：处理 <#list> FreeMarker 循环"""
    if not values:
        # 移除整个 <#list> 块
        pattern = r'<#list\s+' + re.escape(field_name) + r'\s+as\s+\w+>.*?</#list>'
        return re.sub(pattern, "", template_str, flags=re.DOTALL)

    # 找到 <#list field_name as item_var> ... </#list> 块
    list_pattern = r'<#list\s+' + re.escape(field_name) + r'\s+as\s+(\w+)>(.*?)</#list>'
    matches = list(re.finditer(list_pattern, template_str, flags=re.DOTALL))
    if not matches:
        # 简单数组字段，直接替换
        return _render_simple_field(template_str, field_name, "、".join(str(v) for v in values))

    for match in matches:
        item_var = match.group(1)
        block_template = match.group(2)
        rendered_items = []
        for idx, item in enumerate(values):
            item_str = block_template
            if isinstance(item, dict):
                for k, v in item.items():
                    item_str = _render_simple_field(item_str, f"{item_var}.{k}", v)
            elif isinstance(item, str):
                item_str = _render_simple_field(item_str, item_var, item)
            # 替换 ${item_var_index} 为序号（1-based）
            item_str = re.sub(r'\$\{' + re.escape(item_var) + r'_index\}', str(idx), item_str)
            item_str = re.sub(r'\$\{' + re.escape(item_var) + r'_has_next\}', "true" if idx < len(values) - 1 else "false", item_str)
            rendered_items.append(item_str)
        replacement = "".join(rendered_items)
        template_str = template_str[:match.start()] + replacement + template_str[match.end():]

    return template_str


def _render_condition_field(template_str: str, field_name: str, value) -> str:
    """渲染条件字段 <#if field_name> ... </#if>"""
    if_pattern = r'<#if\s+' + re.escape(field_name) + r'\??>/>(.*?)</#if>'
    if value:
        # 保留内容，移除 <#if> 标签
        result = re.sub(if_pattern, r'\1', template_str, flags=re.DOTALL)
    else:
        # 移除整个 <#if> 块
        result = re.sub(if_pattern, '', template_str, flags=re.DOTALL)
    return result


def render_template(template_id: str, form_data: dict) -> dict:
    """
    渲染法律文书模板
    Args:
        template_id: 模板ID (如 MS-TY-001)
        form_data: 用户填写的表单数据
    Returns:
        {"title": str, "content": str, "html": str}
    """
    template = get_template_detail(template_id)
    if not template:
        raise TemplateRenderError(f"模板不存在: {template_id}")

    fields = template["fields"]
    content = _build_template_html(template)

    # 渲染各类型字段
    for field in fields:
        fname = field["name"]
        ftype = field.get("type", "text")
        value = form_data.get(fname)

        if ftype == "object":
            content = _render_object_field(content, fname, value or {})
        elif ftype == "array":
            content = _render_array_field(content, fname, value or [])
        elif ftype == "radio" or ftype == "checkbox":
            content = _render_condition_field(content, fname, value)
            content = _render_simple_field(content, fname, value)
        else:
            content = _render_simple_field(content, fname, value)

    # 清理剩余未替换的 ${...} 占位符
    content = re.sub(r'\$\{[^}]+\}', '', content)
    # 清理剩余 FreeMarker 标签
    content = re.sub(r'<#[^>]+>', '', content)
    content = re.sub(r'</#[^>]+>', '', content)

    # 生成纯文本版本（去除HTML标签）
    text_content = re.sub(r'<[^>]+>', '', content)
    text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()

    return {
        "template_id": template_id,
        "title": template["name"],
        "content": text_content,
        "html": content,
    }


def _build_template_html(template: dict) -> str:
    """根据模板类型构建基础HTML模板"""
    template_id = template["id"]
    name = template["name"]
    category = template.get("category", "")
    cause = template.get("case_cause_default", "")

    # 根据文书类别构建不同的HTML结构
    if category == "civil":
        if "起诉状" in name:
            return _build_complaint_template(name, cause)
        elif "答辩状" in name:
            return _build_defense_template(name, cause)
        elif "身份证明" in name:
            return _build_identity_template(name)
        elif "授权委托" in name:
            return _build_authorization_template(name)
        elif "推选书" in name:
            return _build_election_template(name)
        elif "推荐函" in name:
            return _build_recommend_template(name)
        else:
            return _build_generic_template(name)
    elif category == "legal_aid":
        return _build_aid_template(name)
    elif category == "lawyer":
        return _build_lawyer_template(name)
    return _build_generic_template(name)


def _base_html(title, body):
    """基础HTML骨架"""
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: "SimSun", serif; font-size: 14pt; line-height: 1.8; margin: 2.54cm 3.17cm; }}
.title {{ font-size: 22pt; font-weight: bold; text-align: center; margin-bottom: 1.5cm; letter-spacing: 4pt; }}
.section-title {{ font-size: 16pt; font-weight: bold; margin-top: 1cm; margin-bottom: 0.5cm; }}
.content {{ text-indent: 2em; margin-bottom: 0.5cm; }}
.party-info {{ margin-bottom: 0.5cm; }}
.signature {{ text-align: right; margin-top: 3cm; line-height: 2; }}
table {{ border-collapse: collapse; width: 100%; margin: 1cm 0; }}
td, th {{ border: 1px solid #000; padding: 8px 12px; text-align: left; }}
th {{ background-color: #f5f5f5; font-weight: bold; }}
</style>
</head>
<body>
{body}
</body>
</html>'''


def _build_complaint_template(name, cause):
    """民事起诉状模板"""
    body = f'''
<div class="title">{name}</div>
<div class="party-info">
原告：${{plaintiff_info.name}}，${{plaintiff_info.gender}}，${{plaintiff_info.birth_date}}出生，${{plaintiff_info.nation}}族，${{plaintiff_info.work_unit}}，住${{plaintiff_info.address}}，联系电话：${{plaintiff_info.phone}}。
</div>
<div class="party-info">
被告：${{defendant_info.name}}，${{defendant_info.gender}}，${{defendant_info.birth_date}}出生，${{defendant_info.nation}}族，${{defendant_info.work_unit}}，住${{defendant_info.address}}，联系电话：${{defendant_info.phone}}。
</div>
<div class="section-title">诉讼请求</div>
<#list lawsuit_requests as request>
<div class="content">${{request_index+1}}. ${{request}}</div>
</#list>
<div class="section-title">事实与理由</div>
<div class="content">${{fact_and_reason}}</div>
<div class="section-title">证据和证据来源</div>
<#list evidence_list as evidence>
<div class="content">${{evidence_index+1}}. ${{evidence.name}}：证明${{evidence.content}}</div>
</#list>
<div class="signature">
此致<br>${{filing_court}}<br><br>
起诉人：${{plaintiff_info.name}}<br>${{filing_date}}
</div>'''
    return _base_html(name, body)


def _build_defense_template(name, cause):
    """民事答辩状模板"""
    body = f'''
<div class="title">{name}</div>
<div class="party-info">
答辩人：${{respondent_info.name}}，${{respondent_info.gender}}，${{respondent_info.birth_date}}出生，${{respondent_info.nation}}族，${{respondent_info.work_unit}}，住${{respondent_info.address}}，联系电话：${{respondent_info.phone}}。
</div>
<div class="party-info">
被答辩人：${{plaintiff_info.name}}，${{plaintiff_info.gender}}，${{plaintiff_info.birth_date}}出生，${{plaintiff_info.nation}}族，${{plaintiff_info.work_unit}}，住${{plaintiff_info.address}}，联系电话：${{plaintiff_info.phone}}。
</div>
<div class="content">
答辩人于${{receive_date}}收到贵院送达的被答辩人诉答辩人{cause}一案的起诉状副本，现答辩如下：
</div>
<div class="section-title">答辩请求</div>
<#list objections as objection>
<div class="content">${{objection_index+1}}. ${{objection}}</div>
</#list>
<div class="section-title">事实与理由</div>
<div class="content">${{fact_and_reason}}</div>
<div class="section-title">证据和证据来源</div>
<#list evidence_list as evidence>
<div class="content">${{evidence_index+1}}. ${{evidence.name}}：证明${{evidence.content}}</div>
</#list>
<div class="signature">
此致<br>${{responding_court}}<br><br>
答辩人：${{respondent_info.name}}<br>${{responding_date}}
</div>'''
    return _base_html(name, body)


def _build_identity_template(name):
    """身份证明书模板"""
    body = f'''
<div class="title">{name}</div>
<div class="content">${{unit_full_name}}系我单位，${{legal_representative_name}}同志现任我单位${{legal_representative_position}}职务，为我单位法定代表人，特此证明。</div>
<div class="content">联系地址：${{contact_address}}</div>
<div class="content">联系电话：${{contact_phone}}</div>
<div class="signature">${{unit_full_name}}<br>（公章）<br>${{issue_date}}</div>'''
    return _base_html(name, body)


def _build_authorization_template(name):
    """授权委托书模板"""
    body = f'''
<div class="title">{name}</div>
<div class="content">委托人：${{client_name}}，${{client_gender}}，${{client_birth_date}}出生，${{client_nation}}族，${{client_work_unit}}，住${{client_address}}，联系电话：${{client_phone}}。</div>
<div class="content">受委托人：${{agent1_name}}，${{agent1_unit}}${{agent1_position}}，联系电话：${{agent1_phone}}。</div>
<#if agent2_name??>
<div class="content">受委托人：${{agent2_name}}，与委托人关系：${{agent2_relation}}，住${{agent2_address}}，联系电话：${{agent2_phone}}。</div>
</#if>
<div class="content">现委托上列受委托人在我与${{case_parties}}因${{case_cause}}一案中，作为我参加诉讼的委托代理人。</div>
<div class="content">代理权限：<#if is_special_authorization>特别授权<#else>一般授权</#if>。</div>
<div class="signature">委托人：${{client_name}}<br>${{issue_date}}</div>'''
    return _base_html(name, body)


def _build_election_template(name):
    """代表人推选书模板"""
    body = f'''
<div class="title">{name}</div>
<div class="content">我们共同推选${{representative1_name}}、${{representative2_name}}为我方与${{case_parties}}因${{case_cause}}一案的共同诉讼代表人。</div>
<div class="content">代表人的诉讼行为对全体推选人发生法律效力。</div>
<div class="content">代表人联系地址：${{representative_address}}</div>
<div class="content">代表人联系电话：${{representative_phone}}</div>
<div class="signature">推选人签名/盖章：____________________<br>${{issue_date}}</div>'''
    return _base_html(name, body)


def _build_recommend_template(name):
    """推荐函模板"""
    body = f'''
<div class="title">{name}</div>
<div class="content">${{accepting_court_full_name}}：</div>
<div class="content">关于${{case_parties}}因${{case_cause}}一案，现推荐${{recommended_person_name}}作为本案当事人的诉讼代理人。</div>
<div class="content">代理权限：${{authorization_scope}}。</div>
<div class="signature">推荐单位：____________________（公章）<br>推荐人：____________________<br>${{issue_date}}</div>'''
    return _base_html(name, body)


def _build_aid_template(name):
    """法律援助文书模板"""
    body = f'''
<div class="title">{name}</div>
<table>
<tr><th style="width:25%">申请人姓名</th><td>${{applicant_name}}</td></tr>
<tr><th>性别</th><td>${{applicant_gender}}</td></tr>
<tr><th>出生日期</th><td>${{applicant_birth_date}}</td></tr>
<tr><th>民族</th><td>${{applicant_nation}}</td></tr>
<tr><th>身份证号</th><td>${{applicant_id_no}}</td></tr>
<tr><th>住址</th><td>${{applicant_address}}</td></tr>
<tr><th>联系电话</th><td>${{applicant_phone}}</td></tr>
<tr><th>案由</th><td>${{case_cause}}</td></tr>
<tr><th>案情简述</th><td>${{case_description}}</td></tr>
</table>
<div class="signature">${{issuing_authority}}<br>（公章）<br>${{issue_date}}</div>'''
    return _base_html(name, body)


def _build_lawyer_template(name):
    """律师辅助文书模板"""
    body = f'''
<div class="title">{name}</div>
<div class="section-title">一、案件基本情况</div>
<table>
<tr><th style="width:25%">案号</th><td>${{case_no}}</td></tr>
<tr><th>案由</th><td>${{case_cause}}</td></tr>
<tr><th>当事人信息</th><td>${{parties_info}}</td></tr>
</table>
<div class="section-title">二、案件事实</div>
<div class="content">${{case_facts}}</div>
<div class="section-title">三、法律分析</div>
<div class="content">${{legal_analysis}}</div>
<div class="section-title">四、处理意见</div>
<div class="content">${{handling_opinion}}</div>
<div class="signature">拟稿人：${{drafter}}<br>${{draft_date}}</div>'''
    return _base_html(name, body)


def _build_generic_template(name):
    """通用文书模板"""
    body = f'''<div class="title">{name}</div><div class="content">（文书内容待填写）</div>'''
    return _base_html(name, body)
