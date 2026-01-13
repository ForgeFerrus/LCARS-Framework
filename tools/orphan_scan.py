"""Simple orphan file detector: counts occurrences of module names in other files."""
import os, re, json
root=os.path.dirname(os.path.dirname(__file__))
pyfiles=[]
for dirpath, dirs, files in os.walk(root):
    if '.venv' in dirpath.split(os.sep):
        continue
    for f in files:
        if f.endswith('.py'):
            pyfiles.append(os.path.join(dirpath,f))

# load contents
contents={}
for p in pyfiles:
    try:
        with open(p,'r',encoding='utf-8') as fh:
            contents[p]=fh.read()
    except Exception as e:
        contents[p]=''

# helper to make module name

def module_variants(path):
    rel=os.path.relpath(path, root).replace(os.sep, '.')
    if rel.endswith('.py'):
        rel=rel[:-3]
    bare=os.path.basename(path)[:-3]
    return set([bare, rel])

refs={}
for p in pyfiles:
    vars=module_variants(p)
    count=0
    for q,txt in contents.items():
        if q==p: continue
        for v in vars:
            if re.search(r'\b'+re.escape(v)+r'\b', txt):
                count+=1
                break
    refs[p]=count

orphans=[p for p,c in refs.items() if c==0]
report={'total_files':len(pyfiles),'orphans_count':len(orphans),'orphans':orphans,'sample_refs':sorted(list(refs.items()), key=lambda x:x[1])[:40]}
out_path=os.path.join(root,'tools','orphan_report.json')
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
print('Wrote report to', out_path)
