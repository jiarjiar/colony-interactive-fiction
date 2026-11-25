#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("殖民地.json")
LAUNCHER = Path(__file__).with_name("剧情游戏启动器.html")
DIRECT_PLAY = Path(__file__).with_name("直接试玩.html")

PALETTE_SCENES = {
    "lab_sunlit": ("日照实验室", "军用白的实验室被蓝星阳光照得没有阴影，玻璃器材沿墙排成一条直线。"),
    "meeting_room": ("一号会议室", "殖民分区图占满墙面，长桌上的文件都朝着同一个方向。"),
    "psych_test": ("心理测试室", "测试仪的彩色代码灯依次点亮，机器的判断没有语气。"),
    "hall_quarters": ("霍尔住舱", "自动浴室、折叠椅和窄床塞在一间灰白舱室里，每件东西都在伸手可及的地方。"),
    "command_room": ("基地指挥室", "地图屏幕和通讯台围住中央长桌，通风声稳定得像一条直线。"),
    "base_entrance": ("基地入口", "两道密封门之间铺着消毒垫，门框把室内与绿色荒野切成两个整齐的矩形。"),
    "field_site": ("野外采集区", "低矮丘陵覆盖着鲜绿植被，车辆停在没有泥痕的硬地上。"),
    "forest_lake": ("湖边森林", "水面静得能照出叶脉，林下没有枯叶，也没有风。"),
    "lab_gas": ("毒气实验室", "密封门闭合后，只剩呼吸头盔的送气声和器材表面均匀的高光。"),
    "comms_room": ("通讯室", "主屏中央悬着巡航舰船长的影像，屏幕下方的基地时钟逐秒前进。"),
    "landing_field": ("降落场", "阳光落在灰色飞船和裸露地面上，着陆场没有被阴影遮住的角落。"),
    "fake_airlock": ("救援舰船闸", "舱门内部没有引导灯，也没有接应人员，脚步声进去后没有回声。"),
    "true_cruiser": ("真巡航舰控制室", "大型控制台围成半圆，戴维斯的金色发辫垂在制服肩章旁。"),
    "isolation_deck": ("巡航舰隔离层", "透明隔板把每个人分开，所有随身物品栏都空着。"),
    "lake_camp": ("湖岸隔离营地", "人群住在离基地很远的草地上，只保留火、饮水和彼此能看见的双手。"),
}

SCENE_IMAGES = {
    "lab_sunlit": "概念图/02-一毫米误差.jpg",
    "meeting_room": "概念图/01-蓝星基地.jpg",
    "psych_test": "概念图/02-一毫米误差.jpg",
    "hall_quarters": "概念图/03-住舱毛巾.jpg",
    "command_room": "概念图/11-通讯室.jpg",
    "base_entrance": "概念图/04-地毯救援.jpg",
    "field_site": "概念图/06-两辆采集车.jpg",
    "forest_lake": "概念图/07-湖岸弃装.jpg",
    "lab_gas": "概念图/08-半间实验室.jpg",
    "comms_room": "概念图/11-通讯室.jpg",
    "landing_field": "概念图/12-静默救援舰.jpg",
    "fake_airlock": "概念图/12-静默救援舰.jpg",
    "true_cruiser": "概念图/13-十五点着陆.jpg",
    "isolation_deck": "概念图/09-显形态.jpg",
    "lake_camp": "概念图/14-湖岸隔离地.jpg",
}

nodes: dict[str, dict] = {}


def scene(scene_id: str, arrival: str = "") -> dict:
    name, desc = PALETTE_SCENES[scene_id]
    obj = {
        "id": scene_id,
        "name": name,
        "type": "major",
        "description": desc,
        "image": SCENE_IMAGES[scene_id],
    }
    if arrival:
        obj["arrival"] = arrival
    return obj


def changes(**kwargs) -> dict:
    out = {}
    set_values = kwargs.pop("set", None)
    if set_values:
        out["set"] = set_values
    for key, value in kwargs.items():
        if value is not None:
            out[key] = value
    return out


def add_node(node_id: str, *, scene_id: str, progress: int, texts: list, choices=None,
             next_id=None, routes=None, chapter=None, ambient=None, effect=None, arrival=""):
    if node_id in nodes:
        raise ValueError(f"duplicate node: {node_id}")
    n = {"scene": scene(scene_id, arrival), "progress": progress, "segments": []}
    if chapter:
        n["chapterTitle"] = chapter
    if ambient:
        n["ambient"] = ambient
    if effect:
        n["effect"] = effect
    for item in texts:
        if isinstance(item, tuple):
            n["segments"].append({"speaker": item[0], "text": item[1]})
        else:
            n["segments"].append({"text": item})
    if choices:
        n["choices"] = choices
    if next_id:
        n["next"] = next_id
    if routes:
        n["routes"] = routes
    nodes[node_id] = n


def c(text: str, next_id: str, *, condition=None, delta=None, flags=None,
      important=None, set_values=None, achievement=None, effect=None) -> dict:
    item = {"text": text, "next": next_id}
    if condition is not None:
        item["condition"] = condition
    ch = {}
    if delta is not None:
        ch["val"] = delta
    if flags:
        ch["addFlags"] = flags if isinstance(flags, list) else [flags]
    if important:
        ch["importantFlag"] = important
    if set_values:
        ch["set"] = set_values
    if achievement:
        ch["unlockAchievement"] = achievement
    if ch:
        item["changes"] = ch
    if effect:
        item["effect"] = effect
    return item


