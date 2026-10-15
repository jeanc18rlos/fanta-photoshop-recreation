import sys
from fnx import *
STAGE=int(sys.argv[1])
W,H=1920,1080
BG="#1D1D1D"; DEEP="#0E0E0E"; PASTE="#171717"; ELEV="#303030"; TEXT="#EBEBEB"; MUTED="#B0B0B0"
MENU_H=40; OPT_Y=41; OPT_H=48; BODY_Y=90; STATUS_H=24
TOOL_W=48; PANEL_X=1602; PANEL_W=318; DOC_X=49; DOC_W=PANEL_X-2-DOC_X
from PIL import ImageFont
_FONT="/Applications/Houdini/Houdini22.0.368/Frameworks/Houdini.framework/Versions/22.0/Resources/houdini/fonts/SourceSansPro-Regular.ttf"
def tw(t,size=14): return round(ImageFont.truetype(_FONT,size*4).getlength(t)/4)
Q={'Quiet ?':'True','Emphasis ?':'False'}
AB_LABEL=one('Action Button',Color='Standard',State='Default',**Q,**{'Label ?':'True','Icon ?':'False'})
AB_ICON=one('Action Button',Color='Standard',State='Default',**Q,**{'Label ?':'False','Icon ?':'True'})
AB_ICON_SEL=one('Action Button',Color='Standard',State='Default',**{'Quiet ?':'False','Emphasis ?':'True','Label ?':'False','Icon ?':'True'})
AB_LABEL_T,AB_LABEL_HOLD="01M4V5T78WZ3DH2PFJKKDJWDAX","01M4V5T78WV23WRET6CK0J37NZ"
AB_ICON_I,AB_ICON_HOLD="01M4V5T78VJS62NRYVJCFSWGPR","01M4V5T78VZ9TVJ284VCMXG4MR"
def label_button(key,label,x,y,hold=False,h=32):
    w=tw(label)+20
    ov=[ov_text([AB_LABEL_T],label),ov_size(w,h)]
    if not hold: ov.append(ov_hide([AB_LABEL_HOLD]))
    return inst(key,label,AB_LABEL,x,y,w,h,ov),w
def icon_button(key,name,icon,x,y,hold=False,selected=False):
    cid=AB_ICON_SEL if selected else AB_ICON
    ov=[ov_swap([ICON_PATH[cid][0]],ICON[icon])]
    if not hold: ov.append(ov_hide([ICON_PATH[cid][1]]))
    return inst(key,name,cid,x,y,32,32,ov)
def _paths(cid):
    import re
    ids=json.load(open(f"{PROJ}/{CID[cid]['source'].rsplit('/',1)[0]}/master.ids.json"))["ids"]
    i=[e["id"] for e in ids if e["tag"]=="Instance"][0]; h=[e["id"] for e in ids if e["name"]=="Hold Icon"][0]
    return (i,h)
ICON_PATH={cid:_paths(cid) for cid in (AB_ICON,AB_ICON_SEL)}

screen=frame("screen","Photoshop — Editing Session",0,0,W,H,DEEP)

def section_shell():
    # Region frames; gutters between them show the deep background like Photoshop's panel seams.
    screen.add(frame("menubar","Menu Bar",0,0,W,MENU_H,BG))
    screen.add(frame("options","Options Bar",0,OPT_Y,W,OPT_H,BG))
    screen.add(frame("toolbar","Toolbar",0,BODY_Y,TOOL_W,H-BODY_Y,BG))
    screen.add(frame("document","Document Window",DOC_X,BODY_Y,DOC_W,H-BODY_Y,PASTE))
    screen.add(frame("dock","Panel Dock",PANEL_X,BODY_Y,PANEL_W,H-BODY_Y,DEEP))
def find_node(key):
    def walk(n):
        if n.key==key: return n
        for ch in n.children:
            r=walk(ch)
            if r: return r
    return walk(screen)

