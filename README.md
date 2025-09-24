<p align="center">
  <strong><a href="#zh">简体中文</a> ｜ <a href="#en">English</a></strong>
</p>

# Stellaris Empire Chronicle Generator（群星帝国编年史生成器）

<p align="center">
  <a href="https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/"><img alt="Online" src="https://img.shields.io/badge/Online-Pages-2088FF?logo=github"/></a>
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases"><img alt="Releases" src="https://img.shields.io/github/v/release/luyu14039/Stellaris-Empire-Chronicle-Generator?display_name=release&label=Releases"/></a>
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/issues"><img alt="Issues" src="https://img.shields.io/github/issues/luyu14039/Stellaris-Empire-Chronicle-Generator?label=Issues"/></a>
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/luyu14039/Stellaris-Empire-Chronicle-Generator?style=social"/></a>
</p>

<p align="center">
  <a href="https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/">在线版</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases">Releases</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/issues">Issues</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/stargazers">Stars</a>
</p>

<a id="zh"></a>

将《群星》(Stellaris) 存档中的时间线事件解析为一份可读的“帝国编年史”。v0.12 引入全新现代化 GUI、Windows 可执行文件（.exe），并上线无需安装即可使用的在线页面。

在线页面（推荐直接使用）：
https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/

> 纯前端运行，解析在本地浏览器完成，不上传你的文件。
![alt text](PIC/网页解析器截图.jpeg)
---

## 版本更新说明（Changelog）

- v0.12（2025-09-24）
  - GUI 化：提供基于 `customtkinter` 的现代界面（日志、进度条、搜索、右键菜单、状态指示）。
  - 发布 EXE：已在 Releases 提供打包好的 Windows 可执行文件，免 Python 环境即可使用。
  - 手动/随机生成：解析时可选择“手动输入名称”或“随机生成”，覆盖帝国与星神兽名称等关键内容。
  - 在线页面：发布 GitHub Pages 静态站点，可直接在浏览器内上传文本并生成结果，带时间轴可视化与下载。
  - 细节：统计文件会记录未知星神兽代码，便于反馈补全；内置检查更新入口。
- v0.03（2025-09-18）
  - 扩充事件词典到 80+，覆盖更多起源/危机/特殊事件；新增年度标记过滤；优化占位符与实体生成逻辑。

### 发行说明（Releases）

- 最新发布（Latest）：https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases/latest  
  在 Latest 的 Assets 中下载 Windows 版 `.exe`（v0.12）。
- 全部发布（All Releases）：https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases

---

## 功能（Features）

- 存档时间线解析：识别 `timeline_events` 数据块，按日期排序，拼装自然语言说明。
- 编年史生成：输出完整的“帝国编年史”文本（可选择是否包含年度标记）。
- 两种生成模式：
  - 随机生成：为遭遇的帝国/堕落帝国/星神兽等生成合理名称与设定，用于补全叙事。
  - 手动输入：在解析后逐项引导输入自定义名称，尽量贴合你的实际存档内容。
- 实体设定归档：将参与到编年史中的实体（帝国/堕落帝国/种族等）整理为 Markdown 设定档，便于后续创作引用。
- 统计与提示：记录总事件数、年度标记统计，并收集未知星神兽代码，方便提交 Issue 补全。
- GUI 与体验：现代化界面，运行日志/搜索、进度与阶段展示、一键打开输出目录、检查更新。
- 在线页面：无需安装，浏览器即可解析、展示与下载；内置“文本/时间轴”双视图。

---

## 使用方式（三选一）

### 方式 A：在线页面（最简便）

- 打开：`https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/`
- 选择生成模式（随机/手动），上传存档文本（.txt），点击生成；右侧可查看编年史与时间轴并下载。

准备存档文本（.txt）的途径：
- 从存档中提取 `gamestate` 后重命名为 `gamestate.txt`（见“准备存档文件”）。
- 或使用你在游戏中导出的时间线文本（如果已有导出）。

### 方式 B：Windows 可执行文件（免环境）

- 前往本仓库 Releases 下载 v0.12 对应的 `.exe`。
- 双击运行，按界面提示：选择存档文本、输出目录、玩家帝国名（可选）、是否包含年度标记，并选择“随机/手动”。
- 运行完成后可一键打开输出目录查看结果。

### 方式 C：源码运行（Python 3）

- 文件：`最新版本源码/gui_stellaris_chronicle_generator_v0.12.py`
- 依赖：`customtkinter`

在 Windows PowerShell 中：

```powershell
# 安装依赖
pip install --upgrade pip; pip install customtkinter

# 运行 GUI（在仓库根目录或源码目录）
python 最新版本源码/gui_stellaris_chronicle_generator_v0.12.py
```

> 历史的命令行版本请参阅 `历史版本/` 目录（如 v0.03）。

---

## 准备存档文件

1. 定位存档目录：`C:\Users\<你的用户名>\Documents\Paradox Interactive\Stellaris\save games\...`，找到目标 `.sav`。
2. 将 `.sav` 改后缀为 `.zip` 并解压，得到 `gamestate`。
3. 在线页面建议将其重命名为 `gamestate.txt` 再上传；GUI/EXE 也推荐使用 `.txt` 后缀的文本文件以便选择识别。

![时间线界面示例](PIC/timeline.png "游戏内帝国时间线界面；本项目生成对应的编年史文本")
![事件描述示例](PIC/event_desc.png "示例事件卡片描述；词条来自内置事件映射表")

---

## 输出结果（Outputs）

