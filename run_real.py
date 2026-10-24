import os, json, time, sys
os.environ.setdefault("LLM_BASE_URL","https://api.minimaxi.com/v1")
os.environ.setdefault("LLM_MODEL", sys.argv[2] if len(sys.argv)>2 else "MiniMax-M3.1-Flash")
import importlib; A = importlib.import_module(os.environ.get("AGENT_MOD","agent"))
q = sys.argv[1]
t=time.time()
ag = A.build()
log=[]; usage={"in":0,"out":0,"calls":0}
for chunk in ag.stream({"messages":[{"role":"user","content":q}]}, stream_mode="updates", subgraphs=True):
    ns, upd = chunk
    for node, val in (upd or {}).items():
        if not isinstance(val, dict): continue
        for m in val.get("messages", []) or []:
            who = "子智能体" if ns else "主Agent"
            if m.type=="ai":
                u=getattr(m,"usage_metadata",None) or {}
                usage["in"]+=u.get("input_tokens",0); usage["out"]+=u.get("output_tokens",0); usage["calls"]+=1
                for tc in m.tool_calls: log.append(f"[{who}] 调用 {tc['name']} {json.dumps(tc['args'],ensure_ascii=False)[:200]}")
                if not m.tool_calls: log.append(f"[{who}] 回答：{str(m.content)[:1500]}")
            elif m.type=="tool":
                log.append(f"[{who}] ← {m.name} 返回 {len(str(m.content))} 字符：{str(m.content)[:300]!r}")
print("\n".join(log)); print("用时 %.0f 秒"%(time.time()-t), usage)