def section_menubar():
    mb=find_node("menubar")
    mb.add(frame("ps-badge","Photoshop Badge",10,8,24,24,"#001E36",corner_radius=4,children=[
        text("ps-badge-t","Ps",0,0,24,24,"Ps",size=13,color="#31A8FF",weight=700,align="center")]))
    x=44
    for m in ["File","Edit","Image","Layer","Type","Select","Filter","3D","View","Plugins","Window","Help"]:
        b,w=label_button("menu-"+m,m,x,4); mb.add(b); x+=w
    # Right side: Spectrum share/search/help cluster that Photoshop 2024+ shows in its app bar.
    share=one('Actions / Button /',Color='Accent',State='Default',**{'Outlined ?':'False','Label ?':'True','Icon ?':'True'})
    mb.add(inst("menu-share","Share Button",share,W-12-94,4,94,32,[ov_text(["01M4V5T70TRVW2107VXKQTH74V"],"Share")]))
    xr=W-12-94-8
    for ic,nm in [("Help","Help"),("Search","Search"),("ViewColumn","Workspace")]:
        xr-=32; mb.add(icon_button("appbar-"+nm,nm,ic,xr,4)); xr-=4
    mb.add(text("menu-title","Document Title",(W-360)//2,0,360,MENU_H,"Tropical_Garden.psd",size=13,color=MUTED,align="center"))

PICK_Q=one('Picker',Style='Quiet',**{'Label Position':'Side'},State='Default',**{'Placeholder ?':'False'})
PICK_S=one('Picker',Style='Standard',**{'Label Position':'Side'},State='Default',**{'Placeholder ?':'False'})
PICK_Q_LABEL,PICK_Q_VALUE="01M4V5T75SMXE9WAB6YX45ACY0","01M4V5T75SV1BANS82DJDJQTBD"
PICK_S_LABEL,PICK_S_VALUE="01M4V5T75R3480X3GZR681NBXG","01M4V5T75R0J9RY456RAYHA3DQ"
SLIDER=one('Slider - ',**{'Label Position':'Side'},Fill='No Fill',State='Default')
SLIDER_LABEL,SLIDER_VALUE="01M4V5T76TBECT18HEWEFB5HQ3","01M4V5T76TBR06RF1QJAY3GEY6"
DIVIDER=one('Divider',Size='Small')
def picker(key,label,value,x,y,quiet=True):
    cid,pl,pv=(PICK_Q,PICK_Q_LABEL,PICK_Q_VALUE) if quiet else (PICK_S,PICK_S_LABEL,PICK_S_VALUE)
    h=32 if quiet else 33
    asterisk=[e for e in tree(cid).splitlines() if "Asterisk Container" in e][0].split()[-1]
    return inst(key,label+" Picker",cid,x,y,228,h,[ov_text(path_to(cid,pl),label),ov_text(path_to(cid,pv),value),ov_hide(path_to(cid,asterisk))])
SLIDER_LC,SLIDER_TRACK,SLIDER_VC="01M4V5T76T7G0KADNGBPEC80FK","01M4V5T76TC7PSTJEQH4V1WTJH","01M4V5T76TXYK2BHN6KVCV4SRW"
def ov_field(path,value): return {"target_path":path,"target_prop":{"prop":"visible"},"value":{"kind":"field","value":value}}
def slider(key,label,value,x,y,fraction):
    # Track and fill are fixed 200px vectors, so the instance is sized to keep the track frame at exactly
    # 200px; the handle is then placed through the track frame's right padding.
    lw=tw(label,12); vw=tw(value,12)
    w=lw+vw+24+200
    pad=round((1-fraction)*(200-24))
    al={"child_layout": True, "counter_align": "center", "counter_sizing": "fixed", "counter_spacing": 0.0, "flow_reverse": False, "mode": "horizontal", "padding": [0.0, float(pad), 0.0, 0.0], "primary_align": "start", "primary_sizing": "fixed", "reverse_z": False, "spacing": 0.0, "wrap": False}
    ov=[ov_text(path_to(SLIDER,SLIDER_LABEL),label),ov_text(path_to(SLIDER,SLIDER_VALUE),value),
        ov_field([SLIDER_LC],{"clip_size":[float(lw),17.0]}),ov_field([SLIDER_VC],{"clip_size":[float(vw),17.0]}),
        ov_field([SLIDER_TRACK],{"auto_layout":al}),ov_size(w,32)]
    return inst(key,label+" Slider",SLIDER,x,y,w,32,ov),w

def vdivider(key,x,y,h):
    return inst(key,"Divider",DIVIDER,x,y,1,h,[ov_size(1,h)])
def hdivider(key,x,y,w):
    return inst(key,"Divider",DIVIDER,x,y,w,1,[ov_size(w,1)])

def section_options():
    ob=find_node("options"); y=8
    ob.add(icon_button("opt-preset","Tool Preset","Brush",8,y,hold=True))
    ob.add(vdivider("opt-div1",52,10,28))
    ob.add(picker("opt-size","Size","45 px",64,y))
    ob.add(picker("opt-mode","Mode","Normal",304,y))
    x=548
    for label,value,fraction,icon_key,icon_name,icon in [("Opacity","100%",1.0,"opt-pressure-opacity","Pressure for Opacity","Draw"),("Flow","38%",0.38,"opt-airbrush","Airbrush","Effects"),("Smoothing","10%",0.10,"opt-smoothing-options","Smoothing Options","Settings")]:
        n,w=slider("opt-"+label.lower(),label,value,x,y,fraction); ob.add(n); x+=w+12
        ob.add(icon_button(icon_key,icon_name,icon,x,y)); x+=32+20
    ob.add(vdivider("opt-div2",x-8,10,28))
    ob.add(icon_button("opt-symmetry","Symmetry","FlipHorizontal",x+4,y,hold=True))

SWATCH=one('Swatch',State='Default',Rounding='Regular',Selection='None')
TOOLTIP_L=one('Tooltip',Style='Neutral',**{'Tip Position':'Left'})
def swatch(key,name,color,x,y,size=32):
    ov=[ov_fill([],color)]
    if size!=32: ov.append(ov_size(size,size))
    return inst(key,name,SWATCH,x,y,size,size,ov)
BRUSH_Y=None
def section_toolbar():
    global BRUSH_Y
    tb=find_node("toolbar"); y=10
    groups=[[("Move Tool","Move"),("Rectangular Marquee Tool","RectSelect"),("Polygonal Lasso Tool","PolygonSelect"),("Object Selection Tool","QuickSelect"),("Crop Tool","Crop"),("Eyedropper Tool","Sampler")],
            [("Spot Healing Brush Tool","SpotHeal"),("Brush Tool","Brush"),("Clone Stamp Tool","CloneStamp"),("Eraser Tool","Erase"),("Gradient Tool","LinearGradient"),("Blur Tool","Blur"),("Dodge Tool","Light")],
            [("Pen Tool","VectorDraw"),("Horizontal Type Tool","Text"),("Path Selection Tool","Select"),("Rectangle Tool","Rectangle")],
            [("Hand Tool","Hand"),("Zoom Tool","ZoomIn")]]
    for gi,g in enumerate(groups):
        if gi: tb.add(hdivider(f"tool-div{gi}",12,y+2,24)); y+=9
        for name,icon in g:
            sel=name=="Brush Tool"
            if sel: BRUSH_Y=BODY_Y+y
            tb.add(icon_button("tool-"+icon,name,icon,8,y,hold=name not in ("Hand Tool","Zoom Tool"),selected=sel)); y+=36
    tb.add(icon_button("tool-more","Edit Toolbar","More",8,y)); y+=44
    tb.add(swatch("tool-bg","Background Color","#F4EFE6",18,y+12,22))
    tb.add(swatch("tool-fg","Foreground Color",FG,8,y,22))
    tb.add(icon_button("tool-mask","Quick Mask Mode","RangeMask",8,y+44))
    tb.add(icon_button("tool-screen","Change Screen Mode","ViewSingle",8,y+80,hold=True))
    label="Brush Tool (B)"; w=tw(label,12)+18
    screen.add(inst("tooltip-brush","Tooltip — Brush Tool",TOOLTIP_L,TOOL_W+4,BRUSH_Y+4,w,24,[ov_text(["01M4V5T789VEA5N1F0YWSDYXMW"],label),ov_size(w,24)]))

TAB_SEL=one('Tab - ',Orientation='Horizontal',State='Default',**{'Selected ?':'True','Emphasized ?':'False'})
TAB=one('Tab - ',Orientation='Horizontal',State='Default',**{'Selected ?':'False','Emphasized ?':'False'})
def tab(key,label,icon,x,y,selected=False,show_icon=True):
    cid=TAB_SEL if selected else TAB
    lines=tree(cid).splitlines()
    icon_id=[l for l in lines if "Instance Icon" in l][0].split()[2]
    label_id=[l for l in lines if "Text Label" in l][0].split()[2]
    w=(25 if show_icon else 0)+tw(label,14)
    ov=[ov_text(path_to(cid,label_id),label),ov_size(w,48)]
    ov.append(ov_swap([icon_id],ICON[icon]) if show_icon else ov_hide([icon_id]))
    if selected and not show_icon and w<47: pass
    elif selected: ov.append(ov_hide(["01M4V5T77B9HJMWFWE49V6T2H0"]))
    return inst(key,label+" Tab",cid,x,y,w,48,ov),w
ART_ASSET="7V41GTZAVHTSRD5M771MJ2V2YF"
def section_document():
    doc=find_node("document")
    bar=frame("doc-tabs","Document Tabs",0,0,DOC_W,48,BG)
    bar.add(hdivider("doc-tabs-div",0,47,DOC_W))
    doc.add(bar)
    x=12
    for i,(label,icon,sel) in enumerate([("Tropical_Garden.psd @ 50% (Foliage Paint, RGB/8)","Images",True),("Portrait_Retouch.jpg @ 33.3% (RGB/8)","Image",False),("Poster_Layout.psd @ 25% (Headline, CMYK/8)","Images",False)]):
        # Photoshop marks the active document with a lighter tab body behind the Spectrum tab.
        t,w=tab(f"doc-tab{i}",label,icon,x,0,sel)
        if sel: bar.add(frame(f"doc-tab{i}-bg","Active Tab Background",x-12,0,12+w+2+32+8,48,"#303030"))
        bar.add(t)
        bar.add(icon_button(f"doc-tab{i}-close","Close Document","Cross75",x+w+2,8)); x+=w+2+32+20
    canvas_h=H-BODY_Y-48-32
    area=frame("doc-canvas","Canvas Area",0,48,DOC_W,canvas_h,PASTE)
    doc.add(area)
    aw,ah=1160,820
    ax,ay=(DOC_W-aw)//2,(canvas_h-ah)//2
    area.add(rect("doc-art","Tropical_Garden.psd",ax,ay,aw,ah,"#FFFFFF",
        fills=[{"asset":ART_ASSET,"kind":"image","mode":"fill"}],
        effects=[{"kind":"drop","color":"#00000066","offset":[0.0,4.0],"blur":24.0,"spread":0.0}]))
    # Live selection: Photoshop's marching ants are a black line with a white dash on top.
    sx,sy,sw,sh=ax+640,ay+300,330,260
    area.add(rect("sel-black","Selection Edge",sx,sy,sw,sh,"#00000000",fills=[],strokes=[{"paint":solid("#000000"),"width":1.0,"align":"center"}]))
    area.add(rect("sel-white","Selection Marching Ants",sx,sy,sw,sh,"#00000000",fills=[],strokes=[{"paint":solid("#FFFFFF"),"width":1.0,"align":"center","dash":[4.0,4.0]}]))
    bx,by,bd=sx+150,sy+120,46
    area.add(N("Ellipse","brush-outer",name="Brush Cursor Shadow",x=bx,y=by,width=bd,height=bd,fills=[],strokes=[{"paint":solid("#00000099"),"width":1.0,"align":"outside"}]))
    area.add(N("Ellipse","brush-inner",name="Brush Cursor",x=bx,y=by,width=bd,height=bd,fills=[],strokes=[{"paint":solid("#FFFFFF"),"width":1.0,"align":"inside"}]))
    st=frame("doc-status","Status Bar",0,H-BODY_Y-32,DOC_W,32,BG)
    doc.add(st)
    b,w=label_button("status-zoom","50%",4,0); st.add(b)
    st.add(vdivider("status-div",4+w+4,8,16))
    b,w2=label_button("status-info","4096 px × 2896 px (300 ppi)",4+w+12,0,hold=True); st.add(b)
    b,w3=label_button("status-scratch","Scratch: 412.3M / 1.21G",DOC_W-12-tw("Scratch: 412.3M / 1.21G")-20,0); st.add(b)

COLOR_AREA=one('Color Area',Handle='Center',State='Default')
HUE_SLIDER=one('Color Slider',Handle='In Track',Orientation='Vertical',State='Default')
FG="#803F3F"
COLOR_H,HISTORY_H=300,236
def panel(key,name,y,h,tabs,menu=True):
    p=frame(key,name,0,y,PANEL_W,h,BG)
    x=12
    for i,label in enumerate(tabs):
        t,w=tab(f"{key}-tab{i}",label,"Settings",x,0,selected=i==0,show_icon=False); p.add(t); x+=w+20
    if menu: p.add(icon_button(f"{key}-menu","Panel Menu","MoreSmallListVert",PANEL_W-40,8))
    return p
def section_color():
    dock=find_node("dock")
    p=panel("panel-color","Color Panel",0,COLOR_H,["Color","Swatches","Gradients","Patterns"]); dock.add(p)
    # The centered handle on a red field is hsv(0, 50%, 50%), which is why the foreground is #803F3F.
    p.add(inst("color-area","Color Area",COLOR_AREA,16,60,192,192,[
        ov_fill(["01M4V5T712GQ7FZCEGYFWJ41KJ","01M4V5T712NK161AN8QHBNCBEF"],FG)]))
    hue_stops=["#00FFFF","#0000FF","#FF00FF","#FF0000","#FFFF00","#00FF00","#00FFFF"]
    hue={"kind":"gradient","gradient":{"kind":"linear","start":[0.5,0.0],"end":[0.5,1.0],"stops":[{"color":c,"position":i/6} for i,c in enumerate(hue_stops)]}}
    p.add(inst("color-hue","Hue Slider",HUE_SLIDER,220,56,24,200,[
        {"target_path":[],"target_prop":{"index":0,"prop":"fill_color"},"value":{"fills":[hue],"kind":"fills"}},
        ov_fill(["01M4V5T715XF4V2SSV8NSRK6TW","01M4V5T715VTJAPYKZA2CZ638A"],"#FF1A00")]))
    p.add(swatch("color-bg","Background Color","#F4EFE6",272,76,28))
    p.add(swatch("color-fg","Foreground Color",FG,258,62,28))
    recent=["#803F3F","#FFD93B","#0B1446","#F8C6EC","#56C3F0","#8FB5E3","#F4A276","#5B2A86","#FFFFFF"]
    for i,col in enumerate(recent):
        p.add(swatch(f"color-recent{i}","Recent Color",col,16+i*26,264,22))

NAV=one('Side Navigation',Type='Navigation Item',State='Default',**{'Selected ?':'False'})
NAV_SEL=one('Side Navigation',Type='Navigation Item',State='Default',**{'Selected ?':'True'})
def nav_item(key,label,icon,x,y,w,selected=False):
    cid=NAV_SEL if selected else NAV
    lines=tree(cid).splitlines()
    icon_id=[l for l in lines if "Instance Icon" in l][0].split()[2]
    label_id=[l for l in lines if "Text Label" in l][0].split()[2]
    ov=[ov_text(path_to(cid,label_id),label),ov_size(w,34)]
    ov.append(ov_swap([icon_id],ICON[icon]) if icon else ov_hide([icon_id]))
    return inst(key,label,cid,x,y,w,34,ov)
def section_history():
    dock=find_node("dock")
    p=panel("panel-history","History Panel",COLOR_H+2,HISTORY_H,["History","Actions","Properties"]); dock.add(p)
    steps=[("Open","Images"),("New Layer","Layers"),("Rectangular Marquee","RectSelect"),("Brush Tool","Brush"),("Brush Tool","Brush")]
    for i,(label,icon) in enumerate(steps):
        p.add(nav_item(f"hist{i}",label,icon,8,52+i*34,PANEL_W-16,selected=i==len(steps)-1))

SWATCH_SQ=one('Swatch',State='Default',Rounding='None',Selection='None')
HUE_FILL={"kind":"gradient","gradient":{"kind":"linear","start":[0.0,0.5],"end":[1.0,0.5],"stops":[{"color":c,"position":i/6} for i,c in enumerate(["#FF0000","#FFFF00","#00FF00","#00FFFF","#0000FF","#FF00FF","#FF0000"])]}}
def layer_row(key,label,thumb,y,selected=False,visible=True,trailing=None):
    cid=NAV_SEL if selected else NAV
    lines=tree(cid).splitlines()
    icon_id=[l for l in lines if "Instance Icon" in l][0].split()[2]
    label_id=[l for l in lines if "Text Label" in l][0].split()[2]
    w=PANEL_W-16
    # Widen the gap after the eye icon so the layer thumbnail sits between it and the name.
    al={"child_layout": True, "counter_align": "center", "counter_sizing": "fixed", "counter_spacing": 0.0, "flow_reverse": False, "mode": "horizontal", "padding": [10.0, 12.0, 11.0, 12.0], "primary_align": "start", "primary_sizing": "fixed", "reverse_z": False, "spacing": 50.0, "wrap": False}
    ov=[ov_text(path_to(cid,label_id),label),ov_size(w,40),ov_field([],{"auto_layout":al}),
        ov_swap([icon_id],ICON["Visibility" if visible else "VisibilityOff"])]
    row=[inst(key,"Layer — "+label,cid,8,y,w,40,ov)]
    tx,ty=8+42,y+6
    if thumb=="art":
        row.append(rect(key+"-thumb",label+" Thumbnail",tx,ty,28,28,"#FFFFFF",fills=[{"asset":ART_ASSET,"kind":"image","mode":"fill"}],strokes=[{"paint":solid("#4B4B4B"),"width":1.0,"align":"inside"}]))
    elif thumb=="hue":
        row.append(inst(key+"-thumb",label+" Thumbnail",SWATCH_SQ,tx,ty,28,28,[{"target_path":[],"target_prop":{"index":0,"prop":"fill_color"},"value":{"fills":[HUE_FILL],"kind":"fills"}},ov_size(28,28)]))
    else:
        row.append(inst(key+"-thumb",label+" Thumbnail",SWATCH_SQ,tx,ty,28,28,[ov_fill([],thumb),ov_size(28,28)]))
    if trailing:
        row.append(icon_button(key+"-trail",trailing[0],trailing[1],PANEL_W-48,y+4))
    return row
def section_layers():
    dock=find_node("dock")
    y0=COLOR_H+2+HISTORY_H+2
    h=H-BODY_Y-y0
    p=panel("panel-layers","Layers Panel",y0,h,["Layers","Channels","Paths"]); dock.add(p)
    p.add(picker("layers-filter","Filter","Kind",8,50))
    p.add(icon_button("layers-filter-pixel","Pixel Layer Filter","Image",240,50))
    p.add(icon_button("layers-filter-type","Type Layer Filter","Text",276,50))
    p.add(picker("layers-blend","Blend","Normal",8,86))
    p.add(slider("layers-opacity","Opacity","100%",8,122,1.0)[0])
    b,w=label_button("layers-lock-label","Lock",8,158); p.add(b)
    for i,(nm,ic) in enumerate([("Lock Transparent Pixels","ClassicGridView"),("Lock Image Pixels","Brush"),("Lock Position","Move"),("Lock All","LockClosed")]):
        p.add(icon_button(f"layers-lock{i}",nm,ic,8+w+4+i*36,158))
    p.add(hdivider("layers-div-top",0,194,PANEL_W))
    rows=[("Hue/Saturation 1","hue",False,True,None),
          ("Foliage Paint",FG,True,True,None),
          ("Yellow Dabs","#FFD93B",False,True,("Layer Effects","Effects")),
          ("Sketch","#8FB5E3",False,False,None),
          ("Background","art",False,True,("Locked","LockClosed"))]
    for i,(label,thumb,sel,vis,trail) in enumerate(rows):
        for n in layer_row(f"layer{i}",label,thumb,198+i*40,sel,vis,trail): p.add(n)
    fy=h-44
    p.add(hdivider("layers-div-bottom",0,fy,PANEL_W))
    icons=[("Link Layers","Link"),("Add a Layer Style","Effects"),("Add Layer Mask","RangeMask"),("New Fill or Adjustment Layer","Contrast"),("New Group","FolderAdd"),("New Layer","Add"),("Delete Layer","Delete")]
    x=PANEL_W-8-len(icons)*36+4
    for i,(nm,ic) in enumerate(icons):
        p.add(icon_button(f"layers-foot{i}",nm,ic,x+i*36,fy+6))

SECTIONS=[section_shell,section_menubar,section_options,section_toolbar,section_document,section_color,section_history,section_layers]
for f in SECTIONS[:STAGE]: f()
if __name__=="__main__":
    print(write(screen)); print(shot(f"stage{STAGE}"))