生成结束后，在你选择的输出目录会得到：
- `群星帝国编年史.txt`：按时间顺序的完整编年史（占位符已处理）。
- `动态生成实体设定.md`：本次生成/命名的帝国、堕落帝国、种族等详细设定汇总。
- `生成统计.txt`：事件总数、年度标记包含/过滤统计、未知星神兽代码列表等。

在线页面同样支持直接下载“编年史”文本，并内置“时间轴”可视化浏览。

---

## 已知问题（Known Limitations）

- 事件映射未完全覆盖：尚未收录的事件会显示“未收录事件代码（definition）”。
- 名称解析仍在完善：真实星系/星球/领袖名尚未全面从存档提取，部分需默认或手动输入。
- 随机实体与实际可能有偏差：为保证叙事完整性会生成合乎设定的 AI/堕落帝国信息。
- 在线版为纯前端：大文件或低性能设备下解析速度可能较慢。

---

## 更新计划（Roadmap）

- 持续补全事件代码与描述映射，覆盖更多版本与 DLC。
- 增强“真实名称”解析（星系/星球/领袖等），尽可能还原游玩细节。
- 扩展手动输入项与校验，支持导入自定义名录/模板，改进可视化与多格式导出（Markdown/HTML）。

---

## 仓库结构（快速导览）

- 最新 GUI 源码：`最新版本源码/gui_stellaris_chronicle_generator_v0.12.py`（版本信息见 `最新版本源码/version.py`）。
- 历史命令行版本：`历史版本/`（如 `0.03/`）。
- 在线页面静态资源：`pages/v1.0/`（`index.html`、`main.js`、`style.css`）。

---

## 贡献与反馈（Contributing）

欢迎提交 Issue 补充“事件代码 ↔ 描述”的映射，或反馈统计文件中出现的“未知星神兽代码”。

例如（键值对风格）：

```
"timeline_first_precursor": "太虚古迹_初见先驱者_里程碑_[玩家帝国]首次发现文明先驱"
```

建议附带：截图/`gamestate` 片段/发生日期，便于核对与收录。

---

## 许可与声明（License & Usage）

- 本项目免费供个人学习与非商业用途，欢迎 Fork 与二次开发。
- 未经授权禁止用于盈利性商业用途（包含但不限于出售或收费服务）。
- 版权归作者所有，商业或特殊授权请联系作者。

如果觉得好用，请为仓库点个 Star ⭐，这会极大鼓励我继续维护与改进！

---

<a id="en"></a>

# Stellaris Empire Chronicle Generator

<p align="center">
  <a href="https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/">Online</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases">Releases</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/issues">Issues</a> ·
  <a href="https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/stargazers">Stars</a>
</p>

Turn Stellaris save timeline events into a readable “Empire Chronicle”. v0.12 ships a modern GUI, Windows `.exe` build, and a browser-based online version.

Online page: https://luyu14039.github.io/Stellaris-Empire-Chronicle-Generator-pages/  
Runs fully in the browser (no file upload to server).

## Changelog

- v0.12 (2025-09-24)
  - Modern GUI (customtkinter), with logs, progress, search, context menu, status.
  - Windows EXE in Releases, no Python required.
  - Manual/Random inputs for empire & leviathan names during parsing.
  - GitHub Pages online app with timeline visualization and download.
  - Extra: stats include unknown leviathan codes; built-in update check.
- v0.03 (2025-09-18)
  - Expanded event map (80+), year-marker filter, improved placeholders/entities.

### Releases

- Latest: https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases/latest  
  Download the Windows `.exe` from the Latest release assets (v0.12).
- All: https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator/releases

## Features

- Parse `timeline_events` and produce chronological narrative text.
- Chronicle generation with optional year markers.
- Two modes:
  - Random: auto-generate reasonable names/settings for empires/fallen empires/leviathans.
  - Manual: guided inputs after parsing to match your actual save.
- Entity settings export (Markdown) and statistics file (counts, year markers, unknown leviathans).
- GUI UX: logs/search, progress & steps, open output dir, update check.
- Online app: parse, view, download; text/timeline switch.

## How to Use (3 ways)

- Online: open the URL, pick mode (random/manual), upload `.txt` timeline (e.g., `gamestate.txt`), generate and download.
- Windows EXE: get v0.12 `.exe` from Releases, run, follow the GUI.
- From source: run `最新版本源码/gui_stellaris_chronicle_generator_v0.12.py` with `customtkinter` installed.

PowerShell example:

```powershell
pip install --upgrade pip; pip install customtkinter
python 最新版本源码/gui_stellaris_chronicle_generator_v0.12.py
```

## Prepare Save File

1) Find your `.sav` under `Documents/Paradox Interactive/Stellaris/save games/`  
2) Rename to `.zip` and extract to get `gamestate`  
3) Rename to `gamestate.txt` for the online app or select it in the GUI/EXE

## Outputs

- `群星帝国编年史.txt` — final chronicle
- `动态生成实体设定.md` — entity settings (empires/fallen/species)
- `生成统计.txt` — stats: totals, year markers, unknown leviathans

## Known Limitations

- Event map is incomplete; unknown definitions show as “unmapped”.
- Real names (systems/planets/leaders) are not fully parsed yet.
- Randomly generated entities may differ from your actual save.
- Online version is fully client-side; very large files may be slower.

## Roadmap

- Expand event map and DLC coverage.
- Improve real-name parsing and fidelity to saves.
- More manual inputs, presets/templates, richer exports (Markdown/HTML).

## Contributing & License

Issues and PRs are welcome. Please attach screenshots/save snippets when proposing new mappings.

- Free for personal, non-commercial use.
- Commercial use requires explicit permission.
- © Author. See repository for details.

If this helps you, a ⭐ on GitHub is greatly appreciated!