# beat: id, scene, [segments], action, callback, optional decision choices
chapters = [
    ("第一章：无害行星", 5, 16, [
        ("ch1_lab_01", "lab_sunlit", ["蓝星的早晨从实验室东窗照进来。你叫劳伦斯·霍尔，少校，负责给这颗行星签发最后一份生物安全报告。", "报告结论只有两个字：无害。"], "翻到最后一页", "纸页停在签名栏，窗外的绿色没有动。"),
        ("ch1_lab_02", "lab_sunlit", ["弗兰德利中尉靠在标本柜旁，制服领口比规定松了一格。", ("弗兰德利", "只要你签字，殖民船就能开始装货。")], "看向窗外", "树林一直铺到湖边，没有一处腐败的颜色。"),
        ("ch1_lab_03", "lab_sunlit", ["空气样本、土壤样本、微生物培养皿，全都给出同一个结论。", ("弗兰德利", "我们找到了一颗连细菌都很有礼貌的行星。")], "检查培养皿", "培养基表面干净，边缘也没有第二层菌膜。"),
        ("ch1_lab_04", "lab_sunlit", ["桌上只剩最后一个选择：按程序结束检测，或者再做一次没有必要的复核。"], None, None, [
            ("再比对一遍原始数据", "你把三组记录重新并排。弗兰德利没有催你。", {"delta": 10, "flags": "requested_recheck", "achievement": "first_error"}),
            ("在报告上签字", "笔尖划过签名栏。程序终于得到它要的答案。", {"delta": -7}),
        ]),
        ("ch1_lab_05", "lab_sunlit", [("弗兰德利", "人类一来，这地方就不会这么干净了。"), "他说这话时，用指节敲了敲显微镜的金属底座。"], "看看那台显微镜", "底座有一道旧划痕，载物台的压簧微微向内弯。"),
        ("ch1_lab_06", "lab_sunlit", ["会议广播催弗兰德利去一号会议室。", ("弗兰德利", "别让无害行星把你吃了。")], "让他先走", "门合上后，实验室里只剩通风声。"),
        ("ch1_lab_07", "lab_sunlit", ["你把眼睛贴近目镜。镜筒忽然向前滑了一厘米。", "没有齿轮声。"], "扶住镜筒", "冰凉的金属在掌心里继续移动。"),
        ("ch1_lab_08", "lab_sunlit", ["显微镜的镜臂绕过你的肩，压住喉咙。", "载物台像一只钝手，抵住你的下巴。"], "撞向实验台", "玻璃器皿落地，镜臂没有松开。"),
        ("ch1_lab_09", "lab_sunlit", ["你的手碰到枪套。显微镜把重量全部压在颈侧。"], "拔枪射击底座", "枪声把日照切成一瞬白光；金属和透明胶状物一起摊在地面。"),
        ("ch1_lab_10", "lab_sunlit", ["门口没有人。地上的残骸边缘缓慢回缩，像明胶在冷却。"], None, None, [
            ("立刻呼叫弗兰德利", "你按下通讯键，声音比呼吸稳定。", {"delta": -2, "flags": "called_friendly_early"}),
            ("先刮取一点残留物", "你用玻璃片碰了碰乳白残留物；它避开了最亮的地方。", {"delta": 9, "flags": "found_residue"}),
        ]),
        ("ch1_lab_11", "meeting_room", ["一号会议室里，殖民分区图刚投上墙。你中断会议，把弗兰德利带回实验室。", ("弗兰德利", "最好别是咖啡机。")], "推开实验室门", "碎玻璃还在地上，枪痕也在。"),
        ("ch1_lab_12", "lab_sunlit", ["显微镜完整地躺在盒里。旧划痕、弯曲压簧，一样不少。", "地上的乳白残留物不见了。"], "让弗兰德利检查", "他把盒子转了两次，手指停在那道旧划痕上。"),
        ("ch1_lab_13", "lab_sunlit", [("弗兰德利", "它没有离开过盒子。"), "他说得很慢，像在替一台机器作证。"], "指出地上的弹痕", "弹孔真实存在，但它不能说明你射中了什么。"),
        ("ch1_lab_14", "psych_test", ["心理测试室的门在身后闭合。彩色代码灯从红色转到绿色。", "机器要求你描述刚才发生的事。"], "按事实复述", "纸带吐出一串判断代码，末尾标着“高度不稳定”。"),
        ("ch1_lab_15", "psych_test", [("弗兰德利", "休息几个小时。会议我替你挡着。"), "他没有说相信，也没有说不信。"], None, None, [
            ("接受测试结论，停止追查", "你在医疗建议上签名。检测结果重新成为唯一事实。", {"delta": -15, "target": "rash1_01"}),
            ("把报告折起来带走", "纸带的绿灯仍亮着。你把它折成四层。", {"delta": 6}),
        ]),
        ("ch1_lab_16", "psych_test", ["门外的走廊通向住舱。你经过每一把固定椅子时，都看了一眼它们的脚。"], "回住舱", "自动门认出你的身份，向两侧滑开。"),
        ("ch1_lab_17", "hall_quarters", ["浴室已经放好热水，白毛巾挂在金属杆上。", "系统把这一切称作标准配置。"], "关上住舱门", "门锁发出一次短促确认音。"),
        ("ch1_lab_18", "hall_quarters", ["测试报告压在桌角。绿色代码透过纸背，像没有熄灭。"], "走进浴室", "镜前灯从下方亮起，毛巾的影子落在你肩后。"),
    ]),
    ("第二章：日用品", 17, 32, [
        ("ch2_quarters_01", "hall_quarters", ["你伸手拿毛巾。布料先贴住手腕，然后沿小臂向上收紧。", "它没有纤维摩擦的声音。"], "把手臂压进水池", "热水打湿布面，毛巾的收缩没有变慢。"),
        ("ch2_quarters_02", "hall_quarters", ["白布绕到颈后，打了一个没有人系过的结。"], None, None, [
            ("用水龙头卡住毛巾", "你把布结塞进金属弯管，借身体重量向后拉。", {"delta": 5}),
            ("撞开浴室门", "门框刮过肩膀，布料在边角处短暂松开。", {"delta": -2, "set_values": {"hall_condition": "injured"}}),
        ]),
        ("ch2_quarters_03", "hall_quarters", ["毛巾落地后没有摊开，而是向墙角爬了半米。", "你的腰带扣同时转向腹部。"], "扯开腰带", "扣舌擦过制服，留下一道笔直划痕。"),
        ("ch2_quarters_04", "hall_quarters", ["折叠椅挡在门前。它的一条椅腿抬起，又准确落到锁扣上。"], "踢向椅背", "椅子向后滑，没有翻倒；重心像被重新计算过。"),
        ("ch2_quarters_05", "hall_quarters", ["门缝已经足够宽。走廊灯光从外面切进来。"], "侧身挤出去", "椅腿撞在门框上，离你的脚踝差两厘米。"),
        ("ch2_quarters_06", "hall_quarters", ["空走廊里只有指挥室和实验室两个方向。", "你手里没有可以证明毛巾活过的东西。"], None, None, [
            ("直接去指挥室", "你赤着一只脚跑向指挥区，湿手印断断续续。", {"delta": -4}),
            ("先去实验室取残留物", "你绕向实验室，想带回一件不会只存在于口供里的东西。", {"delta": 8, "flags": "found_residue"}),
        ]),
        ("ch2_quarters_07", "command_room", ["莫里森指挥官站在中央长桌旁。她的蓝眼睛先看你，再看你缺了一半的制服。", "细长教鞭停在殖民地图上。"], "说明住舱里的袭击", "指挥室里没有人打断你，通风声因此显得更响。"),
        ("ch2_quarters_08", "command_room", [("莫里森", "测试报告说你需要隔离。"), ("霍尔", "测试报告没有检查那条毛巾。")], "把测试纸放上桌", "绿色代码落在她面前，像一张替你作反证的证件。"),
        ("ch2_quarters_09", "command_room", ["两名卫兵从门侧走来。莫里森没有提高声音。", ("莫里森", "先去医疗室。")], "跟卫兵离开", "其中一人收走你的手枪，却没有碰你的腰带。"),
        ("ch2_quarters_10", "hall_quarters", ["经过泰勒办公室时，里面传来桌脚拖动的声音。", "随后是一声被截断的呼叫。"], "撞开办公室门", "泰勒船长倒在地上，灰色地毯卷住他的胸口。"),
        ("ch2_quarters_11", "hall_quarters", ["泰勒的脸贴着地面。地毯边缘一寸寸向内折。", "卫兵还在判断该向什么开枪。"], None, None, [
            ("射击地毯边缘", "子弹沿卷边打出一排孔，乳白物从纤维下层渗出。", {"delta": 4, "flags": "shot_rug_edge", "set_values": {"morrison_stance": "aligned"}, "achievement": "public_witness"}),
            ("抓住泰勒的手臂向外拖", "你和卫兵一起拖人，地毯在门槛处被拉成薄片。", {"delta": 7, "flags": "saved_taylor_directly", "set_values": {"morrison_stance": "aligned"}}),
        ]),
        ("ch2_quarters_12", "hall_quarters", ["地毯被枪火切断后缩成一团半透明凝胶。", "原来的地毯仍完整铺在桌后。"], "比较两块地毯", "花纹、磨痕、烟灰点全部一致；数量是唯一差别。"),
        ("ch2_quarters_13", "command_room", ["泰勒被抬进指挥室临时医疗区。莫里森把心理报告翻到背面。", ("莫里森", "从头说。只说看见的。")], "从显微镜讲起", "这一次，每个人都在记录。"),
        ("ch2_quarters_14", "command_room", ["显微镜、毛巾、腰带、椅子、地毯。每一件都是无机物。", "每一件在袭击之后，都有一个完整原件出现。"], "把物件列成两列", "左列写原件，右列写复制品；两列的外观没有差别。"),
        ("ch2_quarters_15", "command_room", [("泰勒", "如果它能做成地毯，也能做成门。"), "没有人去看身后的门。"], "检查门框", "密封条安静地贴在槽里，过分平直。"),
        ("ch2_quarters_16", "command_room", ["莫里森下令封闭基地，暂停殖民信号。", "命令通过同一套可能被复制的通讯设备发出去。"], "确认封锁", "屏幕逐一转为黄色待机，基地没有因此变得更安全。"),
        ("ch2_quarters_17", "command_room", ["第一份失联报告出现在右侧屏幕：多兹的住舱没有回应。"], "调出住舱记录", "录音尾声里有布料贴合皮肤的轻响。"),
    ]),
    ("第三章：成双之物", 33, 49, [
        ("ch3_command_01", "command_room", ["多兹的住舱门打开时，两双手套并排放在床上。", "一双有他的体温，另一双也有。"], "查看最后一段录像", "画面里，手套先套住手指，随后替他握紧枪柄。"),
        ("ch3_command_02", "command_room", ["录像停在枪声之前。桌面上的两双手套没有移动。"], None, None, [
            ("比较两双手套的磨损", "掌心折痕完全相同，连一道旧油污的位置都一致。", {"delta": 9, "flags": "studied_pairs", "achievement": "paired_objects"}),
            ("亲自戴上一只验证", "你把手伸向靠近床沿的那只。它的开口微微张大。", {"delta": -12, "target": "rash2_01"}),
        ]),
        ("ch3_command_03", "base_entrance", ["基地入口的监控显示，富尔顿踏上消毒垫后，垫面从四边同时升高。", "镜头另一端，第二块一模一样的垫子仍在门内。"], "暂停在两块垫子同框处", "编号和刮痕一致，只有门槛两侧各有一块。"),
        ("ch3_command_04", "base_entrance", ["幸存的坦纳不肯再跨过任何门槛。", ("坦纳", "它把他往下拉。地上没有洞。")], "检查门框外缘", "垫子消失的位置留下一层无色薄膜。"),
        ("ch3_command_05", "base_entrance", ["薄膜在采样棒前端收缩。它对金属的动作比对皮肤慢。"], "记录反应差异", "记录板上第一次出现可重复的物理差异。"),
        ("ch3_command_06", "command_room", ["莫里森把所有成对物件列为隔离对象。", "霍尔的清单已经延伸到车辆、门和通讯台。"], "接听野外小队", "昂格尔的车载信号夹着发动机噪声。"),
        ("ch3_command_07", "field_site", [("昂格尔", "这里有两辆车。我的编号在两辆车上。"), "通讯画面里，两台灰色采集车停在同一片绿色坡地。"], None, None, [
            ("“不要靠近任何一辆，原地等。”", "昂格尔停在两车之间，把双手举到镜头前。", {"delta": 6}),
            ("“检查轮胎上的泥痕。”", "他蹲下时，右侧车辆的车门自行打开。", {"delta": 10, "flags": "studied_pairs"}),
        ]),
        ("ch3_command_08", "field_site", ["右侧车辆向前滑动，没有发动机声。", "通讯镜头翻倒在草地上，只拍到两条完全相同的轮胎。"], "呼叫昂格尔", "回答你的只有轮胎碾过通讯器的碎裂声。"),
        ("ch3_command_09", "command_room", ["救援组还没出发，湖边小队的频道又亮了。", ("亨德里克斯", "盖尔进树林穿衣服。他没有回来。")], "要求镜头对准林缘", "画面里挂着两件相同的制服上衣。"),
        ("ch3_command_10", "forest_lake", ["你随小队抵达湖边。水面没有波纹，两件制服在树枝上保持同一角度。", "地上没有脚印离开树林。"], "沿通讯线进入林缘", "断线尽头粘着一小片乳白薄膜。"),
        ("ch3_command_11", "forest_lake", ["林中散着靴子、皮带、扣环和采样盒。每件东西都过分完整。", "没有人的痕迹。"], "先检查衣物数量", "有两条皮带，三只左靴，没有右靴。"),
        ("ch3_command_12", "forest_lake", ["一片树叶贴在金属扣上。叶脉不规则，虫咬缺口只出现一次。", "自然物第一次显得比装备可靠。"], "把叶片夹进纸袋", "纸袋本身让你的手停了半秒。"),
        ("ch3_command_13", "forest_lake", ["远处的车辆没有再靠近。莫里森通过通讯要求撤回基地。"], "徒步返回", "你们把所有装备留在原地，赤手走过绿色坡地。"),
        ("ch3_command_14", "command_room", ["地图上的红点增加到五个。每一个红点都对应一件日常物品。", "基地里没有足够空间隔离所有无机物。"], "提出化学显形测试", "莫里森让你列出能与原生质反应、又不腐蚀金属的毒剂。"),
        ("ch3_command_15", "command_room", ["数据库给出砷化氢。无色、剧毒、可燃。", "实验室有一套封闭喷雾系统。"], "打印测试步骤", "纸从打印口伸出时，三个人同时后退。"),
        ("ch3_command_16", "command_room", [("弗兰德利", "我们已经开始怕纸了。"), ("霍尔", "纸至少会燃烧。")], "折起步骤单", "折痕不完全对称。你把它留在手里。"),
        ("ch3_command_17", "command_room", ["莫里森批准局部测试，条件是实验室与基地彻底隔离。", "她在命令末尾加了一句：枪械不得进入毒气区。"], "确认无火花规定", "你的手枪被锁进门外柜中。"),
        ("ch3_command_18", "lab_gas", ["密封门合拢。头盔面罩把每个人的呼吸放大。", "半间实验室静静等在玻璃后面。"], "接通喷雾系统", "压力表指针从零升到绿色区。"),
    ]),
    ("第四章：半间实验室", 50, 66, [
        ("ch4_gas_01", "lab_gas", ["喷雾器旁有两只砷化氢罐。一只足够完成测试。", "第二只是原计划的备用。"], None, None, [
            ("把备用罐留在门外", "你把第二只罐放进独立维护槽，贴上手写编号。", {"delta": 7, "important": {"flag": "kept_arsine_reserve", "label": "留下一罐砷化氢"}, "achievement": "reserve_canister"}),
            ("两罐全部接入系统", "你需要更高浓度，也愿意失去备用方案。", {"delta": -5}),
        ]),
        ("ch4_gas_02", "lab_gas", ["莫里森隔着面罩看向压力表。", ("莫里森", "开始。")], "打开喷雾阀", "无色气体进入房间，没有烟，也没有气味。"),
        ("ch4_gas_03", "lab_gas", ["十秒。所有器材保持原样。", "二十秒。玻璃表面仍旧清楚。"], "继续等待", "第三十秒时，一只烧杯的高光向下滑了一毫米。"),
        ("ch4_gas_04", "lab_gas", ["烧杯边缘变软，像一圈受热的明胶。", "它没有破碎，只是失去自己作为烧杯的必要。"], "记录第一个变化", "时间和位置被写进密封记录器。"),
        ("ch4_gas_05", "lab_gas", ["第二只烧杯没有变化。两者原先放在同一个架子上。", "随后，架子左半边开始下垂。"], "比较显形顺序", "复制物先失去功能结构，最后才失去表面磨损。"),
        ("ch4_gas_06", "lab_gas", ["显微镜、试管架、半张实验桌依次融成乳白与淡琥珀色的胶状物。", "实验室近一半器材都在动。"], None, None, [
            ("继续记录显形顺序", "你把每一次形变按秒标记，直到记录器屏幕占满。", {"delta": 10, "flags": "recorded_dissolve_order", "achievement": "half_a_lab"}),
            ("把门边卫兵拖出软化区", "你抓住他的头盔肩带，把他从下沉的地面边缘拖开。", {"delta": 4, "flags": "saved_guard", "set_values": {"morrison_stance": "aligned"}, "achievement": "half_a_lab"}),
        ]),
        ("ch4_gas_07", "lab_gas", ["一团原本是椅子的胶质扑向门边。", "头盔警示再次显示：砷化氢可燃，禁止火花。"], None, None, [
            ("按下紧急排气", "风机启动，胶质被气流拉成半透明细丝。", {"delta": 5}),
            ("拔出卫兵备用枪开火", "枪口火花亮起的同时，整间实验室的空气变白。", {"delta": -18, "target": "rash3_01", "effect": "flash"}),
        ]),
        ("ch4_gas_08", "lab_gas", ["排气风机把毒气抽向外部焚化槽。复制物失去形状，却仍向较温暖的地方移动。"], "退到隔离门后", "门在胶质碰到门槛前闭合。"),
        ("ch4_gas_09", "lab_gas", ["观察窗后，真实器材立在融解物之间。", "每一件都像在证明自己不是另一件。"], "封死实验室", "机械锁落下三道，没人愿意确认锁本身。"),
        ("ch4_gas_10", "command_room", ["走廊会议没有桌子。所有人站在空地中央，远离墙面。", "莫里森把选择说成三个词：焚毁、留守、撤离。"], "先讨论撤离", "撤离意味着把人带走，同时不带走任何物件。"),
        ("ch4_gas_11", "command_room", [("泰勒", "衣服也是物件。"), ("弗兰德利", "终于有一条命令不需要制服。")], "列出禁止携带物", "武器、衣服、鞋、通信器、纪念品，一项项被划掉。"),
        ("ch4_gas_12", "command_room", ["焚毁整颗行星需要轨道舰队，至少三天。基地未必能撑过三小时。"], "排除立即焚毁", "地图上的红点没有因此减少。"),
        ("ch4_gas_13", "command_room", ["留守意味着永远无法证明下一件物品安全。", "撤离至少能把未知留在蓝星。"], "支持裸体撤离", "莫里森把它写成正式命令，字句比建议更容易服从。"),
        ("ch4_gas_14", "command_room", ["通讯室还有一条巡航舰航线。最近的船是戴维斯指挥的运输巡航舰。"], "转去通讯室", "你们空手穿过走廊，连门卡都留在原处。"),
        ("ch4_gas_15", "comms_room", ["通讯屏亮起前，基地时钟显示13:02。", "信号穿过蓝星大气时出现短暂雪花。"], "发送紧急呼叫", "远端回应比预计快了七秒。"),
        ("ch4_gas_16", "comms_room", ["屏幕上出现戴维斯船长。他眉浓眼大，金色发辫垂在制服肩章旁。", ("戴维斯", "说明撤离条件。")], "说明禁止携带无机物", "戴维斯没有笑，只确认需要多少隔离舱。"),
        ("ch4_gas_17", "comms_room", [("戴维斯", "十五点整到达。不会提前。"), "基地时钟在他说完时跳到13:04。"], "复述十五点整", "戴维斯点头，把约定写进航行记录。"),
        ("ch4_gas_18", "comms_room", ["通讯结束。屏幕重新映出你们自己的脸。", "每张脸周围都有一圈过于整齐的玻璃反光。"], "下令准备撤离", "基地广播只响一次：什么也不要带。"),
    ]),
    ("第五章：什么也不带", 67, 84, [
        ("ch5_comms_01", "comms_room", ["你把戴维斯的到达时间写在玻璃上：15:00。", "数字正下方是继续走动的基地时钟。"], None, None, [
            ("把时间写进撤离口令", "每个小队都必须复述十五点整。", {"delta": 7, "flags": "heard_davis_eta"}),
            ("只传达立即集合", "你省去时间，避免队员把注意力放在等待上。", {"delta": -5}),
        ]),
        ("ch5_evac_02", "hall_quarters", ["住舱门全部打开。队员把衣物堆在门内，赤脚站进走廊。", "没有人愿意靠近任何一堆东西。"], "检查集合人数", "姓名逐一得到回应，声音替代了身份卡。"),
        ("ch5_evac_03", "hall_quarters", ["弗兰德利把一枚旧徽章放在床上。", ("弗兰德利", "它跟了我十二年。现在这算不算证据？")], None, None, [
            ("“放下。十二年也不能证明今天。”", "他把手收回来，徽章留在白色床单中央。", {"delta": 8}),
            ("“记住它的划痕，别碰。”", "他描述那道划痕，像在给遗物做口供。", {"delta": 3}),
        ]),
        ("ch5_evac_04", "hall_quarters", ["莫里森最后一个走出指挥室。她没有带教鞭，也没有军衔标志。", "命令只剩她的声音。"], "向降落场移动", "人群穿过基地时，自动门一扇扇为裸体的军官打开。"),
        ("ch5_evac_05", "base_entrance", ["入口的消毒垫已经被移走，门槛留下两个颜色相同的矩形。", "没人跨得很快。"], "一步跨过门槛", "脚底碰到温暖硬地；什么也没有合拢。"),
        ("ch5_evac_06", "landing_field", ["阳光比基地内更白。远处，一艘灰色巡航舰已经停在降落场。", "没有人记得听见推进器。"], "停下看一眼", "飞船轮廓符合运输巡航舰的标准图纸。"),
        ("ch5_evac_07", "landing_field", ["弗兰德利先笑了一声。", ("弗兰德利", "戴维斯动作真快。")], "看基地时钟", "外墙时钟显示14:50，秒针刚越过十二点。"),
        ("ch5_evac_08", "landing_field", ["约定时间还差十分钟。飞船静止得像一直停在那里。"], None, None, [
            ("记住14:50", "你把时间说出口。莫里森抬头看了同一面钟。", {"delta": 12, "flags": "noticed_clock", "achievement": "ten_minutes"}),
            ("继续集合队伍", "你让队伍保持间距，不让迟疑打乱命令。", {"delta": -6}),
        ]),
        ("ch5_evac_09", "landing_field", ["人群开始向飞船移动。草叶压在赤足下，四周没有风。", "按理说，着陆声会先穿过基地墙。"], None, None, [
            ("让所有人安静十秒", "队伍停下。十秒里只有人的呼吸，没有冷却引擎的金属声。", {"delta": 11, "flags": "noticed_silence", "achievement": "no_landing_sound"}),
            ("催促队伍靠近", "脚步重新响起，把所有缺失的声音盖住。", {"delta": -7}),
        ]),
        ("ch5_evac_10", "landing_field", ["船体表面有均匀的风蚀坑。每一个坑都像从同一张模板复制。", "着陆架周围没有新鲜压痕。"], "走到着陆架侧面", "地面草茎仍直立，没有被推进气流压倒。"),
        ("ch5_evac_11", "landing_field", ["莫里森看向你，又看向地面。", ("莫里森", "你看到了什么？")], None, None, [
            ("指出没有压痕和热迹", "她蹲下，用手背试了试地面的温度。", {"delta": 10, "flags": "checked_hull"}),
            ("“外形符合巡航舰规格。”", "她站直，重新看向舷梯。", {"delta": -5}),
        ]),
        ("ch5_evac_12", "landing_field", ["舷梯从船腹放下。液压机构没有发出声音。", "船闸内没有灯，也没有站在门口接应的人。"], "在舷梯前停下", "后面的人群也停住，队列像撞上一面看不见的墙。"),
        ("ch5_evac_13", "landing_field", ["你朝船闸呼叫戴维斯。黑暗里没有回答。", "通讯约定要求船长先报呼号。"], None, None, [
            ("要求对方回报呼号", "你重复三次。船闸仍旧黑暗，只有舱门边缘慢慢变亮。", {"delta": 12, "flags": "verified_call_sign"}),
            ("把沉默当作自动接驳程序", "你示意第一组登梯。没有人从船内出来阻止。", {"delta": -8}),
        ]),
        ("ch5_evac_14", "landing_field", ["莫里森把脚放上第一阶，又收回来。", "她的蓝眼睛停在船闸两侧完全相同的铆钉上。"], "观察船闸", "引导灯槽里没有灯，只有一层过于均匀的乳白反光。"),
        ("ch5_evac_15", "landing_field", ["你能看见船闸最深处。那里没有隔离员，没有担架，也没有戴维斯。"], None, None, [
            ("记下船闸的黑暗与无人", "你把这个事实告诉莫里森。她没有再踏上舷梯。", {"delta": 8, "flags": "checked_dark_airlock"}),
            ("让第一组先上去", "队员踏上金属阶梯，声音比它应有的更轻。", {"delta": -6}),
        ]),
        ("ch5_evac_16", "landing_field", ["船体没有任何可见编号错误。它不是因为粗糙而可疑，而是因为太完整。", "身后，基地同样安静地等着。"], "回看基地", "窗户反射出飞船，像另一艘灰色船停在墙里。"),
        ("ch5_evac_17", "landing_field", ["弗兰德利站在队伍前端，赤着脚，手里什么也没有。", ("弗兰德利", "我们到底在等什么？")], "指向外墙时钟", "秒针继续走，离十五点还有七分钟。"),
        ("ch5_evac_18", "landing_field", ["莫里森要你给出一个可以执行的命令。", "舷梯、时间、沉默、地面和黑暗都在同一束阳光下。"], "整理你看到的事实", "每条事实单独都不够；放在一起，它们指向同一个缺口。"),
        ("ch5_evac_19", "landing_field", ["船闸边缘垂下一滴灰白物质。它停在半空，又慢慢收回船体。", "只有站得最近的人看见。"], "后退一步", "莫里森跟着后退，人群却还在原地。"),
        ("ch5_evac_20", "landing_field", ["现在必须下令。等待、登船、攻击或彻底隔离，每一种都要用活人承担后果。"], "走到莫里森身边", "她把最后的命令权交给你们共同看见的事实。"),
    ]),
    ("第六章：十五点", 85, 88, [
        ("ch6_field_01", "landing_field", ["外墙时钟显示14:53。假如它是真船，提前到达却没有任何程序应答。", "假如它不是，舷梯就是一张张开的口——但它没有牙，也不需要牙。"], "面对队伍", "所有人都在等你把观察变成行动。"),
        ("ch6_field_02", "landing_field", ["备用砷化氢罐仍在维护槽；真救援约定仍是15:00；基地之外仍有湖岸空地。", "你只能选择一种秩序。"], "作出命令", "莫里森抬起手，准备把命令传给全队。"),
        ("ch6_field_03", "landing_field", ["飞船保持不动。船闸的黑暗没有变化。", "还有不到七分钟。"], "最后核对时钟", "秒针越过刻度，世界没有替你回答。"),
        ("ch6_field_04", "landing_field", ["莫里森低声问了一句。", ("莫里森", "上，还是不上？")], "回答她", "你的声音越过赤裸的人群，落在灰色船体上。"),
    ]),
]


