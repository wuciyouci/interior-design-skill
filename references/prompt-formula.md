# AI 生图提示词公式（按需查阅）

---

## 触发规则（强制）

**出提示词必带五件套**——任何 AI 生图提示词输出前必须组装齐：

| 组成 | 来源 | 必带内容 |
|---|---|---|
| ① 风格 | `[skill:interior-styles]` 配方表 + Style DNA | 风格英文关键词 + DNA 选词 |
| ② 配色 | 同上 | 主60/辅30/点10 视觉占比参考（颜色词，非硬比例） |
| ③ 灯光 | 同上 | 色温K + 主光方向 + 补光做法，光源可追溯 |
| ④ 材质 | 本文件材质章节 | 材质+纹理+行为三要素（见下） |
| ⑤ 布局锁定 | 本文件 FLUX2 章节 | "保持参考图片布局/家具位置/视角不变"（渲染时） |

**强制原则**：
1. 五件套缺一不可——禁止只写风格不写配色/灯光/材质
2. 白模转效果/平面图转3D 用锁定公式（本文件对应章节）
3. 负面词必带（本文件第八节三层体系）
4. **禁止抽象质量词**（精致/高级/浪漫/漂亮/干净）——用可观察的物理元素替代（见 anti-slop 规则）
5. 输出末尾附审查标注（见主 SKILL 输出审查机制）

---

## 材质体系（强制·必带）[v6.13新增]

> 来源：ToonFlow art_prop.md（8类材质行为表）+ seedance-20 anti-slop-lexicon（抽象词替代规则）。**核心：材质要写"摄影机下的行为"，不是材料名；抽象词是毒药。**

### 规则1：材质三要素（材质+纹理+行为）

写材质必须包含三个层面，缺一不可：
```
【材质】材料是什么（木/织物/金属/玻璃...）
【纹理】表面长什么样（木纹/编织/拉丝/釉面...）
【行为】在光下怎么表现（反光/漫射/透光/磨损...）
```

### 规则2：8类材质行为表（ToonFlow）[v7.0.1去完美化]

| 材质 | 正确写法（摄影机下的行为） |
|---|---|
| 木质 | 木纹自然清晰细腻、表面清洁保养良好、漆面柔光；**允许 subtle tonal variation / natural grain variation / fine pore variation**（自然色调与木纹变化） |
| 织物（棉/麻/帆布） | 编织纹理细腻可见、表面平整干净、垂坠自然；**允许 fine weave variation / natural softness / realistic drape**（细织纹变化/自然柔软/真实垂坠） |
| 金属（不锈钢/铝合金） | 拉丝肌理清晰、反射周围环境色、表面清洁；**允许 restrained brushed variation**（克制的拉丝变化） |
| 玻璃 | 通透清澈、反光明亮干净、边缘光折射、无指印水渍（玻璃的"干净"是功能要求，保留） |
| 陶瓷 | 釉面柔和反光、表面光洁、无磕碰；**允许 subtle glaze variation** |
| 皮革 | 天然纹理/毛孔细腻、表面光洁、色泽均匀；**允许 natural grain variation** |
| 塑料 | 注塑纹理细腻、表面光洁、无划痕 |
| 纸质 | 纤维纹理细腻、表面平整、印刷清晰 |

> **去完美化原则 [v7.0.1]**：删除"无瑕疵/完全无缺陷/绝对完美"表述 → 统一为 **clean and well-maintained + subtle natural variation + controlled surface imperfections where appropriate**。真实材料的自然变化（木纹/石纹/织纹）是质感来源，不是缺陷；"完全无瑕疵"不等于高级质感。

### 规则3：anti-slop 抽象词替代（seedance-20）[v7.0.0细化]

**抽象质量词会破坏生成**——模型不知道强调哪个元素。必须分解为物理元素：

