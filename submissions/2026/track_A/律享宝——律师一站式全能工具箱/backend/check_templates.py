import sys
sys.path.insert(0,'.')
from app.data.template_data import TEMPLATES, get_template_detail

total = len(TEMPLATES)
fz = [t for t in TEMPLATES if t['id'].startswith('FZ-')]
ms = [t for t in TEMPLATES if t['id'].startswith('MS-')]
print(f'Total={total} MS={len(ms)} FZ={len(fz)}')

for t in TEMPLATES:
    if t['id'].startswith('FZ-'):
        fields = get_template_detail(t['id'])['fields']
        fnames = [f['name'] for f in fields]
        is_generic = all(n.startswith('applicant_') or n in ('case_cause','case_description','issuing_authority','issue_date') for n in fnames)
        status = 'GENERIC' if is_generic else 'CUSTOM'
        print(f'  {status:7s} {t["id"]:8s} {t["name"][:20]:20s} fields={len(fields)}')
