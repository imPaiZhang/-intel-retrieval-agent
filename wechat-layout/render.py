# 技术专栏 · 公众号排版（draft.md → 内联 HTML）。运行：cd layout && python3 render.py
import re, base64, html
A = '#2457F5'; INK = '#141414'; G = '#8A8F98'; SOFT = '#F3F6FF'; CODEBG = '#1E2230'
md = open('../draft.md', encoding='utf-8').read()

def esc(t): return html.escape(t, quote=False)
def inl(t):
    parts = re.split(r'(`[^`]+`)', t)
    out = []
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p) > 2:
            out.append(f'<code style="font-family:Menlo,Consolas,monospace;font-size:14px;color:{A};background:{SOFT};background-color:{SOFT};padding:1px 5px;border-radius:3px;">{esc(p[1:-1])}</code>')
        else:
            s = esc(p)
            s = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="font-weight:800;color:{INK};">\1</strong>', s)
            out.append(s)
    return ''.join(out)

P = f'margin:0;padding:0 0 18px;font-size:16px;line-height:1.9;color:#2A2A2A;letter-spacing:0.4px;text-align:justify;'
def para(t): return f'<p style="{P}">{inl(t)}</p>'

def code(lines, lang):
    body = '<br/>'.join(esc(l).replace(' ', '&nbsp;') or '&nbsp;' for l in lines)
    tag = f'<p style="margin:0 0 8px;font-size:11px;line-height:1.2;color:#7C86A2;letter-spacing:2px;font-family:Menlo,Consolas,monospace;">{esc(lang.upper() or "OUTPUT")}</p>'
    return (f'<section style="box-sizing:border-box;margin:4px 0 22px;padding:14px 14px 16px;background:{CODEBG};background-color:{CODEBG};border-radius:8px;color:#E6E9F2;">{tag}'
            f'<p style="margin:0;font-size:12.5px;line-height:1.75;color:#E6E9F2;font-family:Menlo,Consolas,\'Courier New\',monospace;word-break:break-all;white-space:normal;">{body}</p></section>')

def ul(items):
    lis = ''.join(f'<p style="margin:0 0 10px;padding:0 0 0 18px;font-size:16px;line-height:1.85;color:#2A2A2A;"><span style="display:inline-block;width:18px;margin-left:-18px;color:{A};font-weight:900;">•</span>{inl(i)}</p>' for i in items)
    return f'<section style="box-sizing:border-box;margin:0 0 18px;padding:14px 16px 6px;background:{SOFT};background-color:{SOFT};border-radius:8px;">{lis}</section>'

def table(rows):
    rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\|[\s\-|]+\|$', r.strip())]
    h, body = rows[0], rows[1:]
    th = ''.join(f'<td style="padding:9px 8px;font-size:14px;font-weight:800;color:#FFFFFF;background:{A};background-color:{A};border:1px solid {A};text-align:center;">{inl(c) or "&nbsp;"}</td>' for c in h)
    trs = ''
    for i, r in enumerate(body):
        bg = '#FFFFFF' if i % 2 == 0 else SOFT
        trs += '<tr>' + ''.join(f'<td style="padding:9px 8px;font-size:14px;line-height:1.5;color:#2A2A2A;background:{bg};background-color:{bg};border:1px solid #DDE3F3;text-align:{"left" if j==0 else "center"};{"font-weight:700;" if j==2 else ""}">{inl(c)}</td>' for j, c in enumerate(r)) + '</tr>'
    return f'<section style="box-sizing:border-box;margin:4px 0 22px;"><table style="width:100%;max-width:100%;border-collapse:collapse;"><tbody><tr>{th}</tr>{trs}</tbody></table></section>'

def h2(t):
    m = re.match(r'([一二三四五六七八九十]+)、(.+)', t)
    num = '0' + str('一二三四五六七八九'.index(m.group(1)) + 1) if m else ''
    title = m.group(2) if m else t
    return (f'<section style="box-sizing:border-box;margin:40px 0 20px;">'
            f'<p style="margin:0;font-size:44px;line-height:1;font-weight:900;color:{A};font-family:Impact,\'Arial Narrow\',sans-serif;letter-spacing:-1px;">{num}</p>'
            f'<section style="box-sizing:border-box;width:36px;height:4px;margin:10px 0 12px;background:{A};background-color:{A};"></section>'
            f'<p style="margin:0;font-size:20px;line-height:1.5;font-weight:900;color:{INK};">{inl(title)}</p></section>')

def img_src(name, embed):
    if not embed: return 'img/' + name
    return 'data:image/jpeg;base64,' + base64.b64encode(open('img/' + name, 'rb').read()).decode()

def shot(name, cap, embed):
    return (f'<section style="box-sizing:border-box;margin:2px 0 24px;padding:8px;background:#F5F6F8;background-color:#F5F6F8;border-left:3px solid {A};">'
            f'<img src="{img_src(name, embed)}" alt="{esc(cap)}" style="width:100%;max-width:100%;height:auto;display:block;border:1px solid #E4E7EC;"/>'
            f'<p style="margin:8px 0 0;font-size:12px;line-height:1.6;color:{G};">{esc(cap)}　<span style="color:{A};font-weight:700;">图源：LangChain 博客原文截图</span></p></section>')

def todo(t):
    return (f'<section style="box-sizing:border-box;margin:6px 0 14px;padding:12px 14px;background:#FFF6D9;background-color:#FFF6D9;border:2px dashed #F2B705;">'
            f'<p style="margin:0 0 4px;font-size:11px;font-weight:800;letter-spacing:2px;color:#B07A00;">TODO · 发布前替换本框</p>'
            f'<p style="margin:0;font-size:14px;line-height:1.7;font-weight:700;color:{INK};">{esc(t)}</p></section>')