| 抽象词（禁止） | 替代（物理元素） |
|---|---|
| beautiful / 漂亮 | color, texture, composition, material, light behavior |
| ultra-realistic / 超真实 | material behavior, skin texture, lens artifacts, natural motion |
| 精致 / 高级 / 优雅 | 材质+纹理+光行为（具体写出） |
| 干净整洁 | 无污渍、表面平整、光洁（具体写出） |
| luxurious / stunning / gorgeous / premium-looking | **禁止**——抽象设计审美判断（除非用户明确要求） |
| 8K / 4K / ultra HD / 高清 | 属于 **OUTPUT / RENDER SETTINGS**（渲染输出设置），不在核心设计 Prompt 中；用户要求时可保留在 OUTPUT 段 |

**行业化渲染目标词允许存在**（属于"渲染目标/摄影表现语言"，不是抽象审美判断）：
`advertising-grade commercial render, studio commercial lighting, ultra-sharp crisp details, controlled reflections, polished material detail`

**反例 vs 正例**：
```
✗ "浅橡木床架，精致高级，干净整洁"
✓ "浅橡木床架，木纹自然清晰，表面有轻微使用划痕，漆面柔光反射"
```

### 规则4：材质触发

出现家具/软装/场景描述 → 材质必带三要素写法；任何提示词输出前，检查是否有抽象词残留（有则替换）。

### 规则5：接缝与接触线（分缝必写）[v6.13新增·实测验证]

**问题**：效果图生成后家具与墙面接触缝被 AI 抹平（桌子像长在墙上）——模型默认"无缝干净"，不写缝就融成一片。**2026-08-09 实测：写入后接触线保持住（奶油/轻奢双风格验证通过）。**

**写法**（正面点名，禁止写具体位置防污染布局）：
- **接触线**：家具与墙面接触处分界清晰，接触阴影细微分明（英文：clean contact shadows at furniture-wall junctions, sharp object-wall separation）
- **材质缝**：砖缝清晰均匀 / 板缝自然整齐 / 石材对缝精细 / 踢脚线收口分明
- 放在风格材质段或光影段末尾，与其他材质词一起
- ❌ 禁止："右侧桌子贴墙"（布局词污染参考图）；"不要抹掉缝"（正面零否定）

> **Construction Detail 层标注 [v7.0.1]**：本规则（接触线/分缝/收口/柜门缝隙/台面接缝/墙柜过渡/地板板缝）属于 **Construction Detail 层**，与 Material Fidelity（材料本身）分开，两者不要混成一层。

### 规则6：Material Fidelity（材质保真）[v7.0.1新增]

> 描述真实材料在镜头下的物理表现。**原则："增强物理表现，不增强纹理强度。"**

**九个关注点**：
1. **Material Identity**：材料是什么（明确材料名）
2. **Texture Scale**：纹理尺度真实（木纹/织纹的疏密符合真实比例）
3. **Grain / Pattern Direction**：木纹、织物、石材纹理方向合理（木纹沿板长方向）
4. **Roughness Variation**：表面粗糙度存在细微自然变化（哑光≠完全均匀）
5. **Specular Response**：高光/反射符合材料类型（木=柔和低反射，金属=清晰反射）
6. **Micro Surface**：细微表面结构存在，但不能过度锐化
7. **Edge Transition**：边缘、倒角、柜门、台面边缘具有真实光线过渡
8. **Contact / Joint Detail**：接缝、收口、接触阴影合理（见 Construction Detail）
9. **Material-specific Light Interaction**：不同材料对光的响应不同（石材吸光/木材漫射/玻璃透射）

**禁止用以下词代替 Material Fidelity**（会制造"过度纹理"假质感）：
```
ultra detailed material, maximum texture, extreme texture,
hyper-detailed wood grain, luxurious material, premium material,
super realistic material
```

**正确示例**：oak with subtle tonal variation and natural grain direction / stone with restrained veining and matte micro-surface / linen with fine weave variation and soft realistic drape

---

## 一、通用公式

```
[空间类型] interior, [风格关键词], [材质], [颜色词], [灯光氛围], [装饰细节]
Negative prompt: [禁用词列表]
```

## 二、多视角生成

