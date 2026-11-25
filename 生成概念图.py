#!/usr/bin/env python3
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "概念图"
ARTS = (
    ('01-蓝星基地', '蓝星基地', '安全评估：无已知危险'),
    ('02-一毫米误差', '一毫米误差', '显微镜的高光向下滑动'),
    ('03-住舱毛巾', '住舱毛巾', '布料先于手臂收紧'),
    ('04-地毯救援', '地毯救援', '公开证据第一次留在所有人眼前'),
    ('05-两双手套', '两双手套', '磨损、油污和折痕完全一致'),
    ('06-两辆采集车', '两辆采集车', '同一个编号停在坡地两侧'),
    ('07-湖岸弃装', '湖岸弃装', '自然物第一次比装备可靠'),
    ('08-半间实验室', '半间实验室', '砷化氢把复制物从用途还原成形状'),
    ('09-显形态', '显形态', '没有血液和器官，只有失去用途的乳白薄膜'),
    ('10-无物撤离', '无物撤离', '只带身体离开基地'),
    ('11-通讯室', '通讯室', '标准呼号必须由人回答'),
    ('12-静默救援舰', '静默救援舰', '它提前十分钟出现，草地没有听见'),
    ('13-十五点着陆', '十五点着陆', '先有脚底的震动，随后才有飞船'),
    ('14-湖岸隔离地', '湖岸隔离地', '距离成为最后一种诚实'),
)
missing = [f"{slug}.jpg" for slug, _, _ in ARTS if not (OUT / f"{slug}.jpg").is_file()]
if missing:
    raise FileNotFoundError(f"缺少概念图：{', '.join(missing)}")

cards = "\n".join(
    f'''<figure><a href="{slug}.jpg"><img src="{slug}.jpg" alt="{escape(title)}"></a><figcaption><b>{i:02d} · {escape(title)}</b><span>{escape(subtitle)}</span></figcaption></figure>'''
    for i, (slug, title, subtitle) in enumerate(ARTS, 1)
)
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>《殖民地》概念图总览</title><style>
:root{{--ink:#18201e;--paper:#e4e6e2;--muted:#9aa19c;--leaf:#7daa5a;--warn:#d78458}}*{{box-sizing:border-box}}body{{margin:0;background:var(--ink);color:var(--paper);font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC",sans-serif}}header{{max-width:1400px;margin:auto;padding:64px 28px 32px;display:flex;justify-content:space-between;gap:30px;align-items:end}}h1{{font-size:clamp(38px,6vw,82px);margin:0;letter-spacing:.08em}}header p{{max-width:560px;color:var(--muted);line-height:1.8;margin:0}}main{{max-width:1400px;margin:auto;padding:20px 28px 90px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:34px}}figure{{margin:0;background:#25302d;border:1px solid #525a58;border-radius:18px;overflow:hidden}}img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;transition:.2s}}a:hover img{{filter:brightness(1.06)}}figcaption{{padding:18px 20px 22px;display:flex;justify-content:space-between;gap:18px;align-items:baseline}}figcaption b{{font-size:20px}}figcaption span{{color:var(--muted);font-size:14px;text-align:right}}footer{{max-width:1400px;margin:auto;padding:0 28px 60px;color:var(--muted);line-height:1.8}}@media(max-width:800px){{header{{display:block}}header p{{margin-top:20px}}main{{grid-template-columns:1fr}}figcaption{{display:block}}figcaption span{{display:block;text-align:left;margin-top:8px}}}}</style></head><body><header><div><small>PHILIP K. DICK · INTERACTIVE ADAPTATION</small><h1>殖民地</h1></div><p>十四张视觉开发图以正常日光、冷静观察和可测量的物理误差为核心。复制物没有怪物外形；它们只比真实物品更整齐、更饱和，也更愿意执行“物品”的用途。</p></header><main>{cards}</main><footer>视觉锚点：正常光线而非黑暗｜乳白半透明显形态｜复制品反光过度均匀｜为剧情 UI 保留负空间｜无血液与器官意象。点击任意画面可打开原尺寸 JPG。</footer></body></html>'''
(OUT / "总览.html").write_text(html, encoding="utf-8")
print(f"已更新 {len(ARTS)} 张概念图的总览页：{OUT}")