def build_main():
    flat = []
    for chapter, p0, p1, beats in chapters:
        for i, b in enumerate(beats):
            flat.append((chapter if i == 0 else None, p0, p1, i, len(beats), b))
    for idx, (chapter, p0, p1, i, total, b) in enumerate(flat):
        node_id, scene_id, texts, action, callback, decisions = (*b, None) if len(b) == 5 else b
        progress = round(p0 + (p1 - p0) * i / max(total - 1, 1))
        next_main = flat[idx + 1][5][0] if idx + 1 < len(flat) else "ch6_final_decision"
        if decisions:
            choices = []
            for key, (label, cb_text, spec) in enumerate(decisions, 1):
                cb_id = f"{node_id}_cb_{key}"
                target = spec.get("target", next_main)
                choices.append(c(label, cb_id, delta=spec.get("delta"), flags=spec.get("flags"),
                                 important=spec.get("important"), set_values=spec.get("set_values"),
                                 achievement=spec.get("achievement"), effect=spec.get("effect")))
                add_node(cb_id, scene_id=scene_id, progress=progress, texts=[cb_text],
                         choices=[c("继续", target)])
            add_node(node_id, scene_id=scene_id, progress=progress, texts=texts, choices=choices,
                     chapter=chapter, ambient="static" if scene_id in {"psych_test", "command_room", "comms_room"} else "none")
        else:
            cb_id = f"{node_id}_cb"
            add_node(node_id, scene_id=scene_id, progress=progress, texts=texts,
                     choices=[c(action, cb_id)], chapter=chapter,
                     ambient="static" if scene_id in {"psych_test", "command_room", "comms_room"} else "none")
            add_node(cb_id, scene_id=scene_id, progress=progress, texts=[callback], choices=[c("继续", next_main)])


