import json,hashlib
from lib import *
OUT=os.environ.get("FANTA_SHOTS",os.path.join(HERE,"shots"))
os.makedirs(OUT,exist_ok=True)
A='0123456789ABCDEFGHJKMNPQRSTVWXYZ'
def uid(key):
    n=int.from_bytes(hashlib.sha256(("ps1:"+key).encode()).digest()[:17],'big')
    s=''.join(A[(n>>(5*i))&31] for i in range(21))
    return "01M4YJ"+s[:20]
def col(h): return f'fnxColor("{h}")'
def J(v):
    # JSON with fnxColor() calls for strings prefixed '#'
    if isinstance(v,dict): return "{"+", ".join(f'"{k}": {J(x)}' for k,x in v.items())+"}"
    if isinstance(v,(list,tuple)): return "["+", ".join(J(x) for x in v)+"]"
    if isinstance(v,str) and v.startswith("#") and len(v) in (7,9): return col(v)
    if isinstance(v,bool): return "true" if v else "false"
    if isinstance(v,int): return str(v)
    if isinstance(v,float): return repr(v)
    return json.dumps(v)
def solid(h): return {"color":h,"kind":"solid"}
def attrs(d):
    out=[]
    for k in sorted(d):
        v=d[k]
        if v is None: continue
        if isinstance(v,str) and not (v.startswith("#") and len(v) in (7,9)): out.append(f'{k}={json.dumps(v)}')
        else: out.append(f'{k}={{{J(v)}}}')
    return " ".join(out)
class N:
    def __init__(s,tag,key,children=None,**a): s.tag=tag;s.key=key;s.a=a;s.children=children or []
    def add(s,*c): s.children+= [x for x in c if x is not None]; return s
    def render(s,ind):
        a=dict(s.a); a["id"]=uid(s.key); a.setdefault("blend_mode","normal"); a.setdefault("opacity",1.0)
        if s.tag=="Frame": a.setdefault("scrollable",False)
        pad="  "*ind
        if not s.children: return f"{pad}<{s.tag} {attrs(a)} />"
        inner="\n".join(c.render(ind+1) for c in s.children)
        return f"{pad}<{s.tag} {attrs(a)}>\n{inner}\n{pad}</{s.tag}>"
def frame(key,name,x,y,w,h,fill=None,children=None,**kw):
    a=dict(name=name,x=x,y=y,clip_size=[w,h]); 
    if fill: a["background"]=solid(fill)
    a.update(kw); return N("Frame",key,children,**a)
def rect(key,name,x,y,w,h,fill,**kw):
    a=dict(name=name,x=x,y=y,width=w,height=h,fills=[solid(fill)]); a.update(kw); return N("Rect",key,**a)
def text(key,name,x,y,w,h,content,size=12,color="#EBEBEB",weight=400,align="left",**kw):
    a=dict(name=name,x=x,y=y,local_size=[w,h],content=content,align=align,auto_resize="none",vertical_align="center",
      style={"color":color,"font_family":"Source Sans Pro","italic":False,"letter_spacing":0.0,"line_height":1.2,"line_height_auto_percent":100.0,"size_px":float(size),"weight":weight})
    a.update(kw); return N("Text",key,**a)
def ov_text(path,value): return {"target_path":path,"target_prop":{"prop":"text_content"},"value":{"kind":"text","value":value}}
def ov_swap(path,cid): return {"target_path":path,"target_prop":{"prop":"visible"},"value":{"component":cid[2:] if cid.startswith("c_") else cid,"kind":"swap_instance"}}
def ov_size(w,h,path=None): return {"target_path":path or [],"target_prop":{"prop":"visible"},"value":{"kind":"field","value":{"clip_size":[float(w),float(h)]}}}
def ov_hide(path): return {"target_path":path,"target_prop":{"prop":"visible"},"value":{"kind":"visible","value":False}}
def ov_fill(path,h): return {"target_path":path,"target_prop":{"index":0,"prop":"fill_color"},"value":{"fills":[solid(h)],"kind":"fills"}}
def inst(key,name,cid,x,y,w,h,overrides=None,**kw):
    a=dict(name=name,x=x,y=y,component=cid[2:] if cid.startswith("c_") else cid,local_size=[w,h])
    if overrides: a["overrides"]=overrides
    a.update(kw); return N("Instance",key,**a)
HEAD='''/** @jsxRuntime classic */
/** @jsx fnxElement */
import { AiArtifact, Audio, Boolean, Ellipse, Embed, Frame, Image, Instance, Model3D, NodeGraph, Rect, Text, TextPath, Vector, Video } from "../../fnx";
// @generated fanta source — the design is the source of truth; ids are mirrored in the .ids sidecar
export default function Photoshop_Screen() {
  return (
'''
PAGE_ID="01M4YH6Z96MQSHNPFYYH4NSDPF"
def page_source(screen):
    body=screen.render(3)
    return HEAD+f'    <Frame background={{{J(solid("#1D1D1D"))}}} blend_mode="normal" id="{PAGE_ID}" name="🖌️  Photoshop Screen" opacity={{1.0}} scrollable={{false}} x={{0.0}} y={{0.0}}>\n{body}\n    </Frame>\n  );\n}}\n'
PATH=f"{PROJ}/pages/photoshop-screen/page.fnx"
def write(screen):
    src=page_source(screen)
    raw=c.call("validate_fnx_source",{"path":"pages/photoshop-screen/page.fnx","source":src})
    if not raw.startswith("{"): raise SystemExit(raw[:3000])
    r=json.loads(raw)
    if any(d.get("severity")!="warning" for d in r.get("diagnostics",[])) or r.get("diagnostics"): raise SystemExit(json.dumps(r)[:3000])
    open(PATH,"w").write(src)
    return r
def shot(name,node="screen",maxd=1600):
    import time; time.sleep(1.5)
    return c.call("get_screenshot",{"page":23,"node":"n_"+uid(node),"max_dimension":maxd},img=os.path.join(OUT,f"{name}.png"))
def zoom(name,node,maxd=1600):
    return c.call("get_screenshot",{"page":23,"node":"n_"+uid(node),"max_dimension":maxd},img=os.path.join(OUT,f"{name}.png"))
