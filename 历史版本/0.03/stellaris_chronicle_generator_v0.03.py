#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群星（Stellaris）帝国编年史生成器

该脚本能够解析群星游戏存档文件，并根据玩家帝国的时间线事件
自动生成一部完整的帝国编年史，包括动态生成的AI帝国设定。

作者: luyu14039
日期: 2025年9月18日
版本: v0.03
"""

import re
import json
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class TimelineEvent:
    """时间线事件数据结构"""
    date: str
    definition: str
    data: Dict[str, Any]
    raw_text: str


@dataclass
class GeneratedEntity:
    """动态生成的实体（帝国、种族等）"""
    entity_type: str  # "empire", "species", "fallen_empire", "pre_ftl"
    name: str
    properties: Dict[str, Any]
    placeholder_id: str


class StellarisChronicleGenerator:
    """群星帝国编年史生成器"""
    
    def __init__(self):
        """初始化生成器"""
        print("=" * 60)
        print("群星（Stellaris）帝国编年史生成器 v0.03")
        print("=" * 60)
        print("⚠️  本项目正在开发中！事件代码不全，欢迎联系Github主页补充反馈！")
        print("=" * 60)
        
        # 存储解析后的事件
        self.timeline_events: List[TimelineEvent] = []
        
        # 动态生成的实体
        self.generated_entities: Dict[str, GeneratedEntity] = {}
        
        # 占位符计数器
        self.entity_counters = {
            'empire': 0,
            'species': 0,
            'fallen_empire': 0,
            'pre_ftl': 0
        }
        
        # 玩家帝国名称（默认值）
        self.player_empire_name = "玩家帝国"
        
        # 配置选项
        self.include_year_markers = True  # 是否包含年度标记事件
        
        # 初始化事件代码映射表
        self.event_descriptions = self._initialize_event_descriptions()
        
        # 初始化帝国生成数据
        self.empire_generation_data = self._initialize_empire_data()
    
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
            "timeline_leviathan_encountered": "眠者将醒_发现星神兽_帝国事件_[玩家帝国]遭遇了{leviathan_name}",
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
            "timeline_origin_shroudwalker_apprentice": "虚境导师_帝国起源_[玩家帝国]一群被称为\'虚行者\'的神秘灵能主义者对这个文明产生了兴趣，并决定将他们收为学徒。他们承诺会教给他们虚境的奥秘，但这背后可能隐藏着更深层次的动机",
            "timeline_origin_imperial_vassal": "帝国封邑_帝国起源_[玩家帝国]这个文明是某个更强大的星际帝国的一个小附庸。他们受制于宗主国的法律和异想天开，但他们也受到宗主国的保护，并可以从宗主国的先进技术中受益",
            "timeline_origin_overtuned": "强夺天工_帝国起源_[玩家帝国]这个文明已经掌握了基因工程的艺术，他们不断地调整自己的身体，以追求完美。他们的领导人痴迷于效率和生产力，他们将不惜一切代价来实现自己的目标",
            "timeline_origin_toxic_knights": "毒圣骑士_帝国起源_[玩家帝国]一群神秘的骑士来到了这个文明的母星，他们承诺会保护他们免受银河系中潜伏的恐怖势力的侵害。他们带来了一种神秘的\'毒液\'，他们说这种毒液可以赋予他们超人的力量，但代价是什么呢？",
            "timeline_origin_payback": "血债血偿_帝国起源_[玩家帝国]这个文明的母星曾被一个更强大的星际帝国征服和奴役。在多年的压迫之后，他们终于成功地发动了一场成功的起义，并赢得了自由。但他们永远不会忘记他们所遭受的苦难，他们发誓要向他们的前压迫者复仇",
            "timeline_origin_broken_shackles": "粉碎的枷锁_帝国起源_[玩家帝国]这个文明由来自银河系各地不同物种的难民和逃亡的奴隶组成。他们在共同的苦难中找到了团结，并建立了一个新的社会，在这个社会中，所有人都生而平等。他们发誓要解放所有被奴役的人民，并粉碎压迫他们的枷锁",
            "timeline_origin_fear_of_the_dark": "黑暗之怖_帝国起源_[玩家帝国]这个文明对黑暗有着一种非理性的恐惧。他们相信，在群星之间的虚空中潜伏着一些可怕的东西，他们会不惜一切代价避免与它接触。他们将自己的文明局限在自己的太阳系中，并希望永远不会有任何东西来打扰他们",
            "timeline_origin_riftworld": "裂隙当空_帝国起源_[玩家帝国]这个文明的母星正处于被一个巨大的、不断扩大的时空裂缝吞噬的边缘。他们必须在自己的世界被撕裂之前找到逃离的方法",
            "timeline_origin_cybernetic_creed": "义体信条_帝国起源_[玩家帝国]这个文明相信，有机体是脆弱和不完美的。他们寻求通过控制论来超越自己的肉体，并成为一种新的、更高级的存在形式",
            "timeline_origin_synthetic_fertility": "合成繁衍_帝国起源_[玩家帝国]这个文明已经失去了自然繁殖的能力。他们现在依靠先进的机器人技术和基因工程来创造新的后代。但这种对技术的依赖也让他们变得脆弱",
            "timeline_origin_arc_welders": "电弧焊机_帝国起源_[玩家帝国]这个文明由一群技术娴熟的工程师和工匠组成，他们擅长建造和维修大型结构。他们以其在电弧焊方面的专业知识而闻名，他们可以用它来创造出令人惊叹的艺术品和强大的战争机器"
        }
    
    def _initialize_empire_data(self) -> Dict[str, Any]:
        """初始化帝国生成所需的数据"""
        return {
            # 物种肖像列表
            'portraits': [
                {'name': '类人', 'weight': 15},
                {'name': '哺乳类', 'weight': 12},
                {'name': '爬行类', 'weight': 12},
                {'name': '鸟类', 'weight': 12},
                {'name': '节肢类', 'weight': 12},
                {'name': '软体类', 'weight': 10},
                {'name': '真菌类', 'weight': 9},
                {'name': '岩石类', 'weight': 8},
                {'name': '植物类', 'weight': 7},
                {'name': '水生类', 'weight': 3}
            ],
            
            # 名称列表映射
            'name_lists': {
                '类人': ['人类联合国', '地球联邦', '太阳系联盟', '人类殖民者联邦', '地球共同体', '泰拉联邦'],
                '哺乳类': ['兽族联盟', '野兽帝国', '毛族共和国', '兽人王国', '野性部落', '爪牙联邦'],
                '爬行类': ['鳞甲帝国', '爬虫联盟', '冷血王朝', '蜥蜴共和国', '蛇族联邦', '龙血帝国'],
                '鸟类': ['羽翼王国', '飞行者联盟', '天空帝国', '翼族共和国', '鸟人联邦', '高翔集群'],
                '节肢类': ['虫族蜂巢', '节肢帝国', '甲壳联盟', '昆虫王国', '蛛网共同体', '多足联合'],
                '软体类': ['触手帝国', '软体联盟', '海洋王国', '湿润共和国', '粘液联邦', '深渊集群'],
                '真菌类': ['菌丝网络', '真菌王国', '孢子联盟', '腐蚀帝国', '菌落共同体', '孢子集群'],
                '岩石类': ['岩石联盟', '石头帝国', '矿物王国', '晶体共和国', '地质联邦', '硅基集群'],
                '植物类': ['叶绿联盟', '植物王国', '花园帝国', '根系网络', '光合共同体', '绿叶集群'],
                '水生类': ['深海帝国', '水族联盟', '海洋王国', '潮汐共和国', '水流联邦', '深蓝集群']
            },
            
            # 思潮列表
            'ethics': [
                {'name': '排外主义', 'opposite': '亲外主义', 'weight': 20},
                {'name': '亲外主义', 'opposite': '排外主义', 'weight': 15},
                {'name': '唯物主义', 'opposite': '唯心主义', 'weight': 25},
                {'name': '唯心主义', 'opposite': '唯物主义', 'weight': 20},
                {'name': '威权主义', 'opposite': '平等主义', 'weight': 22},
                {'name': '平等主义', 'opposite': '威权主义', 'weight': 18},
                {'name': '军国主义', 'opposite': '和平主义', 'weight': 25},
                {'name': '和平主义', 'opposite': '军国主义', 'weight': 15}
            ],
            
            # 政体列表
            'authorities': [
                {'name': '民主制', 'weight': 25, 'forbidden_ethics': ['威权主义', '极端威权主义']},
                {'name': '寡头制', 'weight': 30, 'requirements': {}},
                {'name': '独裁制', 'weight': 25, 'forbidden_ethics': ['平等主义', '极端平等主义']},
                {'name': '帝制', 'weight': 20, 'required_ethics': ['威权主义', '极端威权主义']}
            ],
            
            # 堕落帝国配置
            'fallen_empires': [
                {
                    'name': '希拉多种帝国',
                    'type': '圣地守护者',
                    'ethics': ['极端唯心主义', '和平主义'],
                    'personality': '狂热的孤立主义者',
                    'species': '希拉多种族'
                },
                {
                    'name': '阿尔法知识者联盟',
                    'type': '知识管理者', 
                    'ethics': ['极端唯物主义', '和平主义'],
                    'personality': '固执的学者',
                    'species': '阿尔法种族'
                },
                {
                    'name': '军事孤立者帝国',
                    'type': '军事孤立者',
                    'ethics': ['极端排外主义', '军国主义'],
                    'personality': '警惕的帝国主义者',
                    'species': '孤立者种族'
                },
                {
                    'name': '永恒警卫者',
                    'type': '艺术赞助者',
                    'ethics': ['极端平等主义', '唯心主义'],
                    'personality': '慈善的保护者',
                    'species': '警卫者种族'
                }
            ],
            
            # 特质列表
            'traits': {
                'positive': [
                    {'name': '智慧', 'cost': 2, 'weight': 20},
                    {'name': '强壮', 'cost': 1, 'weight': 15},
                    {'name': '天生工程师', 'cost': 1, 'weight': 10},
                    {'name': '快速增殖', 'cost': 2, 'weight': 15},
                    {'name': '适应性强', 'cost': 2, 'weight': 12},
                    {'name': '长寿', 'cost': 1, 'weight': 8},
                    {'name': '天生物理学家', 'cost': 1, 'weight': 10},
                    {'name': '天生社会学家', 'cost': 1, 'weight': 10}
                ],
                'negative': [
                    {'name': '柔弱', 'gain': 1, 'weight': 15},
                    {'name': '生长缓慢', 'gain': 1, 'weight': 12},
                    {'name': '离经叛道', 'gain': 1, 'weight': 10},
                    {'name': '不善变通', 'gain': 2, 'weight': 8},
                    {'name': '令人厌恶', 'gain': 1, 'weight': 5},
                    {'name': '短寿', 'gain': 1, 'weight': 10}
                ]
            },
            
            # 事件倾向性
            'event_tendencies': {
                'timeline_first_war_declared': {
                    'favored_ethics': ['军国主义', '极端军国主义', '威权主义'],
                    'weights': [40, 60, 30]
                },
                'timeline_first_contact': {
                    'favored_ethics': ['亲外主义', '极端亲外主义'],
                    'weights': [35, 50]
                },
                'timeline_first_espionage_operation': {
                    'favored_ethics': ['排外主义', '威权主义', '军国主义'],
                    'weights': [30, 25, 35]
                },
                'timeline_elections': {
                    'favored_ethics': ['平等主义', '极端平等主义'],
                    'weights': [40, 60],
                    'forbidden_ethics': ['威权主义', '极端威权主义']
                }
            }
        }
    
    def set_player_empire_name(self, empire_name: str):
        """
        设置玩家帝国名称
        
        Args:
            empire_name: 玩家输入的帝国名称
        """
        if empire_name and empire_name.strip():
            self.player_empire_name = empire_name.strip()
            print(f"✅ 玩家帝国名称设置为: {self.player_empire_name}")
        else:
            print("✅ 使用默认帝国名称: 玩家帝国")
    
    def set_year_markers_option(self, include_year_markers: bool):
        """
        设置是否包含年度标记事件
        
        Args:
            include_year_markers: 是否包含年度标记事件
        """
        self.include_year_markers = include_year_markers
        if include_year_markers:
            print("✅ 将包含年度标记事件")
        else:
            print("✅ 将跳过年度标记事件")
    
    def parse_save_file(self, file_path: str) -> bool:
        """
        解析存档文件并提取timeline_events
        
        Args:
            file_path: 存档文件路径
            
        Returns:
            bool: 是否成功解析
        """
        print(f"\n🔍 开始解析存档文件: {file_path}")
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
            
            # 定位timeline_events数据块
            timeline_match = re.search(r'timeline_events\s*=\s*\{', content)
            if not timeline_match:
                print("❌ 未找到timeline_events数据块")
                return False
            
            print("✅ 找到timeline_events数据块，开始提取事件...")
            
            # 提取timeline_events内容
            start_pos = timeline_match.end() - 1  # 包含开头的{
            brace_count = 0
            end_pos = start_pos
            
            for i, char in enumerate(content[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            timeline_content = content[start_pos:end_pos]
            print(f"✅ timeline_events内容提取完成，长度: {len(timeline_content):,} 字符")
            
            # 解析事件
            self._parse_timeline_events(timeline_content)
            
            print(f"✅ 事件解析完成，共找到 {len(self.timeline_events)} 个事件")
            return True
            
        except FileNotFoundError:
            print(f"❌ 文件未找到: {file_path}")
            return False
        except Exception as e:
            print(f"❌ 解析文件时出错: {str(e)}")
            return False
    
    def _parse_timeline_events(self, timeline_content: str):
        """
        解析timeline_events内容
        
        Args:
            timeline_content: timeline_events的原始内容
        """
        # 更精确的事件块解析
        events = []
        lines = timeline_content.split('\n')
        current_event = None
        brace_count = 0
        in_event = False
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 计算大括号数量
            line_brace_count = line.count('{') - line.count('}')
            brace_count += line_brace_count
            
            # 检测事件开始 - 同时包含date和definition的行，或者单独的开始大括号
            if not in_event and line == '{' and brace_count >= 2:
                in_event = True
                current_event = {'lines': [], 'start_line': line_num}
            elif in_event and current_event is not None:
                current_event['lines'].append(line)
                
                # 检测事件结束 - 单独的结束大括号且层级正确
                if line == '}' and brace_count == 1:
                    # 解析完整事件
                    event_text = '\n'.join(current_event['lines'])
                    parsed_event = self._parse_single_event(event_text)
                    if parsed_event:
                        events.append(parsed_event)
                    
                    in_event = False
                    current_event = None
        
        # 按日期排序并存储
        events.sort(key=lambda x: x.date)
        self.timeline_events = events
    
    def _parse_single_event(self, event_text: str) -> Optional[TimelineEvent]:
        """
        解析单个事件
        
        Args:
            event_text: 事件的完整文本
            
        Returns:
            TimelineEvent: 解析后的事件对象，如果解析失败返回None
        """
        try:
            # 提取date和definition - 适应实际格式
            date_match = re.search(r'date\s*=\s*"([^"]+)"', event_text)
            definition_match = re.search(r'definition\s*=\s*"([^"]+)"', event_text)
            
            if not date_match or not definition_match:
                return None
            
            date_str = date_match.group(1)
            definition = definition_match.group(1)
            
            # 解析data部分
            data = {}
            data_match = re.search(r'data\s*=\s*\{([^}]*)\}', event_text, re.DOTALL)
            if data_match:
                data_content = data_match.group(1).strip()
                
                # 检查是否是纯数字序列（如 "0 7"）
                if re.match(r'^[\d\s]+$', data_content):
                    # 数字序列形式
                    numbers = [int(x) for x in data_content.split() if x.isdigit()]
                    data['numbers'] = numbers
                elif re.search(r'^\s*\d+\s*=', data_content, re.MULTILINE):
                    # 数组形式: 0="value1" 1="value2"
                    data_pairs = re.findall(r'(\d+)\s*=\s*"([^"]*)"', data_content)
                    data['items'] = [value for _, value in sorted(data_pairs, key=lambda x: int(x[0]))]
                else:
                    # 键值对形式
                    data_pairs = re.findall(r'(\w+)\s*=\s*"([^"]*)"', data_content)
                    for key, value in data_pairs:
                        data[key] = value
            
            return TimelineEvent(
                date=date_str,
                definition=definition,
                data=data,
                raw_text=event_text
            )
            
        except Exception as e:
            print(f"⚠️  解析事件时出错: {str(e)}")
            return None
    
    def generate_initial_chronicle(self) -> str:
        """
        生成初版编年史（包含占位符）
        
        Returns:
            str: 初版编年史文本
        """
        print("\n📝 开始生成初版编年史...")
        
        chronicle_lines = []
        chronicle_lines.append("=" * 60)
        chronicle_lines.append("群星帝国编年史")
        chronicle_lines.append("=" * 60)
        chronicle_lines.append("")
        
        # 统计过滤的事件数量
        filtered_events = 0
        total_events = len(self.timeline_events)
        
        for event in self.timeline_events:
            # 检查是否应该跳过年度标记事件
            if not self.include_year_markers and event.definition == "timeline_event_year":
                filtered_events += 1
                continue
                
            event_text = self._convert_event_to_text(event)
            chronicle_lines.append(f"{event.date} - {event_text}")
        
        initial_chronicle = "\n".join(chronicle_lines)
        
        if filtered_events > 0:
            print(f"✅ 初版编年史生成完成，共 {total_events - filtered_events} 个事件（已过滤 {filtered_events} 个年度标记事件）")
        else:
            print(f"✅ 初版编年史生成完成，共 {total_events} 个事件")
        
        return initial_chronicle
    
    def _convert_event_to_text(self, event: TimelineEvent) -> str:
        """
        将事件转换为描述文本
        
        Args:
            event: 时间线事件
            
        Returns:
            str: 事件描述文本
        """
        # 查找事件描述模板
        if event.definition in self.event_descriptions:
            template = self.event_descriptions[event.definition]
            
            # 准备格式化参数
            format_args = {'date': event.date}
            format_args.update(event.data)
            
            # 安全的格式化，避免缺少参数
            try:
                # 先找出模板中需要的所有占位符
                import string
                formatter = string.Formatter()
                required_fields = [field for _, field, _, _ in formatter.parse(template) if field]
                
                # 为缺失的字段提供默认值
                for field in required_fields:
                    if field not in format_args:
                        if field == 'location':
                            format_args[field] = '未知星系'
                        elif field == 'colony_name':
                            format_args[field] = '新殖民地'
                        elif field == 'system_name':
                            format_args[field] = '未知恒星系'
                        elif field == 'leader_name':
                            format_args[field] = '未知领袖'
                        elif field == 'planet_name':
                            format_args[field] = '未知星球'
                        elif field == 'fleet_name':
                            format_args[field] = '无敌舰队'
                        elif field == 'ship_name':
                            format_args[field] = '旗舰'
                        elif field == 'new_capital':
                            format_args[field] = '新首都'
                        elif field == 'leviathan_name':
                            format_args[field] = '星兽'
                        elif field.endswith('_empire'):
                            # 需要生成帝国占位符
                            format_args[field] = f'帝国{len(self.generated_entities) + 1}'
                        elif field.endswith('_fallen_empire'):
                            format_args[field] = f'堕落帝国{len([e for e in self.generated_entities.values() if e.entity_type == "fallen_empire"]) + 1}'
                        else:
                            format_args[field] = f'未知_{field}'
                
                text = template.format(**format_args)
                
                # 处理需要生成实体的占位符
                text = self._process_entity_placeholders(text, event)
                
                return text
                
            except Exception as e:
                print(f"⚠️  格式化事件描述时出错 ({event.definition}): {str(e)}")
                return f"{event.definition} ({event.date}) - 格式化错误"
        else:
            # 未收录的事件代码
            return f"未收录事件代码 ({event.definition})，欢迎补充！"
    
    def _process_entity_placeholders(self, text: str, event: TimelineEvent) -> str:
        """
        处理文本中的实体占位符
        
        Args:
            text: 包含占位符的文本
            event: 当前事件
            
        Returns:
            str: 处理后的文本
        """
        # 查找所有需要替换的占位符
        placeholders = re.findall(r'\[([^\]]+)\]', text)
        
        for placeholder in placeholders:
            if placeholder not in self.generated_entities:
                # 生成新实体
                entity = self._generate_entity_for_placeholder(placeholder, event)
                if entity:
                    self.generated_entities[placeholder] = entity
        
        return text
    
    def _generate_entity_for_placeholder(self, placeholder: str, event: TimelineEvent) -> Optional[GeneratedEntity]:
        """
        为占位符生成对应的实体
        
        Args:
            placeholder: 占位符文本 (如 "帝国1", "种族1")
            event: 触发生成的事件
            
        Returns:
            GeneratedEntity: 生成的实体
        """
        if placeholder.startswith('帝国'):
            return self._generate_ai_empire(placeholder, event)
        elif placeholder.startswith('堕落帝国'):
            return self._generate_fallen_empire(placeholder, event)
        elif placeholder.startswith('种族'):
            return self._generate_species(placeholder, event)
        elif placeholder == '玩家帝国':
            # 玩家帝国不需要生成，直接使用占位符
            return None
        
        return None
    
    def _generate_ai_empire(self, placeholder: str, event: TimelineEvent) -> GeneratedEntity:
        """生成AI帝国"""
        self.entity_counters['empire'] += 1
        
        # 根据事件类型确定倾向性
        event_bias = None
        if event.definition in self.empire_generation_data['event_tendencies']:
            event_bias = event.definition
        
        # 生成物种
        portrait = self._weighted_random(self.empire_generation_data['portraits'])
        species_name = f"{portrait['name']}种族{self.entity_counters['empire']}"
        
        # 生成思潮（基于事件倾向）
        ethics = self._generate_ethics(event_bias)
        
        # 生成政体
        authority = self._select_authority(ethics)
        
        # 生成帝国名称
        name_options = self.empire_generation_data['name_lists'][portrait['name']]
        empire_name = random.choice(name_options) + f"第{self.entity_counters['empire']}共同体"
        
        # 生成特质
        traits = self._generate_traits()
        
        properties = {
            'name': empire_name,
            'species': species_name,
            'portrait': portrait['name'],
            'ethics': ethics,
            'authority': authority,
            'traits': traits,
            'personality': self._generate_personality(ethics),
            'type': 'ai_empire'
        }
        
        return GeneratedEntity(
            entity_type='empire',
            name=empire_name,
            properties=properties,
            placeholder_id=placeholder
        )
    
    def _generate_fallen_empire(self, placeholder: str, event: TimelineEvent) -> GeneratedEntity:
        """生成堕落帝国"""
        # 从预定义的堕落帝国中选择
        fallen_empire_config = random.choice(self.empire_generation_data['fallen_empires'])
        
        properties = {
            'name': fallen_empire_config['name'],
            'species': fallen_empire_config['species'],
            'type_name': fallen_empire_config['type'],
            'ethics': fallen_empire_config['ethics'],
            'personality': fallen_empire_config['personality'],
            'type': 'fallen_empire'
        }
        
        return GeneratedEntity(
            entity_type='fallen_empire',
            name=fallen_empire_config['name'],
            properties=properties,
            placeholder_id=placeholder
        )
    
    def _generate_species(self, placeholder: str, event: TimelineEvent) -> GeneratedEntity:
        """生成种族"""
        self.entity_counters['species'] += 1
        
        portrait = self._weighted_random(self.empire_generation_data['portraits'])
        species_name = f"{portrait['name']}族{self.entity_counters['species']}"
        traits = self._generate_traits()
        
        properties = {
            'name': species_name,
            'portrait': portrait['name'],
            'traits': traits,
            'type': 'species'
        }
        
        return GeneratedEntity(
            entity_type='species',
            name=species_name,
            properties=properties,
            placeholder_id=placeholder
        )
    
    def _weighted_random(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """权重随机选择"""
        total_weight = sum(item['weight'] for item in items)
        random_value = random.randint(1, total_weight)
        
        current_weight = 0
        for item in items:
            current_weight += item['weight']
            if random_value <= current_weight:
                return item
        
        return items[-1]  # fallback
    
    def _generate_ethics(self, event_bias: Optional[str] = None) -> List[str]:
        """生成思潮"""
        ethics = []
        total_points = 3
        
        # 如果有事件倾向性，优先考虑
        if event_bias and event_bias in self.empire_generation_data['event_tendencies']:
            tendency = self.empire_generation_data['event_tendencies'][event_bias]
            if 'favored_ethics' in tendency:
                favored_ethic = random.choice(tendency['favored_ethics'])
                ethics.append(favored_ethic)
                total_points -= 1
        
        # 分配剩余点数
        available_ethics = [e['name'] for e in self.empire_generation_data['ethics']]
        used_opposites = set()
        
        while total_points > 0 and len(ethics) < 3:
            # 过滤掉已使用思潮的对立面
            filtered_ethics = []
            for ethic_data in self.empire_generation_data['ethics']:
                ethic_name = ethic_data['name']
                if ethic_name not in ethics and ethic_name not in used_opposites:
                    filtered_ethics.append(ethic_data)
            
            if not filtered_ethics:
                break
                
            selected_ethic_data = self._weighted_random(filtered_ethics)
            selected_ethic = selected_ethic_data['name']
            
            ethics.append(selected_ethic)
            used_opposites.add(selected_ethic_data['opposite'])
            total_points -= 1
        
        return ethics
    
    def _select_authority(self, ethics: List[str]) -> str:
        """根据思潮选择政体"""
        available_authorities = []
        
        for auth in self.empire_generation_data['authorities']:
            # 检查禁止的思潮
            if 'forbidden_ethics' in auth:
                if any(ethic in ethics for ethic in auth['forbidden_ethics']):
                    continue
            
            # 检查必需的思潮
            if 'required_ethics' in auth:
                if not any(ethic in ethics for ethic in auth['required_ethics']):
                    continue
            
            available_authorities.append(auth)
        
        if not available_authorities:
            available_authorities = [auth for auth in self.empire_generation_data['authorities'] 
                                   if 'requirements' in auth and not auth['requirements']]
        
        selected_auth = self._weighted_random(available_authorities)
        return selected_auth['name']
    
    def _generate_traits(self) -> List[str]:
        """生成种族特质"""
        selected_traits = []
        total_cost = 0
        max_attempts = 20
        attempts = 0
        
        while total_cost <= 2 and len(selected_traits) < 5 and attempts < max_attempts:
            # 70%概率选择正面特质，30%概率选择负面特质
            use_positive = random.random() < 0.7
            trait_pool = (self.empire_generation_data['traits']['positive'] if use_positive 
                         else self.empire_generation_data['traits']['negative'])
            
            trait = self._weighted_random(trait_pool)
            
            if trait['name'] not in selected_traits:
                if use_positive:
                    new_cost = total_cost + trait['cost']
                else:
                    new_cost = total_cost - trait['gain']
                
                if new_cost <= 2:
                    selected_traits.append(trait['name'])
                    total_cost = new_cost
            
            attempts += 1
        
        return selected_traits
    
    def _generate_personality(self, ethics: List[str]) -> str:
        """根据思潮生成性格"""
        personality_map = {
            '军国主义': '好战的征服者',
            '极端军国主义': '残酷的征服者',
            '和平主义': '和平的商人',
            '极端和平主义': '生态的和平主义者',
            '排外主义': '孤立的帝国主义者',
            '极端排外主义': '狂热的排外主义者',
            '亲外主义': '友好的外交官',
            '极端亲外主义': '狂热的友谊使者',
            '威权主义': '专制的统治者',
            '极端威权主义': '独裁的暴君',
            '平等主义': '民主的理想主义者',
            '极端平等主义': '狂热的平等主义者',
            '唯物主义': '理性的探索者',
            '极端唯物主义': '技术的狂热者',
            '唯心主义': '精神的哲学家',
            '极端唯心主义': '狂热的信徒'
        }
        
        for ethic in ethics:
            if ethic in personality_map:
                return personality_map[ethic]
        
        return '谨慎的帝国主义者'
    
    def generate_final_chronicle(self, initial_chronicle: str) -> str:
        """
        生成最终编年史（替换所有占位符）
        
        Args:
            initial_chronicle: 初版编年史文本
            
        Returns:
            str: 最终编年史文本
        """
        print("\n🔄 开始替换占位符，生成最终编年史...")
        
        final_chronicle = initial_chronicle
        
        # 替换所有生成的实体占位符
        for placeholder, entity in self.generated_entities.items():
            pattern = f"\\[{re.escape(placeholder)}\\]"
            final_chronicle = re.sub(pattern, entity.name, final_chronicle)
        
        # 替换玩家帝国占位符
        final_chronicle = re.sub(r'\[玩家帝国\]', self.player_empire_name, final_chronicle)
        
        print(f"✅ 占位符替换完成，共替换了 {len(self.generated_entities)} 个实体")
        
        return final_chronicle
    
    def generate_entities_settings_file(self) -> str:
        """
        生成实体设定文件内容
        
        Returns:
            str: 设定文件内容
        """
        print("\n� 生成实体设定文件...")
        
        lines = []
        lines.append("=" * 60)
        lines.append("群星帝国编年史 - 动态生成实体设定")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append(f"总计生成实体: {len(self.generated_entities)} 个")
        lines.append("")
        
        # 按类型分组
        entities_by_type = {}
        for entity in self.generated_entities.values():
            entity_type = entity.entity_type
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        # 输出各类型实体
        for entity_type, entities in entities_by_type.items():
            type_names = {
                'empire': 'AI帝国',
                'fallen_empire': '堕落帝国', 
                'species': '种族',
                'pre_ftl': '前FTL文明'
            }
            
            lines.append(f"## {type_names.get(entity_type, entity_type.upper())} ({len(entities)}个)")
            lines.append("")
            
            for entity in entities:
                lines.append(f"### {entity.name}")
                lines.append(f"- **占位符**: [{entity.placeholder_id}]")
                
                if entity.entity_type == 'empire':
                    lines.append(f"- **种族**: {entity.properties['species']}")
                    lines.append(f"- **物种肖像**: {entity.properties['portrait']}")
                    lines.append(f"- **思潮**: {', '.join(entity.properties['ethics'])}")
                    lines.append(f"- **政体**: {entity.properties['authority']}")
                    lines.append(f"- **特质**: {', '.join(entity.properties['traits'])}")
                    lines.append(f"- **性格**: {entity.properties['personality']}")
                
                elif entity.entity_type == 'fallen_empire':
                    lines.append(f"- **种族**: {entity.properties['species']}")
                    lines.append(f"- **类型**: {entity.properties['type_name']}")
                    lines.append(f"- **思潮**: {', '.join(entity.properties['ethics'])}")
                    lines.append(f"- **性格**: {entity.properties['personality']}")
                
                elif entity.entity_type == 'species':
                    lines.append(f"- **物种肖像**: {entity.properties['portrait']}")
                    lines.append(f"- **特质**: {', '.join(entity.properties['traits'])}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def save_chronicle_files(self, final_chronicle: str, entities_settings: str, output_dir: str):
        """
        保存编年史和设定文件
        
        Args:
            final_chronicle: 最终编年史内容
            entities_settings: 实体设定内容
            output_dir: 输出目录
        """
        print(f"\n💾 保存文件到目录: {output_dir}")
        
        # 保存最终编年史
        chronicle_file = os.path.join(output_dir, "群星帝国编年史.txt")
        with open(chronicle_file, 'w', encoding='utf-8') as f:
            f.write(final_chronicle)
        print(f"✅ 编年史已保存: {chronicle_file}")
        
        # 保存实体设定
        settings_file = os.path.join(output_dir, "动态生成实体设定.md")
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(entities_settings)
        print(f"✅ 实体设定已保存: {settings_file}")
        
        # 生成统计信息
        stats_file = os.path.join(output_dir, "生成统计.txt")
        self._save_generation_stats(stats_file)
        print(f"✅ 生成统计已保存: {stats_file}")
    
    def _save_generation_stats(self, stats_file: str):
        """保存生成统计信息"""
        stats_lines = []
        stats_lines.append("=" * 40)
        stats_lines.append("群星帝国编年史生成统计")
        stats_lines.append("=" * 40)
        stats_lines.append("")
        stats_lines.append(f"解析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        stats_lines.append(f"总事件数: {len(self.timeline_events)}")
        
        # 计算年度标记事件数量
        year_marker_count = sum(1 for e in self.timeline_events if e.definition == "timeline_event_year")
        
        if self.include_year_markers:
            stats_lines.append(f"已知事件: {sum(1 for e in self.timeline_events if e.definition in self.event_descriptions)}")
            stats_lines.append(f"未知事件: {sum(1 for e in self.timeline_events if e.definition not in self.event_descriptions)}")
            stats_lines.append(f"年度标记事件: {year_marker_count} (已包含)")
        else:
            filtered_total = len(self.timeline_events) - year_marker_count
            known_events = sum(1 for e in self.timeline_events if e.definition in self.event_descriptions and e.definition != "timeline_event_year")
            unknown_events = sum(1 for e in self.timeline_events if e.definition not in self.event_descriptions)
            
            stats_lines.append(f"实际输出事件数: {filtered_total}")
            stats_lines.append(f"已知事件: {known_events}")
            stats_lines.append(f"未知事件: {unknown_events}")
            stats_lines.append(f"年度标记事件: {year_marker_count} (已过滤)")
        
        stats_lines.append("")
        stats_lines.append("生成实体统计:")
        for entity_type, count in self.entity_counters.items():
            if count > 0:
                stats_lines.append(f"- {entity_type}: {count}个")
        stats_lines.append("")
        
        # 未知事件列表
        unknown_events = [e.definition for e in self.timeline_events if e.definition not in self.event_descriptions]
        if unknown_events:
            stats_lines.append("未知事件代码:")
            for event_code in set(unknown_events):
                count = unknown_events.count(event_code)
                stats_lines.append(f"- {event_code} (出现{count}次)")
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(stats_lines))
    
    def run(self, save_file_path: str, skip_input: bool = False):
        """
        执行完整的编年史生成流程
        
        Args:
            save_file_path: 存档文件路径
            skip_input: 是否跳过用户输入（当命令行已提供帝国名称时）
        """
        print("🚀 开始执行群星帝国编年史生成...")
        
        # 获取用户输入的帝国名称（如果尚未设置）
        if not skip_input and self.player_empire_name == "玩家帝国":
            print("\n" + "=" * 40)
            print("🏛️  帝国名称设置")
            print("=" * 40)
            try:
                user_empire_name = input("请输入您的帝国名称（直接按回车使用默认名称'玩家帝国'）: ")
                self.set_player_empire_name(user_empire_name)
            except KeyboardInterrupt:
                print("\n\n❌ 用户取消操作")
                return
            except EOFError:
                print("⚠️  检测到非交互环境，使用默认帝国名称")
                
            print("=" * 40)
        
        # 获取用户对年度标记的偏好设置
        if not skip_input:
            print("\n" + "=" * 40)
            print("📅 年度标记设置")
            print("=" * 40)
            print("年度标记事件是形如 '2384.01.01 - 年度标记_2384.01.01_时光荏苒，2384.01.01年悄然而至。' 的条目")
            try:
                user_choice = input("是否包含年度标记事件？(y/N): ").strip().lower()
                include_markers = user_choice in ['y', 'yes', '是', '1', 'true']
                self.set_year_markers_option(include_markers)
            except KeyboardInterrupt:
                print("\n\n❌ 用户取消操作")
                return
            except EOFError:
                print("⚠️  检测到非交互环境，使用默认设置（包含年度标记）")
                
            print("=" * 40)
        
        # 步骤1: 解析存档文件
        if not self.parse_save_file(save_file_path):
            print("❌ 存档文件解析失败，程序终止")
            return
        
        # 步骤2: 生成初版编年史
        print("\n📝 生成初版编年史...")
        initial_chronicle = self.generate_initial_chronicle()
        
        # 步骤3: 动态生成实体并替换占位符
        print("\n🤖 动态生成AI实体...")
        final_chronicle = self.generate_final_chronicle(initial_chronicle)
        
        # 步骤4: 生成实体设定文件
        entities_settings = self.generate_entities_settings_file()
        
        # 步骤5: 保存所有文件
        output_dir = os.path.dirname(save_file_path)
        self.save_chronicle_files(final_chronicle, entities_settings, output_dir)
        
        print("\n🎉 群星帝国编年史生成完成！")
        print(f"📁 输出文件位置: {output_dir}")
        print("📚 生成文件:")
        print("  - 群星帝国编年史.txt (最终编年史)")
        print("  - 动态生成实体设定.md (AI帝国设定)")
        print("  - 生成统计.txt (统计信息)")
        print(f"\n🌟 您的帝国 '{self.player_empire_name}' 的编年史已生成完成！")


def main():
    """主函数"""
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("使用方法: ")
        print("  python stellaris_chronicle_generator.py <存档文件路径>")
        print("  python stellaris_chronicle_generator.py <存档文件路径> <帝国名称>")
        print("  python stellaris_chronicle_generator.py <存档文件路径> <帝国名称> <是否包含年度标记>")
        print("")
        print("例如: ")
        print("  python stellaris_chronicle_generator.py timeline_events.txt")
        print("  python stellaris_chronicle_generator.py timeline_events.txt 泰拉联邦")
        print("  python stellaris_chronicle_generator.py timeline_events.txt 泰拉联邦 no")
        print("")
        print("年度标记选项:")
        print("  yes/y/1/true: 包含年度标记事件")
        print("  no/n/0/false: 不包含年度标记事件")
        sys.exit(1)
    
    save_file_path = sys.argv[1]
    empire_name = sys.argv[2] if len(sys.argv) >= 3 else None
    year_markers_option = sys.argv[3] if len(sys.argv) == 4 else None
    
    if not os.path.exists(save_file_path):
        print(f"错误: 文件不存在 - {save_file_path}")
        sys.exit(1)
    
    # 创建生成器
    generator = StellarisChronicleGenerator()
    
    # 处理命令行参数
    skip_input = False
    
    # 如果命令行提供了帝国名称，直接使用
    if empire_name:
        generator.set_player_empire_name(empire_name)
        skip_input = True
    
    # 如果命令行提供了年度标记选项，直接使用
    if year_markers_option:
        include_markers = year_markers_option.lower() in ['yes', 'y', '1', 'true']
        generator.set_year_markers_option(include_markers)
        skip_input = True
    
    if skip_input:
        print("=" * 40)
        # 运行生成器，跳过交互输入
        generator.run(save_file_path, skip_input=True)
    else:
        # 运行生成器，需要交互输入
        generator.run(save_file_path)


if __name__ == "__main__":
    main()