| 视角 | 关键词 | 适用 |
|------|--------|------|
| 全景 | wide-angle shot, full room view | 展示整体效果 |
| 中景 | mid-shot, focused on main area | 展示核心区域 |
| 特写 | close-up shot, details | 展示材质/软装 |
| 俯视 | top-down view, floor plan | 展示布局分区 |
| 人眼视角 | eye-level view, realistic | 最真实体验 |

## 三、AI 工具选型

| 需求 | 推荐工具 | 说明 |
|------|---------|------|
| 快速效果图 | Midjourney/豆包 | 关键词体系稳定，出图质量高 |
| 局部替换修改 | DALL-E 3 | 自然语言描述精准，可局部编辑 |
| 控制结构 | Stable Diffusion + ControlNet | 保持原布局换风格 |
| 超精细控制 | SD + LoRA | 材质/风格微调 |
| 批量出图 | 豆包/即梦/Kling | 快速出多张供选择 |
| **白模转效果（Flux2Klein本地）** | ComfyUI ReferenceLatent | 锁定布局换风格，见下 |

## 四、FLUX2 白模转效果提示词（锁定布局+换风格）

> 适用：Blender 白模 → ComfyUI（Flux2Klein + ReferenceLatent 工作流）渲染彩色效果图。实测公式，**最大化保持**参考图布局、家具位置、空间关系和相机视角。
> ⚠️ 明确声明：AI 图像模型**无法保证像素级或几何级 100% 复刻**——任何提示词都不得使用"100%复刻/100%还原/绝对一致"这类绝对承诺词（主 SKILL 一致性审查 ⑳）。

**公式**：
```
保持参考图片的布局、家具位置、视角完全不变，仅将风格换成【风格】
+ 风格材质词（按 `[skill:interior-materials]` 材质配方表取：如奶油风 = 奶白乳胶漆墙面、奶杏棉麻床品、浅橡木床架、柔光砖/木纹砖地面、奶咖窗帘）
+ 光逻辑（窗光方向 + 人工光源，色温自洽）
+ 专业室内设计渲染效果图风格，广告级渲染品质，advertising-grade commercial render, studio commercial lighting, ultra-sharp crisp details, controlled reflections, polished material detail（**引擎词 UE5/Lumen 实测效果弱，不再使用**——广告级词为主）
```

**负面词**：
```
白色模型，素模，灰色，无纹理，样板间，塑料感，模糊，扭曲透视，灰暗，
垃圾，灰尘，污渍，脏乱，使用痕迹，磨损，划痕，生活痕迹
```

**增强 LoRA（可选·实测有效）**：`klein_9b_enhancer_v2`（C 站 Klein 9B 增强，8000步）——LoraLoaderModelOnly 挂 UNET，strength **0.7**，提示词开头加触发词 `enhance this image,`。2026-08-09 实测：清晰度明显提升、布局保持（奶油/轻奢双风格验证）

**铁律（实测踩坑总结）**：
1. ❌ 禁止写具体布局词（"右侧有书桌""一个衣柜"）——会污染参考图，模型信提示词不信参考图
2. ❌ 禁止写"渲染/重新渲染/根据图片渲染"——模型会保持白模不动，不上色
3. ❌ 禁止写"严格照抄参考图"——模型连白模材质一起抄，还是不上色
4. ✅ 只有"锁定布局 + 换风格"组合正确：布局句锁定参考图，风格句驱动上色
5. 换风格 = 只改风格材质段，布局句原样保留
6. 家具错位/变门等 = 抽卡问题，换 seed 重跑即可
7. 场景单调 = 白模本身简单（家具少），不是提示词问题；要丰富场景需在白模里加家具
8. **地板脏污/细碎垃圾** = 负面词必须带全：`垃圾，碎屑，灰尘，污渍，脏乱，杂物，地面脏污，墙壁污渍，纸屑`（正面词同时写"干净整洁"）——漏写就会出现"一堆细小垃圾"

## 四·五、Design Layer / Render Layer 分离 [v7.0.0新增]

> 核心：**"更好看"不能成为改变用户设计风格的理由。Render Layer 的职责是让正确的设计看起来更好，不是重新设计。**

