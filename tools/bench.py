import glob,json,os,statistics,sys,time
sys.argv=["x"]
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fanta import C
PROJ=os.environ.get("FANTA_PROJECT",os.path.dirname(HERE))
OUT=os.environ.get("FANTA_SHOTS",os.path.join(HERE,"shots")); os.makedirs(OUT,exist_ok=True)
c=C()
def t(fn,n=5):
    xs=[]
    for _ in range(n):
        a=time.perf_counter(); r=fn(); xs.append((time.perf_counter()-a)*1000)
    return r,{"median_ms":round(statistics.median(xs),1),"min_ms":round(min(xs),1),"max_ms":round(max(xs),1),"runs":n}
res={}
st,res["get_editor_state"]=t(lambda: json.loads(c.call("get_editor_state",{})))
p8=st["pages"][8]; res["darkest_page"]={"name":p8["name"],"nodes":p8["nodes"],"total_document_nodes":st["total_nodes"],"pages":st["page_count"]}
_,res["list_darkest_depth1"]=t(lambda: c.call("batch_get",{"page":8,"depth":1,"include_geometry":True}))
_,res["list_darkest_depth3"]=t(lambda: c.call("batch_get",{"page":8,"depth":3}),3)
def comps():
    n=0;off=0
    while True:
        r=json.loads(c.call("get_design_system",{"offset":off,"limit":200})); k=len(r["components"]); n+=k
        if k<200: return n
        off+=200
res["component_count"],res["design_system_full_pagination"]=t(comps,3)
sections=["n_01M4V5T73HEKQT89X143JE62X6","n_01M4V5T730DNPHP4KPZW312MRD","n_01M4V5T77NAHDMAJYCMTP3R629","n_01M4V5T771KX2F6NJYM5W8JD0K","n_01M4V5T78ESS1KW14BJ6BDZ0NF","n_01M4V5T7APPN25F8K4FETQXD0N","n_01M4V5T79MPAQZXENET3T0Q6EW","n_01M4V5T79JSFVWZCBGN01KMMJ6"]
roots=set()
for f in glob.glob(os.path.join(PROJ,"components/**/def.json"),recursive=True):
    roots.add("n_"+json.load(open(f))["root"])
def walk():
    frontier=list(sections); visited=0; masters=0; calls=0
    while frontier:
        batch=frontier[:150]; frontier=frontier[150:]; calls+=1
        for n in json.loads(c.call("batch_get",{"ids":batch,"detail":"summary"}))["nodes"]:
            visited+=1
            if n["id"] in roots: masters+=1; continue
            if n.get("kind")=="instance": continue
            frontier+= [x for x in n.get("children",[]) if isinstance(x,str)]
    return {"nodes_visited":visited,"masters_found":masters,"batch_get_calls":calls}
res["walk_result"],res["walk_darkest_tree"]=t(walk,3)
_,res["screenshot_darkest_1024"]=t(lambda: c.call("get_screenshot",{"page":8,"max_dimension":1024},img=os.path.join(OUT,"bench-1024.png")),3)
_,res["screenshot_darkest_2048"]=t(lambda: c.call("get_screenshot",{"page":8,"max_dimension":2048},img=os.path.join(OUT,"bench-2048.png")),3)
src=open(os.path.join(PROJ,"pages/photoshop-screen/page.fnx")).read()
_,res["validate_photoshop_page_fnx"]=t(lambda: c.call("validate_fnx_source",{"path":"pages/photoshop-screen/page.fnx","source":src}))
_,res["screenshot_photoshop_screen"]=t(lambda: c.call("get_screenshot",{"page":23,"max_dimension":1920},img=os.path.join(OUT,"bench-photoshop.png")),3)
st23=json.loads(c.call("get_editor_state",{}))["pages"][23]; res["photoshop_page_nodes"]=st23["nodes"]
print(json.dumps(res,indent=1))
json.dump(res,open(os.path.join(os.path.dirname(HERE),"benchmark","results.json"),"w"),indent=1)
