import json, os, socket, sys
D = os.path.expanduser("~/Library/Application Support/Fanta/fanta_live_mcp.json")
class C:
    def __init__(s):
        p = json.load(open(D))["socket"]
        s.s = socket.socket(socket.AF_UNIX); s.s.connect(p); s.f = s.s.makefile("rwb"); s.i = 0
        s.req("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"cli","version":"1"}})
        s.f.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}).encode()+b"\n"); s.f.flush()
    def req(s, m, p):
        s.i += 1; s.f.write(json.dumps({"jsonrpc":"2.0","id":s.i,"method":m,"params":p}).encode()+b"\n"); s.f.flush()
        while True:
            line = s.f.readline()
            if not line: raise SystemExit("closed")
            r = json.loads(line)
            if r.get("id") == s.i: return r
    def call(s, name, args, img=None):
        r = s.req("tools/call", {"name":name, "arguments":args})
        if "error" in r: return "ERROR: "+json.dumps(r["error"])
        out = []
        for c in r["result"].get("content", []):
            if c.get("type") == "text": out.append(c["text"])
            elif c.get("type") == "image":
                import base64; fn = img or (sys.argv[3] if len(sys.argv)>3 else "shot.png")
                open(fn,"wb").write(base64.b64decode(c["data"])); out.append("[image saved "+fn+"]")
        return ("ERROR(isError) " if r["result"].get("isError") else "") + "\n".join(out)
if __name__ == "__main__":
    c = C()
    if sys.argv[1] == "list":
        for t in c.req("tools/list", {})["result"]["tools"]:
            print("==", t["name"]); print(t.get("description","")); print(json.dumps(t["inputSchema"])[:3000])
    else:
        a = sys.argv[2] if len(sys.argv)>2 else "{}"
        if a.startswith("@"): a = open(a[1:]).read()
        print(c.call(sys.argv[1], json.loads(a)))