def add_rash(prefix: str, scene_id: str, lines: list[str], ending_id: str, title: str, closing: str):
    for i, line in enumerate(lines, 1):
        nid = f"{prefix}_{i:02d}"
        target = f"{prefix}_{i+1:02d}" if i < len(lines) else ending_id
        add_node(nid, scene_id=scene_id, progress=min(99, 12 + i), texts=[line], choices=[c("继续", target)])
    nodes[ending_id] = {"isEnding": True, "title": title, "type": "RASH ENDING", "progress": 100,
                        "ambient": "static", "achievement": None,
                        "description": lines[-1], "closing": closing, "effect": "silence"}


def add_closure(prefix: str, scene_id: str, lines: list[str], ending_id: str):
    for i, line in enumerate(lines, 1):
        nid = f"{prefix}_{i:02d}"
        if i == len(lines):
            add_node(nid, scene_id=scene_id, progress=99, texts=[line], next_id=ending_id)
            continue
        target = f"{prefix}_{i+1:02d}"
        action = "继续" if i % 3 else "看清接下来发生的事"
        add_node(nid, scene_id=scene_id, progress=min(98, 88 + i), texts=[line], choices=[c(action, target)])


build_main()

# Final decision and wait routing.
add_node("ch6_final_decision", scene_id="landing_field", progress=89,
         texts=["你把所有物理事实放在同一个命令里。不同的人会因为不同证据停步。"],
         choices=[
             c("“谁也不要靠近任何飞船。我们留在蓝星。”", "end_quarantine_01",
               condition={"all": [{"flag": "noticed_clock"}, {"flag": "noticed_silence"}, {"flag": "checked_hull"}, {"flag": "checked_dark_airlock"}, {"flag": "heard_davis_eta"}]},
               delta=15, important={"flag": "committed_quarantine", "label": "拒绝一切飞船"}, set_values={"evacuation_order": "quarantine"}),
             c("用备用砷化氢验证并烧毁这艘船", "end_burn_01", condition="hasFlag 'kept_arsine_reserve'",
               delta=6, important={"flag": "committed_burn", "label": "点燃救援舰"}, set_values={"evacuation_order": "burn"}),
             c("“再等到十五点，并要求戴维斯回报呼号。”", "ch6_wait_route",
               condition="hasFlag 'noticed_clock'", delta=10,
               important={"flag": "committed_wait", "label": "延迟十分钟"},
               flags="held_morrison_back", set_values={"evacuation_order": "wait"}),
             c("“按撤离命令登船。”", "end_original_01", condition="default", delta=-10,
               set_values={"evacuation_order": "board"}),
         ])