SHOTS = [  # 段落开头 → 段后插图
    ('正好 10 月 23 日', 'LC01-原文标题.jpg', 'LangChain 10 月 23 日发布的《Context Engineering Starts with Retrieval》'),
    ('LangChain 那篇文章把检索出问题归成三种', 'LC02-三种检索问题.jpg', '原文：检索出问题的三种情况——找得太笨、一次拿太多、拿回来的不对或过期'),
    ('对应这三个问题', 'LC03-harness总览.jpg', '原文配图：Agent = 模型 + harness，三类问题各有对应的工具'),
    ('这个工具最关键的设计', 'LC04-返回文件路径.jpg', '原文：让检索工具只返回文件路径，正文存到 /retrieved/'),
    ('这里有一个很容易忽略的地方', 'LC05-子智能体筛选.jpg', '原文：主 Agent 和子智能体用同一个 backend；搜索、分派、汇总三步'),
    ('到这里，按 LangChain 文章的说法', 'LC06-大结果转存.jpg', '原文：超过约 2 万 token 的工具结果，会被转存到 /large_tool_results/'),
    ('这就是 LangChain 文章里说的 grep 的局限', 'LC07-grep的局限.jpg', '原文：grep 只认你给的那几个字，搜“Company A funding”会漏掉换了说法的标题'),
    ('第一，检索出来的文字永远是资料', 'LC08-检索文本不可信.jpg', '原文：检索到的文字是资料不是指令，没有任何提示词写法能完全防住提示注入'),
    ('回过头看，LangChain 那篇文章', 'LC09-五条检索策略.jpg', '原文最后总结的五条检索策略'),
]

def build(embed):
    lines = md.split('\n'); i = 0; out = []
    title = lines[0].lstrip('# ').strip()
    out.append(f'<section style="box-sizing:border-box;padding:26px 0 6px;"><section style="box-sizing:border-box;width:48px;height:5px;margin:0 0 14px;background:{A};background-color:{A};"></section>'
               f'<p style="margin:0;font-size:24px;line-height:1.45;font-weight:900;color:{INK};">{esc(title)}</p>'
               f'<p style="margin:12px 0 26px;font-size:12px;line-height:1.5;color:{G};letter-spacing:3px;">排长 &nbsp;·&nbsp; 技术专栏 &nbsp;·&nbsp; 2026.10</p></section>')
    i = 1
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('```'):
            lang = l[3:].strip(); j = i + 1; buf = []
            while not lines[j].startswith('```'): buf.append(lines[j]); j += 1
            out.append(code(buf, lang)); i = j + 1; continue
        if l.startswith('## '): out.append(h2(l[3:].strip())); i += 1; continue
        if l.strip() == '---':
            out.append(f'<section style="box-sizing:border-box;margin:34px 0 18px;border-top:1px solid #E5E7EB;"></section>'); i += 1; continue
        if l.startswith('|'):
            buf = []
            while i < len(lines) and lines[i].startswith('|'): buf.append(lines[i]); i += 1
            out.append(table(buf)); continue
        if l.startswith('- '):
            buf = []
            while i < len(lines) and lines[i].startswith('- '): buf.append(lines[i][2:]); i += 1
            if '待排长补' in ''.join(buf) or out and '参考资料' in out[-1]:
                refs = ''
                for b in buf:
                    if '待排长补' in b: refs += todo('代码与测试脚本：填代码仓库或网盘链接（code.zip 已打包好）')
                    else: refs += f'<p style="margin:0 0 6px;font-size:12px;line-height:1.7;color:{G};word-break:break-all;">{inl(b)}</p>'
                out.append(refs)
            else:
                out.append(ul(buf))
            continue
        if l.strip() == '参考资料':
            out.append(f'<p style="margin:0 0 10px;font-size:13px;font-weight:800;color:#555;letter-spacing:2px;">参考资料</p>'); i += 1; continue
        # 普通段落（单行）
        out.append(para(l.strip()))
        for k, name, cap in SHOTS:
            if l.startswith(k): out.append(shot(name, cap, embed))
        i += 1
    return (f'<section style="box-sizing:border-box;max-width:100%;margin:0 auto;padding:0 16px 28px;background:#FFFFFF;background-color:#FFFFFF;'
            f'font-family:-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">' + ''.join(out) + '</section>')

open('wechat-body-fragment.html', 'w', encoding='utf-8').write(build(False))
body = build(True)
open('preview.html', 'w', encoding='utf-8').write(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>预览 · 让 Agent 只读该读的那几条</title>
<style>body{{margin:0;background:#E9EBEF;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}.bar{{max-width:430px;margin:16px auto 0;display:flex;gap:8px}}button{{flex:1;padding:12px;border:0;background:{A};color:#fff;font-weight:700;letter-spacing:2px;cursor:pointer}}.tip{{max-width:430px;margin:8px auto 0;font-size:12px;color:#666;line-height:1.6}}.phone{{max-width:430px;margin:12px auto 40px;background:#fff;box-shadow:0 8px 30px rgba(0,0,0,.1)}}</style></head>
<body><div class="bar"><button onclick="cp()">复制正文到公众号</button></div><div class="tip">电脑浏览器打开，点按钮后到公众号编辑器 Cmd/Ctrl+V。图片若没粘上，按图注顺序从「原图」文件夹手动上传。</div><div class="phone"><div id="wechat-content">{body}</div></div>
<script>function cp(){{var r=document.createRange();r.selectNodeContents(document.getElementById("wechat-content"));var s=window.getSelection();s.removeAllRanges();s.addRange(r);document.execCommand("copy");s.removeAllRanges();alert("已复制，去公众号编辑器粘贴");}}</script></body></html>''')
print('ok', len(body))
