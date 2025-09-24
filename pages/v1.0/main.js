/**
 * 群星帝国编年史生成器 - JavaScript版本
 * 将Python版本的核心逻辑转换为纯前端实现
 */

class StellarisChronicleGenerator {
    constructor() {
        this.timelineEvents = [];
        this.playerEmpireName = "玩家帝国";
        this.includeYearMarkers = true;
        this.generationMode = "random"; // "random" 或 "manual"
        this.manualInputs = {}; // 存储手动输入的内容
        this.parsedInputRequirements = []; // 解析出的需要输入的内容
        this.eventDescriptions = this.initializeEventDescriptions();
        this.planetNames = this.initializePlanetNames();
        this.leviathanCodes = this.initializeLeviathanCodes();
        this.empireNames = this.initializeEmpireNames();
        
        // 绑定DOM元素
        this.initializeDOM();
        this.bindEvents();
        
        this.log('🛰 在线版本初始化完成');
        this.log('ℹ 项目主页: https://github.com/luyu14039/Stellaris-Empire-Chronicle-Generator');
        this.log('💬 欢迎反馈问题 / 提交改进建议 (Issue)');
    }

    initializeDOM() {
        this.saveFileInput = document.getElementById('saveFileInput');
        this.empireNameInput = document.getElementById('empireNameInput');
        this.includeYearCheckbox = document.getElementById('includeYearMarkers');
        this.randomModeRadio = document.getElementById('randomMode');
        this.manualModeRadio = document.getElementById('manualMode');
        this.empireNameSection = document.getElementById('empireNameSection');
        this.manualInputSection = document.getElementById('manualInputSection');
        this.manualInputHeader = document.getElementById('manualInputHeader');
        this.inputGuideContent = document.getElementById('inputGuideContent');
        this.operationTitle = document.getElementById('operationTitle');
        this.generateBtn = document.getElementById('generateBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.clearLogBtn = document.getElementById('clearLogBtn');
        this.themeToggleBtn = document.getElementById('themeToggle');
        this.fxToggleBtn = document.getElementById('fxToggle');
        this.statusText = document.getElementById('statusText');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.logOutput = document.getElementById('logOutput');
        this.searchInput = document.getElementById('searchInput');
        this.fileName = document.getElementById('fileName');
        this.resultSection = document.getElementById('resultSection');
        this.chronicleOutput = document.getElementById('chronicleOutput');
        this.timelineVisualization = document.getElementById('timelineVisualization');
        this.starfieldCanvas = document.getElementById('starfield');
        if (this.starfieldCanvas) this.starfieldCtx = this.starfieldCanvas.getContext('2d');
    }

    bindEvents() {
        // 文件选择
        this.saveFileInput.addEventListener('change', (e) => this.onFileSelected(e));
        
        // 生成模式选择
        this.randomModeRadio.addEventListener('change', () => this.onGenerationModeChange());
        this.manualModeRadio.addEventListener('change', () => this.onGenerationModeChange());
        
        // 手动输入折叠功能
        if (this.manualInputHeader) {
            this.manualInputHeader.addEventListener('click', () => this.toggleManualInputCollapse());
        }
        
        // 结果标签页切换
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.switchResultTab(e.target.dataset.tab);
            }
        });
        
        // 按钮点击
        this.generateBtn.addEventListener('click', () => this.startGeneration());
        this.downloadBtn.addEventListener('click', () => this.downloadResult());
        this.clearLogBtn.addEventListener('click', () => this.clearLog());
        
        if (this.themeToggleBtn) this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        if (this.fxToggleBtn) this.fxToggleBtn.addEventListener('click', () => this.toggleEffects());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchLog();
            }
        });
        
        // 快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.startGeneration();
            }
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                this.clearLog();
            }
        });
    }

    /* ====== 主题与特效 ====== */
    toggleTheme() {
        document.body.classList.toggle('light-theme');
        const light = document.body.classList.contains('light-theme');
        if (this.themeToggleBtn) this.themeToggleBtn.textContent = light ? '切换深色' : '切换主题';
        this.log(light ? '🌞 切换到浅色主题' : '🌌 切换到深色主题');
    }

    toggleEffects() {
        document.body.classList.toggle('effects-off');
        const off = document.body.classList.contains('effects-off');
        if (this.fxToggleBtn) this.fxToggleBtn.textContent = off ? '开启特效' : '关闭特效';
        if (off) { this.stopStarfield(); this.log('🚫 已关闭动态特效'); }
        else { this.startStarfield(); this.log('✨ 已开启动态特效'); }
    }

    /* ====== 星空动画 ====== */
    startStarfield() {
        if (!this.starfieldCanvas || !this.starfieldCtx) return;
        if (this._starfieldRunning) return;
        this._stars = this.createStars(180);
        this.resizeStarfield();
        window.addEventListener('resize', this._onResizeStarfield = () => this.resizeStarfield());
        this._starfieldRunning = true;
        const loop = () => { if (!this._starfieldRunning) return; this.drawStarfield(); requestAnimationFrame(loop); };
        loop();
    }
    stopStarfield() {
        this._starfieldRunning = false;
        if (this._onResizeStarfield) { window.removeEventListener('resize', this._onResizeStarfield); this._onResizeStarfield = null; }
    }
    resizeStarfield() {
        if (!this.starfieldCanvas) return; this.starfieldCanvas.width = window.innerWidth; this.starfieldCanvas.height = window.innerHeight;
    }
    createStars(count) {
        const arr = []; for (let i=0;i<count;i++){arr.push({x:Math.random(),y:Math.random(),z:Math.random(),r:Math.random()*1.4+0.2,vy:Math.random()*0.0008+0.00015});} return arr;
    }
    drawStarfield() {
        const ctx = this.starfieldCtx; const w = this.starfieldCanvas.width; const h = this.starfieldCanvas.height; ctx.clearRect(0,0,w,h); ctx.save(); ctx.globalCompositeOperation='lighter';
        for (const s of this._stars){ s.y += s.vy*(0.2+(1-s.z)*1.6); if(s.y>1){s.y=0;s.x=Math.random();s.z=Math.random();} const a = 0.35+(1-s.z)*0.65; const px=s.x*w; const py=s.y*h; const rad=s.r*(0.6+(1-s.z)*1.3); const g=ctx.createRadialGradient(px,py,0,px,py,rad*4); g.addColorStop(0,`rgba(${180+(1-s.z)*50},${200+(1-s.z)*30},255,${a})`); g.addColorStop(1,'rgba(0,0,10,0)'); ctx.fillStyle=g; ctx.beginPath(); ctx.arc(px,py,rad,0,Math.PI*2); ctx.fill(); }
        ctx.restore();
    }

    onGenerationModeChange() {
        this.generationMode = this.randomModeRadio.checked ? 'random' : 'manual';
        
        if (this.generationMode === 'manual') {
            this.manualInputSection.style.display = 'block';
            this.empireNameSection.style.display = 'none';
            this.operationTitle.textContent = '6. 操作';
            this.generateBtn.textContent = '开始解析';
            this.log('🔧 切换到手动输入模式');
        } else {
            this.manualInputSection.style.display = 'none';
            this.empireNameSection.style.display = 'block';
            this.operationTitle.textContent = '5. 操作';
            this.generateBtn.textContent = '开始生成';
            this.log('🎲 切换到随机生成模式');
        }
        
        // 重置状态
        this.manualInputs = {};
        this.parsedInputRequirements = [];
        this.resetInputGuide();
    }

    resetInputGuide() {
        this.inputGuideContent.innerHTML = '<p class="guide-hint">请先开始解析，系统将分析需要填写的内容</p>';
        // 重置折叠状态
        this.inputGuideContent.classList.remove('expanded');
        if (this.manualInputHeader) {
            this.manualInputHeader.classList.remove('expanded');
        }
    }

    toggleManualInputCollapse() {
        const content = this.inputGuideContent;
        const header = this.manualInputHeader;
        
        if (content.classList.contains('expanded')) {
            // 折叠
            content.style.maxHeight = '0px';
            content.style.overflow = 'hidden';
            content.classList.remove('expanded');
            header.classList.remove('expanded');
        } else {
            // 展开
            content.classList.add('expanded');
            header.classList.add('expanded');
            
            // 设置适当的最大高度，如果内容很多就限制高度并启用滚动
            const scrollHeight = content.scrollHeight;
            if (scrollHeight > 500) {
                content.style.maxHeight = '500px';
                content.style.overflowY = 'auto';
            } else {
                content.style.maxHeight = scrollHeight + 'px';
                content.style.overflowY = 'visible';
            }
        }
    }

    switchResultTab(tabName) {
        // 切换标签按钮状态
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // 切换内容显示
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabName === 'text' ? 'textContent' : 'timelineContent').classList.add('active');
        
        // 如果切换到时间轴，生成时间轴可视化
        if (tabName === 'timeline' && this.timelineEvents.length > 0) {
            this.generateTimelineVisualization();
        }
    }

    updateCompletedCount() {
        const completedCountElement = document.getElementById('completedCount');
        if (completedCountElement) {
            const completedCount = Object.values(this.manualInputs).filter(value => value && value.trim()).length;
            completedCountElement.textContent = completedCount;
            
            // 如果所有必填项都完成了，显示可以生成的提示
            if (completedCount >= this.parsedInputRequirements.filter(req => req.required !== false).length) {
                const scrollHint = document.querySelector('.scroll-hint');
                if (scrollHint) {
                    scrollHint.innerHTML = '✅ 必填项已完成，可以开始生成！';
                    scrollHint.style.color = '#7fe5a1';
                }
            }
        }
    }

    onFileSelected(event) {
        const file = event.target.files[0];
        if (file) {
            this.fileName.textContent = file.name;
            this.generateBtn.disabled = false;
            this.log(`📥 选择存档: ${file.name}`);
            
            // 重置手动输入状态
            if (this.generationMode === 'manual') {
                this.resetInputGuide();
                this.manualInputs = {};
                this.parsedInputRequirements = [];
            }
        } else {
            this.fileName.textContent = '未选择文件';
            this.generateBtn.disabled = true;
        }
    }

    async startGeneration() {
        if (!this.saveFileInput.files[0]) {
            this.log('⚠ 请先选择存档文件', 'warning');
            return;
        }

        const file = this.saveFileInput.files[0];
        
        // 根据模式决定流程
        if (this.generationMode === 'manual' && this.parsedInputRequirements.length === 0) {
            // 手动模式且还未解析：先解析并显示输入引导
            await this.parseAndShowInputGuide(file);
        } else {
            // 随机模式或手动模式已完成输入：直接生成
            await this.performFullGeneration(file);
        }
    }

    async parseAndShowInputGuide(file) {
        // 清空之前的结果
        this.clearLog();
        this.resultSection.style.display = 'none';
        
        this.log('==== 开始解析存档 (手动输入模式) ====');
        this.log(`存档文件: ${file.name}`);
        this.log('📋 解析模式: 分析需要手动输入的内容');

        this.setStatus('解析中...', '#e0b458');
        this.updateProgress(0, '初始化');
        this.lockUI(true);

        try {
            // 读取文件
            this.updateProgress(20, '读取存档文件');
            const content = await this.readFileAsText(file);
            
            // 解析存档
            this.updateProgress(50, '解析存档数据');
            const success = this.parseSaveFile(content);
            
            if (!success) {
                this.log('❌ 解析失败，任务终止', 'error');
                this.setStatus('解析失败', '#d9534f');
                return;
            }

            // 分析需要输入的内容
            this.updateProgress(80, '分析输入需求');
            this.analyzeInputRequirements();
            
            // 生成输入引导界面
            this.updateProgress(95, '生成输入引导');
            this.generateInputGuide();
            
            this.updateProgress(100, '解析完成');
            this.log('🎯 解析完成！请在下方填写相关信息后点击"开始生成"');
            this.setStatus('等待输入', '#4cbf56');
            this.generateBtn.textContent = '开始生成';
            
        } catch (error) {
            this.log(`❌ 解析过程中发生错误: ${error.message}`, 'error');
            console.error(error);
            this.setStatus('解析失败', '#d9534f');
        } finally {
            this.lockUI(false);
        }
    }

    async performFullGeneration(file) {
        const empireNameValue = this.empireNameInput.value.trim();
        const includeYear = this.includeYearCheckbox.checked;

        // 清空之前的结果（除了解析日志）
        if (this.generationMode === 'random') {
            this.clearLog();
        }
        this.resultSection.style.display = 'none';
        
        this.log('==== 开始生成编年史 ====');
        this.log(`存档文件: ${file.name}`);
        this.log(`生成模式: ${this.generationMode === 'random' ? '随机生成' : '手动输入'}`);
        
        if (this.generationMode === 'random') {
            this.log(`玩家帝国: ${empireNameValue || '随机生成'}`);
        } else {
            this.log(`手动输入项目: ${this.parsedInputRequirements.length} 个`);
        }
        this.log(`年度标记: ${includeYear ? '包含' : '不包含'}`);

        this.setStatus('生成中...', '#e0b458');
        this.updateProgress(0, '初始化');
        this.lockUI(true);

        try {
            // 设置参数
            this.updateProgress(5, '设置参数');
            this.includeYearMarkers = includeYear;
            
            // 处理帝国名称逻辑
            if (this.generationMode === 'random') {
                // 随机模式：优先使用用户输入，没有输入则使用默认值"玩家帝国"
                if (empireNameValue) {
                    this.playerEmpireName = empireNameValue;
                    this.log(`👑 使用用户指定的帝国名称: ${this.playerEmpireName}`);
                } else {
                    this.playerEmpireName = "玩家帝国";
                    this.log(`👑 使用默认帝国名称: ${this.playerEmpireName}`);
                }
            } else {
                // 手动模式，使用用户在输入引导中填写的内容
                this.playerEmpireName = this.manualInputs['empire_name'] || empireNameValue || "玩家帝国";
                this.log(`👑 手动模式帝国名称: ${this.playerEmpireName}`);
            }

            // 如果是手动模式，跳过解析步骤（已经解析过了）
            if (this.generationMode === 'random' || this.timelineEvents.length === 0) {
                // 读取文件
                this.updateProgress(15, '读取存档文件');
                const content = await this.readFileAsText(file);
                
                // 解析存档
                this.updateProgress(25, '解析存档数据');
                const success = this.parseSaveFile(content);
                
                if (!success) {
                    this.log('❌ 解析失败，任务终止', 'error');
                    this.setStatus('解析失败', '#d9534f');
                    return;
                }
            } else {
                this.updateProgress(25, '使用已解析数据');
            }

            // 生成初版编年史
            this.updateProgress(45, '生成初版编年史');
            const initialChronicle = this.generateInitialChronicle();
            
            // 完善编年史（处理占位符）
            this.updateProgress(65, '处理占位符');
            const finalChronicle = this.generateFinalChronicle(initialChronicle);
            
            // 显示结果
            this.updateProgress(90, '显示结果');
            this.displayResult(finalChronicle);
            
            this.updateProgress(100, '完成');
            this.log('\n🎉 生成完成!');
            this.setStatus('完成', '#4cbf56');
            
        } catch (error) {
            this.log(`❌ 运行过程中发生错误: ${error.message}`, 'error');
            console.error(error);
            this.setStatus('生成失败', '#d9534f');
        } finally {
            this.lockUI(false);
        }
    }

    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('文件读取失败'));
            reader.readAsText(file, 'UTF-8');
        });
    }

    parseSaveFile(content) {
        this.log(`🔍 开始解析存档文件`);
        
        try {
            // 查找 timeline_events 数据块
            const timelineMatch = content.match(/timeline_events\s*=\s*\{/);
            if (!timelineMatch) {
                this.log("❌ 未找到timeline_events数据块", 'error');
                return false;
            }

            const start = timelineMatch.index + timelineMatch[0].length - 1;
            let braceCount = 0;
            let end = start;
            
            // 找到匹配的结束大括号
            for (let i = start; i < content.length; i++) {
                const char = content[i];
                if (char === '{') braceCount++;
                else if (char === '}') {
                    braceCount--;
                    if (braceCount === 0) {
                        end = i + 1;
                        break;
                    }
                }
            }

            const block = content.substring(start, end);
            this.parseTimelineEvents(block);
            
            this.log(`✅ 事件解析完成，共 ${this.timelineEvents.length} 个`, 'success');
            return true;
            
        } catch (error) {
            this.log(`❌ 解析失败: ${error.message}`, 'error');
            return false;
        }
    }

    parseTimelineEvents(text) {
        const events = [];
        const lines = text.split('\n');
        let currentEvent = null;
        let braceCount = 0;
        let inEvent = false;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmed = line.trim();
            if (!trimmed) continue;

            braceCount += (trimmed.match(/\{/g) || []).length - (trimmed.match(/\}/g) || []).length;

            if (!inEvent && trimmed === '{' && braceCount >= 2) {
                inEvent = true;
                currentEvent = { lines: [], start: i };
            } else if (inEvent && currentEvent) {
                currentEvent.lines.push(trimmed);
                if (trimmed === '}' && braceCount === 1) {
                    const eventText = currentEvent.lines.join('\n');
                    const event = this.parseSingleEvent(eventText);
                    if (event) {
                        events.push(event);
                    }
                    inEvent = false;
                    currentEvent = null;
                }
            }
        }

        // 按日期排序
        events.sort((a, b) => a.date.localeCompare(b.date));
        this.timelineEvents = events;
    }

    parseSingleEvent(text) {
        try {
            // 提取日期
            const dateMatch = text.match(/date\s*=\s*"([^"]+)"/);
            const definitionMatch = text.match(/definition\s*=\s*"([^"]+)"/);
            
            if (!dateMatch || !definitionMatch) {
                return null;
            }

            const date = dateMatch[1];
            const definition = definitionMatch[1];
            const data = {};

            // 提取data部分
            const dataMatch = text.match(/data\s*=\s*\{([^}]*)\}/s);
            if (dataMatch) {
                const dataBody = dataMatch[1].trim();
                
                // 处理数字列表
                if (/^[\d\s]+$/.test(dataBody)) {
                    const numbers = dataBody.split(/\s+/).filter(x => /^\d+$/.test(x)).map(x => parseInt(x));
                    data.numbers = numbers;
                } 
                // 处理索引化的字符串
                else if (/^\s*\d+\s*=/.test(dataBody)) {
                    const pairs = [...dataBody.matchAll(/(\d+)\s*=\s*"([^"]*)"/g)];
                    data.items = pairs.sort((a, b) => parseInt(a[1]) - parseInt(b[1])).map(pair => pair[2]);
                }
                // 处理键值对
                else {
                    const kvMatches = [...dataBody.matchAll(/(\w+)\s*=\s*"([^"]*)"/g)];
                    kvMatches.forEach(match => {
                        data[match[1]] = match[2];
                    });
                }
            }

            return {
                date,
                definition,
                data,
                rawText: text
            };

        } catch (error) {
            this.log(`⚠ 解析事件出错: ${error.message}`, 'warning');
            return null;
        }
    }

    generateInitialChronicle() {
        const lines = [
            '='.repeat(60),
            '群星帝国编年史',
            '='.repeat(60),
            ''
        ];

        let filtered = 0;
        
        this.timelineEvents.forEach(event => {
            if (!this.includeYearMarkers && event.definition === 'timeline_event_year') {
                filtered++;
                return;
            }
            
            const eventText = this.convertEventToText(event);
            lines.push(`${event.date} - ${eventText}`);
        });

        this.log(`✅ 初版编年史生成完成，共 ${this.timelineEvents.length - filtered} 条`, 'success');
        return lines.join('\n');
    }

    convertEventToText(event) {
        if (!this.eventDescriptions[event.definition]) {
            return `未收录事件代码 (${event.definition})，欢迎补充！`;
        }

        const template = this.eventDescriptions[event.definition];
        let result = template;

        // 替换玩家帝国名称
        result = result.replace(/\[玩家帝国\]/g, this.playerEmpireName);

        // 处理模板变量
        const formatArgs = { date: event.date, ...event.data };

        // 查找所有需要替换的变量
        const variables = [...template.matchAll(/\{(\w+)\}/g)];
        
        variables.forEach(match => {
            const varName = match[1];
            let value = formatArgs[varName];

            if (value === undefined) {
                // 在手动模式下，优先使用用户输入
                if (this.generationMode === 'manual') {
                    // 查找对应的手动输入值
                    const eventIndex = this.timelineEvents.indexOf(event);
                    
                    if (varName === 'colony_name') {
                        const key = `colony_${eventIndex}_${event.date}`;
                        value = this.manualInputs[key];
                    } else if (varName === 'leviathan_name') {
                        const leviathanType = event.data.leviathan_type || 'unknown';
                        const key = `leviathan_${leviathanType}`;
                        value = this.manualInputs[key];
                    } else if (['target_empire', 'defeated_empire', 'subject_empire', 'fallen_empire'].includes(varName)) {
                        const key = `empire_${varName}_${eventIndex}`;
                        value = this.manualInputs[key];
                    }
                }

                // 如果还是没有值，使用默认值或随机生成
                if (!value) {
                    const defaults = {
                        'location': '未知星系',
                        'system_name': '未知恒星系',
                        'leader_name': '未知领袖',
                        'planet_name': '未知星球',
                        'fleet_name': '无敌舰队',
                        'ship_name': '旗舰',
                        'new_capital': '新首都',
                        'target_empire': '未知帝国',
                        'defeated_empire': '未知帝国',
                        'subject_empire': '未知帝国',
                        'fallen_empire': '未知失落帝国'
                    };

                    if (varName === 'colony_name') {
                        value = this.getRandomPlanetName();
                    } else if (varName === 'leviathan_name') {
                        value = this.getLeviathanName(event.data);
                    } else if (['target_empire', 'defeated_empire', 'subject_empire', 'fallen_empire'].includes(varName)) {
                        // 随机模式下生成随机帝国名称，手动模式下使用默认值
                        if (this.generationMode === 'random') {
                            value = this.getRandomEmpireName();
                        } else {
                            value = defaults[varName] || `{${varName}}`;
                        }
                    } else {
                        value = defaults[varName] || `{${varName}}`;
                    }
                }
            }

            result = result.replace(match[0], value);
        });

        return result;
    }

    generateFinalChronicle(initial) {
        // 目前简化版本，直接返回初版
        // 未来可以在这里添加更复杂的占位符处理逻辑
        return initial;
    }

    getRandomPlanetName() {
        const names = this.planetNames;
        return names[Math.floor(Math.random() * names.length)];
    }

    getRandomEmpireName() {
        const names = this.empireNames;
        return names[Math.floor(Math.random() * names.length)];
    }

    getLeviathanName(data) {
        // 在手动模式下，优先使用用户输入
        if (this.generationMode === 'manual' && this.manualInputs[`leviathan_${data.leviathan_type || 'unknown'}`]) {
            return this.manualInputs[`leviathan_${data.leviathan_type || 'unknown'}`];
        }
        
        // 简化版本的星神兽名称处理
        if (data.leviathan_type) {
            return this.leviathanCodes[data.leviathan_type] || '未知星神兽';
        }
        return '神秘星神兽';
    }

    analyzeInputRequirements() {
        this.parsedInputRequirements = [];
        const requiredInputs = new Set();
        
        // 分析所有事件，找出需要用户输入的占位符
        this.timelineEvents.forEach((event, index) => {
            const template = this.eventDescriptions[event.definition];
            if (!template) return;
            
            // 查找模板中的变量
            const variables = [...template.matchAll(/\{(\w+)\}/g)];
            
            variables.forEach(match => {
                const varName = match[1];
                
                // 检查是否需要用户输入
                if (varName === 'colony_name' && !event.data[varName]) {
                    const key = `colony_${index}_${event.date}`;
                    if (!requiredInputs.has(key)) {
                        requiredInputs.add(key);
                        this.parsedInputRequirements.push({
                            type: 'colony_name',
                            key: key,
                            eventDate: event.date,
                            eventDesc: '殖民地建立',
                            placeholder: '新殖民地名称',
                            hint: '为这个新建立的殖民地命名'
                        });
                    }
                } else if (varName === 'leviathan_name' && !event.data[varName]) {
                    const leviathanType = event.data.leviathan_type || 'unknown';
                    const key = `leviathan_${leviathanType}`;
                    if (!requiredInputs.has(key)) {
                        requiredInputs.add(key);
                        this.parsedInputRequirements.push({
                            type: 'leviathan_name',
                            key: key,
                            eventDate: event.date,
                            eventDesc: '星神兽遭遇',
                            placeholder: '星神兽名称',
                            hint: `为这个星神兽命名 (类型: ${this.leviathanCodes[leviathanType] || '未知'})`
                        });
                    }
                } else if (['target_empire', 'defeated_empire', 'subject_empire', 'fallen_empire'].includes(varName) && !event.data[varName]) {
                    const key = `empire_${varName}_${index}`;
                    if (!requiredInputs.has(key)) {
                        requiredInputs.add(key);
                        this.parsedInputRequirements.push({
                            type: 'empire_name',
                            key: key,
                            eventDate: event.date,
                            eventDesc: this.getEventDescription(event.definition),
                            placeholder: '帝国名称',
                            hint: `为相关帝国命名 (${this.getEmpireRoleDescription(varName)})`
                        });
                    }
                }
            });
        });

        // 总是询问玩家帝国名称
        this.parsedInputRequirements.unshift({
            type: 'empire_name',
            key: 'empire_name',
            eventDate: '通用',
            eventDesc: '玩家帝国',
            placeholder: '玩家帝国名称',
            hint: '您的帝国名称（留空将显示为"玩家帝国"）',
            required: false
        });

        this.log(`📊 分析完成：发现 ${this.parsedInputRequirements.length} 个需要填写的项目`);
    }

    getEventDescription(definition) {
        const template = this.eventDescriptions[definition];
        if (!template) return '未知事件';
        
        // 提取事件的简要描述
        const parts = template.split('_');
        return parts.length > 2 ? parts[2] : '事件';
    }

    getEmpireRoleDescription(varName) {
        const roles = {
            'target_empire': '目标帝国',
            'defeated_empire': '被击败帝国',
            'subject_empire': '附庸帝国',
            'fallen_empire': '失落帝国'
        };
        return roles[varName] || '相关帝国';
    }

    generateInputGuide() {
        if (this.parsedInputRequirements.length === 0) {
            this.inputGuideContent.innerHTML = '<p class="guide-hint">未发现需要手动输入的内容，可以直接生成</p>';
            return;
        }

        let html = `
            <div class="input-summary">
                <p class="guide-hint">系统分析发现以下 <strong>${this.parsedInputRequirements.length}</strong> 个项目需要您填写：</p>
                <div class="progress-indicator">
                    <span class="completed-count">已完成: <span id="completedCount">0</span></span>
                    <span class="total-count">总计: ${this.parsedInputRequirements.length}</span>
                </div>
            </div>
        `;
        
        this.parsedInputRequirements.forEach((req, index) => {
            const isRequired = req.required !== false;
            html += `
                <div class="input-item ${isRequired ? 'input-required' : ''}">
                    <div class="input-item-title">${index + 1}. ${req.eventDesc} (${req.eventDate})</div>
                    <div class="input-item-desc">${req.hint}</div>
                    <input type="text" 
                           id="manual_input_${req.key}" 
                           placeholder="${req.placeholder}"
                           data-key="${req.key}"
                           ${isRequired ? 'required' : ''}>
                </div>
            `;
        });
        
        if (this.parsedInputRequirements.length > 6) {
            html += '<p class="guide-hint scroll-hint" style="margin-top: 16px; color: #ffc981; font-weight: 500;">📜 内容较多，请向下滚动查看所有输入项</p>';
        }
        html += '<p class="guide-hint" style="margin-top: 16px;">填写完成后，点击"开始生成"按钮</p>';
        
        this.inputGuideContent.innerHTML = html;
        
        // 自动展开内容
        setTimeout(() => {
            const content = this.inputGuideContent;
            const header = this.manualInputHeader;
            
            content.classList.add('expanded');
            if (header) {
                header.classList.add('expanded');
            }
            
            // 计算并设置适当的高度
            const scrollHeight = content.scrollHeight;
            if (scrollHeight > 500) {
                content.style.maxHeight = '500px';
                content.style.overflowY = 'auto';
                this.log(`📋 输入项较多(${this.parsedInputRequirements.length}个)，已启用滚动查看`);
            } else {
                content.style.maxHeight = scrollHeight + 'px';
                content.style.overflowY = 'visible';
            }
        }, 200);
        
        // 绑定输入事件
        this.parsedInputRequirements.forEach(req => {
            const input = document.getElementById(`manual_input_${req.key}`);
            if (input) {
                input.addEventListener('input', (e) => {
                    this.manualInputs[req.key] = e.target.value.trim();
                    // 检查是否完成
                    if (e.target.value.trim()) {
                        e.target.parentElement.classList.add('input-complete');
                        e.target.parentElement.classList.remove('input-required');
                    } else if (req.required !== false) {
                        e.target.parentElement.classList.remove('input-complete');
                        e.target.parentElement.classList.add('input-required');
                    }
                    
                    // 更新完成计数
                    this.updateCompletedCount();
                });
            }
        });
    }

    displayResult(chronicle) {
        this.chronicleOutput.textContent = chronicle;
        this.resultSection.style.display = 'block';
        this.downloadBtn.disabled = false;
        
        // 默认显示文本标签页
        this.switchResultTab('text');
        
        // 滚动到结果区域
        this.resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    generateTimelineVisualization() {
        if (!this.timelineVisualization || this.timelineEvents.length === 0) return;
        
        this.log('🎨 生成时间轴可视化');
        
        let html = '';
        
        this.timelineEvents.forEach((event, index) => {
            // 时间轴中始终不显示年度标记
            if (event.definition === 'timeline_event_year') {
                return;
            }
            
            const eventText = this.convertEventToText(event);
            const eventType = this.getEventType(event.definition);
            const eventIcon = this.getEventIcon(event.definition);
            
            // 解析日期显示
            const date = this.formatTimelineDate(event.date);
            
            html += `
                <div class="timeline-event ${eventType}" data-index="${index}">
                    <div class="timeline-icon">${eventIcon}</div>
                    <div class="timeline-content">
                        <div class="timeline-date">${date}</div>
                        <div class="timeline-title">${this.getEventTitle(event.definition)}</div>
                        <div class="timeline-desc">${eventText}</div>
                    </div>
                </div>
            `;
        });
        
        this.timelineVisualization.innerHTML = html || '<p style="text-align:center; color:#8fa2b4; margin:40px 0;">暂无时间轴数据</p>';
        
        // 添加进入动画
        if (html) {
            const events = this.timelineVisualization.querySelectorAll('.timeline-event');
            events.forEach((event, index) => {
                event.style.opacity = '0';
                event.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    event.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    event.style.opacity = '1';
                    event.style.transform = 'translateX(0)';
                }, index * 100);
            });
        }
    }

    getEventType(definition) {
        // 根据事件类型返回分类
        if (definition.includes('first_') || definition.includes('里程碑')) {
            return 'milestone';
        } else if (definition.includes('crisis') || definition.includes('war') || definition.includes('危机')) {
            return 'crisis';
        } else if (definition.includes('empire') || definition.includes('帝国')) {
            return 'empire';
        }
        return 'event';
    }

    getEventIcon(definition) {
        // 根据事件类型返回图标
        const iconMap = {
            'timeline_first_robot': '🤖',
            'timeline_first_colony': '🌍',
            'timeline_first_contact': '👽',
            'timeline_first_war_declared': '⚔️',
            'timeline_first_war_won': '🏆',
            'timeline_encountered_leviathan': '🐉',
            'timeline_destroyed_leviathan': '⚔️',
            'timeline_galactic_community_formed': '🏛️',
            'timeline_become_the_crisis': '💀',
            'timeline_great_khan': '👑',
            'timeline_elections': '🗳️',
            'timeline_new_colony': '🌎',
            'timeline_first_gateway': '🌀',
            'timeline_first_terraforming': '🔧',
            'timeline_first_ascension_perk': '⭐',
            'timeline_synthetic_evolution': '🔄',
            'timeline_event_year': '📅'
        };
        
        return iconMap[definition] || '📋';
    }

    getEventTitle(definition) {
        // 提取事件标题
        const template = this.eventDescriptions[definition];
        if (!template) return '未知事件';
        
        const parts = template.split('_');
        if (parts.length >= 3) {
            return parts[2].replace(/里程碑|帝国事件|危机事件|星系事件/g, '');
        }
        
        return '事件';
    }

    formatTimelineDate(dateStr) {
        // 格式化日期显示，如 "2200.01.01" 转为 "2200年1月1日"
        const parts = dateStr.split('.');
        if (parts.length === 3) {
            const year = parts[0];
            const month = parseInt(parts[1]);
            const day = parseInt(parts[2]);
            return `${year}年${month}月${day}日`;
        }
        return dateStr;
    }

    downloadResult() {
        const content = this.chronicleOutput.textContent;
        if (!content) {
            this.log('⚠ 没有可下载的内容', 'warning');
            return;
        }

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `群星编年史_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.log('💾 编年史已下载', 'success');
    }

    // UI 工具方法
    log(message, type = 'info') {
        const logDiv = document.createElement('div');
        logDiv.className = `log-message ${type}`;
        const time = new Date().toLocaleTimeString();
        logDiv.dataset.time = time;
        logDiv.textContent = message;
        this.logOutput.appendChild(logDiv);
        this.logOutput.scrollTop = this.logOutput.scrollHeight;
    }

    clearLog() {
        this.logOutput.innerHTML = '';
        this.log('📝 日志已清空');
    }

    searchLog() {
        const keyword = this.searchInput.value.trim();
        if (!keyword) return;

        const messages = this.logOutput.querySelectorAll('.log-message');
        let found = false;

        messages.forEach(msg => {
            msg.classList.remove('highlight');
            if (msg.textContent.includes(keyword) && !found) {
                msg.classList.add('highlight');
                msg.scrollIntoView({ behavior: 'smooth', block: 'center' });
                found = true;
            }
        });

        if (found) {
            this.log(`🔍 找到匹配: ${keyword}`);
        } else {
            this.log('🔍 未找到匹配关键字');
        }
    }

    setStatus(text, color) {
        this.statusText.textContent = `状态: ${text}`;
        this.statusText.style.color = color;
    }

    updateProgress(value, step) {
        this.progressFill.style.width = `${value}%`;
        this.progressText.textContent = step;
    }

    lockUI(running) {
        if (running) {
            this.generateBtn.disabled = true;
            this.generateBtn.innerHTML = '<span class="spinner"></span> 生成中...';
            this.downloadBtn.disabled = true;
            this.saveFileInput.disabled = true;
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.textContent = '开始生成';
            this.saveFileInput.disabled = false;
        }
    }

    // 初始化数据
    initializeEventDescriptions() {
        return {
            // 基于Python版本的事件描述映射表
            "timeline_first_robot": "电动之躯_首台机器人_里程碑_[玩家帝国]在{location}首次组装了一台机器人",
            "timeline_first_precursor_discovered": "太虚古迹_初见先驱者_里程碑_[玩家帝国]首次发现文明先驱",
            "timeline_first_precursor": "太虚古迹_初见先驱者_里程碑_[玩家帝国]首次发现文明先驱",
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
            "timeline_encountered_leviathan": "眠者将醒_发现星神兽_帝国事件_[玩家帝国]遭遇了{leviathan_name}",
            "timeline_become_the_crisis": "星海天罚_化身天灾_危机事件_黑暗已经降临银河系。[玩家帝国]抛弃了所有外交伪装，宣称自己是银河生存的最大威胁。他们的舰队正在集结，而情报人员则低声传递着一项最终的、末日般的计划。他们不再仅仅是一个帝国，而是演变成了一场危机。",
            "timeline_modularity": "全面模组_帝国事件_[玩家帝国]完全变为模组化",
            "timeline_destroyed_leviathan": "守护者不再_摧毁星神兽_帝国事件_[玩家帝国]摧毁了{leviathan_name}",
            "timeline_first_deficit": "贪婪之价_首现赤字_里程碑_[玩家帝国]首次出现资源短缺",
            "timeline_deficit": "资源短缺_资源短缺_帝国事件_[玩家帝国]发生了资源短缺",
            "timeline_first_war_lost": "败者之尘_初尝败绩_里程碑_[玩家帝国]首次被[帝国{defeated_empire}]击败",
            "timeline_event_year": "年度标记_{date}_时光荏苒，{date}年悄然而至。",

            // 起源事件
            "timeline_origin_default": "繁荣一统_帝国起源_[玩家帝国]通过斗争和胜利，这个社会已经实现了每一个年轻文明的抱负：一个有着统一目标的家园，一条通向璀璨繁星的道路",
            "timeline_origin_separatists": "分离主义者_帝国起源_[玩家帝国]这个文明并非诞生于全球统一，而是由一群大胆的殖民者建立的，他们在一个崭新的世界上寻求自己的命运",
            "timeline_origin_mechanists": "机械师_帝国起源_[玩家帝国]尽管该文明在生物层面仍是有机体，但他们早已对自动化的机器人劳工习以为常。他们已经将许多卑微（甚至不那么卑微）的苦差事都交给了自动化仆从",
            "timeline_origin_syncretic_evolution": "协同进化_帝国起源_[玩家帝国]在一颗共享的母星上，两个不同的物种并肩演化，相得益彰。一个物种发展出了高级认知能力，而另一个物种则进化出了超凡的力量和耐力——这是一个完美的组合",
            "timeline_origin_life_seeded": "生命之籽_帝国起源_[玩家帝国]这个文明在一位远超其想象的远古仁善存在的监护下逐渐演化，他们的母星是一颗完美的盖亚星球，这样的环境无疑是智慧生命发展的摇篮",
            "timeline_origin_post_apocalyptic": "后启示录_帝国起源_[玩家帝国]在一场将母星变为辐射废土的灭世核战争之后，这个文明的幸存者们终于从地下的防辐射掩体中走了出来，准备在群星中建立一个新的、更光明的未来",
            "timeline_origin_remnants": "复国孑遗_帝国起源_[玩家帝国]这个文明的母星曾是一个庞大、先进帝国的首都。但在一场神秘的灾难之后，帝国分崩离析，只留下了这个星球上不断衰败的城市和这个曾经自豪的文明的遗民"
        };
    }

    initializePlanetNames() {
        return [
            "新伊甸", "太阳城", "星辰港", "晨曦星", "暮光城", "银河港", "星云基地", "虹光星",
            "黄金港", "蓝宝石城", "翡翠星", "钻石港", "水晶城", "珍珠港", "琥珀星", "玛瑙城",
            "自由港", "和平星", "希望城", "繁荣港", "兴旺星", "昌盛城", "富饶港", "丰收星",
            "北极星", "南十字", "天狼星", "织女星", "牛郎星", "北斗星", "启明星", "长庚星",
            "凤凰城", "龙腾港", "麒麟星", "玄武城", "朱雀港", "白虎星", "青龙城", "神鹰港",
            "雷神港", "海神城", "火神星", "土神港", "木神城", "金神星", "水神港", "风神城"
        ];
    }

    initializeLeviathanCodes() {
        return {
            "guardian_dragon": "以太巨龙",
            "guardian_sphere": "神秘球体", 
            "guardian_dreadnought": "古代无畏舰",
            "guardian_horror": "恐惧实体",
            "guardian_fortress": "装甲堡垒"
        };
    }

    initializeEmpireNames() {
        return [
            "星辰联邦", "银河共和国", "天狼帝国", "织女联盟", "北极星王国", "天鹰联邦",
            "猎户座帝国", "仙女座联盟", "半人马联邦", "天龙帝国", "凤凰共和国", "麒麟王国",
            "白虎联盟", "青龙帝国", "朱雀联邦", "玄武王国", "神鹰共和国", "雷神联盟",
            "海神帝国", "火神王国", "风神联邦", "土神共和国", "水神联盟", "木神帝国",
            "金神王国", "日神联邦", "月神共和国", "星神联盟", "光明帝国", "黑暗联邦",
            "永恒王国", "无限共和国", "至高联盟", "终极帝国", "绝对王国", "完美联邦",
            "和谐共和国", "统一联盟", "秩序帝国", "正义王国", "自由联邦", "平等共和国"
        ];
    }
}

// 辅助函数
String.prototype.repeat = String.prototype.repeat || function(count) {
    if (count < 1) return '';
    let result = '', pattern = this.valueOf();
    while (count > 1) {
        if (count & 1) result += pattern;
        count >>>= 1, pattern += pattern;
    }
    return result + pattern;
};

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    const app = new StellarisChronicleGenerator();
    app.startStarfield();
    
    // 全局错误处理
    window.addEventListener('error', (event) => {
        console.error('全局错误:', event.error);
        if (app) {
            app.log(`❌ 发生未捕获错误: ${event.error.message}`, 'error');
        }
    });
    
    // 全局引用，便于调试
    window.stellarisApp = app;
});