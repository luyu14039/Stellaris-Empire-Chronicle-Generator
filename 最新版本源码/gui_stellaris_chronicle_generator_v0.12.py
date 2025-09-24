#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern GUI (beta) for Stellaris Chronicle Generator
依赖: customtkinter
安装: pip install customtkinter

说明:
 - 本文件为全新现代化界面，不修改原来的 gui_stellaris_chronicle_v0.03_5.py
 - 保留动态加载 StellarisChronicleGenerator 类逻辑
 - 日志彩色输出、线程安全更新、进度条与阶段显示
 - 动态按钮反馈：运行中变色 + 文本变化 + 禁用其他控件
 - Tooltips & 右键菜单
"""

import os
import sys
import queue
import threading
import traceback
import importlib.util  # 仍保留，若未来需要动态扩展
from datetime import datetime
from typing import Optional, Dict
import webbrowser
import json
import urllib.request
import urllib.error

# ------------------ 项目元信息（集中在 version.py） ------------------
try:
    from version import VERSION, GITHUB_URL, REPO_OWNER, REPO_NAME, PREF_CHANNEL
except Exception:
    # 回退：若缺失 version.py，提供安全默认值并警告
    VERSION = "0.0.0"
    REPO_OWNER = "luyu14039"
    REPO_NAME = "Stellaris-Empire-Chronicle-Generator"
    GITHUB_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
    PREF_CHANNEL = "releases"
    print("⚠ 未找到 version.py，使用默认版本信息。")

try:
    import customtkinter as ctk
except ImportError:
    print("请先安装依赖: pip install customtkinter")
    raise

"""
为便携性起见，直接内嵌核心生成器（原 stellaris_chronicle_generator_v0.03.py）。
这样只需保留本文件与 version.py 即可运行 GUI。
若未来仍想使用外部独立脚本，可恢复原动态加载逻辑。
"""

# === 内嵌核心生成器开始 ===
import re
import random
from dataclasses import dataclass
from typing import List, Tuple, Any

@dataclass
class TimelineEvent:
    date: str
    definition: str
    data: Dict[str, Any]
    raw_text: str

@dataclass
class GeneratedEntity:
    entity_type: str  # "empire", "species", "fallen_empire", "pre_ftl"
    name: str
    properties: Dict[str, Any]
    placeholder_id: str

class StellarisChronicleGenerator:  # 精简自 v0.03，逻辑保持一致
    def __init__(self):
        print("=" * 60)
        print("群星（Stellaris）帝国编年史生成器 核心已内嵌 (基于 v0.03)")
        print("=" * 60)
        self.timeline_events: List[TimelineEvent] = []
        self.generated_entities: Dict[str, GeneratedEntity] = {}
        self.entity_counters = { 'empire': 0, 'species': 0, 'fallen_empire': 0, 'pre_ftl': 0 }
        self.player_empire_name = "玩家帝国"
        self.include_year_markers = True
        self.event_descriptions = self._initialize_event_descriptions()
        self.empire_generation_data = self._initialize_empire_data()
        self.planet_names = self._initialize_planet_names()
        self.leviathan_codes = self._initialize_leviathan_codes()
        self.unknown_leviathan_codes = set()  # 用于收集未知的星神兽代码
        
        # 新增：用户选择模式相关属性
        self.generation_mode = "random"  # "random" 或 "manual"
        self.manual_empire_names: Dict[str, str] = {}  # 手动输入的帝国名称
        self.manual_leviathan_names: Dict[str, str] = {}  # 手动输入的星神兽名称
        self.pending_entities: List[Dict[str, Any]] = []  # 待用户输入的实体信息

    # ---- 以下方法从原脚本复制（做少量裁剪：去除命令行 run 交互） ----
    def _initialize_event_descriptions(self) -> Dict[str, str]:
        """初始化事件代码到描述的映射表"""
        return {
            # 基于之前提供的对照表，加上实际文件中的事件定义
            "timeline_first_robot": "电动之躯_首台机器人_里程碑_[玩家帝国]在{location}首次组装了一台机器人",
            "timeline_first_precursor_discovered": "太虚古迹_初见先驱者_里程碑_[玩家帝国]首次发现文明先驱",
            "timeline_first_precursor": "太虚古迹_初见先驱者_里程碑_[玩家帝国]首次发现文明先驱", # 备选
            "timeline_first_colony": "新世界_殖民先登_里程碑_[玩家帝国]在{colony_name}首先设立了殖民地",
            "timeline_new_colony": "新殖民地_新殖民地_帝国事件_[玩家帝国]在{colony_name}设立殖民地",
            "timeline_elections": "选举_选举_帝国事件_[玩家帝国]举行了选举",
            "timeline_first_contact": "海内存知己_首遇智慧生命_里程碑_[玩家帝国]首先遭遇智慧生命",
            "timeline_first_ascension_perk": "崇高之路_首个飞升天赋_里程碑_[玩家帝国]首次选择飞升天赋",
            "timeline_first_espionage_operation": "行走的秘密_谍海初涉_里程碑_[玩家帝国]首次执行谍报活动",
            "timeline_first_rare_tech": "创新先锋_首个稀有科技_里程碑_[玩家帝国]首次研究了稀有科技",
            "timeline_first_unique_system": "千载一见_首得独特星系_里程碑_[玩家帝国]控制了一个独特的{system_name}恒星系",
            "timeline_first_max_level_leader_cap": "举贤纳言_内阁扩容_里程碑_[玩家帝国]将内阁扩容到上限",
            "timeline_first_gateway": "群星之门_首见星门_里程碑_[玩家帝国]在{system_name}恒星系首次发现了一座远古星门",
            "timeline_first_species_modification": "设计进化_首度物种修饰_里程碑_[玩家帝国]首次修饰了物种",
            "timeline_first_relic": "岁月遗珠_首获遗珍_里程碑_[玩家帝国]首次取得遗珍",
            "timeline_galactic_community_formed": "新秩序_星海共同体_星系事件_星系的各国汇聚一堂形成一个政治实体。星海共同体建立了，这座集外交、辩论和权力斗争为一体的论坛将塑造群星的未来。它的实际作用还有待观察。",
            "timeline_first_storm": "再无宁港_首遇风暴_里程碑_[玩家帝国]在其境内的{system_name}恒星系首次遭遇粒子风暴",
            "timeline_first_shroud": "空间裂隙_初探星界裂隙_里程碑_[玩家帝国]首次探索星界裂隙",
            "timeline_first_destiny_trait": "卓越之证_首获命定特质_里程碑_[玩家帝国]的{leader_name}首次获得命定特质",
            "timeline_synthetic_evolution": "合成化_社会合成化_帝国事件_[玩家帝国]完成了合成飞升",
            "timeline_first_terraforming": "星球新生_初探环境改造_里程碑_[玩家帝国]首次环境改造了{planet_name}",
            "timeline_first_war_declared": "戒撼星际_首战打响_里程碑_[玩家帝国]首先向[帝国{target_empire}]宣战",
            "timeline_first_war_won": "星光凯旋_首获凯旋_里程碑_[玩家帝国]首次击败了[帝国{defeated_empire}]",
            "timeline_first_subject": "忠诚之链_第一附属国_里程碑_[玩家帝国]收[帝国{subject_empire}]为附庸",
            "timeline_first_wormhole": "宇宙密道_初探虫洞_里程碑_[玩家帝国]首次在{system_name}恒星系发现虫洞",
            "timeline_fallen_empire_encountered": "失落帝国_失落帝国_帝国事件_[玩家帝国]遭遇了[堕落帝国{fallen_empire}]",
            "timeline_great_khan": "脱缰汗国_大可汗_危机事件_一位新起的军阀将支离破碎的掠夺者部落联合起来，锻造成一个无情的汗国。大汗带着等离子与碳纤维横扫星系，推翻帝国，奴役星球。无法无天的掠夺者现在以一个可怕的目标凝聚一群，舰队在他们的力量面前一支又一支崩溃。掠夺的时代结束，征服的纪元开始。",
            "timeline_first_repeatable_tech": "学海无涯_首个循环科技_里程碑_[玩家帝国]首次研究了循环科技",
            "timeline_first_100k_fleet": "无敌主宰_首支100K舰队_里程碑_[玩家帝国]首次组建了前所未有的强大舰队, {fleet_name}",
            "timeline_first_juggernaut": "首舰下水_首舰下水_里程碑_[玩家帝国]首次建造了, {ship_name}",
            "timeline_war_declared": "宣战_宣战_帝国事件_[玩家帝国]向[帝国{target_empire}]宣战",
            "timeline_capital_changed": "拔地而起_迁都_帝国事件_[玩家帝国]迁都至{new_capital}",
            "timeline_first_terraform": "改天换地_首次环境改造_里程碑_[玩家帝国]进行了环境改造",
            "timeline_first_arc_site": "叩问古人_首次探索考古地点_里程碑_[玩家帝国]首次进行了考古地点发掘",
            "timeline_galactic_community_resolution": "议案通过_星系事件_星海共同体已经发布了一则声明。一项新的决议即将重塑星际法则。有些文明欢欣鼓舞，其他文明则愤怒不已，但所有成员都必须遵从这一规定。",
            "timeline_first_vassal": "忠诚之链_第一附属国_里程碑_[玩家帝国]收某个帝国为附庸",
            "timeline_new_vassal": "再添附庸_新的仆从_帝国事件_[玩家帝国]又收了一个新的附庸",
            "timeline_first_astral_rift": "空间裂隙_初探星界裂隙_里程碑_[玩家帝国]首次侦测到并探索了一处星界裂隙",
            "timeline_war_declared_attacker": "战争号角_主动宣战_帝国事件_[玩家帝国]作为攻击方，向另一个帝国主动宣战",
            "timeline_first_storm_within_borders": "虚空风暴_首遇风暴_里程碑_[玩家帝国]在境内首次遭遇了太空风暴",
            "timeline_meet_fallen_empire_discover": "昔日巨像_遭遇失落帝国_帝国事件_[玩家帝国]的飞船遭遇了一个古老而停滞的失落帝国",
            "timeline_council_max_expansion": "议会全席_内阁扩容_里程碑_[玩家帝国]将议会席位扩充至上限",
            
            # 补充事件 - 新增事件代码
            "timeline_encountered_leviathan": "眠者将醒_发现星神兽_帝国事件_[玩家帝国]遭遇了{leviathan_name}",
            "timeline_become_the_crisis": "星海天罚_化身天灾_危机事件_黑暗已经降临银河系。[玩家帝国]抛弃了所有外交伪装，宣称自己是银河生存的最大威胁。他们的舰队正在集结，而情报人员则低声传递着一项最终的、末日般的计划。他们不再仅仅是一个帝国，而是演变成了一场危机。",
            "timeline_modularity": "全面模组_帝国事件_[玩家帝国]完全变为模组化",
            "timeline_destroyed_leviathan": "守护者不再_摧毁星神兽_帝国事件_[玩家帝国]摧毁了{leviathan_name}",
            "timeline_first_deficit": "贪婪之价_首现赤字_里程碑_[玩家帝国]首次出现资源短缺",
            "timeline_deficit": "资源短缺_资源短缺_帝国事件_[玩家帝国]发生了资源短缺",
            "timeline_first_war_lost": "败者之尘_初尝败绩_里程碑_[玩家帝国]首次被[帝国{defeated_empire}]击败",
            
            # 年度标记事件
            "timeline_event_year": "年度标记_{date}_时光荏苒，{date}年悄然而至。",
            
            # 起源相关事件 - 完整起源列表
            "timeline_origin_default": "繁荣一统_帝国起源_[玩家帝国]通过斗争和胜利，这个社会已经实现了每一个年轻文明的抱负：一个有着统一目标的家园，一条通向璀璨繁星的道路",
            "timeline_origin_separatists": "分离主义者_帝国起源_[玩家帝国]这个文明并非诞生于全球统一，而是由一群大胆的殖民者建立的，他们在一个崭新的世界上寻求自己的命运",
            "timeline_origin_mechanists": "机械师_帝国起源_[玩家帝国]尽管该文明在生物层面仍是有机体，但他们早已对自动化的机器人劳工习以为常。他们已经将许多卑微（甚至不那么卑微）的苦差事都交给了自动化仆从",
            "timeline_origin_syncretic_evolution": "协同进化_帝国起源_[玩家帝国]在一颗共享的母星上，两个不同的物种并肩演化，相得益彰。一个物种发展出了高级认知能力，而另一个物种则进化出了超凡的力量和耐力——这是一个完美的组合",
            "timeline_origin_life_seeded": "生命之籽_帝国起源_[玩家帝国]这个文明在一位远超其想象的远古仁善存在的监护下逐渐演化，他们的母星是一颗完美的盖亚星球，这样的环境无疑是智慧生命发展的摇篮",
            "timeline_origin_post_apocalyptic": "后启示录_帝国起源_[玩家帝国]在一场将母星变为辐射废土的灭世核战争之后，这个文明的幸存者们终于从地下的防辐射掩体中走了出来，准备在群星中建立一个新的、更光明的未来",
            "timeline_origin_remnants": "复国孑遗_帝国起源_[玩家帝国]这个文明的母星曾是一个庞大、先进帝国的首都。但在一场神秘的灾难之后，帝国分崩离析，只留下了这个星球上不断衰败的城市和这个曾经自豪的文明的遗民",
            "timeline_origin_shattered_ring": "破碎之环_帝国起源_[玩家帝国]这个文明并非在行星上，而是在一个巨大的人造环形世界的一部分上演化。尽管他们已经忘记了它的起源，但他们的祖先毫无疑问曾是技术大师",
            "timeline_origin_void_dwellers": "虚空居者_帝国起源_[玩家帝国]数十万年来，这个文明的先辈们一直生活在他们太阳系深空的轨道栖息地里。对于他们而言，他们的母星只是一个被遗忘已久的传说——一个他们现在希望能重新发现的传说",
            "timeline_origin_scion": "先辈子弟_帝国起源_[玩家帝国]出于某种原因，一个古老而强大的堕落帝国对这个年轻的文明产生了兴趣，并决定将他们置于自己的羽翼之下。至于未来会怎样，只有时间才能证明",
            "timeline_origin_galactic_doorstep": "繁星门阶_帝国起源_[玩家帝国]这个文明的母星位于一个由未知先行者建造的废弃巨构——星门附近。尽管目前它还处于休眠状态，但这个文明正在努力解开它的秘密，希望它能成为通往银河系的捷径",
            "timeline_origin_tree_of_life": "生命之树_帝国起源_[玩家帝国]这个蜂巢思维文明与一个古老的生命之树共生。它扎根于他们的母星，并与其所有的人口进行心灵感应连接，赋予他们生命，并加速他们的成长",
            "timeline_origin_shoulders_of_giants": "屹于巨人之肩_帝国起源_[玩家帝国]在他们的母星上发现了一系列可以追溯到数百万年前的古代遗迹。尽管其建设者的身份仍然是个谜，但这个文明已经学会了破译他们留下的一些基本文本，并正处于技术革命的边缘",
            "timeline_origin_lithoid": "降世灾星_帝国起源_[玩家帝国]这个岩石物种并非在他们的母星上演化而来。他们乘坐一颗巨大的小行星来到这里，在撞击中幸存下来，然后逐渐占据了主导地位",
            "timeline_origin_common_ground": "共同命运_帝国起源_[玩家帝国]这个文明是银河联盟的创始成员之一，银河联盟是一个旨在促进星际合作和商业发展的新生组织。另外两个创始成员国也已经实现了超光速旅行，并准备好与他们的邻国一起探索银河系",
            "timeline_origin_hegemon": "一方霸主_帝国起源_[玩家帝国]这个文明是霸权联盟的领导者，霸权联盟是一个强大的政治集团，另外两个成员国都曾是其附庸。现在他们已经都实现了超光速旅行，他们已经准备好在银河系的舞台上维护他们的统治地位了",
            "timeline_origin_doomsday": "末日将临_帝国起源_[玩家帝国]这个文明的母星极不稳定。根据他们最可靠的科学模型的预测，在他们的文明开始星际航行的几十年内，它将被一场灾难所吞噬。生存的唯一希望就在于群星之中",
            "timeline_origin_lost_colony": "失落行星_帝国起源_[玩家帝国]这个文明的祖先乘坐殖民船来到他们的母星，但所有关于他们母星的记录都已丢失。也许在银河系的某个地方，他们可以找到他们失散已久的同胞",
            "timeline_origin_necrophage": "食尸文化_帝国起源_[玩家帝国]这个文明由两个物种组成，一个是被转化为主物种的次级物种，另一个是作为次级物种存在的原生生物。他们通过转化其他物种的人口来繁衍，将他们带入自己不朽的行列",
            "timeline_origin_clone_army": "克隆大军_帝国起源_[玩家帝国]这个文明是由古代、技术先进的克隆战士创造的，他们已经在一个被遗忘的时代为他们的主人赢得了无数的战争。但现在他们的主人已经不在了，他们必须为自己开创一条新的道路",
            "timeline_origin_here_be_dragons": "与龙共舞_帝国起源_[玩家帝国]一条以太巨龙在他们的母星上空盘旋，保护着它，就像保护自己的孩子一样。这个文明已经学会了与它共存，甚至崇拜它。只要巨龙还活着，就没有人敢威胁他们的母星",
            "timeline_origin_ocean_paradise": "海洋天堂_帝国起源_[玩家帝国]这个文明在一个被巨大海洋覆盖的星球上演化而来。他们的母星是一个水生天堂，充满了生命和丰富的资源",
            "timeline_origin_progenitor_hive": "始祖蜂巢_帝国起源_[玩家帝国]这个蜂巢思维文明由一个古老而强大的祖先蜂后领导，它通过心灵感应网络将其意志强加给它的子民。只要蜂后还活着，蜂巢就会繁荣昌盛",
            "timeline_origin_subterranean": "地底人_帝国起源_[玩家帝国]由于他们母星的表面环境恶劣，这个文明的祖先们在地下寻求庇护。他们已经适应了地下的生活，并学会了利用其丰富的资源",
            "timeline_origin_star_slingshot": "射向星际_帝国起源_[玩家帝国]在他们的太阳系中发现了一个巨大的量子弹弓，这是一个由未知先行者建造的废弃巨构。在对其进行了数十年的研究之后，这个文明终于学会了如何使用它，并准备好以前所未有的速度将自己弹射到银河系中",
            "timeline_origin_shroudwalker_apprentice": "虚境导师_帝国起源_[玩家帝国]一群被称为'虚行者'的神秘灵能主义者对这个文明产生了兴趣，并决定将他们收为学徒。他们承诺会教给他们虚境的奥秘，但这背后可能隐藏着更深层次的动机",
            "timeline_origin_imperial_vassal": "帝国封邑_帝国起源_[玩家帝国]这个文明是某个更强大的星际帝国的一个小附庸。他们受制于宗主国的法律和异想天开，但他们也受到宗主国的保护，并可以从宗主国的先进技术中受益",
            "timeline_origin_overtuned": "强夺天工_帝国起源_[玩家帝国]这个文明已经掌握了基因工程的艺术，他们不断地调整自己的身体，以追求完美。他们的领导人痴迷于效率和生产力，他们将不惜一切代价来实现自己的目标",
            "timeline_origin_toxic_knights": "毒圣骑士_帝国起源_[玩家帝国]一群神秘的骑士来到了这个文明的母星，他们承诺会保护他们免受银河系中潜伏的恐怖势力的侵害。他们带来了一种神秘的'毒液'，他们说这种毒液可以赋予他们超人的力量，但代价是什么呢？",
            "timeline_origin_payback": "血债血偿_帝国起源_[玩家帝国]这个文明的母星曾被一个更强大的星际帝国征服和奴役。在多年的压迫之后，他们终于成功地发动了一场成功的起义，并赢得了自由。但他们永远不会忘记他们所遭受的苦难，他们发誓要向他们的前压迫者复仇",
            "timeline_origin_broken_shackles": "粉碎的枷锁_帝国起源_[玩家帝国]这个文明由来自银河系各地不同物种的难民和逃亡的奴隶组成。他们在共同的苦难中找到了团结，并建立了一个新的社会，在这个社会中，所有人都生而平等。他们发誓要解放所有被奴役的人民，并粉碎压迫他们的枷锁",
            "timeline_origin_fear_of_the_dark": "黑暗之怖_帝国起源_[玩家帝国]这个文明对黑暗有着一种非理性的恐惧。他们相信，在群星之间的虚空中潜伏着一些可怕的东西，他们会不惜一切代价避免与它接触。他们将自己的文明局限在自己的太阳系中，并希望永远不会有任何东西来打扰他们",
            "timeline_origin_riftworld": "裂隙当空_帝国起源_[玩家帝国]这个文明的母星正处于被一个巨大的、不断扩大的时空裂缝吞噬的边缘。他们必须在自己的世界被撕裂之前找到逃离的方法",
            "timeline_origin_cybernetic_creed": "义体信条_帝国起源_[玩家帝国]这个文明相信，有机体是脆弱和不完美的。他们寻求通过控制论来超越自己的肉体，并成为一种新的、更高级的存在形式",
            "timeline_origin_synthetic_fertility": "合成繁衍_帝国起源_[玩家帝国]这个文明已经失去了自然繁殖的能力。他们现在依靠先进的机器人技术和基因工程来创造新的后代。但这种对技术的依赖也让他们变得脆弱",
            "timeline_origin_arc_welders": "电弧焊机_帝国起源_[玩家帝国]这个文明由一群技术娴熟的工程师和工匠组成，他们擅长建造和维修大型结构。他们以其在电弧焊方面的专业知识而闻名，他们可以用它来创造出令人惊叹的艺术品和强大的战争机器"
        }

    def _initialize_empire_data(self) -> Dict[str, Any]:
        return {
            'portraits': [ {'name':'类人','weight':15},{'name':'哺乳类','weight':12},{'name':'爬行类','weight':12},{'name':'鸟类','weight':12},{'name':'节肢类','weight':12},{'name':'软体类','weight':10},{'name':'真菌类','weight':9},{'name':'岩石类','weight':8},{'name':'植物类','weight':7},{'name':'水生类','weight':3} ],
            'name_lists': {
                '类人':['人类联合国','地球联邦','太阳系联盟','人类殖民者联邦','地球共同体','泰拉联邦'],
                '哺乳类':['兽族联盟','野兽帝国','毛族共和国','兽人王国','野性部落','爪牙联邦'],
                '爬行类':['鳞甲帝国','爬虫联盟','冷血王朝','蜥蜴共和国','蛇族联邦','龙血帝国'],
                '鸟类':['羽翼王国','飞行者联盟','天空帝国','翼族共和国','鸟人联邦','高翔集群'],
                '节肢类':['虫族蜂巢','节肢帝国','甲壳联盟','昆虫王国','蛛网共同体','多足联合'],
                '软体类':['触手帝国','软体联盟','海洋王国','湿润共和国','粘液联邦','深渊集群'],
                '真菌类':['菌丝网络','真菌王国','孢子联盟','腐蚀帝国','菌落共同体','孢子集群'],
                '岩石类':['岩石联盟','石头帝国','矿物王国','晶体共和国','地质联邦','硅基集群'],
                '植物类':['叶绿联盟','植物王国','花园帝国','根系网络','光合共同体','绿叶集群'],
                '水生类':['深海帝国','水族联盟','海洋王国','潮汐共和国','水流联邦','深蓝集群']
            },
            'ethics': [
                {'name':'排外主义','opposite':'亲外主义','weight':20},
                {'name':'亲外主义','opposite':'排外主义','weight':15},
                {'name':'唯物主义','opposite':'唯心主义','weight':25},
                {'name':'唯心主义','opposite':'唯物主义','weight':20},
                {'name':'威权主义','opposite':'平等主义','weight':22},
                {'name':'平等主义','opposite':'威权主义','weight':18},
                {'name':'军国主义','opposite':'和平主义','weight':25},
                {'name':'和平主义','opposite':'军国主义','weight':15}
            ],
            'authorities': [
                {'name':'民主制','weight':25,'forbidden_ethics':['威权主义','极端威权主义']},
                {'name':'寡头制','weight':30,'requirements':{}},
                {'name':'独裁制','weight':25,'forbidden_ethics':['平等主义','极端平等主义']},
                {'name':'帝制','weight':20,'required_ethics':['威权主义','极端威权主义']}
            ],
            'fallen_empires': [
                {'name':'希拉多种帝国','type':'圣地守护者','ethics':['极端唯心主义','和平主义'],'personality':'狂热的孤立主义者','species':'希拉多种族'},
                {'name':'阿尔法知识者联盟','type':'知识管理者','ethics':['极端唯物主义','和平主义'],'personality':'固执的学者','species':'阿尔法种族'},
                {'name':'军事孤立者帝国','type':'军事孤立者','ethics':['极端排外主义','军国主义'],'personality':'警惕的帝国主义者','species':'孤立者种族'},
                {'name':'永恒警卫者','type':'艺术赞助者','ethics':['极端平等主义','唯心主义'],'personality':'慈善的保护者','species':'警卫者种族'}
            ],
            'traits': {
                'positive': [ {'name':'智慧','cost':2,'weight':20},{'name':'强壮','cost':1,'weight':15},{'name':'天生工程师','cost':1,'weight':10},{'name':'快速增殖','cost':2,'weight':15},{'name':'适应性强','cost':2,'weight':12},{'name':'长寿','cost':1,'weight':8},{'name':'天生物理学家','cost':1,'weight':10},{'name':'天生社会学家','cost':1,'weight':10} ],
                'negative': [ {'name':'柔弱','gain':1,'weight':15},{'name':'生长缓慢','gain':1,'weight':12},{'name':'离经叛道','gain':1,'weight':10},{'name':'不善变通','gain':2,'weight':8},{'name':'令人厌恶','gain':1,'weight':5},{'name':'短寿','gain':1,'weight':10} ]
            }
        }

    def _initialize_planet_names(self) -> List[str]:
        """初始化星球名称词表"""
        return [
            # 希腊神话
            "阿尔忒弥斯", "阿波罗", "雅典娜", "赫拉", "波塞冬", "黑帝斯", "阿瑞斯", "阿佛洛狄忒",
            "赫菲斯托斯", "得墨忒尔", "赫斯提亚", "赫耳墨斯", "狄俄倪索斯",
            # 罗马神话  
            "朱庇特", "玛尔斯", "维纳斯", "密涅瓦", "涅普顿", "普路托", "巴克斯", "伏尔甘",
            "刻瑞斯", "维斯塔", "墨丘利", "朱诺",
            # 北欧神话
            "奥丁", "索尔", "弗雷", "弗蕾亚", "巴德尔", "洛基", "提尔", "海姆达尔",
            "维达尔", "瓦利", "霍德尔", "布拉基",
            # 天体名称
            "天狼", "参宿", "织女", "牛郎", "北极", "南十字", "猎户", "仙女",
            "天鹰", "天鹅", "天琴", "天蝎", "狮子", "双子", "处女", "白羊",
            # 科幻风格
            "新伊甸", "星辰", "曙光", "黎明", "希望", "新世界", "理想乡", "乌托邦",
            "新地球", "第二家园", "避风港", "新纪元", "创世纪", "复兴", "新生", "觉醒",
            # 中国古典
            "昆仑", "蓬莱", "瀛洲", "方壶", "太虚", "紫微", "天枢", "天璇",
            "天玑", "天权", "玉衡", "开阳", "摇光", "太白", "荧惑", "镇星",
            # 各种语言的星辰
            "Stella", "Astrum", "Sirius", "Vega", "Altair", "Rigel", "Betelgeuse", "Capella",
            "Aldebaran", "Antares", "Spica", "Pollux", "Regulus", "Deneb", "Arcturus", "Procyon",
            # 更多奇幻名称
            "艾泽拉斯", "洛丹伦", "暴风城", "铁炉堡", "达纳苏斯", "雷霆崖", "奥格瑞玛", "幽暗城",
            "银月城", "埃索达", "沙塔斯", "达拉然", "奎尔丹纳斯", "外域", "德拉诺", "阿古斯"
        ]

    def _initialize_leviathan_codes(self) -> Dict[str, str]:
        """初始化星神兽代码到名称的映射"""
        return {
            "0 39": "神秘堡垒",
            "0 134217816": "幽魂",
            # 可以继续添加更多已知的星神兽代码
        }

    def _get_random_planet_name(self) -> str:
        """获取随机星球名称"""
        return random.choice(self.planet_names)
    
    def _get_leviathan_name(self, data: Dict[str, Any]) -> str:
        """根据data数据获取星神兽名称"""
        if 'numbers' not in data:
            return "星神兽"
            
        # 将数字列表转换为代码字符串
        numbers = data['numbers']
        if len(numbers) >= 2:
            code = f"{numbers[0]} {numbers[1]}"
            
            # 优先检查手动输入的名称
            if self.generation_mode == "manual" and code in self.manual_leviathan_names:
                return self.manual_leviathan_names[code]
            
            # 检查是否是已知的星神兽
            if code in self.leviathan_codes:
                return self.leviathan_codes[code]
            else:
                # 记录未知代码
                self.unknown_leviathan_codes.add(code)
                return "星神兽"
        
        return "星神兽"

    def set_player_empire_name(self, name: str):
        if name and name.strip():
            self.player_empire_name = name.strip()
            print(f"✅ 玩家帝国名称设置为: {self.player_empire_name}")
        else:
            print("✅ 使用默认帝国名称: 玩家帝国")

    def set_year_markers_option(self, include: bool):
        self.include_year_markers = include
        print("✅ 将包含年度标记事件" if include else "✅ 将跳过年度标记事件")

    def set_generation_mode(self, mode: str):
        """设置生成模式：'random' 或 'manual'"""
        if mode in ["random", "manual"]:
            self.generation_mode = mode
            print(f"✅ 生成模式设置为: {'随机生成' if mode == 'random' else '手动输入'}")
        else:
            print(f"⚠ 无效的生成模式: {mode}")

    def analyze_events_for_manual_input(self) -> List[Dict[str, Any]]:
        """分析事件，找出需要手动输入的帝国名称和星神兽种类"""
        pending_entities = []
        
        for event in self.timeline_events:
            # 分析需要帝国名称的事件
            template = self.event_descriptions.get(event.definition, "")
            placeholders = re.findall(r'\[([^\]]+)\]', template)
            
            for placeholder in placeholders:
                if placeholder.startswith('帝国') and placeholder != '玩家帝国':
                    entity_info = {
                        'type': 'empire',
                        'placeholder': placeholder,
                        'event_date': event.date,
                        'event_description': template.split('_')[-1] if '_' in template else template,
                        'event_definition': event.definition
                    }
                    # 避免重复添加相同的占位符
                    if not any(e['placeholder'] == placeholder for e in pending_entities):
                        pending_entities.append(entity_info)
                
                elif placeholder.startswith('堕落帝国'):
                    entity_info = {
                        'type': 'fallen_empire',
                        'placeholder': placeholder,
                        'event_date': event.date,
                        'event_description': template.split('_')[-1] if '_' in template else template,
                        'event_definition': event.definition
                    }
                    if not any(e['placeholder'] == placeholder for e in pending_entities):
                        pending_entities.append(entity_info)
            
            # 分析需要星神兽名称的事件
            if event.definition in ['timeline_encountered_leviathan', 'timeline_destroyed_leviathan']:
                leviathan_code = "未知"
                if 'numbers' in event.data and len(event.data['numbers']) >= 2:
                    leviathan_code = f"{event.data['numbers'][0]} {event.data['numbers'][1]}"
                
                entity_info = {
                    'type': 'leviathan',
                    'code': leviathan_code,
                    'event_date': event.date,
                    'event_description': '星神兽相关事件',
                    'event_definition': event.definition,
                    'placeholder': f"星神兽_{leviathan_code}"  # 添加缺失的placeholder字段
                }
                # 避免重复添加相同代码的星神兽
                if not any(e.get('code') == leviathan_code and e['type'] == 'leviathan' for e in pending_entities):
                    pending_entities.append(entity_info)
        
        # 按日期排序
        pending_entities.sort(key=lambda x: x['event_date'])
        self.pending_entities = pending_entities
        
        print(f"🔍 分析完成，发现 {len(pending_entities)} 个需要手动输入的实体")
        return pending_entities

    def set_manual_empire_name(self, placeholder: str, name: str):
        """设置手动输入的帝国名称"""
        if name and name.strip():
            self.manual_empire_names[placeholder] = name.strip()
            print(f"✅ 设置帝国名称: [{placeholder}] -> {name.strip()}")
        else:
            print(f"⚠ 帝国名称不能为空: {placeholder}")

    def set_manual_leviathan_name(self, code: str, name: str):
        """设置手动输入的星神兽名称"""
        if name and name.strip():
            self.manual_leviathan_names[code] = name.strip()
            print(f"✅ 设置星神兽名称: {code} -> {name.strip()}")
        else:
            print(f"⚠ 星神兽名称不能为空: {code}")

    def parse_save_file(self, path: str) -> bool:
        print(f"\n🔍 开始解析存档文件: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'timeline_events\s*=\s*\{', content)
            if not m:
                print("❌ 未找到timeline_events数据块")
                return False
            start = m.end() - 1
            brace = 0; end = start
            for i, ch in enumerate(content[start:], start):
                if ch == '{': brace += 1
                elif ch == '}':
                    brace -= 1
                    if brace == 0:
                        end = i + 1
                        break
            block = content[start:end]
            self._parse_timeline_events(block)
            print(f"✅ 事件解析完成，共 {len(self.timeline_events)} 个")
            return True
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return False

    def _parse_timeline_events(self, text: str):
        events = []
        lines = text.split('\n')
        current = None; brace = 0; in_event = False
        for ln, line in enumerate(lines):
            s = line.strip()
            if not s: continue
            brace += s.count('{') - s.count('}')
            if not in_event and s == '{' and brace >= 2:
                in_event = True; current = {'lines': [], 'start': ln}
            elif in_event and current is not None:
                current['lines'].append(s)
                if s == '}' and brace == 1:
                    evt_txt = '\n'.join(current['lines'])
                    evt = self._parse_single_event(evt_txt)
                    if evt: events.append(evt)
                    in_event = False; current = None
        events.sort(key=lambda e: e.date)
        self.timeline_events = events

    def _parse_single_event(self, txt: str):
        try:
            dm = re.search(r'date\s*=\s*"([^"]+)"', txt)
            dfm = re.search(r'definition\s*=\s*"([^"]+)"', txt)
            if not dm or not dfm: return None
            date = dm.group(1); definition = dfm.group(1)
            data = {}
            dmatch = re.search(r'data\s*=\s*\{([^}]*)\}', txt, re.DOTALL)
            if dmatch:
                body = dmatch.group(1).strip()
                if re.match(r'^[\d\s]+$', body):
                    nums = [int(x) for x in body.split() if x.isdigit()]; data['numbers'] = nums
                elif re.search(r'^\s*\d+\s*=', body, re.MULTILINE):
                    pairs = re.findall(r'(\d+)\s*=\s*"([^"]*)"', body)
                    data['items'] = [v for _, v in sorted(pairs, key=lambda x: int(x[0]))]
                else:
                    kvs = re.findall(r'(\w+)\s*=\s*"([^"]*)"', body)
                    for k,v in kvs: data[k]=v
            return TimelineEvent(date=date, definition=definition, data=data, raw_text=txt)
        except Exception as e:
            print(f"⚠ 解析事件出错: {e}")
            return None

    def generate_initial_chronicle(self) -> str:
        lines = ["="*60, "群星帝国编年史", "="*60, ""]
        filtered = 0
        for ev in self.timeline_events:
            if not self.include_year_markers and ev.definition == 'timeline_event_year':
                filtered += 1; continue
            lines.append(f"{ev.date} - {self._convert_event_to_text(ev)}")
        print(f"✅ 初版编年史生成完成，共 {len(self.timeline_events)-filtered} 条")
        return '\n'.join(lines)

    def _convert_event_to_text(self, ev: TimelineEvent) -> str:
        if ev.definition not in self.event_descriptions:
            return f"未收录事件代码 ({ev.definition})，欢迎补充！"
        template = self.event_descriptions[ev.definition]
        import string
        fmt_args: Dict[str, Any] = {'date': ev.date, **ev.data}
        formatter = string.Formatter()
        needed = [f for _,f,_,_ in formatter.parse(template) if f]
        for f in needed:
            if f not in fmt_args:
                defaults = {
                    'location':'未知星系',
                    'system_name':'未知恒星系',
                    'leader_name':'未知领袖',
                    'planet_name':'未知星球',
                    'fleet_name':'无敌舰队',
                    'ship_name':'旗舰',
                    'new_capital':'新首都'
                }
                
                # 特殊处理colony_name，使用随机星球名称
                if f == 'colony_name':
                    fmt_args[f] = self._get_random_planet_name()
                # 特殊处理leviathan_name，根据事件数据确定星神兽名称
                elif f == 'leviathan_name':
                    fmt_args[f] = self._get_leviathan_name(ev.data)
                elif f in defaults:
                    fmt_args[f] = defaults[f]
                elif f.endswith('_empire'):
                    fmt_args[f] = f"帝国{len(self.generated_entities)+1}"
                elif f.endswith('_fallen_empire'):
                    fmt_args[f] = f"堕落帝国{len([e for e in self.generated_entities.values() if e.entity_type=='fallen_empire'])+1}"
                else:
                    fmt_args[f] = f"未知_{f}"
        try:
            text = template.format(**fmt_args)
            return self._process_entity_placeholders(text, ev)
        except Exception as e:
            return f"格式化错误({ev.definition}): {e}"

    def _process_entity_placeholders(self, text: str, ev: TimelineEvent) -> str:
        phs = re.findall(r'\[([^\]]+)\]', text)
        for ph in phs:
            if ph not in self.generated_entities:
                ent = self._generate_entity_for_placeholder(ph, ev)
                if ent: self.generated_entities[ph] = ent
        return text

    def _generate_entity_for_placeholder(self, ph: str, ev: TimelineEvent):
        if ph.startswith('帝国'): return self._generate_ai_empire(ph, ev)
        if ph.startswith('堕落帝国'): return self._generate_fallen_empire(ph, ev)
        if ph.startswith('种族'): return self._generate_species(ph, ev)
        return None

    def _weighted_random(self, items: List[Dict[str, Any]]):
        total = sum(i['weight'] for i in items); r = random.randint(1,total); cur=0
        for it in items:
            cur += it['weight']
            if r <= cur: return it
        return items[-1]

    def _generate_ai_empire(self, ph: str, ev: TimelineEvent) -> GeneratedEntity:
        self.entity_counters['empire'] += 1
        
        # 检查是否有手动输入的名称
        if self.generation_mode == "manual" and ph in self.manual_empire_names:
            empire_name = self.manual_empire_names[ph]
        else:
            # 使用随机生成
            portrait = self._weighted_random(self.empire_generation_data['portraits'])
            name_options = self.empire_generation_data['name_lists'][portrait['name']]
            empire_name = random.choice(name_options) + f"第{self.entity_counters['empire']}共同体"
        
        # 其他属性仍然随机生成
        portrait = self._weighted_random(self.empire_generation_data['portraits'])
        ethics = self._generate_ethics(None)
        authority = self._select_authority(ethics)
        traits = self._generate_traits()
        props = {'name':empire_name,'species':f"{portrait['name']}种族{self.entity_counters['empire']}", 'portrait':portrait['name'], 'ethics':ethics, 'authority':authority,'traits':traits,'personality':self._generate_personality(ethics),'type':'ai_empire'}
        return GeneratedEntity('empire', empire_name, props, ph)

    def _generate_fallen_empire(self, ph: str, ev: TimelineEvent) -> GeneratedEntity:
        cfg = random.choice(self.empire_generation_data['fallen_empires'])
        props = {'name':cfg['name'],'species':cfg['species'],'type_name':cfg['type'],'ethics':cfg['ethics'],'personality':cfg['personality'],'type':'fallen_empire'}
        return GeneratedEntity('fallen_empire', cfg['name'], props, ph)

    def _generate_species(self, ph: str, ev: TimelineEvent) -> GeneratedEntity:
        self.entity_counters['species'] += 1
        portrait = self._weighted_random(self.empire_generation_data['portraits'])
        traits = self._generate_traits()
        name = f"{portrait['name']}族{self.entity_counters['species']}"
        props = {'name':name,'portrait':portrait['name'],'traits':traits,'type':'species'}
        return GeneratedEntity('species', name, props, ph)

    def _generate_ethics(self, bias):
        ethics = []
        total = 3
        avail = [e['name'] for e in self.empire_generation_data['ethics']]
        used_oppo = set()
        while total > 0 and len(ethics) < 3:
            pool = [e for e in self.empire_generation_data['ethics'] if e['name'] not in ethics and e['opposite'] not in used_oppo]
            if not pool: break
            sel = self._weighted_random(pool)
            ethics.append(sel['name'])
            used_oppo.add(sel['opposite'])
            total -= 1
        return ethics

    def _select_authority(self, ethics: List[str]) -> str:
        choices = []
        for a in self.empire_generation_data['authorities']:
            if 'forbidden_ethics' in a and any(e in ethics for e in a['forbidden_ethics']):
                continue
            if 'required_ethics' in a and not any(e in ethics for e in a.get('required_ethics', [])) and a.get('required_ethics'):
                continue
            choices.append(a)
        if not choices: choices = self.empire_generation_data['authorities']
        return self._weighted_random(choices)['name']

    def _generate_traits(self) -> List[str]:
        res = []; cost = 0; attempts = 0
        while cost <= 2 and len(res) < 5 and attempts < 20:
            pos = random.random() < 0.7
            pool = self.empire_generation_data['traits']['positive' if pos else 'negative']
            t = self._weighted_random(pool)
            if t['name'] in res: attempts +=1; continue
            new_cost = cost + (t['cost'] if pos else -t['gain'])
            if new_cost <= 2:
                res.append(t['name']); cost = new_cost
            attempts += 1
        return res

    def _generate_personality(self, ethics: List[str]) -> str:
        m = {
            '军国主义':'好战的征服者','极端军国主义':'残酷的征服者','和平主义':'和平的商人','极端和平主义':'生态的和平主义者',
            '排外主义':'孤立的帝国主义者','极端排外主义':'狂热的排外主义者','亲外主义':'友好的外交官','极端亲外主义':'狂热的友谊使者',
            '威权主义':'专制的统治者','极端威权主义':'独裁的暴君','平等主义':'民主的理想主义者','极端平等主义':'狂热的平等主义者',
            '唯物主义':'理性的探索者','极端唯物主义':'技术的狂热者','唯心主义':'精神的哲学家','极端唯心主义':'狂热的信徒'
        }
        for e in ethics:
            if e in m: return m[e]
        return '谨慎的帝国主义者'

    def generate_final_chronicle(self, initial: str) -> str:
        out = initial
        for ph, ent in self.generated_entities.items():
            out = re.sub(rf'\[{re.escape(ph)}\]', ent.name, out)
        out = re.sub(r'\[玩家帝国\]', self.player_empire_name, out)
        print(f"✅ 占位符替换完成，共替换 {len(self.generated_entities)} 个实体")
        return out

    def generate_entities_settings_file(self) -> str:
        from datetime import datetime as _dt
        lines = ["="*60, "群星帝国编年史 - 动态生成实体设定", "="*60, "", f"生成时间: {_dt.now().strftime('%Y-%m-%d %H:%M:%S')}", f"总计生成实体: {len(self.generated_entities)} 个", ""]
        groups: Dict[str, List[GeneratedEntity]] = {}
        for ent in self.generated_entities.values():
            groups.setdefault(ent.entity_type, []).append(ent)
        type_names = {'empire':'AI帝国','fallen_empire':'堕落帝国','species':'种族','pre_ftl':'前FTL文明'}
        for t, ents in groups.items():
            lines.append(f"## {type_names.get(t, t)} ({len(ents)}个)")
            lines.append("")
            for ent in ents:
                lines.append(f"### {ent.name}")
                lines.append(f"- 占位符: [{ent.placeholder_id}]")
                if t=='empire':
                    lines.append(f"- 种族: {ent.properties['species']}")
                    lines.append(f"- 肖像: {ent.properties['portrait']}")
                    lines.append(f"- 思潮: {', '.join(ent.properties['ethics'])}")
                    lines.append(f"- 政体: {ent.properties['authority']}")
                    lines.append(f"- 特质: {', '.join(ent.properties['traits'])}")
                    lines.append(f"- 性格: {ent.properties['personality']}")
                elif t=='fallen_empire':
                    lines.append(f"- 种族: {ent.properties['species']}")
                    lines.append(f"- 类型: {ent.properties['type_name']}")
                    lines.append(f"- 思潮: {', '.join(ent.properties['ethics'])}")
                    lines.append(f"- 性格: {ent.properties['personality']}")
                elif t=='species':
                    lines.append(f"- 肖像: {ent.properties['portrait']}")
                    lines.append(f"- 特质: {', '.join(ent.properties['traits'])}")
                lines.append("")
        return '\n'.join(lines)

    def save_chronicle_files(self, final_txt: str, settings_txt: str, out_dir: str):
        os.makedirs(out_dir, exist_ok=True)
        chron = os.path.join(out_dir, "群星帝国编年史.txt")
        with open(chron, 'w', encoding='utf-8') as f: f.write(final_txt)
        print(f"✅ 编年史已保存: {chron}")
        setting = os.path.join(out_dir, "动态生成实体设定.md")
        with open(setting, 'w', encoding='utf-8') as f: f.write(settings_txt)
        print(f"✅ 实体设定已保存: {setting}")
        stats = os.path.join(out_dir, "生成统计.txt")
        self._save_stats(stats)
        print(f"✅ 生成统计已保存: {stats}")

    def _save_stats(self, path: str):
        from datetime import datetime as _dt
        year_markers = sum(1 for e in self.timeline_events if e.definition=='timeline_event_year')
        lines = ["="*40, "群星帝国编年史生成统计", "="*40, "", f"解析时间: {_dt.now().strftime('%Y-%m-%d %H:%M:%S')}", f"总事件数: {len(self.timeline_events)}"]
        if self.include_year_markers:
            lines.append(f"年度标记事件: {year_markers} (已包含)")
        else:
            lines.append(f"年度标记事件: {year_markers} (已过滤)")
        
        # 添加未知星神兽代码的提示
        if self.unknown_leviathan_codes:
            lines.append("")
            lines.append("发现未知星神兽代码:")
            lines.append("="*25)
            for code in sorted(self.unknown_leviathan_codes):
                lines.append(f"- {code}")
            lines.append("")
            lines.append("这些代码对应的星神兽名称尚未收录，欢迎提交反馈！")
            lines.append("请访问项目GitHub页面反馈这些未知代码对应的星神兽名称。")
        
        lines.append("")
        with open(path, 'w', encoding='utf-8') as f: f.write('\n'.join(lines))

# === 内嵌核心生成器结束 ===


# ------------------ 日志记录器 ------------------
class GuiLogger:
    def __init__(self, textbox: 'ctk.CTkTextbox'):
        self.textbox = textbox
        self.queue: queue.Queue[str] = queue.Queue()
        self._stopping = False
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr

    def write(self, data: str):
        if not data:
            return
        for line in data.splitlines(keepends=True):
            self.queue.put(line)

    def flush(self):
        pass

    def start(self, root: 'ctk.CTk'):
        self._poll(root)

    def stop(self):
        self._stopping = True

    def _poll(self, root: 'ctk.CTk'):
        if self._stopping:
            return
        try:
            while True:
                line = self.queue.get_nowait()
                self._append_colored(line)
        except queue.Empty:
            pass
        root.after(80, lambda: self._poll(root))

    def _append_colored(self, line: str):
        tag = self._decide_tag(line)
        self.textbox.insert('end', line)
        # 简化: CTkTextbox 当前不支持 tag 颜色，改为前缀符号即可；可扩展为富文本
        self.textbox.see('end')

    @staticmethod
    def _decide_tag(line: str) -> str:
        s = line.strip()
        if not s:
            return 'default'
        if s.startswith('❌') or '错误' in s or '失败' in s:
            return 'error'
        if s.startswith('⚠') or '警告' in s:
            return 'warn'
        if s.startswith('✅') or s.startswith('🎉'):
            return 'success'
        if s.startswith('📥'):
            return 'info'
        return 'default'

# ------------------ 用户选择对话框 ------------------
class UserChoiceDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("选择生成模式")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"400x250+{x}+{y}")
        
        self._build_dialog()
        
    def _build_dialog(self):
        # 标题
        title = ctk.CTkLabel(self.dialog, text="选择帝国名称和星神兽种类的生成方式", 
                           font=ctk.CTkFont(size=16, weight='bold'))
        title.pack(pady=(20, 10))
        
        # 说明
        desc = ctk.CTkLabel(self.dialog, 
                           text="请选择您希望如何处理编年史中的帝国名称和星神兽种类：",
                           font=ctk.CTkFont(size=12))
        desc.pack(pady=(0, 20))
        
        # 选项A：随机生成
        btn_random = ctk.CTkButton(self.dialog, text="A. 随机生成", 
                                 width=300, height=40,
                                 font=ctk.CTkFont(size=14),
                                 command=lambda: self._set_result("random"))
        btn_random.pack(pady=(0, 10))
        
        random_tip = ctk.CTkLabel(self.dialog, 
                                text="系统将自动为所有帝国和星神兽生成随机名称",
                                font=ctk.CTkFont(size=11),
                                text_color="#8aa0b3")
        random_tip.pack(pady=(0, 15))
        
        # 选项B：手动输入
        btn_manual = ctk.CTkButton(self.dialog, text="B. 手动输入", 
                                 width=300, height=40,
                                 font=ctk.CTkFont(size=14),
                                 fg_color="#2d6a4f", hover_color="#2f855a",
                                 command=lambda: self._set_result("manual"))
        btn_manual.pack(pady=(0, 10))
        
        manual_tip = ctk.CTkLabel(self.dialog, 
                                text="程序将引导您为每个帝国和星神兽输入自定义名称",
                                font=ctk.CTkFont(size=11),
                                text_color="#8aa0b3")
        manual_tip.pack()
        
    def _set_result(self, choice):
        self.result = choice
        self.dialog.destroy()
        
    def show(self):
        self.dialog.wait_window()
        return self.result

# ------------------ 手动输入对话框 ------------------
class ManualInputDialog:
    def __init__(self, parent, entities_info):
        self.entities_info = entities_info
        self.results = {}
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("手动输入名称")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        self._build_dialog()
        
    def _build_dialog(self):
        # 标题
        title = ctk.CTkLabel(self.dialog, text="请为以下实体输入名称", 
                           font=ctk.CTkFont(size=16, weight='bold'))
        title.pack(pady=(10, 5))
        
        subtitle = ctk.CTkLabel(self.dialog, 
                              text=f"根据您的存档分析，发现 {len(self.entities_info)} 个需要命名的实体",
                              font=ctk.CTkFont(size=12))
        subtitle.pack(pady=(0, 10))
        
        # 滚动框架
        scrollable_frame = ctk.CTkScrollableFrame(self.dialog, height=350)
        scrollable_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.entries = {}
        
        for i, entity in enumerate(self.entities_info):
            # 实体信息框
            entity_frame = ctk.CTkFrame(scrollable_frame)
            entity_frame.pack(fill='x', pady=(0, 10))
            
            # 实体类型和时间
            if entity['type'] == 'empire':
                type_text = "🏛️ 帝国"
                placeholder_text = entity.get('placeholder', '未知')
            elif entity['type'] == 'fallen_empire':
                type_text = "👑 堕落帝国"
                placeholder_text = entity.get('placeholder', '未知')
            elif entity['type'] == 'leviathan':
                type_text = "🐲 星神兽"
                placeholder_text = f"代码: {entity.get('code', '未知')}"
            else:
                type_text = "❓ 未知"
                placeholder_text = entity.get('placeholder', '未知')
            
            header = ctk.CTkLabel(entity_frame, 
                                text=f"{type_text} - {entity['event_date']}年",
                                font=ctk.CTkFont(size=13, weight='bold'))
            header.pack(anchor='w', padx=10, pady=(8, 2))
            
            desc = ctk.CTkLabel(entity_frame, 
                              text=f"事件: {entity['event_description']}",
                              font=ctk.CTkFont(size=11))
            desc.pack(anchor='w', padx=10, pady=(0, 2))
            
            placeholder_label = ctk.CTkLabel(entity_frame, 
                                           text=f"标识: {placeholder_text}",
                                           font=ctk.CTkFont(size=11),
                                           text_color="#8aa0b3")
            placeholder_label.pack(anchor='w', padx=10, pady=(0, 5))
            
            # 输入框
            entry_frame = ctk.CTkFrame(entity_frame, fg_color='transparent')
            entry_frame.pack(fill='x', padx=10, pady=(0, 8))
            
            label = ctk.CTkLabel(entry_frame, text="名称:", width=50, anchor='w')
            label.pack(side='left')
            
            entry = ctk.CTkEntry(entry_frame, placeholder_text=f"请输入{type_text}的名称")
            entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
            
            # 存储引用
            key = entity.get('placeholder') if entity['type'] != 'leviathan' else entity.get('code', '未知')
            if key:  # 确保key不为空
                self.entries[key] = {
                    'entry': entry,
                    'type': entity['type']
                }
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self.dialog, fg_color='transparent')
        button_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(button_frame, text="取消", 
                                 fg_color="#d9534f", hover_color="#c9302c",
                                 command=self._cancel)
        cancel_btn.pack(side='left')
        
        confirm_btn = ctk.CTkButton(button_frame, text="确认", 
                                  command=self._confirm)
        confirm_btn.pack(side='right')
        
    def _cancel(self):
        self.results = None
        self.dialog.destroy()
        
    def _confirm(self):
        self.results = {}
        has_empty = False
        
        for key, entry_info in self.entries.items():
            value = entry_info['entry'].get().strip()
            if not value:
                has_empty = True
                continue
            self.results[key] = {
                'name': value,
                'type': entry_info['type']
            }
        
        if has_empty:
            # 简单提示，可以扩展为更详细的验证
            pass
            
        self.dialog.destroy()
        
    def show(self):
        self.dialog.wait_window()
        return self.results

# ------------------ ToolTip ------------------
class Tooltip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window: Optional[ctk.CTkToplevel] = None
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)

    def show(self, _):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 28
        self.tip_window = ctk.CTkToplevel(self.widget)  # type: ignore[arg-type]
        try:  # 运行期存在，类型检查忽略
            self.tip_window.overrideredirect(True)  # type: ignore[attr-defined]
            self.tip_window.geometry(f"+{x}+{y}")  # type: ignore[attr-defined]
        except Exception:
            pass
        frame = ctk.CTkFrame(self.tip_window, corner_radius=8)
        frame.pack(fill='both', expand=True)
        label = ctk.CTkLabel(frame, text=self.text, justify='left', fg_color='transparent')
        label.pack(padx=8, pady=6)

    def hide(self, _):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ------------------ 主界面 ------------------
class ModernGUI:
    def __init__(self):
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')  # 可改为 "green", "dark-blue"
        self.root = ctk.CTk()
        self.root.title("群星编年史生成器 (Modern UI Beta)")
        self.root.geometry('1080x680')
        self.root.minsize(960, 600)

        # 状态变量
        self.save_file = ctk.StringVar()
        self.empire_name = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.include_year = ctk.BooleanVar(value=True)
        self.current_step = ctk.StringVar(value='就绪')
        self.progress_value = 0

        self.running_thread: Optional[threading.Thread] = None
        self._last_success: Optional[bool] = None
        self.logger: Optional[GuiLogger] = None
        self._spinner_phase = 0
        self._spinner_running = False

        self._build_layout()
        self._bind_shortcuts()
        self._init_logger()
        self._apply_context_menu()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # 布局
    def _build_layout(self):
        # 顶部标题栏
        header = ctk.CTkFrame(self.root, corner_radius=12)
        header.pack(fill='x', padx=14, pady=(12, 8))
        title = ctk.CTkLabel(header, text='群星（Stellaris）帝国编年史生成器', font=ctk.CTkFont(size=20, weight='bold'))
        title.pack(anchor='w', padx=14, pady=(10, 2))
        subtitle = ctk.CTkLabel(
            header,
            text=f'Modern UI Beta v{VERSION}  •  作者: luyu14039  •  试用新版界面',
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(anchor='w', padx=14, pady=(0, 4))

        link_label = ctk.CTkLabel(
            header,
            text='GitHub: ' + GITHUB_URL,
            font=ctk.CTkFont(size=12, underline=True),
            text_color='#4d8dff',
            cursor='hand2'
        )
        link_label.pack(anchor='w', padx=16, pady=(0, 8))
        link_label.bind('<Button-1>', lambda _ : self._open_github())

        # 主内容分裂：左配置，右日志
        body = ctk.CTkFrame(self.root, corner_radius=14)
        body.pack(fill='both', expand=True, padx=14, pady=(0, 12))
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, corner_radius=14)
        left.grid(row=0, column=0, sticky='nsw', padx=(12, 8), pady=12)
        right = ctk.CTkFrame(body, corner_radius=14)
        right.grid(row=0, column=1, sticky='nsew', padx=(8, 12), pady=12)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # 左侧滚动容器 (避免窗口缩放挤压)
        self._left_inner = left
        self._build_left_panel(left)
        self._build_right_panel(right)

        footer = ctk.CTkLabel(
            self.root,
            text=f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  Modern UI Beta v{VERSION}",
            font=ctk.CTkFont(size=11)
        )
        footer.pack(fill='x', pady=(0, 6))

    def _build_left_panel(self, parent):
        pady_block = (10, 4)
        # 存档选择
        sec1 = ctk.CTkLabel(parent, text='1. 选择存档 (.txt)', font=ctk.CTkFont(size=14, weight='bold'))
        sec1.pack(anchor='w', padx=14, pady=pady_block)
        row1 = ctk.CTkFrame(parent, fg_color='transparent')
        row1.pack(fill='x', padx=14)
        btn_choose_save = ctk.CTkButton(row1, text='浏览...', width=90, command=self.choose_save_file)
        btn_choose_save.pack(side='left')
        entry_save = ctk.CTkEntry(row1, textvariable=self.save_file, placeholder_text='选择群星导出的存档文本')
        entry_save.pack(side='left', fill='x', expand=True, padx=8)

        # 帝国名称
        sec2 = ctk.CTkLabel(parent, text='2. 玩家帝国名称 (可留空)', font=ctk.CTkFont(size=14, weight='bold'))
        sec2.pack(anchor='w', padx=14, pady=pady_block)
        entry_empire = ctk.CTkEntry(parent, textvariable=self.empire_name, placeholder_text='留空=玩家帝国')
        entry_empire.pack(fill='x', padx=14)

        # 选项
        sec3 = ctk.CTkLabel(parent, text='3. 选项', font=ctk.CTkFont(size=14, weight='bold'))
        sec3.pack(anchor='w', padx=14, pady=pady_block)
        chk_year = ctk.CTkCheckBox(parent, text='生成年度标记', variable=self.include_year)
        chk_year.pack(anchor='w', padx=22, pady=(0, 6))

        # 输出目录
        sec4 = ctk.CTkLabel(parent, text='4. 输出目录', font=ctk.CTkFont(size=14, weight='bold'))
        sec4.pack(anchor='w', padx=14, pady=pady_block)
        row_out = ctk.CTkFrame(parent, fg_color='transparent')
        row_out.pack(fill='x', padx=14)
        btn_out = ctk.CTkButton(row_out, text='选择目录', width=90, command=self.choose_output_dir)
        btn_out.pack(side='left')
        entry_out = ctk.CTkEntry(row_out, textvariable=self.output_dir, placeholder_text='选择输出目录')
        entry_out.pack(side='left', fill='x', expand=True, padx=8)

        # 运行区域
        sec5 = ctk.CTkLabel(parent, text='5. 运行', font=ctk.CTkFont(size=14, weight='bold'))
        sec5.pack(anchor='w', padx=14, pady=pady_block)
        run_row = ctk.CTkFrame(parent, fg_color='透明' if False else 'transparent')
        run_row.pack(fill='x', padx=14, pady=(0,4))
        self.run_button = ctk.CTkButton(run_row, text='开始生成', command=self.start_generation, fg_color='#3d82f7', hover_color='#4d8dff')
        self.run_button.pack(side='left')
        self.open_dir_button = ctk.CTkButton(run_row, text='打开输出目录', command=self.open_output_dir, state='disabled')
        self.open_dir_button.pack(side='left', padx=6)
        self.clear_log_button = ctk.CTkButton(run_row, text='清空日志', command=self.clear_log, fg_color='#444c55')
        self.clear_log_button.pack(side='left', padx=6)
        self.update_button = ctk.CTkButton(run_row, text='检查更新', command=self.check_update, fg_color='#2d6a4f', hover_color='#2f855a')
        self.update_button.pack(side='left', padx=6)

        self.status_label = ctk.CTkLabel(parent, text='状态: 就绪', text_color='#6dd283', anchor='w')
        self.status_label.pack(fill='x', padx=16, pady=(6, 4))

        # Tooltips
        for w, tip in [
            (btn_choose_save, '选择 Stellaris 导出的 txt 存档'),
            (entry_save, '存档文件路径'),
            (entry_empire, '你的玩家帝国显示名称，可留空'),
            (chk_year, '是否生成每年的标记分隔'),
            (btn_out, '选择保存输出文件的目录'),
            (self.run_button, '开始解析并生成编年史'),
            (self.open_dir_button, '任务成功后打开输出目录'),
            (self.clear_log_button, '清空右侧日志窗口'),
            (self.update_button, '从 GitHub 查询最新版本'),
        ]:
            Tooltip(w, tip)

    def _build_right_panel(self, parent):
        # 进度
        top_bar = ctk.CTkFrame(parent, fg_color='transparent')
        top_bar.grid(row=0, column=0, sticky='ew', pady=(6, 0), padx=10)
        self.progress_bar = ctk.CTkProgressBar(top_bar)
        self.progress_bar.pack(fill='x', expand=True, side='left')
        self.progress_bar.set(0)
        self.step_label = ctk.CTkLabel(top_bar, textvariable=self.current_step, width=140, anchor='w')
        self.step_label.pack(side='left', padx=(10,0))

        # 日志标题与操作
        title_row = ctk.CTkFrame(parent, fg_color='transparent')
        title_row.grid(row=1, column=0, sticky='ew', padx=10, pady=(10, 4))
        lbl = ctk.CTkLabel(title_row, text='运行状态 / 日志', font=ctk.CTkFont(size=15, weight='bold'))
        lbl.pack(side='left')
        self.log_search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(title_row, textvariable=self.log_search_var, placeholder_text='搜索关键字 (回车) ', width=200)
        self.search_entry.pack(side='right')
        self.search_entry.bind('<Return>', self._search_log)

        # 日志框
        log_frame = ctk.CTkFrame(parent, corner_radius=12)
        log_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 10))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(log_frame, wrap='word')
        self.log_text.grid(row=0, column=0, sticky='nsew')

        # 底部提示
        hint_text = (
            f"提示: 当前版本 v{VERSION} (Beta)"
            "欢迎在 GitHub 提交 Issue 反馈改进。"
        )
        hint = ctk.CTkLabel(parent, text=hint_text, font=ctk.CTkFont(size=11), text_color='#8aa0b3', wraplength=720, justify='left')
        hint.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 6))

        Tooltip(self.search_entry, '输入关键字并按回车，高亮首次匹配')

        self.log_text.bind('<Button-3>', self._popup_menu)

    # 日志搜索
    def _search_log(self, _):
        key = self.log_search_var.get().strip()
        if not key:
            return
        content = self.log_text.get('1.0', 'end')
        idx = content.find(key)
        if idx >= 0:
            # 定位行
            upto = content[:idx]
            line_no = upto.count('\n') + 1
            self.log_text.see(f"{line_no}.0")
            print(f"🔍 找到匹配: 第 {line_no} 行")
        else:
            print("🔍 未找到匹配关键字")

    # 日志与上下文菜单
    def _apply_context_menu(self):
        self._ctx_menu = ctk.CTkOptionMenu
        # 使用原生 tk 菜单（ctk 未封装右键菜单）
        import tkinter as tk
        self._menu = tk.Menu(self.root, tearoff=0)
        self._menu.add_command(label='复制全部', command=self._copy_all)
        self._menu.add_command(label='清空日志', command=self.clear_log)

    def _popup_menu(self, event):
        import tkinter as tk
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()

    def _copy_all(self):
        data = self.log_text.get('1.0', 'end')
        self.root.clipboard_clear()
        self.root.clipboard_append(data)
        print('✅ 日志已复制到剪贴板')

    # 绑定快捷键
    def _bind_shortcuts(self):
        self.root.bind('<Control-r>', lambda _: self.start_generation())
        self.root.bind('<Control-l>', lambda _: self.clear_log())

    def _init_logger(self):
        self.logger = GuiLogger(self.log_text)
        sys.stdout = self.logger
        sys.stderr = self.logger
        self.logger.start(self.root)
        print(f'🛰 Modern UI 初始化完成 - 版本 v{VERSION}')
        print(f'ℹ 项目主页: {GITHUB_URL}')
        print('💬 欢迎反馈问题 / 提交改进建议 (Issue)')
        print('🔧 使用检查更新功能以确认是否有新版本。')

    def _open_github(self):
        try:
            webbrowser.open(GITHUB_URL)
        except Exception as e:
            print(f'⚠ 打开 GitHub 失败: {e}')

    # 选择/清理
    def choose_save_file(self):
        import tkinter.filedialog as fd
        path = fd.askopenfilename(title='选择群星存档文本文件', filetypes=[('Text Files','*.txt'), ('All Files','*.*')])
        if path:
            self.save_file.set(path)
            print(f'📥 选择存档: {path}')

    def choose_output_dir(self):
        import tkinter.filedialog as fd
        path = fd.askdirectory(title='选择输出目录')
        if path:
            self.output_dir.set(path)
            print(f'📁 输出目录: {path}')

    def clear_log(self):
        self.log_text.delete('1.0', 'end')
        print('📝 日志已清空')

    # 运行逻辑
    def start_generation(self):
        if StellarisChronicleGenerator is None:
            print('❌ 缺少核心脚本，无法运行')
            return
        if self.running_thread and self.running_thread.is_alive():
            print('⚠ 已有任务在运行...')
            return
        save_file = self.save_file.get().strip()
        out_dir = self.output_dir.get().strip()
        if not save_file:
            print('⚠ 请先选择存档文件')
            return
        if not os.path.isfile(save_file):
            print('❌ 存档文件不存在')
            return
        if not out_dir:
            print('⚠ 请选择输出目录')
            return
        if not os.path.isdir(out_dir):
            print('❌ 输出目录无效')
            return

        empire = self.empire_name.get().strip()
        include_year = self.include_year.get()
        
        # 步骤1：显示用户选择对话框
        print('🔧 请选择生成模式...')
        choice_dialog = UserChoiceDialog(self.root)
        generation_mode = choice_dialog.show()
        
        if not generation_mode:
            print('⚠ 用户取消操作')
            return
            
        print(f'✅ 用户选择: {"随机生成" if generation_mode == "random" else "手动输入"}')
        
        # 步骤2：如果选择手动输入，先解析事件并获取用户输入
        manual_inputs = None
        if generation_mode == "manual":
            print('🔍 正在分析存档，请稍候...')
            try:
                # 临时创建生成器进行分析
                temp_gen = StellarisChronicleGenerator()  # type: ignore
                if not temp_gen.parse_save_file(save_file):
                    print('❌ 存档解析失败，无法进行手动输入分析')
                    return
                
                # 分析需要手动输入的实体
                pending_entities = temp_gen.analyze_events_for_manual_input()
                
                if not pending_entities:
                    print('ℹ 未发现需要手动输入的实体，将使用随机生成模式')
                    generation_mode = "random"
                else:
                    print(f'📝 需要您为 {len(pending_entities)} 个实体输入名称')
                    
                    # 显示手动输入对话框
                    input_dialog = ManualInputDialog(self.root, pending_entities)
                    manual_inputs = input_dialog.show()
                    
                    if manual_inputs is None:
                        print('⚠ 用户取消手动输入')
                        return
                    
                    print(f'✅ 收到 {len(manual_inputs)} 个手动输入的名称')
                    
            except Exception as e:
                print(f'❌ 分析存档时发生错误: {e}')
                return

        self.clear_log()
        print('==== 开始生成任务 (Modern Enhanced) ====')
        print(f'存档文件: {save_file}')
        print(f'输出目录: {out_dir}')
        print(f'玩家帝国: {empire or "玩家帝国(默认)"}')
        print(f'年度标记: {"包含" if include_year else "不包含"}')
        print(f'生成模式: {"随机生成" if generation_mode == "random" else "手动输入"}')

        self._lock_ui(True)
        self._set_status('运行中...', '#e0b458')
        self._update_progress(0, '初始化')
        self._start_spinner()

        def task():
            success = False
            try:
                gen = StellarisChronicleGenerator()  # type: ignore
                self._set_step(5, '设置参数')
                
                # 设置生成模式
                gen.set_generation_mode(generation_mode)
                
                # 如果是手动输入模式，设置用户输入的名称
                if generation_mode == "manual" and manual_inputs:
                    for key, input_data in manual_inputs.items():
                        if input_data['type'] == 'empire':
                            gen.set_manual_empire_name(key, input_data['name'])
                        elif input_data['type'] == 'fallen_empire':
                            gen.set_manual_empire_name(key, input_data['name'])
                        elif input_data['type'] == 'leviathan':
                            gen.set_manual_leviathan_name(key, input_data['name'])
                
                if empire:
                    gen.set_player_empire_name(empire)
                gen.set_year_markers_option(include_year)
                
                self._set_step(15, '解析存档')
                if not gen.parse_save_file(save_file):
                    print('❌ 解析失败，任务终止')
                else:
                    self._set_step(45, '初版编年史')
                    initial = gen.generate_initial_chronicle()
                    self._set_step(65, '替换占位符')
                    final = gen.generate_final_chronicle(initial)
                    self._set_step(80, '生成设定')
                    entities = gen.generate_entities_settings_file()
                    self._set_step(90, '保存文件')
                    gen.save_chronicle_files(final, entities, out_dir)
                    self._set_step(100, '完成')
                    print('\n🎉 生成完成 (Modern Enhanced)!')
                    print(f'输出目录: {out_dir}')
                    success = True
            except Exception as e:
                print(f'❌ 运行过程中发生错误: {e}')
                traceback.print_exc()
            finally:
                self._last_success = success
                self.root.after(0, self._on_task_finish)

        self.running_thread = threading.Thread(target=task, daemon=True)
        self.running_thread.start()

    # UI 锁定
    def _lock_ui(self, running: bool):
        if running:
            self.run_button.configure(text='生成中...', state='disabled', fg_color='#a6781f')
            self.open_dir_button.configure(state='disabled')
            self.clear_log_button.configure(state='disabled')
        else:
            self.run_button.configure(text='开始生成', state='normal', fg_color='#3d82f7')
            if self._last_success:
                self.open_dir_button.configure(state='normal')
            self.clear_log_button.configure(state='normal')
            self._stop_spinner()

    def _set_status(self, text: str, color: str):
        self.status_label.configure(text=f'状态: {text}', text_color=color)

    # 进度
    def _update_progress(self, value: int, step: str):
        self.progress_value = value
        self.progress_bar.set(value / 100)
        self.current_step.set(step)

    def _set_step(self, value: int, step: str):
        self.root.after(0, lambda: self._update_progress(value, step))

    # Spinner (按钮动态反馈)
    def _start_spinner(self):
        self._spinner_running = True
        self._spinner_phase = 0
        def spin():
            if not self._spinner_running:
                return
            frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
            self.run_button.configure(text=f'{frames[self._spinner_phase % len(frames)]} 生成中...')
            self._spinner_phase += 1
            self.root.after(120, spin)
        spin()

    def _stop_spinner(self):
        self._spinner_running = False

    # ------------------ 更新检查 ------------------
    def check_update(self):
        if self.running_thread and self.running_thread.is_alive():
            print('⚠ 当前任务运行中，稍后再检查更新。')
            return
        print('🔍 正在检查更新...')
        threading.Thread(target=self._do_check_update, daemon=True).start()

    def _do_check_update(self):
        try:
            latest = self._fetch_latest_version()
            if not latest:
                print('⚠ 无法获取远端版本信息。')
                return
            cmp = self._compare_versions(latest, VERSION)
            if cmp > 0:
                print(f'⬆ 检测到新版本: v{latest}  当前: v{VERSION}')
                print(f'➡ 访问 {GITHUB_URL} 获取最新代码。')
            elif cmp == 0:
                print(f'✅ 已是最新版本 v{VERSION}')
            else:
                print(f'ℹ 本地版本 v{VERSION} 高于远端 (可能是开发分支)。')
        except Exception as e:
            print(f'❌ 检查更新失败: {e}')

    def _fetch_latest_version(self) -> Optional[str]:
        base_api = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}'
        urls = []
        if PREF_CHANNEL == 'releases':
            urls.append(base_api + '/releases/latest')
            urls.append(base_api + '/tags')  # 备用
        else:
            urls.append(base_api + '/tags')
            urls.append(base_api + '/releases/latest')
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': f'StellarisChronicleGUI/{VERSION}'})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode('utf-8', errors='ignore'))
                # releases/latest 结构: { tag_name: 'v0.12' }
                if isinstance(data, dict) and 'tag_name' in data:
                    tag = str(data['tag_name']).lstrip('vV')
                    if tag:
                        return tag
                # tags 结构: [ { name: 'v0.11'}, ... ]
                if isinstance(data, list):
                    for item in data:
                        name = str(item.get('name','')).lstrip('vV')
                        if name:
                            return name
            except urllib.error.HTTPError as e:
                # 尝试下一个
                continue
            except Exception:
                continue
        return None

    @staticmethod
    def _compare_versions(a: str, b: str) -> int:
        def norm(v: str):
            return [int(x) if x.isdigit() else 0 for x in v.replace('-', '.').split('.')]
        pa = norm(a)
        pb = norm(b)
        # 对齐长度
        length = max(len(pa), len(pb))
        pa += [0] * (length - len(pa))
        pb += [0] * (length - len(pb))
        for x, y in zip(pa, pb):
            if x > y:
                return 1
            if x < y:
                return -1
        return 0

    # 任务结束
    def _on_task_finish(self):
        if self._last_success:
            self._set_status('完成', '#4cbf56')
        else:
            self._set_status('失败', '#d9534f')
        self._lock_ui(False)

    def open_output_dir(self):
        path = self.output_dir.get().strip()
        if path and os.path.isdir(path):
            try:
                os.startfile(path)
            except Exception as e:
                print(f'❌ 打开目录失败: {e}')
        else:
            print('⚠ 尚未生成成功的输出目录')

    # 关闭
    def on_close(self):
        if self.running_thread and self.running_thread.is_alive():
            # 简化不弹窗；可扩展为确认
            print('⚠ 后台任务仍在运行，直接关闭可能中断。')
        if self.logger:
            sys.stdout = self.logger._orig_stdout
            sys.stderr = self.logger._orig_stderr
            self.logger.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = ModernGUI()
    app.run()


if __name__ == '__main__':
    main()
