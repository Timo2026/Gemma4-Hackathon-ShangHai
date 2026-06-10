"""Extract PRD V1.2 tables to text file"""
import docx
import os

doc_path = r'D:\LocalCodeProject\lvxiangbao\wendang\律享宝律师工具箱平台V1.2迭代升级PRD需求文档.docx'
out_path = r'D:\LocalCodeProject\lvxiangbao\backend\app\templates\_prd_tbl.txt'

doc = docx.Document(doc_path)

with open(out_path, 'w', encoding='utf-8') as f:
    for i, t in enumerate(doc.tables):
        f.write('=== TABLE %d (%dr x %dc) ===\n' % (i, len(t.rows), len(t.columns)))
        for ri, r in enumerate(t.rows):
            for ci, c in enumerate(r.cells):
                f.write('  R%dC%d: %s\n' % (ri, ci, c.text))
        f.write('\n')

print('Done, size:', os.path.getsize(out_path))