### Design Layer（设计层）——不可随意改变的设计意图
负责：风格、色彩、材质、家具、空间功能、灯光色温、布局、设计语言。

### Render Layer（渲染层）——让设计更好地被看见
负责：natural material separation, realistic shadows, controlled highlights, subtle tonal contrast, realistic reflections, depth, photographic exposure, commercial interior photography, material readability, clean contact shadows, realistic global illumination。

**Render Layer 不得改变 Design Layer 的**：风格、主材、主色、色温、家具风格、布局。

| 允许（渲染层优化） | 不允许（改动设计层） |
|---|---|
| 增加浅橡木与暖白墙之间的明度层次 | 为了"高级感"改成胡桃木 |
| 增加自然阴影和材质分离 | 改成 2700K 暖光 |
| 提高浅木纹理可读性 | 加入中古藤编元素 |

**执行**：出提示词时先组装 Design Layer（风格 DNA + 材质 + 色温 + 布局锁定），再加 Render Layer 渲染目标词（广告级渲染词），最后负面词。对照主 SKILL 一致性审查 ⑲（DESIGN_RENDER_SEPARATION）。

---

## 五、平面图 → 3D 立体户型渲染（无需白模）

> 适用：户型平面图（2D 线稿）→ 酷家乐式 3D 立体户型渲染图。**布局 100% 复刻平面图，不用搭白模**。与白模转效果互补：平面图出"立体户型图"（看布局），白模出"透视效果图"（看感觉）。

**公式**（同一套锁定公式，风格段换成 3D 立体）：
```
保持参考图片的布局、家具位置、房间结构完全不变，仅将风格换成 3D 立体户型渲染图风格，
墙体拉伸有高度形成立体空间，家具立体有体积感，俯视斜角透视角度，
【风格材质词】+ 柔和自然光 + 真实材质质感 + 专业室内设计渲染
```

**关键细节**：
- 家具类型/数量要在提示词里点名锁定："圆形餐桌保持圆形餐桌，两个沙发保持两个沙发"——否则模型会改家具（桌变床、双沙发变一沙发）
- 负面词加：`平面图，线稿，2D图纸，标注文字，尺寸线，家具变形，家具数量变化`
- 完整脏污负面词同上

## 六、布局审查固定流程（Blender 白模搭完后必跑）

> 强制流程：方案确定 → Blender 搭白模 → **审查脚本校验** → 全 PASS 才允许 ComfyUI 渲染。没有审查就渲染 = 白跑（曾出现床是 0.9m 单人床、餐桌碎片在墙外等与方案不符的问题）。

**步骤**：
1. 方案确定 → 编辑 `scripts/verify_layout.py` 顶部的 `PLAN` 配置（家具目标/容差/最小尺寸/间距）
2. Blender 搭完白模 → 立即跑审查：
   ```python
   import importlib.util
   spec = importlib.util.spec_from_file_location("verify_layout", r"scripts/verify_layout.py")
   mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
   mod.verify()
   ```
3. 全部 ✅ PASS → 才允许 ComfyUI 渲染；有 ❌ FAIL → 先修布局再渲染
4. 审查项：家具存在性 / 位置容差 / 最小尺寸 / 间距（GB 50096 走道 ≥0.6m）/ 越界
5. 注意：书桌类带椅子的家具，椅子在桌前属正常，用 `exclude` 配置排除椅子再算间距（否则椅子占了走道误报 FAIL）

## 七、专业效果图风格约束（渲染引擎质感）

> 方向：**专业室内设计渲染效果图**（知末/酷家乐品类）——一眼看出是设计渲染效果，保证完美才能给用户看。已删除"做真实/生活痕迹/镜头语言"体系（不适合室内效果图，那是真人视频的方向）。引擎词参考：UE5（Lumen/Nanite/PBR）、V-Ray/Corona（archviz 常用）。

