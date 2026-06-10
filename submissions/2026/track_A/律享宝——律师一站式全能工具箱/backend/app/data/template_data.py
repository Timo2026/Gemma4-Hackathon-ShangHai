"""
律享宝 V1.2 - 法律文书模板库数据
90份模板的分类、字段定义和FreeMarker模板
"""

# ==================== 模板分类 ====================
TEMPLATE_CATEGORIES = [
    {
        "id": "civil",
        "name": "民事诉讼文书（最高法2024版）",
        "sub_categories": [
            {"id": "civil_general", "name": "通用诉讼文书", "count": 6},
            {"id": "civil_special", "name": "案由专项文书", "count": 22},
        ]
    },
    {
        "id": "legal_aid",
        "name": "法律援助文书（司法部2024版）",
        "sub_categories": [
            {"id": "aid_apply", "name": "申请受理类", "count": 8},
            {"id": "aid_decision", "name": "决定指派类", "count": 5},
            {"id": "aid_manage", "name": "办案管理类", "count": 9},
            {"id": "aid_duty", "name": "值班律师类", "count": 7},
            {"id": "aid_quality", "name": "质量监督类", "count": 3},
        ]
    },
    {
        "id": "lawyer",
        "name": "律师办案辅助文书",
        "sub_categories": [
            {"id": "lawyer_aux", "name": "办案辅助文书", "count": 12},
        ]
    },
]