add_node("ch6_wait_route", scene_id="landing_field", progress=90,
         texts=["你让全队退离舷梯，要求船内回应。黑暗没有给出呼号。"],
         routes=[
             {"condition": {"all": [{"flag": "noticed_clock"}, {"flag": "noticed_silence"}, {"flag": "verified_call_sign"}]}, "next": "end_rescue_01"},
             {"condition": "default", "next": "end_partial_01"},
         ])

# Rash endings.
add_rash("rash1", "psych_test", [
    "你把测试纸交回医疗系统，允许它替你解释显微镜。",
    "殖民会议在一小时后恢复，暂停信号被撤销。",
    "第一批物资进入基地；仓库管理员报告出现了重复编号。",
    "三天后，两艘外形相同的补给艇同时停在轨道码头。",
    "没有人能指出哪一艘是后来出现的。",
    "一个月后，你在返航医疗舱里接受治疗，舷窗外有两个相同的地球。",
    "报告仍写着：蓝星环境检测合格。",
], "ending_rash_tested", "检测合格", "世界接受了结论。结论也接受了世界。")
add_rash("rash2", "command_room", [
    "你把手伸进靠近床沿的手套，内衬贴合每一条掌纹。",
    "它在腕部收紧时没有留下折痕。",
    "另一只相同手套躺在床上，救援人员无法确认哪一只该切开。",
    "你试图拔枪，五根手指替你握住枪柄。",
    "莫里森命令封闭住舱，门内只剩均匀的布料摩擦声。",
    "三天后，手套在密封袋里恢复普通形状。",
    "事故记录把这次验证称作未经批准的人体实验。",
], "ending_rash_glove", "第二只手套", "它学会了你的手。你没有学会它。")
add_rash("rash3", "lab_gas", [
    "扳机扣下，枪口火花先于子弹出现。",
    "无色气体在一瞬间变成白光，隔离门自动落锁。",
    "莫里森从观察窗外看见器材和人影一起失去边界。",
    "排气系统烧毁，基地失去唯一可用的显形实验。",
    "三天后，幸存者仍不敢触碰任何开关。",
    "救援舰收到的最后一条完整记录只剩一行：砷化氢可燃。",
    "实验室被永久封存，里面的形状继续缓慢改变。",
], "ending_rash_spark", "无火花规定", "规定不是因为谨慎而存在。它来自已经发生过的火。")