**渲染三铁律**（生成效果图提示词时必守）：
1. **光源可追溯** — 每个光源必须有明确来源："从右侧窗户45°斜入的午后阳光，色温约4500K"——**禁止无来源的全局照明**（解决"无灯槽却出灯槽光"：光源必须物理自洽，天花板平的就没有灯槽光）
2. **空间结构锁定** — 同一空间换视角/换时段/换天气时，家具位置/窗帘位置/房间结构**必须可辨认不变**（解决"窗帘乱放"）
3. **展厅级干净（效果图专用）** — 效果图 = 画面干净、物品**全新品相**（像新买的东西放里面）：正面词写"全新/崭新/干净整洁"，负面词压"使用痕迹、磨损、划痕、污渍、灰尘、杂物"（⚠️ 此规则只适用于效果图；真人实拍视频才用"生活痕迹"）

**室内类型速查**（写提示词时选对应模板）：
| 类型 | 核心元素 | 氛围词 |
|---|---|---|
| 出租屋/单身公寓 | 单人床+小书桌+简易衣柜+小阳台+台灯 | 温馨私密、独居的真实 |
| 老小区客厅 | 沙发+茶几+电视柜+餐桌+窗帘+墙上海报 | 市井日常、几代人的生活痕迹 |
| 高层公寓客厅 | 落地窗+城市窗景+沙发组+电视背景墙+绿植 | 开阔通透、都市中产日常 |
| 写字楼办公室 | 玻璃隔断+工位+文件柜+会议桌+百叶窗 | 秩序井然、冷调专业 |
| 咖啡厅/奶茶店 | 吧台+卡座+落地窗街景+暖调灯光 | 都市第三空间、松弛 |
| 便利店（深夜） | 货架+收银台+冰柜冷光+落地玻璃街景 | 深夜安全屋、孤岛式照明 |
| 面馆/小餐馆 | 餐桌+调味瓶+开放式厨房蒸汽+暖调灯 | 市井烟火、人情味 |
| 医院走廊/病房 | 长走廊+日光灯+护士站+白墙扶手 | 清冷肃穆、漫长的等待 |
| 地下车库 | 环氧地坪+车位线+承重柱+日光灯冷光 | 冷硬、孤寂、回声感 |

**渲染质感词**（写"效果图感"用，禁抽象词）：
- **广告级组合（实测有效·主推）**：`advertising-grade commercial render, studio commercial lighting, ultra-sharp crisp details, controlled reflections, polished material detail`——2026-08-09 实测生效
- **⚠️ 引擎词实测弱（2026-08-09 验证）**：UE5/Lumen/Nanite/PBR 词对 Klein 效果不明显（Klein 训练集不吃引擎词），V-Ray/archviz 同理——**不再使用引擎词，用广告级词替代**
- **陷阱**：删"4K/8K/ultra HD"分辨率词（被误判为增强指令覆盖几何精度）——它们属于 OUTPUT/RENDER SETTINGS 层，用户要求 8K 输出时放在 OUTPUT 段，不混入设计 Prompt；禁平台词（ArtStation/trending）；灯光写物理路径不写抽象"电影感"（呼应光比体系）
- **软装完整搭配**：装饰画/绿植/灯具/摆件点缀齐全——效果图感的关键（画面整洁但软装完整，不是空房间）

## 七·五、效果图"干净+质感"操作清单 [v6.13新增]

> 来源：2026-08-09 网络调研（fal.ai Klein 官方指南/SwarmUI/CivitAI/MyAIForce）+ 本地软件验证（ToonFlow Q4 颗粒声明 / seedance-20"命名缺陷=种植缺陷"）。**目标：画面干净（像新买的东西放里面）+ 材质有质感（不塑料）**。

### A. 参数定标（FLUX.2 Klein 专用）

| 参数 | 值 | 说明 |
|---|---|---|
| 普通 CFG | **1.0 固定** | Klein 是蒸馏模型，CFG 拉高=过饱和崩坏 |
| guidance（蒸馏CFG） | **2.5-3.0**（默认3.5偏高=塑料感来源） | 提示词没被遵循再升回 3.5 |
| 步数 | 8-12（质量向） | 4 步蒸馏模型加步数不提升画质 |
| 采样器 | **euler + beta/normal**（或 heunpp2 质量向） | ❌ euler+karras 感知质量降 5-10% |

