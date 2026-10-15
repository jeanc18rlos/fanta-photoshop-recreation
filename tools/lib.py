import os
import json,sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fanta import C
PROJ=os.environ.get("FANTA_PROJECT",os.path.dirname(HERE))
def load_components():
    # Mirrors get_design_system's component list, read from the project's def.json files.
    out=[]
    for root,dirs,files in os.walk(os.path.join(PROJ,"components")):
        if "def.json" in files:
            d=json.load(open(os.path.join(root,"def.json")))
            rel=os.path.relpath(os.path.join(root,"master.fnx"),PROJ)
            out.append({"id":"c_"+d["id"],"name":d["name"],"root":"n_"+d["root"],"source":rel})
    return out
M=json.load(open(os.path.join(HERE,"darkest_masters.json")))
DS=load_components()
PAGE_ROOT="n_01M4YH6Z96MQSHNPFYYH4NSDPF"
AG={"agent_id":"ps-builder","agent_name":"Pixel Mage","page":23,"workspace":"canvas"}
def find(family,**kv):
    out=[]
    for root,v in M.items():
        if family not in " / ".join(v["path"]): continue
        props=dict(p.split("=",1) for p in v["name"].split(", ") if "=" in p)
        if all(props.get(k)==val for k,val in kv.items()): out.append((v["cid"],v["name"],v["size"],root))
    return out
def one(family,**kv):
    r=find(family,**kv)
    if len(r)!=1: raise SystemExit(f"{family} {kv}: {len(r)} -> {[x[1] for x in r][:8]}")
    return r[0][0]
ICON={c["name"]:c["id"] for c in DS if c["name"].isalnum()}
def props(family):
    import collections
    d=collections.defaultdict(set)
    for root,v in M.items():
        if family in " / ".join(v["path"]):
            for p in v["name"].split(", "):
                if "=" in p: k,val=p.split("=",1); d[k].add(val)
    return dict(d)
c=C()
def batch(ops,label,action=None):
    a=dict(AG); a["action"]=action or label
    r=c.call("batch_design",{"ops":ops,"label":label,"activity":a})
    if r.startswith("ERROR"): raise SystemExit(r[:3000])
    return json.loads(r)
def get(ids,detail="summary",geom=True):
    return json.loads(c.call("batch_get",{"ids":ids,"detail":detail,"include_geometry":geom}))["nodes"]
CID={x["id"]:x for x in DS}
def tree(cid):
    src=CID[cid]["source"].rsplit("/",1)[0]
    ids=json.load(open(f"{PROJ}/{src}/master.ids.json"))["ids"]
    fnx=open(f"{PROJ}/{src}/master.fnx").read()
    import re
    out=[]
    for i,e in enumerate(ids):
        depth=0;p=e.get("parent_index")
        while p is not None: depth+=1;p=ids[p].get("parent_index")
        extra=""
        m=re.search(r'<(\w+)[^<]*?id="'+e["id"]+r'"',fnx)
        tagtxt=""
        if e["tag"]=="Instance":
            mm=re.search(r'component="([^"]+)"[^>]*id="'+e["id"]+'"',fnx) or re.search(r'id="'+e["id"]+r'"[^>]*component="([^"]+)"',fnx)
            if mm: extra=" comp="+(CID.get("c_"+mm.group(1),{}).get("name",mm.group(1)) if len(mm.group(1))==26 else mm.group(1))
        if e["tag"]=="Text":
            mm=re.search(r'id="'+e["id"]+r'"[^>]*>\s*\{?"?([^<]{0,60})',fnx)
            if mm: extra=" text="+mm.group(1).strip()
        out.append(("  "*depth)+f'{e["tag"]} {e["name"]} {e["id"]}{extra}')
    return "\n".join(out)
def path_to(cid,node_id):
    ids=json.load(open(f"{PROJ}/{CID[cid]['source'].rsplit('/',1)[0]}/master.ids.json"))["ids"]
    idx=[e["id"] for e in ids].index(node_id); out=[]
    while ids[idx].get("parent_index") is not None:
        out.append(ids[idx]["id"]); idx=ids[idx]["parent_index"]
    return out[::-1]