# Formal closures.
add_closure("end_original", "fake_airlock", [
    "你让队伍继续登梯。莫里森停了一秒，随后服从自己的撤离命令。",
    "弗兰德利进入船闸，回头说这里连灯都舍不得开。",
    "他的声音没有回声。下一个人跟着消失在黑暗里。",
    "你最后一次看基地时，外墙时钟显示14:56。",
    "船闸地面微温，触感不像金属，也不像皮肤。",
    "舱门在最后一人进入后合拢，接缝没有机械运动。",
    "灰色船体恢复成一块没有开口的完整表面。",
    "十五点整，另一阵推进声从云层上方压下来。",
    "真正的戴维斯按约定着陆，草地被气流压成向外的圆。",
    "他呼叫霍尔、莫里森和基地，没有人回答。",
    "观察镜显示降落场空无一物，地面也没有第二艘船的压痕。",
    "戴维斯把等待时间延长到十五分钟，然后开始写失联报告。",
    "三天后，轨道搜索把着陆场分成小格；每一格都只有真船留下的烧痕。",
    "一个月后，名单上的人仍被标成失踪，因为没有遗体，也没有残骸。",
    "最后一段船闸录像被封进只读档案；黑暗里始终没有出现一盏灯。",
    "报告第一句仍然是：蓝星环境无已知危险。"
    "他删掉了那一句，重新开始。",
], "ending_original")
add_closure("end_partial", "landing_field", [
    "你拉住莫里森，要求她和你再等十分钟。证据不足以让全队服从。",
    "弗兰德利说会在船上替你留一条毯子，然后带着其他人登梯。",
    "假船没有催促。它只在最后一人进去后合上舱门。",
    "灰色轮廓向上移动，没有风，也没有声音，随后从天空消失。",
    "十四点五十九分，地面只剩你和莫里森赤脚站着。",
    "十五点整，推进器的震动先穿过脚底，再传到空气。",
    "戴维斯的真船在远处降落，草和尘土向四周倒伏。",
    "你们通过呼号确认身份，仍然等到他本人出现在舱门口。",
    "三天后，你和莫里森在透明隔板两侧复盘每一个失去的人。",
    "队员留下的衣物和记录被逐件装箱，却没有一只箱子获准离开轨道。",
    "一个月后，调查委员会把事故写成判断与指挥失败。"
    "莫里森在签字前加了一行：两名幸存者也属于失败的一部分。",
    "那只慢了十分钟的基地时钟被装进真空证物箱，再也没有人校准它。",
], "ending_partial")
add_closure("end_rescue", "landing_field", [
    "你说出三个事实：时间未到、没有着陆声、呼号无人回应。",
    "莫里森把它们重复一遍，然后命令全员后撤到空地。",
    "假船的舷梯保持放下，像一项等待签字的程序。",
    "两分钟后，船体边缘开始下垂，风蚀坑连成乳白细线。",
    "队员没有开枪。所有人只是继续后退。",
    "十四点五十九分，假船收起舷梯，整个轮廓向内塌缩。",
    "十五点整，真正的推进声越过山脊；地面先震动，随后扬尘。",
    "戴维斯在空中保持距离，按约定回报呼号和航行记录编号。",
    "第一组人员裸体进入独立隔离舱，舱门只由船内人员操作。",
    "每个人先报出名字，再由两名同伴从远处确认；没有任何物件替人作证。",
    "弗兰德利隔着透明墙说，这次灯至少是亮的。",
    "莫里森逐项撤销旧撤离命令，把那十分钟写成新程序的第一条。",
    "三天后，全员仍分舱生活，禁止接触任何个人物品。",
    "假船消失的位置被轨道镜反复拍摄，草地上只剩一圈没有热量的压痕。"
    "一个月后，地球冻结蓝星殖民计划，建立无机拟态隔离标准。",
    "莫里森在听证会上没有称你勇敢，只说你要求大家多等了十分钟。",
    "基地时钟与通讯记录被封存；它们不再证明真实，只证明误差曾被看见。",
], "ending_rescue")
add_closure("end_burn", "landing_field", [
    "你让人取来维护槽里的备用砷化氢罐。手写编号仍在。",
    "队伍把罐体滚向舷梯，没有人用手扶住它。",
    "气体被送进船闸，灰色墙面从内侧变成乳白。",
    "飞船仍维持轮廓，像一张纸拒绝承认自己正在湿透。",
    "你命令所有人退到着陆场外，只留远程点火线。",
    "若卫兵获救，他替你接通最后一个端口；否则你自己留在维护沟里。",
    "点火不是爆炸声，而是一阵短促的白光，随后才有热浪。",
    "假船的外壳向地面摊开，数千吨形状变成一层颤动薄膜。",
    "十五点整，真船只能在高空盘旋，着陆场被有毒燃烧物覆盖。",
    "你通过无线电逐字解释火场；戴维斯没有祝贺，只把真船再升高两百米。",
    "三天后，幸存者沿湖岸移动，等轨道救援建立新的接触程序。",
    "每次白色薄膜在灰烬下鼓起，卫兵就后退，不再用枪验证它。",
    "一个月后，军方把蓝星列为永久封锁区。"
    "行动报告称未知载体已被销毁，却没人能证明被销毁的是唯一一个。",
    "烧毁的备用罐留在维护沟底，编号只剩一半。",
], "ending_burn")
add_closure("end_quarantine", "lake_camp", [
    "你拒绝登上眼前的船，也要求十五点到达的船不要着陆。",
    "莫里森把命令传给全队：离开基地，去湖岸，只带身体。",
    "假船在降落场等待到十五点前一秒，然后无声离开。",
    "真巡航舰按时出现在云层上方，推进声让湖面起了第一圈波纹。",
    "你用语音告诉戴维斯保持轨道，不投送任何设备。",
    "戴维斯问你们能坚持多久。没有人给出符合规格的答案。",
    "三天后，队员用火、石头和活植物划出营地边界。",
    "基地仍在远处反光，门会自动打开，但没有人回去。",
    "第一场雨冲散营地标记，所有人重新用脚步量出同一条边界。",
    "弗兰德利开始用太阳高度计时，不再问现在几点。",
    "轨道舰投下过一次密封补给；补给落在界外，直到夜里也没人触碰。",
    "一个月后，地球宣布蓝星永久禁入。你们被称为隔离居民，不是幸存者。",
    "家属收到的是隔离期限未定，而不是死亡通知；两个说法都没有归期。"
    "军衔仍在声音里，但轮值表由所有人共同记住，不写在任何物件上。",
    "莫里森每天与轨道通讯一次；戴维斯每次都重新报出完整呼号。",
    "湖岸没有墙，只有每个人都同意不跨过的距离。",
    "基地里的衣服、武器和时钟留在原处，逐渐分不清哪些曾被人使用。",
    "傍晚，湖面映出两个太阳般的亮点。你没有走近确认。",
], "ending_quarantine")