# ==================== 通用起诉状字段 ====================
SHARED_COMPLAINT_FIELDS = [
    {"name": "plaintiff_info", "label": "原告信息", "type": "object", "required": True, "properties": [
        {"name": "name", "label": "姓名/名称", "type": "text", "required": True},
        {"name": "gender", "label": "性别", "type": "select", "required": False, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "birth_date", "label": "出生日期", "type": "date", "required": False, "format": "yyyy年MM月dd日"},
        {"name": "nation", "label": "民族", "type": "text", "required": False},
        {"name": "work_unit", "label": "工作单位/职业", "type": "text", "required": False},
        {"name": "address", "label": "住址", "type": "text", "required": True},
        {"name": "phone", "label": "联系电话", "type": "text", "required": True},
    ]},
    {"name": "defendant_info", "label": "被告信息", "type": "object", "required": True, "properties": [
        {"name": "name", "label": "姓名/名称", "type": "text", "required": True},
        {"name": "gender", "label": "性别", "type": "select", "required": False, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "birth_date", "label": "出生日期", "type": "date", "required": False, "format": "yyyy年MM月dd日"},
        {"name": "nation", "label": "民族", "type": "text", "required": False},
        {"name": "work_unit", "label": "工作单位/职业", "type": "text", "required": False},
        {"name": "address", "label": "住址", "type": "text", "required": True},
        {"name": "phone", "label": "联系电话", "type": "text", "required": True},
    ]},
    {"name": "lawsuit_requests", "label": "诉讼请求", "type": "array", "required": True, "item": {"type": "text", "label": "诉讼请求"}},
    {"name": "fact_and_reason", "label": "事实与理由", "type": "textarea", "required": True, "placeholder": "请详细陈述事实与理由"},
    {"name": "evidence_list", "label": "证据清单", "type": "array", "required": True, "item": {"type": "object", "properties": [
        {"name": "name", "label": "证据名称", "type": "text", "required": True},
        {"name": "content", "label": "证明内容", "type": "text", "required": True},
    ]}},
    {"name": "filing_court", "label": "受理法院", "type": "text", "required": True, "placeholder": "请输入受理法院全称"},
    {"name": "filing_date", "label": "起诉日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
]

# ==================== 通用答辩状字段 ====================
SHARED_DEFENSE_FIELDS = [
    {"name": "respondent_info", "label": "答辩人信息", "type": "object", "required": True, "properties": [
        {"name": "name", "label": "姓名", "type": "text", "required": True},
        {"name": "gender", "label": "性别", "type": "select", "required": True, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "birth_date", "label": "出生日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "nation", "label": "民族", "type": "text", "required": True},
        {"name": "work_unit", "label": "工作单位/职业", "type": "text", "required": True},
        {"name": "address", "label": "住址", "type": "text", "required": True},
        {"name": "phone", "label": "联系电话", "type": "text", "required": True},
    ]},
    {"name": "plaintiff_info", "label": "被答辩人信息", "type": "object", "required": True, "properties": [
        {"name": "name", "label": "姓名", "type": "text", "required": True},
        {"name": "gender", "label": "性别", "type": "select", "required": True, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "birth_date", "label": "出生日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "nation", "label": "民族", "type": "text", "required": True},
        {"name": "work_unit", "label": "工作单位/职业", "type": "text", "required": True},
        {"name": "address", "label": "住址", "type": "text", "required": True},
        {"name": "phone", "label": "联系电话", "type": "text", "required": True},
    ]},
    {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
    {"name": "receive_date", "label": "收到起诉状日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    {"name": "objections", "label": "答辩请求", "type": "array", "required": True, "item": {"type": "text", "label": "答辩请求"}},
    {"name": "fact_and_reason", "label": "事实与理由", "type": "textarea", "required": True, "placeholder": "请详细陈述事实与理由"},
    {"name": "evidence_list", "label": "证据清单", "type": "array", "required": True, "item": {"type": "object", "properties": [
        {"name": "name", "label": "证据名称", "type": "text", "required": True},
        {"name": "content", "label": "证明内容", "type": "text", "required": True},
    ]}},
    {"name": "responding_court", "label": "受理法院", "type": "text", "required": True, "placeholder": "请输入受理法院全称"},
    {"name": "responding_date", "label": "答辩日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
]

# ==================== 法律援助通用字段 ====================
SHARED_AID_FIELDS = [
    {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
    {"name": "applicant_gender", "label": "申请人性别", "type": "select", "required": True, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
    {"name": "applicant_birth_date", "label": "出生日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    {"name": "applicant_nation", "label": "民族", "type": "text", "required": True},
    {"name": "applicant_id_no", "label": "身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
    {"name": "applicant_address", "label": "住址", "type": "text", "required": True, "placeholder": "请输入住址"},
    {"name": "applicant_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
    {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
    {"name": "case_description", "label": "案情简述", "type": "textarea", "required": True, "placeholder": "请简要描述案情"},
    {"name": "issuing_authority", "label": "出具机关/机构", "type": "text", "required": True, "placeholder": "请输入出具机关"},
    {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
]

# ==================== 律师辅助文书通用字段 ====================
SHARED_LAWYER_FIELDS = [
    {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
    {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
    {"name": "parties_info", "label": "当事人信息", "type": "textarea", "required": True, "placeholder": "请输入当事人信息"},
    {"name": "case_facts", "label": "案件事实", "type": "textarea", "required": True, "placeholder": "请详细描述案件事实"},
    {"name": "legal_analysis", "label": "法律分析", "type": "textarea", "required": True, "placeholder": "请输入法律分析"},
    {"name": "handling_opinion", "label": "处理意见", "type": "textarea", "required": True, "placeholder": "请输入处理意见"},
    {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人姓名"},
    {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
]


# ==================== 法律援助文书专用字段（FZ-001~032） ====================
_FZ_FIELDS = {
    "FZ-001": [  # 法律援助咨询登记表
        {"name": "consultant_name", "label": "咨询人姓名", "type": "text", "required": True, "placeholder": "请输入咨询人姓名"},
        {"name": "consultant_gender", "label": "咨询人性别", "type": "select", "required": False, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "consultant_id_no", "label": "身份证号", "type": "text", "required": False, "placeholder": "请输入身份证号"},
        {"name": "consultant_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
        {"name": "consultation_date", "label": "咨询日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "consultation_content", "label": "咨询内容", "type": "textarea", "required": True, "placeholder": "请详细描述咨询内容"},
        {"name": "consultant_signature", "label": "咨询人签名", "type": "text", "required": True, "placeholder": "请输入咨询人签名"},
        {"name": "recorder_signature", "label": "记录人签名", "type": "text", "required": True, "placeholder": "请输入记录人签名"},
    ],
    "FZ-002": [  # 法律援助申请表
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "applicant_gender", "label": "申请人性别", "type": "select", "required": True, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
        {"name": "applicant_id_no", "label": "身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "applicant_address", "label": "住址", "type": "text", "required": True, "placeholder": "请输入住址"},
        {"name": "applicant_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
        {"name": "economic_status", "label": "经济困难状况", "type": "textarea", "required": True, "placeholder": "请描述经济困难状况"},
        {"name": "case_brief", "label": "案情简述", "type": "textarea", "required": True, "placeholder": "请简要描述案情"},
        {"name": "application_reason", "label": "申请理由", "type": "textarea", "required": True, "placeholder": "请输入申请法律援助的理由"},
        {"name": "application_date", "label": "申请日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "applicant_signature", "label": "申请人签名", "type": "text", "required": True, "placeholder": "请输入申请人签名"},
    ],
    "FZ-003": [  # 授权委托书（法律援助用）
        {"name": "client_name", "label": "委托人姓名", "type": "text", "required": True, "placeholder": "请输入委托人姓名"},
        {"name": "client_id_no", "label": "委托人身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "agent_name", "label": "代理人姓名", "type": "text", "required": True, "placeholder": "请输入代理人姓名"},
        {"name": "agent_law_firm", "label": "代理人律所", "type": "text", "required": True, "placeholder": "请输入律师事务所"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_no", "label": "案号", "type": "text", "required": False, "placeholder": "请输入案号"},
        {"name": "authorization_scope", "label": "授权范围", "type": "text", "required": True, "placeholder": "请输入授权范围"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "client_signature", "label": "委托人签名", "type": "text", "required": True, "placeholder": "请输入委托人签名"},
    ],
    "FZ-004": [  # 经济困难状况说明表
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "applicant_id_no", "label": "身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "applicant_address", "label": "住址", "type": "text", "required": True, "placeholder": "请输入住址"},
        {"name": "family_income", "label": "家庭收入", "type": "text", "required": True, "placeholder": "请输入家庭年收入"},
        {"name": "family_expenses", "label": "家庭支出", "type": "text", "required": True, "placeholder": "请输入家庭年支出"},
        {"name": "property_status", "label": "财产状况", "type": "textarea", "required": True, "placeholder": "请描述财产状况"},
        {"name": "debt_status", "label": "债务状况", "type": "textarea", "required": True, "placeholder": "请描述债务状况"},
        {"name": "declaration", "label": "声明", "type": "textarea", "required": True, "placeholder": "请输入声明内容"},
        {"name": "applicant_signature", "label": "申请人签名", "type": "text", "required": True, "placeholder": "请输入申请人签名"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-005": [  # 法律援助申请材料接收凭证
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "receive_date", "label": "接收日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "materials_list", "label": "材料清单", "type": "array", "required": True, "item": {"type": "object", "properties": [
            {"name": "name", "label": "材料名称", "type": "text", "required": True},
            {"name": "quantity", "label": "份数", "type": "text", "required": False},
        ]}},
        {"name": "receiver_signature", "label": "接收人签名", "type": "text", "required": True, "placeholder": "请输入接收人签名"},
        {"name": "applicant_signature", "label": "申请人签名", "type": "text", "required": True, "placeholder": "请输入申请人签名"},
    ],
    "FZ-006": [  # 补充材料/说明通知书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "required_materials", "label": "需补充材料", "type": "array", "required": True, "item": {"type": "text", "label": "材料名称"}},
        {"name": "deadline", "label": "补正期限", "type": "text", "required": True, "placeholder": "请输入补正期限"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-007": [  # 法律援助协作函
        {"name": "to_authority", "label": "致机关/单位", "type": "text", "required": True, "placeholder": "请输入致函机关/单位"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_no", "label": "案号", "type": "text", "required": False, "placeholder": "请输入案号"},
        {"name": "collaboration_content", "label": "协作内容", "type": "textarea", "required": True, "placeholder": "请输入协作内容"},
        {"name": "contact_info", "label": "联系方式", "type": "text", "required": True, "placeholder": "请输入联系方式"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-008": [  # 法律援助审查表
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "applicant_id_no", "label": "身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "case_brief", "label": "案情简述", "type": "textarea", "required": True, "placeholder": "请简要描述案情"},
        {"name": "economic_status_review", "label": "经济状况审查", "type": "textarea", "required": True, "placeholder": "请输入经济状况审查意见"},
        {"name": "legal_review", "label": "法律审查", "type": "textarea", "required": True, "placeholder": "请输入法律审查意见"},
        {"name": "review_opinion", "label": "审查意见", "type": "textarea", "required": True, "placeholder": "请输入审查意见"},
        {"name": "reviewer_signature", "label": "审查人签名", "type": "text", "required": True, "placeholder": "请输入审查人签名"},
        {"name": "review_date", "label": "审查日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-009": [  # 给予法律援助决定书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "decision_reason", "label": "决定理由", "type": "textarea", "required": True, "placeholder": "请输入给予法律援助的理由"},
        {"name": "assistance_type", "label": "援助类型", "type": "select", "required": True, "options": [{"value": "刑事辩护", "label": "刑事辩护"}, {"value": "民事代理", "label": "民事代理"}, {"value": "行政代理", "label": "行政代理"}]},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-010": [  # 不予法律援助决定书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "rejection_reason", "label": "不予援助理由", "type": "textarea", "required": True, "placeholder": "请输入不予法律援助的理由"},
        {"name": "appeal_right", "label": "救济权利", "type": "textarea", "required": True, "placeholder": "请输入救济权利说明"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-011": [  # 指派通知书
        {"name": "to_law_firm", "label": "致律师事务所", "type": "text", "required": True, "placeholder": "请输入律师事务所名称"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "assigned_lawyer", "label": "指派律师", "type": "text", "required": True, "placeholder": "请输入指派律师姓名"},
        {"name": "deadline", "label": "办理期限", "type": "text", "required": True, "placeholder": "请输入办理期限"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-012": [  # 委托代理/辩护协议
        {"name": "client_name", "label": "委托人姓名", "type": "text", "required": True, "placeholder": "请输入委托人姓名"},
        {"name": "client_id_no", "label": "委托人身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "law_firm_name", "label": "律师事务所名称", "type": "text", "required": True, "placeholder": "请输入律所名称"},
        {"name": "law_firm_address", "label": "律所地址", "type": "text", "required": True, "placeholder": "请输入律所地址"},
        {"name": "assigned_lawyer", "label": "指派律师", "type": "text", "required": True, "placeholder": "请输入指派律师姓名"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "rights_obligations", "label": "权利义务", "type": "textarea", "required": True, "placeholder": "请输入权利义务条款"},
        {"name": "agreement_date", "label": "协议日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-013": [  # 法律援助公函
        {"name": "to_authority", "label": "致机关/单位", "type": "text", "required": True, "placeholder": "请输入致函机关/单位"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "assigned_lawyer", "label": "指派律师", "type": "text", "required": True, "placeholder": "请输入指派律师姓名"},
        {"name": "authorization_scope", "label": "授权范围", "type": "text", "required": True, "placeholder": "请输入授权范围"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-014": [  # 案件承办情况通报/报告记录
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "report_content", "label": "报告内容", "type": "textarea", "required": True, "placeholder": "请输入承办情况报告内容"},
        {"name": "reporter", "label": "报告人", "type": "text", "required": True, "placeholder": "请输入报告人姓名"},
        {"name": "report_date", "label": "报告日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "receiver_signature", "label": "接收人签名", "type": "text", "required": True, "placeholder": "请输入接收人签名"},
    ],
    "FZ-015": [  # 法律援助机构介绍信
        {"name": "to_authority", "label": "致机关/单位", "type": "text", "required": True, "placeholder": "请输入致函机关/单位"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "introduced_person", "label": "被介绍人", "type": "text", "required": True, "placeholder": "请输入被介绍人姓名"},
        {"name": "purpose", "label": "目的", "type": "text", "required": True, "placeholder": "请输入介绍目的"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-016": [  # 更换法律援助人员申请表
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "current_lawyer", "label": "当前承办律师", "type": "text", "required": True, "placeholder": "请输入当前承办律师姓名"},
        {"name": "replacement_reason", "label": "更换原因", "type": "textarea", "required": True, "placeholder": "请输入更换原因"},
        {"name": "proposed_lawyer", "label": "拟更换律师", "type": "text", "required": False, "placeholder": "请输入拟更换律师姓名"},
        {"name": "applicant_signature", "label": "申请人签名", "type": "text", "required": True, "placeholder": "请输入申请人签名"},
        {"name": "application_date", "label": "申请日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-017": [  # 更换法律援助人员通知书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "original_lawyer", "label": "原承办律师", "type": "text", "required": True, "placeholder": "请输入原承办律师姓名"},
        {"name": "new_lawyer", "label": "新承办律师", "type": "text", "required": True, "placeholder": "请输入新承办律师姓名"},
        {"name": "reason", "label": "更换原因", "type": "textarea", "required": True, "placeholder": "请输入更换原因"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-018": [  # 终止法律援助决定书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "termination_reason", "label": "终止原因", "type": "textarea", "required": True, "placeholder": "请输入终止法律援助的原因"},
        {"name": "appeal_right", "label": "救济权利", "type": "textarea", "required": True, "placeholder": "请输入救济权利说明"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-019": [  # 终止法律援助公函
        {"name": "to_authority", "label": "致机关/单位", "type": "text", "required": True, "placeholder": "请输入致函机关/单位"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "termination_reason", "label": "终止原因", "type": "textarea", "required": True, "placeholder": "请输入终止法律援助的原因"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-020": [  # 法律援助异议审查决定书
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "objection_content", "label": "异议内容", "type": "textarea", "required": True, "placeholder": "请输入异议内容"},
        {"name": "review_result", "label": "审查结果", "type": "textarea", "required": True, "placeholder": "请输入审查结果"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-021": [  # 结案报告表
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "handling_process", "label": "办理过程", "type": "textarea", "required": True, "placeholder": "请描述办理过程"},
        {"name": "handling_result", "label": "办理结果", "type": "textarea", "required": True, "placeholder": "请描述办理结果"},
        {"name": "expense_settlement", "label": "费用结算", "type": "text", "required": False, "placeholder": "请输入费用结算情况"},
        {"name": "handler_signature", "label": "承办人签名", "type": "text", "required": True, "placeholder": "请输入承办人签名"},
        {"name": "closing_date", "label": "结案日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-022": [  # 送达回证
        {"name": "document_name", "label": "文书名称", "type": "text", "required": True, "placeholder": "请输入文书名称"},
        {"name": "receiver_name", "label": "接收人姓名", "type": "text", "required": True, "placeholder": "请输入接收人姓名"},
        {"name": "receiver_address", "label": "接收人地址", "type": "text", "required": True, "placeholder": "请输入接收人地址"},
        {"name": "delivery_date", "label": "送达日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "receiver_signature", "label": "接收人签名", "type": "text", "required": True, "placeholder": "请输入接收人签名"},
        {"name": "remarks", "label": "备注", "type": "text", "required": False, "placeholder": "请输入备注"},
    ],
    "FZ-023": [  # 法律帮助申请表
        {"name": "applicant_name", "label": "申请人姓名", "type": "text", "required": True, "placeholder": "请输入申请人姓名"},
        {"name": "applicant_id_no", "label": "身份证号", "type": "text", "required": True, "placeholder": "请输入身份证号"},
        {"name": "case_brief", "label": "案情简述", "type": "textarea", "required": True, "placeholder": "请简要描述案情"},
        {"name": "help_content", "label": "申请帮助内容", "type": "textarea", "required": True, "placeholder": "请输入申请法律帮助的内容"},
        {"name": "application_date", "label": "申请日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "applicant_signature", "label": "申请人签名", "type": "text", "required": True, "placeholder": "请输入申请人签名"},
    ],
    "FZ-024": [  # 值班律师提供法律帮助通知书（公安机关）
        {"name": "to_authority", "label": "致公安机关", "type": "text", "required": True, "placeholder": "请输入公安机关名称"},
        {"name": "suspect_name", "label": "犯罪嫌疑人姓名", "type": "text", "required": True, "placeholder": "请输入犯罪嫌疑人姓名"},
        {"name": "case_cause", "label": "涉嫌罪名/案由", "type": "text", "required": True, "placeholder": "请输入涉嫌罪名"},
        {"name": "assigned_lawyer", "label": "值班律师", "type": "text", "required": True, "placeholder": "请输入值班律师姓名"},
        {"name": "notification_date", "label": "通知日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-025": [  # 值班律师提供法律帮助通知书（国家安全机关）
        {"name": "to_authority", "label": "致国家安全机关", "type": "text", "required": True, "placeholder": "请输入国家安全机关名称"},
        {"name": "suspect_name", "label": "犯罪嫌疑人姓名", "type": "text", "required": True, "placeholder": "请输入犯罪嫌疑人姓名"},
        {"name": "case_cause", "label": "涉嫌罪名/案由", "type": "text", "required": True, "placeholder": "请输入涉嫌罪名"},
        {"name": "assigned_lawyer", "label": "值班律师", "type": "text", "required": True, "placeholder": "请输入值班律师姓名"},
        {"name": "notification_date", "label": "通知日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-026": [  # 值班律师提供法律帮助通知书（人民检察院）
        {"name": "to_authority", "label": "致人民检察院", "type": "text", "required": True, "placeholder": "请输入人民检察院名称"},
        {"name": "suspect_name", "label": "犯罪嫌疑人姓名", "type": "text", "required": True, "placeholder": "请输入犯罪嫌疑人姓名"},
        {"name": "case_cause", "label": "涉嫌罪名/案由", "type": "text", "required": True, "placeholder": "请输入涉嫌罪名"},
        {"name": "assigned_lawyer", "label": "值班律师", "type": "text", "required": True, "placeholder": "请输入值班律师姓名"},
        {"name": "notification_date", "label": "通知日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-027": [  # 值班律师提供法律帮助通知书（人民法院）
        {"name": "to_authority", "label": "致人民法院", "type": "text", "required": True, "placeholder": "请输入人民法院名称"},
        {"name": "suspect_name", "label": "犯罪嫌疑人/被告人姓名", "type": "text", "required": True, "placeholder": "请输入犯罪嫌疑人/被告人姓名"},
        {"name": "case_cause", "label": "涉嫌罪名/案由", "type": "text", "required": True, "placeholder": "请输入涉嫌罪名"},
        {"name": "assigned_lawyer", "label": "值班律师", "type": "text", "required": True, "placeholder": "请输入值班律师姓名"},
        {"name": "notification_date", "label": "通知日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-028": [  # 值班律师提供法律帮助情况登记表
        {"name": "lawyer_name", "label": "值班律师姓名", "type": "text", "required": True, "placeholder": "请输入律师姓名"},
        {"name": "help_date", "label": "帮助日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "help_content", "label": "帮助内容", "type": "textarea", "required": True, "placeholder": "请描述法律帮助内容"},
        {"name": "help_result", "label": "帮助结果", "type": "textarea", "required": True, "placeholder": "请描述帮助结果"},
        {"name": "lawyer_signature", "label": "律师签名", "type": "text", "required": True, "placeholder": "请输入律师签名"},
    ],
    "FZ-029": [  # 值班律师法律帮助工作台账
        {"name": "statistical_period", "label": "统计期间", "type": "text", "required": True, "placeholder": "请输入统计期间"},
        {"name": "total_help_count", "label": "帮助总人次", "type": "text", "required": True, "placeholder": "请输入帮助总人次"},
        {"name": "criminal_count", "label": "刑事帮助人次", "type": "text", "required": False, "placeholder": "请输入刑事帮助人次"},
        {"name": "civil_count", "label": "民事帮助人次", "type": "text", "required": False, "placeholder": "请输入民事帮助人次"},
        {"name": "administrative_count", "label": "行政帮助人次", "type": "text", "required": False, "placeholder": "请输入行政帮助人次"},
        {"name": "recorder", "label": "记录人", "type": "text", "required": True, "placeholder": "请输入记录人"},
        {"name": "record_date", "label": "记录日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-030": [  # 庭审旁听情况记录表
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "court", "label": "审理法院", "type": "text", "required": True, "placeholder": "请输入审理法院"},
        {"name": "hearing_date", "label": "开庭日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "performance_evaluation", "label": "出庭表现评价", "type": "textarea", "required": True, "placeholder": "请评价出庭表现"},
        {"name": "observer_signature", "label": "旁听人签名", "type": "text", "required": True, "placeholder": "请输入旁听人签名"},
        {"name": "record_date", "label": "记录日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-031": [  # 征询办案机关意见函
        {"name": "to_authority", "label": "致办案机关", "type": "text", "required": True, "placeholder": "请输入办案机关名称"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "consultation_content", "label": "征询内容", "type": "textarea", "required": True, "placeholder": "请输入征询内容"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-032": [  # 受援人回访记录表
        {"name": "recipient_name", "label": "受援人姓名", "type": "text", "required": True, "placeholder": "请输入受援人姓名"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "service_evaluation", "label": "服务评价", "type": "textarea", "required": True, "placeholder": "请输入对法律援助服务的评价"},
        {"name": "suggestions", "label": "建议", "type": "textarea", "required": False, "placeholder": "请输入建议"},
        {"name": "interviewer_signature", "label": "回访人签名", "type": "text", "required": True, "placeholder": "请输入回访人签名"},
        {"name": "interview_date", "label": "回访日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
}

# ==================== 律师辅助文书专用字段（FZ-033~044） ====================
_LAWYER_FIELDS = {
    "FZ-033": [  # 类案检索报告
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "retriever", "label": "检索人", "type": "text", "required": True, "placeholder": "请输入检索人姓名"},
        {"name": "retrieval_date", "label": "检索日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "platforms", "label": "检索平台", "type": "text", "required": True, "placeholder": "请输入检索平台"},
        {"name": "key_points", "label": "裁判要点", "type": "array", "required": True, "item": {"type": "text", "label": "裁判要点"}},
        {"name": "dispute_focus", "label": "争议焦点", "type": "textarea", "required": True, "placeholder": "请输入争议焦点"},
        {"name": "reference_analysis", "label": "参照分析", "type": "textarea", "required": True, "placeholder": "请输入参照分析"},
        {"name": "conclusion", "label": "结论", "type": "textarea", "required": True, "placeholder": "请输入检索结论"},
    ],
    "FZ-034": [  # 案件汇报提纲
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "case_basic_info", "label": "案件基本情况", "type": "textarea", "required": True, "placeholder": "请输入案件基本情况"},
        {"name": "evidence_analysis", "label": "证据分析", "type": "textarea", "required": True, "placeholder": "请输入证据分析"},
        {"name": "legal_application", "label": "法律适用", "type": "textarea", "required": True, "placeholder": "请输入法律适用分析"},
        {"name": "handling_opinions", "label": "处理意见", "type": "textarea", "required": True, "placeholder": "请输入处理意见"},
        {"name": "risks", "label": "风险提示", "type": "textarea", "required": False, "placeholder": "请输入风险提示"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-035": [  # 类案批量侦查数据分析报告
        {"name": "survey_overview", "label": "调研概况", "type": "textarea", "required": True, "placeholder": "请输入调研概况"},
        {"name": "basic_data", "label": "基础数据", "type": "textarea", "required": True, "placeholder": "请输入基础数据"},
        {"name": "case_features", "label": "案件特征", "type": "textarea", "required": True, "placeholder": "请输入案件特征"},
        {"name": "problems", "label": "突出问题", "type": "array", "required": True, "item": {"type": "text", "label": "问题"}},
        {"name": "causes", "label": "成因分析", "type": "textarea", "required": True, "placeholder": "请输入成因分析"},
        {"name": "suggestions", "label": "整改建议", "type": "textarea", "required": True, "placeholder": "请输入整改建议"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-036": [  # 专项侦查工作方案
        {"name": "case_brief", "label": "简要案情", "type": "textarea", "required": True, "placeholder": "请输入简要案情"},
        {"name": "case_analysis", "label": "案情分析", "type": "textarea", "required": True, "placeholder": "请输入案情分析"},
        {"name": "organization", "label": "组织分工", "type": "textarea", "required": True, "placeholder": "请输入组织分工"},
        {"name": "measures", "label": "侦查措施", "type": "array", "required": True, "item": {"type": "text", "label": "侦查措施"}},
        {"name": "timeline", "label": "时限安排", "type": "text", "required": True, "placeholder": "请输入时限安排"},
        {"name": "risk_prevention", "label": "风险防控", "type": "textarea", "required": False, "placeholder": "请输入风险防控措施"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-037": [  # 审查报告（捕诉合一）
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
        {"name": "litigation_process", "label": "诉讼经过", "type": "textarea", "required": True, "placeholder": "请输入诉讼经过"},
        {"name": "parties_info", "label": "当事人信息", "type": "textarea", "required": True, "placeholder": "请输入当事人信息"},
        {"name": "case_occurrence", "label": "案发经过", "type": "textarea", "required": True, "placeholder": "请输入案发经过"},
        {"name": "evidence_review", "label": "证据审查", "type": "textarea", "required": True, "placeholder": "请输入证据审查意见"},
        {"name": "facts_found", "label": "查明事实", "type": "textarea", "required": True, "placeholder": "请输入查明事实"},
        {"name": "handling_opinion", "label": "处理意见", "type": "textarea", "required": True, "placeholder": "请输入处理意见"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-038": [  # 书面质证意见书
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "evidence_name", "label": "质证证据名称", "type": "text", "required": True, "placeholder": "请输入证据名称"},
        {"name": "authenticity_objection", "label": "真实性异议", "type": "textarea", "required": True, "placeholder": "请输入真实性异议"},
        {"name": "legality_objection", "label": "合法性异议", "type": "textarea", "required": True, "placeholder": "请输入合法性异议"},
        {"name": "relevance_objection", "label": "关联性异议", "type": "textarea", "required": True, "placeholder": "请输入关联性异议"},
        {"name": "purpose_objection", "label": "证明目的异议", "type": "textarea", "required": True, "placeholder": "请输入证明目的异议"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-039": [  # 辩护词
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "defendant_name", "label": "被告人姓名", "type": "text", "required": True, "placeholder": "请输入被告人姓名"},
        {"name": "case_cause", "label": "指控罪名", "type": "text", "required": True, "placeholder": "请输入指控罪名"},
        {"name": "defense_opinions", "label": "辩护意见", "type": "array", "required": True, "item": {"type": "object", "properties": [
            {"name": "point", "label": "辩护要点", "type": "text", "required": True},
            {"name": "detail", "label": "详细论述", "type": "textarea", "required": True},
        ]}},
        {"name": "conclusion", "label": "结论", "type": "textarea", "required": True, "placeholder": "请输入辩护结论"},
        {"name": "drafter", "label": "辩护人", "type": "text", "required": True, "placeholder": "请输入辩护人"},
        {"name": "draft_date", "label": "日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-040": [  # 公诉意见书
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "defendant_name", "label": "被告人姓名", "type": "text", "required": True, "placeholder": "请输入被告人姓名"},
        {"name": "case_cause", "label": "指控罪名", "type": "text", "required": True, "placeholder": "请输入指控罪名"},
        {"name": "court_task", "label": "出庭任务", "type": "text", "required": True, "placeholder": "请输入出庭任务"},
        {"name": "investigation_result", "label": "法庭调查结果", "type": "textarea", "required": True, "placeholder": "请输入法庭调查结果"},
        {"name": "sentencing_suggestion", "label": "量刑建议", "type": "textarea", "required": True, "placeholder": "请输入量刑建议"},
        {"name": "drafter", "label": "公诉人", "type": "text", "required": True, "placeholder": "请输入公诉人"},
        {"name": "draft_date", "label": "日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-041": [  # 不起诉理由说明书
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "suspect_name", "label": "犯罪嫌疑人姓名", "type": "text", "required": True, "placeholder": "请输入犯罪嫌疑人姓名"},
        {"name": "case_cause", "label": "涉嫌罪名", "type": "text", "required": True, "placeholder": "请输入涉嫌罪名"},
        {"name": "case_source", "label": "案件来源", "type": "text", "required": True, "placeholder": "请输入案件来源"},
        {"name": "investigation_facts", "label": "侦查机关认定事实", "type": "textarea", "required": True, "placeholder": "请输入侦查机关认定事实"},
        {"name": "review_facts", "label": "审查查明事实", "type": "textarea", "required": True, "placeholder": "请输入审查查明事实"},
        {"name": "non_prosecution_reason", "label": "不起诉理由", "type": "textarea", "required": True, "placeholder": "请输入不起诉理由"},
        {"name": "legal_basis", "label": "法律依据", "type": "textarea", "required": True, "placeholder": "请输入法律依据"},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-042": [  # 司法建议书
        {"name": "to_unit", "label": "主送单位", "type": "text", "required": True, "placeholder": "请输入主送单位"},
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "problem_found", "label": "发现问题", "type": "textarea", "required": True, "placeholder": "请输入发现的问题"},
        {"name": "facts", "label": "事实依据", "type": "textarea", "required": True, "placeholder": "请输入事实依据"},
        {"name": "legal_basis", "label": "法律依据", "type": "textarea", "required": True, "placeholder": "请输入法律依据"},
        {"name": "suggestions", "label": "建议内容", "type": "textarea", "required": True, "placeholder": "请输入建议内容"},
        {"name": "feedback_requirement", "label": "反馈要求", "type": "text", "required": False, "placeholder": "请输入反馈要求"},
        {"name": "issuing_authority", "label": "出具机关", "type": "text", "required": True, "placeholder": "请输入出具机关"},
        {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
    "FZ-043": [  # 律师会见笔录
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "interviewee_name", "label": "被会见人姓名", "type": "text", "required": True, "placeholder": "请输入被会见人姓名"},
        {"name": "meeting_time", "label": "会见时间", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        {"name": "location", "label": "会见地点", "type": "text", "required": True, "placeholder": "请输入会见地点"},
        {"name": "meeting_content", "label": "会见内容", "type": "textarea", "required": True, "placeholder": "请详细记录会见内容"},
        {"name": "lawyer_signature", "label": "律师签名", "type": "text", "required": True, "placeholder": "请输入律师签名"},
        {"name": "interviewee_signature", "label": "被会见人签名", "type": "text", "required": True, "placeholder": "请输入被会见人签名"},
    ],
    "FZ-044": [  # 庭审发问提纲
        {"name": "case_no", "label": "案号", "type": "text", "required": True, "placeholder": "请输入案号"},
        {"name": "question_object", "label": "发问对象", "type": "text", "required": True, "placeholder": "请输入发问对象"},
        {"name": "questions", "label": "问题清单", "type": "array", "required": True, "item": {"type": "object", "properties": [
            {"name": "order", "label": "序号", "type": "text", "required": True},
            {"name": "content", "label": "问题内容", "type": "text", "required": True},
            {"name": "purpose", "label": "发问目的", "type": "text", "required": False},
        ]}},
        {"name": "drafter", "label": "拟稿人", "type": "text", "required": True, "placeholder": "请输入拟稿人"},
        {"name": "draft_date", "label": "拟稿日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
    ],
}


def _resolve_fields(template):
    """解析模板字段：引用共享字段集或返回自定义字段"""
    fields = template.get("fields", [])
    if isinstance(fields, list):
        return fields
    # 共享字段引用
    shared_map = {
        "__shared_complaint__": SHARED_COMPLAINT_FIELDS,
        "__shared_defense__": SHARED_DEFENSE_FIELDS,
        "__shared_aid_form__": SHARED_AID_FIELDS,
        "__shared_lawyer_form__": SHARED_LAWYER_FIELDS,
    }
    return shared_map.get(fields, [])


def _make_ay_template(tid, name, cause, scene, is_complaint=True):
    """快速创建案由专项文书"""
    return {
        "id": tid, "name": name, "category": "civil", "sub_category": "civil_special",
        "source": "最高人民法院2024版", "scene": scene,
        "fields": "__shared_complaint__" if is_complaint else "__shared_defense__",
        "case_cause_default": cause,
    }


def _make_fz_template(tid, name, scene, sub_cat):
    """快速创建法律援助文书"""
    return {
        "id": tid, "name": name, "category": "legal_aid", "sub_category": sub_cat,
        "source": "司法部2024版", "scene": scene,
        "fields": _FZ_FIELDS.get(tid, SHARED_AID_FIELDS),
    }


def _make_fz_lawyer(tid, name, scene):
    """快速创建律师辅助文书"""
    return {
        "id": tid, "name": name, "category": "lawyer", "sub_category": "lawyer_aux",
        "source": "律师办案规范", "scene": scene,
        "fields": _LAWYER_FIELDS.get(tid, SHARED_LAWYER_FIELDS),
    }


# ==================== 完整模板列表（90份） ====================
TEMPLATES = [
    # ── 通用诉讼文书 MS-TY-001~006 ──
    {
        "id": "MS-TY-001", "name": "法定代表人身份证明书", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "法人诉讼时证明法定代表人身份",
        "fields": [
            {"name": "unit_full_name", "label": "单位全称", "type": "text", "required": True, "placeholder": "请输入单位全称"},
            {"name": "legal_representative_name", "label": "法定代表人姓名", "type": "text", "required": True, "placeholder": "请输入法定代表人姓名"},
            {"name": "legal_representative_position", "label": "职务", "type": "text", "required": True, "placeholder": "请输入职务"},
            {"name": "contact_address", "label": "联系地址", "type": "text", "required": True, "placeholder": "请输入联系地址"},
            {"name": "contact_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },
    {
        "id": "MS-TY-002", "name": "主要负责人身份证明书", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "其他组织诉讼时证明主要负责人身份",
        "fields": [
            {"name": "unit_full_name", "label": "单位全称", "type": "text", "required": True, "placeholder": "请输入单位全称"},
            {"name": "main_responsible_name", "label": "主要负责人姓名", "type": "text", "required": True, "placeholder": "请输入主要负责人姓名"},
            {"name": "main_responsible_position", "label": "职务", "type": "text", "required": True, "placeholder": "请输入职务"},
            {"name": "contact_address", "label": "联系地址", "type": "text", "required": True, "placeholder": "请输入联系地址"},
            {"name": "contact_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },
    {
        "id": "MS-TY-003", "name": "共同诉讼代表人推选书", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "共同诉讼当事人推选诉讼代表人",
        "fields": [
            {"name": "representative1_name", "label": "代表人1姓名", "type": "text", "required": True, "placeholder": "请输入代表人1姓名"},
            {"name": "representative2_name", "label": "代表人2姓名", "type": "text", "required": True, "placeholder": "请输入代表人2姓名"},
            {"name": "case_parties", "label": "对方当事人", "type": "text", "required": True, "placeholder": "请输入对方当事人"},
            {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
            {"name": "representative_address", "label": "代表人联系地址", "type": "text", "required": True, "placeholder": "请输入代表人联系地址"},
            {"name": "representative_phone", "label": "代表人联系电话", "type": "text", "required": True, "placeholder": "请输入代表人联系电话"},
            {"name": "other_representatives", "label": "其他代表人（可选）", "type": "array", "required": False, "item": {"type": "text", "label": "代表人姓名"}},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },
    {
        "id": "MS-TY-004", "name": "授权委托书（自然人用）", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "自然人委托他人代为诉讼",
        "fields": [
            {"name": "client_name", "label": "委托人姓名", "type": "text", "required": True, "placeholder": "请输入委托人姓名"},
            {"name": "client_gender", "label": "委托人性别", "type": "select", "required": True, "options": [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]},
            {"name": "client_birth_date", "label": "委托人出生日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
            {"name": "client_nation", "label": "委托人民族", "type": "text", "required": True, "placeholder": "请输入民族"},
            {"name": "client_work_unit", "label": "工作单位/职业", "type": "text", "required": True, "placeholder": "请输入工作单位或职业"},
            {"name": "client_address", "label": "委托人住址", "type": "text", "required": True, "placeholder": "请输入住址"},
            {"name": "client_phone", "label": "委托人联系方式", "type": "text", "required": True, "placeholder": "请输入联系方式"},
            {"name": "agent1_name", "label": "受委托人1姓名", "type": "text", "required": True, "placeholder": "请输入受委托人1姓名"},
            {"name": "agent1_unit", "label": "受委托人1律所/单位", "type": "text", "required": True, "placeholder": "请输入受委托人1所在律所或单位"},
            {"name": "agent1_position", "label": "受委托人1职务", "type": "text", "required": True, "placeholder": "请输入受委托人1职务"},
            {"name": "agent1_phone", "label": "受委托人1联系方式", "type": "text", "required": True, "placeholder": "请输入受委托人1联系方式"},
            {"name": "case_parties", "label": "对方当事人", "type": "text", "required": True, "placeholder": "请输入对方当事人"},
            {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
            {"name": "is_special_authorization", "label": "代理权限", "type": "radio", "required": True, "options": [{"value": False, "label": "一般授权"}, {"value": True, "label": "特别授权"}]},
            {"name": "special_authorizations", "label": "特别授权内容", "type": "checkbox", "required": False,
             "show_when": {"field": "is_special_authorization", "value": True},
             "options": [
                {"value": "代为承认、放弃、变更诉讼请求", "label": "代为承认、放弃、变更诉讼请求"},
                {"value": "代为进行和解", "label": "代为进行和解"},
                {"value": "代为提起反诉或者上诉", "label": "代为提起反诉或者上诉"},
                {"value": "代为签收法律文书", "label": "代为签收法律文书"},
             ]},
            {"name": "agent2_name", "label": "受委托人2姓名（可选）", "type": "text", "required": False, "placeholder": "请输入受委托人2姓名"},
            {"name": "agent2_relation", "label": "受委托人2与委托人关系", "type": "text", "required": False, "placeholder": "请输入与委托人关系"},
            {"name": "agent2_address", "label": "受委托人2住址", "type": "text", "required": False, "placeholder": "请输入受委托人2住址"},
            {"name": "agent2_phone", "label": "受委托人2联系方式", "type": "text", "required": False, "placeholder": "请输入受委托人2联系方式"},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },
    {
        "id": "MS-TY-005", "name": "授权委托书（法人/其他组织用）", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "法人或其他组织委托他人代为诉讼",
        "fields": [
            {"name": "client_unit_full_name", "label": "委托单位全称", "type": "text", "required": True, "placeholder": "请输入委托单位全称"},
            {"name": "client_unit_address", "label": "单位地址", "type": "text", "required": True, "placeholder": "请输入单位地址"},
            {"name": "legal_representative_name", "label": "法定代表人/主要负责人姓名", "type": "text", "required": True, "placeholder": "请输入法定代表人或主要负责人姓名"},
            {"name": "legal_representative_position", "label": "职务", "type": "text", "required": True, "placeholder": "请输入职务"},
            {"name": "legal_representative_phone", "label": "联系电话", "type": "text", "required": True, "placeholder": "请输入联系电话"},
            {"name": "agent1_name", "label": "受委托人1姓名", "type": "text", "required": True, "placeholder": "请输入受委托人1姓名"},
            {"name": "agent1_unit", "label": "受委托人1单位", "type": "text", "required": True, "placeholder": "请输入受委托人1单位"},
            {"name": "agent1_position", "label": "受委托人1职务", "type": "text", "required": True, "placeholder": "请输入受委托人1职务"},
            {"name": "agent1_phone", "label": "受委托人1联系电话", "type": "text", "required": True, "placeholder": "请输入受委托人1联系电话"},
            {"name": "case_parties", "label": "对方当事人", "type": "text", "required": True, "placeholder": "请输入对方当事人"},
            {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
            {"name": "is_special_authorization", "label": "代理权限", "type": "radio", "required": True, "options": [{"value": False, "label": "一般授权"}, {"value": True, "label": "特别授权"}]},
            {"name": "special_authorizations", "label": "特别授权内容", "type": "checkbox", "required": False,
             "show_when": {"field": "is_special_authorization", "value": True},
             "options": [
                {"value": "代为承认、放弃、变更诉讼请求", "label": "代为承认、放弃、变更诉讼请求"},
                {"value": "代为进行和解", "label": "代为进行和解"},
                {"value": "代为提起反诉或者上诉", "label": "代为提起反诉或者上诉"},
                {"value": "代为签收法律文书", "label": "代为签收法律文书"},
             ]},
            {"name": "agent2_name", "label": "受委托人2姓名（可选）", "type": "text", "required": False, "placeholder": "请输入受委托人2姓名"},
            {"name": "agent2_unit", "label": "受委托人2单位", "type": "text", "required": False, "placeholder": "请输入受委托人2单位"},
            {"name": "agent2_position", "label": "受委托人2职务", "type": "text", "required": False, "placeholder": "请输入受委托人2职务"},
            {"name": "agent2_phone", "label": "受委托人2联系电话", "type": "text", "required": False, "placeholder": "请输入受委托人2联系电话"},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },
    {
        "id": "MS-TY-006", "name": "推荐函", "category": "civil", "sub_category": "civil_general",
        "source": "最高人民法院2024版", "scene": "社区/单位推荐诉讼代理人",
        "fields": [
            {"name": "accepting_court_full_name", "label": "受理法院全称", "type": "text", "required": True, "placeholder": "请输入受理法院全称"},
            {"name": "case_parties", "label": "案件当事人", "type": "text", "required": True, "placeholder": "请输入案件当事人"},
            {"name": "case_cause", "label": "案由", "type": "text", "required": True, "placeholder": "请输入案由"},
            {"name": "recommended_person_name", "label": "被推荐人姓名", "type": "text", "required": True, "placeholder": "请输入被推荐人姓名"},
            {"name": "authorization_scope", "label": "代理权限", "type": "text", "required": True, "placeholder": "请输入代理权限"},
            {"name": "issue_date", "label": "出具日期", "type": "date", "required": True, "format": "yyyy年MM月dd日"},
        ],
    },

    # ── 案由专项文书 MS-AY-001~022 ──
    _make_ay_template("MS-AY-001", "民事起诉状（买卖合同纠纷）", "买卖合同纠纷", "买卖合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-002", "民事答辩状（买卖合同纠纷）", "买卖合同纠纷", "买卖合同纠纷案件答辩", False),
    _make_ay_template("MS-AY-003", "民事起诉状（金融借款合同纠纷）", "金融借款合同纠纷", "金融借款合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-004", "民事答辩状（金融借款合同纠纷）", "金融借款合同纠纷", "金融借款合同纠纷案件答辩", False),
    _make_ay_template("MS-AY-005", "民事起诉状（物业服务合同纠纷）", "物业服务合同纠纷", "物业服务合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-006", "民事答辩状（物业服务合同纠纷）", "物业服务合同纠纷", "物业服务合同纠纷案件答辩", False),
    _make_ay_template("MS-AY-007", "民事起诉状（银行信用卡纠纷）", "银行信用卡纠纷", "银行信用卡纠纷案件起诉", True),
    _make_ay_template("MS-AY-008", "民事答辩状（银行信用卡纠纷）", "银行信用卡纠纷", "银行信用卡纠纷案件答辩", False),
    _make_ay_template("MS-AY-009", "民事起诉状（机动车交通事故责任纠纷）", "机动车交通事故责任纠纷", "机动车交通事故责任纠纷案件起诉", True),
    _make_ay_template("MS-AY-010", "民事答辩状（机动车交通事故责任纠纷）", "机动车交通事故责任纠纷", "机动车交通事故责任纠纷案件答辩", False),
    _make_ay_template("MS-AY-011", "民事起诉状（劳动争议纠纷）", "劳动争议纠纷", "劳动争议纠纷案件起诉", True),
    _make_ay_template("MS-AY-012", "民事答辩状（劳动争议纠纷）", "劳动争议纠纷", "劳动争议纠纷案件答辩", False),
    _make_ay_template("MS-AY-013", "民事起诉状（融资租赁合同纠纷）", "融资租赁合同纠纷", "融资租赁合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-014", "民事答辩状（融资租赁合同纠纷）", "融资租赁合同纠纷", "融资租赁合同纠纷案件答辩", False),
    _make_ay_template("MS-AY-015", "民事起诉状（保证保险合同纠纷）", "保证保险合同纠纷", "保证保险合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-016", "民事答辩状（保证保险合同纠纷）", "保证保险合同纠纷", "保证保险合同纠纷案件答辩", False),
    _make_ay_template("MS-AY-017", "民事起诉状（证券虚假陈述责任纠纷）", "证券虚假陈述责任纠纷", "证券虚假陈述责任纠纷案件起诉", True),
    _make_ay_template("MS-AY-018", "民事答辩状（证券虚假陈述责任纠纷）", "证券虚假陈述责任纠纷", "证券虚假陈述责任纠纷案件答辩", False),
    _make_ay_template("MS-AY-019", "民事起诉状（民间借贷纠纷）", "民间借贷纠纷", "民间借贷纠纷案件起诉", True),
    _make_ay_template("MS-AY-020", "民事答辩状（民间借贷纠纷）", "民间借贷纠纷", "民间借贷纠纷案件答辩", False),
    _make_ay_template("MS-AY-021", "民事起诉状（建设工程施工合同纠纷）", "建设工程施工合同纠纷", "建设工程施工合同纠纷案件起诉", True),
    _make_ay_template("MS-AY-022", "民事答辩状（建设工程施工合同纠纷）", "建设工程施工合同纠纷", "建设工程施工合同纠纷案件答辩", False),

    # ── 法律援助申请受理类 FZ-001~008 ──
    _make_fz_template("FZ-001", "法律援助咨询登记表", "法律援助咨询登记", "aid_apply"),
    _make_fz_template("FZ-002", "法律援助申请表", "法律援助申请", "aid_apply"),
    _make_fz_template("FZ-003", "授权委托书（法律援助用）", "法律援助授权委托", "aid_apply"),
    _make_fz_template("FZ-004", "经济困难状况说明表", "经济困难状况说明", "aid_apply"),
    _make_fz_template("FZ-005", "法律援助申请材料接收凭证", "法律援助申请材料接收", "aid_apply"),
    _make_fz_template("FZ-006", "补充材料/说明通知书", "补充材料通知", "aid_apply"),
    _make_fz_template("FZ-007", "法律援助协作函", "法律援助协作", "aid_apply"),
    _make_fz_template("FZ-008", "法律援助审查表", "法律援助审查", "aid_apply"),

    # ── 法律援助决定指派类 FZ-009~013 ──
    _make_fz_template("FZ-009", "给予法律援助决定书", "给予法律援助决定", "aid_decision"),
    _make_fz_template("FZ-010", "不予法律援助决定书", "不予法律援助决定", "aid_decision"),
    _make_fz_template("FZ-011", "指派通知书", "法律援助指派通知", "aid_decision"),
    _make_fz_template("FZ-012", "委托代理/辩护协议", "委托代理或辩护协议", "aid_decision"),
    _make_fz_template("FZ-013", "法律援助公函", "法律援助公函", "aid_decision"),

    # ── 法律援助办案管理类 FZ-014~022 ──
    _make_fz_template("FZ-014", "法律援助案件承办情况通报/报告记录", "案件承办情况通报", "aid_manage"),
    _make_fz_template("FZ-015", "法律援助机构介绍信", "法律援助机构介绍", "aid_manage"),
    _make_fz_template("FZ-016", "更换法律援助人员申请表", "更换法律援助人员申请", "aid_manage"),
    _make_fz_template("FZ-017", "更换法律援助人员通知书", "更换法律援助人员通知", "aid_manage"),
    _make_fz_template("FZ-018", "终止法律援助决定书", "终止法律援助决定", "aid_manage"),
    _make_fz_template("FZ-019", "终止法律援助公函", "终止法律援助公函", "aid_manage"),
    _make_fz_template("FZ-020", "法律援助异议审查决定书", "法律援助异议审查决定", "aid_manage"),
    _make_fz_template("FZ-021", "结案报告表", "法律援助结案报告", "aid_manage"),
    _make_fz_template("FZ-022", "送达回证", "法律援助送达回证", "aid_manage"),

    # ── 法律援助值班律师类 FZ-023~029 ──
    _make_fz_template("FZ-023", "法律帮助申请表", "法律帮助申请", "aid_duty"),
    _make_fz_template("FZ-024", "值班律师提供法律帮助通知书（公安机关）", "值班律师法律帮助通知（公安机关）", "aid_duty"),
    _make_fz_template("FZ-025", "值班律师提供法律帮助通知书（国家安全机关）", "值班律师法律帮助通知（国家安全机关）", "aid_duty"),
    _make_fz_template("FZ-026", "值班律师提供法律帮助通知书（人民检察院）", "值班律师法律帮助通知（人民检察院）", "aid_duty"),
    _make_fz_template("FZ-027", "值班律师提供法律帮助通知书（人民法院）", "值班律师法律帮助通知（人民法院）", "aid_duty"),
    _make_fz_template("FZ-028", "值班律师提供法律帮助情况登记表", "值班律师法律帮助情况登记", "aid_duty"),
    _make_fz_template("FZ-029", "值班律师法律帮助工作台账", "值班律师法律帮助工作台账", "aid_duty"),

    # ── 法律援助质量监督类 FZ-030~032 ──
    _make_fz_template("FZ-030", "庭审旁听情况记录表", "庭审旁听情况记录", "aid_quality"),
    _make_fz_template("FZ-031", "征询办案机关意见函", "征询办案机关意见", "aid_quality"),
    _make_fz_template("FZ-032", "受援人回访记录表", "受援人回访记录", "aid_quality"),

    # ── 律师办案辅助文书 FZ-033~044 ──
    _make_fz_lawyer("FZ-033", "类案检索报告", "类案检索与比对分析"),
    _make_fz_lawyer("FZ-034", "案件汇报提纲", "案件汇报与讨论"),
    _make_fz_lawyer("FZ-035", "类案批量侦查数据分析报告", "批量侦查数据分析"),
    _make_fz_lawyer("FZ-036", "专项侦查工作方案", "专项侦查工作计划"),
    _make_fz_lawyer("FZ-037", "审查报告（捕诉合一）", "捕诉合一审查报告"),
    _make_fz_lawyer("FZ-038", "书面质证意见书", "证据质证意见"),
    _make_fz_lawyer("FZ-039", "辩护词", "刑事案件辩护"),
    _make_fz_lawyer("FZ-040", "公诉意见书", "公诉案件出庭意见"),
    _make_fz_lawyer("FZ-041", "不起诉理由说明书", "不起诉理由说明"),
    _make_fz_lawyer("FZ-042", "司法建议书", "司法建议"),
    _make_fz_lawyer("FZ-043", "律师会见笔录", "律师会见记录"),
    _make_fz_lawyer("FZ-044", "庭审发问提纲", "庭审发问准备"),
]

# 构建索引
TEMPLATES_BY_ID = {t["id"]: t for t in TEMPLATES}


def get_template_list(category=None, sub_category=None, keyword=None):
    """获取模板列表，支持分类筛选和关键词搜索"""
    result = TEMPLATES
    if category:
        result = [t for t in result if t.get("category") == category]
    if sub_category:
        result = [t for t in result if t.get("sub_category") == sub_category]
    if keyword:
        kw = keyword.lower()
        result = [t for t in result if kw in t["name"].lower() or kw in t.get("scene", "").lower() or kw in t.get("id", "").lower()]
    return result


def get_template_detail(template_id: str):
    """获取模板详情（含解析后的字段定义）"""
    t = TEMPLATES_BY_ID.get(template_id)
    if not t:
        return None
    result = {k: v for k, v in t.items() if k != "fields"}
    result["fields"] = _resolve_fields(t)
    return result