### B. 提示词层（干净靠正面锁定，不靠负面堆砌）

1. **删抽象堆砌词**：masterpiece/best quality/hyperrealistic/8K——模型读成冲突信号磨平细节
2. **换"后期流程词"**：clean digital file, histogram equalization, gamma correction, unsharp mask——显著提升干净感
3. **景深是第一杠杆**：浅景深（85mm f/2, background softly blurred）把 AI 易画脏的中远景杂项化入焦外；室内加 "clear foreground-midground-background separation"
4. **留白用专业词**：negative space composition / breathing space / no redundant elements（别直写"more blank space"会出大块纯白死区）
5. **全新品相正面词**：brand-new items, spotless, pristine surfaces, crisp and clean（负面词压使用痕迹/磨损/划痕/污渍/灰尘/杂物）

### C. 材质词升级（防塑料感）

1. **布料五维**：垂坠 drape + 织纹 weave + 微光泽 sheen + 重量 weight + 纹理 grainy texture；用**具体面料名**（linen/chenille/tweed）替代"有纹理的布料"
2. **"no plastic sheen" 放句尾**（否则被后续词覆盖）
3. 木加 wood grain、金属加 brushed 拉丝纹理 + clean reflections、墙面加 micro-surface details（细腻微肌理，非划痕）
4. 塑料感本质 = 均匀高光+缺微细节；写物理行为不写形容词（呼应材质三要素）

### D. 后处理层（直出是"脏"的最大元凶）

1. **两遍采样**：先小尺寸底图（如 896×1152）→ 潜空间放大 1.5x → 第二遍重绘 denoise **0.25-0.35**（皮肤 0.1-0.2）
2. **放大前先降噪**：图有杂讯直接超分=放大噪点；禁止 8x 单次，链式 2x/4x（4x-UltraSharp/RealESRGAN/SwinIR）
3. **Klein 生态**：图生图放大用 **Basic Scheduler**（Flux2Scheduler 会把 denoise 锁死 1.0），denoise 0.75-0.85；KleinTiledUpscaler 分块防平地区幻觉
4. **纹理重复伪影**：出 1024+ 大图前挂 JigSaw Hi-Res（YaRN RoPE rescaling）防"灰罩/重影"；分块放大 512px+96px重叠+接缝修复（UltimateSDUpscale 0.18 denoise 羽化12px）
5. **可选增强**：Detail Daemon（detail_amount 0.1-1.0 别过锐）、材质一致性 LoRA（Krea-Extracted：texture_detail 5-8）——LoRA 堆多反而糊

### E. 效果图 vs 真人视频（干净度分道）

| 场景 | 品相 | 负面词 |
|---|---|---|
| **效果图（本 SKILL）** | 全新品相，展厅级干净 | 使用痕迹/磨损/划痕/污渍/灰尘/杂物 |
| 真人实拍视频（ToonFlow） | 生活痕迹：褶皱/磨损/包浆 | 磨皮/塑料感/全新样板间 |

---

## 八、负面提示词三层体系

### L1：全局禁用（所有风格通用）
```
cluttered, low quality, blurry, distorted perspective, poorly proportioned, warped
```

### L2：风格排斥（特定风格互斥）
```
现代简约 → ornate, vintage, heavy drapery, excessive decor
轻奢风 → cheap plastic, rustic, shabby, unfinished surfaces
北欧风 → luxury, heavy curtains, dark saturated colors
新中式 → European style, pastel colors, shoji screen
侘寂风 → bright colors, perfect symmetry, polished new surfaces
```

### L3：场景细化（按房间功能）
```
客厅 → messy, oversized furniture blocking path
卧室 → harsh overhead only, cold clinical lighting
厨房 → dirty grease, cluttered countertops
卫生间 → mold, water spots, poor ventilation
书房 → glare on screen, uncomfortable seating
```