# Ending pages: judgment, not plot summary.
ENDING_PAGES = {
    "ending_original": ("比人更大的仿制品", "TRUE ENDING", "救援按时抵达。只是你们登上的，不是救援。", "完美的复制品不需要骗过所有人。它只需要被当成应该出现的东西。", "original_end"),
    "ending_partial": ("留在地面的人", "BRANCH ENDING", "十分钟救下了两个人，也把其他人的缺席固定成余生。", "你看见了误差。你没有让所有人都停下来。", "partial_end"),
    "ending_rescue": ("按时抵达", "NORMAL ENDING", "所有人活着离开蓝星，隔离从此成为一种新的日常。", "他们没有识破世界。他们只是多等了十分钟。", "rescue_end"),
    "ending_burn": ("燃烧的归途", "BRANCH ENDING", "火证明那艘船能够被毁，却没有证明剩下的东西真实。", "有些归途只能先被烧掉。", "burn_end"),
    "ending_quarantine": ("无物之地", "HIDDEN ENDING", "你们保住了地球，也失去了回到地球的资格。", "当一切外形都可能撒谎，距离成了最后一种诚实。", "quarantine_end"),
}
for eid, (title, typ, desc, closing, ach) in ENDING_PAGES.items():
    nodes[eid] = {"isEnding": True, "title": title, "type": typ, "progress": 100,
                  "ambient": "static" if eid != "ending_quarantine" else "wind",
                  "achievement": ach, "description": desc, "closing": closing,
                  "effect": "silence"}

achievements = {
    "first_error": {"title": "一毫米", "description": "第一次主动复核‘无害’结论。"},
    "public_witness": {"title": "共同目击", "description": "在地毯袭击中保住公开证据。"},
    "paired_objects": {"title": "成双之物", "description": "确认原件与复制品能够同时存在。"},
    "half_a_lab": {"title": "半间实验室", "description": "见证砷化氢让复制物显形。"},
    "reserve_canister": {"title": "留下一罐", "description": "为还不知道的危险保留一种办法。"},
    "ten_minutes": {"title": "十分钟", "description": "注意到救援舰比约定时间早到。"},
    "no_landing_sound": {"title": "没有声音", "description": "停下来听见缺失的着陆声。"},
    "original_end": {"title": "比人更大的仿制品", "description": "到达原作真结局。"},
    "partial_end": {"title": "地面上的两个人", "description": "让两个人留下。"},
    "rescue_end": {"title": "按时抵达", "description": "让全队等到真正的十五点。"},
    "burn_end": {"title": "燃烧的归途", "description": "毁掉最大的复制品。"},
    "quarantine_end": {"title": "无物之地", "description": "拒绝一切无法证明的救援。"},
}

story = {
    "meta": {
        "title": "殖民地",
        "author": "菲利普·迪克｜互动改编",
        "version": "1.0.0",
        "description": "蓝星被判定绝对安全之后，基地里的无机物开始复制、移动并捕食。你是霍尔少校，必须在每一件完美物品中寻找一毫米误差。",
        "theme": "void",
        "ambient": "none",
        "readingMode": "grouped",
        "cover": {"label": "COLONY", "tagline": "正常光线下，完美表面出现一毫米错误。"},
        "variableName": "误差",
        "initialVariable": 38,
    },
    "startNodeId": "ch1_lab_01",
    "variables": {"morrison_stance": "formal", "evacuation_order": "board", "hall_condition": "fit"},
    "achievements": achievements,
    "nodes": nodes,
}


def validate(data: dict):
    ns = data["nodes"]
    refs = []
    for nid, n in ns.items():
        if n.get("isEnding"):
            continue
        if not any(k in n for k in ("choices", "next", "routes")):
            raise AssertionError(f"dead end: {nid}")
        if n.get("next"):
            refs.append((nid, n["next"]))
        refs += [(nid, x["next"]) for x in n.get("choices", [])]
        refs += [(nid, x["next"]) for x in n.get("routes", [])]
    missing = [(src, dst) for src, dst in refs if dst not in ns]
    if missing:
        raise AssertionError(f"missing refs: {missing[:10]}")
    reachable = set()
    stack = [data["startNodeId"]]
    while stack:
        nid = stack.pop()
        if nid in reachable:
            continue
        reachable.add(nid)
        n = ns[nid]
        if n.get("next"):
            stack.append(n["next"])
        stack += [x["next"] for x in n.get("choices", [])]
        stack += [x["next"] for x in n.get("routes", [])]
    unreachable = set(ns) - reachable
    if unreachable:
        raise AssertionError(f"unreachable: {sorted(unreachable)[:10]}")
    endings = [n for n in ns.values() if n.get("isEnding")]
    if len(endings) != 8:
        raise AssertionError(f"expected 8 endings, got {len(endings)}")
    if not 270 <= len(ns) <= 320:
        raise AssertionError(f"node count outside target: {len(ns)}")
    return len(ns), len(endings)


def build_direct_play(data: dict) -> None:
    if not LAUNCHER.exists():
        raise FileNotFoundError(f"missing launcher: {LAUNCHER}")
    source = LAUNCHER.read_text(encoding="utf-8")
    marker = "    applySettings();\n    renderCachedStories();\n  </script>"
    if source.count(marker) != 1:
        raise AssertionError("launcher boot marker changed; direct-play build needs review")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    boot = (
        "    applySettings();\n"
        "    renderCachedStories();\n"
        f"    const AUTOLOAD_STORY = {payload};\n"
        "    loadStory(AUTOLOAD_STORY, { animate: false, cache: false });\n"
        "    startGame(Boolean(getValidAutoSave()));\n"
        "  </script>"
    )
    DIRECT_PLAY.write_text(source.replace(marker, boot), encoding="utf-8")


count, ending_count = validate(story)
OUT.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
build_direct_play(story)
print(
    f"generated {OUT} and {DIRECT_PLAY}: "
    f"{count} nodes, {ending_count} endings, {len(achievements)} achievements"
)
