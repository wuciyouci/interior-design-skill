#!/usr/bin/env python3
"""interior-design L2 审计 — L1 通用+领域专项 + Consistency Check（v7.0.0 升级）

用法:
  python audit.py <SKILL.md路径>          # L1 文件审计 + 文件级一致性检查
  python audit.py --prompt <提示词文本>    # L2 提示词运行时一致性检查 (PASS/WARN/FAIL)
  python audit.py --prompt-file <文件路径> # 同上，从文件读提示词
"""
import sys, re, json
from pathlib import Path

# === 文件级检查数据 ===
ABSOLUTE_CLAIMS = ["100%复刻", "100% 复刻", "100%还原", "100% 还原", "绝对一致",
                   "绝对相同", "保证复刻", "完全一致", "100%保持一致", "像素级 100%"]
ABSOLUTE_RULE_WORDS = ["不可妥协", "永不单吊灯", "必须严格执行的硬约束"]
HARD_601030 = [r"必须.*(?:60%|30%|10%).*比例", r"60%.*30%.*10%.*硬约束", r"严格.*(?:60/30/10|60\s*/\s*30\s*/\s*10)"]

# === 运行时提示词检查数据（可扩展）===
# 高风险漂移对：目标风格 -> (核心特征, 漂移特征, 默认色温K)
# v1.3.0 市场实况校准：modern minimalist 色温 4000K→3000K（无主灯暖光市场主流）；
# mid-century modern 补骨骼线柜门/洞石；cream style 补肤感哑光；wabi-sabi 补微水泥。
STYLE_DNA_HINTS = {
    "modern minimalist": {
        "core": ["modern minimalist", "clean lines", "matte white", "light oak",
                 "linear led", "no main light", "3000k", "black steel", "linear lighting", "integrated storage"],
        "drift": ["walnut", "rattan", "caramel leather", "brass", "mustard yellow",
                  "deep green", "edison", "2700k", "tapered", "danish", "mid-century"],
        "preferred_k": 3000,
    },
    "mid-century modern": {
        "core": ["mid-century", "walnut", "teak", "rattan", "brass", "mustard",
                 "deep green", "3000k", "tapered leg", "caramel leather", "edison",
                 "bone-inlay cabinet", "travertine"],
        "drift": ["palace", "gilded", "rococo", "ornate classical", "neon",
                  "crystal chandelier", "industrial loft"],
        "preferred_k": 3000,
    },
    "cream style": {
        "core": ["cream", "milk apricot", "beige", "curved", "soft healing", "3000k",
                 "matte skin-feel cabinet", "cocoa egg milk"],
        "drift": ["cold gray", "industrial", "sharp angular", "dark walnut dominant"],
        "preferred_k": 3000,
    },
    "wabi-sabi": {
        "core": ["wabi-sabi", "plaster", "linen", "beige", "terracotta", "natural aging",
                 "imperfection", "microcement"],
        "drift": ["glossy", "polished luxury", "neon", "saturated bright color", "symmetrical formal"],
        "preferred_k": 2700,
    },
}
# 渲染层词（出现在设计 Prompt 中允许，但不得改变设计层内容）
RENDER_LAYER_WORDS = ["advertising-grade", "studio commercial lighting", "ultra-sharp",
                      "controlled reflections", "polished material detail", "8k", "4k",
                      "ultra hd", "photorealistic", "global illumination", "contact shadows"]
# Material Fidelity 假质感词（v7.0.1：禁止用这些词代替真实材质物理表现）
MF_FAKE_WORDS = ["ultra detailed material", "maximum texture", "extreme texture",
                 "hyper-detailed wood grain", "luxurious material", "premium material",
                 "super realistic material"]
# 灯光层级词：区分主照明层与辅助/重点层（同层级色温冲突检测用）
LAYER_MAIN = ["ambient", "general", "overall", "main light", "linear", "cove", "wash",
              "ceiling", "基础", "主光", "主照明", "线性", "洗墙", "顶光", "主灯"]
LAYER_ACCENT = ["accent", "task", "floor lamp", "pendant", "table lamp", "wall sconce",
                "reading", "art light", "落地灯", "吊灯", "台灯", "壁灯", "重点", "补光", "氛围"]
# 设计层泄漏判断：渲染词 + 设计层改变词同时出现 -> 泄漏（如"为了高级感改成胡桃木"）
DESIGN_CHANGE_LEAK_WORDS = ["改成胡桃木", "升级为胡桃木", "改用2700k", "加入藤编", "为了高级感"]

def _find(text, words):
    """查找命中词，排除'禁止/不得/不使用/无绝对'等规则语境行（规则文本本身会举例这些词）"""
    low = text.lower()
    lines = low.split('\n')
    hits = []
    for w in words:
        wl = w.lower()
        for ln in lines:
            if wl in ln and not re.search(r'禁止|不得|不使用|无绝对|不要|不能|勿|不可|不是|降级|修订|→', ln):
                hits.append(w)
                break
    return hits

# === L1 + 文件级一致性 ===
def audit(skill_path):
    path = Path(skill_path).resolve()
    if not path.exists():
        return {"error": f"文件不存在: {skill_path}"}
    text = path.read_text(encoding='utf-8')

    # === 通用检查（L1，保持原有）===
    lines = text.split('\n')
    fm_m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    fm = {}
    if fm_m:
        for l in fm_m.group(1).split('\n'):
            kv = re.match(r'^(\w+):\s*(.+)', l)
            if kv: fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")

    refs_dir = path.parent / 'references'
    vers_dir = path.parent / 'versions'
    check_dirs = [path.parent] + ([refs_dir] if refs_dir.is_dir() else []) + ([vers_dir] if vers_dir.is_dir() else [])
    ghost = []
    for p in re.findall(r'[参见参考]+\s*[`]*([\w/\-\.]+\.md)', text):
        p1 = p.split('/', 1)[1] if '/' in p else p
        if re.search(r'[XYZ]', p1):
            continue  # 模板占位引用（如 SKILL-vX.Y.Z.md）不算幽灵
        if not any((d / p).exists() or (d / p1).exists() for d in check_dirs): ghost.append(p)

    triggers = re.findall(r"'\w[\w\d\s]*'", fm.get('description',''))
    desc_len = len(fm.get('description',''))

    generic = {
        "行数": {"value": len(lines), "hard_pass": len(lines)<=1500, "recommended_pass": len(lines)<=500},
        "frontmatter": {"parse_ok": bool(fm_m), "version": fm.get('version'), "version_semver": bool(re.match(r'^\d+\.\d+\.\d+', fm.get('version','')))},
        "description": {"length": desc_len, "over_500": desc_len>500},
        "触发词": {"count": len(triggers), "pass": len(triggers)>=5},
        "幽灵引用": {"count": len(ghost), "files": ghost, "pass": len(ghost)==0},
        "references目录": str(refs_dir) if refs_dir.is_dir() else "不存在"
    }

    # === 领域专项（L1，保持原有）===
    hardrule_price_ban = bool(re.search(r'禁止.*(?:输出|编造|估算).*(?:价格|单价|市场价)', text))
    budget_rule_price_ok = bool(re.search(r'市场参考', text))
    budget_conflict = hardrule_price_ban and budget_rule_price_ok
    style_rows = len(re.findall(r'^\|\s*\d+\s*\|', text, re.MULTILINE))
    style_complete = style_rows >= 28
    hard_rules = len(re.findall(r'### 硬规则\d', text))
    rules_with_exemption = len(re.findall(r'> 说明[：:]', text))
    has_selfcheck = bool(re.search(r'【极简自检】', text))
    has_brand_ban = bool(re.search(r'禁止.*(?:装修)?品牌', text))
    has_brand_disclaimer = bool(re.search(r'不构成.*推荐|仅用于.*搜索|不主动推荐', text))

    domain = {
        "预算规则冲突": {"detected": budget_conflict, "detail": "硬规则2禁市场价区间·但预算规则写了'市场参考范围'" if budget_conflict else "无冲突"},
        "风格表完整性": {"count": style_rows, "pass": style_complete, "detail": f"检测到{style_rows}种风格·期望≥28"},
        "硬规则数": {"count": hard_rules, "pass": hard_rules>=4},
        "豁免说明": {"count": rules_with_exemption, "detail": "硬规则中含'说明/豁免'的条数"},
        "自检报告格式": has_selfcheck,
        "品牌措辞": {"禁令存在": has_brand_ban, "免责存在": has_brand_disclaimer}
    }

    # === 文件级一致性检查（v7.0.0 新增）===
    claims = _find(text, ABSOLUTE_CLAIMS)
    abs_words = _find(text, ABSOLUTE_RULE_WORDS)
    hard_601030_hits = [m for pat in HARD_601030 for m in re.findall(pat, text)]
    dna_count = len(re.findall(r'^MUST_HAVE:', text, re.MULTILINE))
    has_design_render = bool(re.search(r'Design Layer|Render Layer|DESIGN_RENDER_SEPARATION', text))
    has_consistency_matrix = bool(re.search(r'Cross-Rule Consistency Matrix|跨规则一致性', text))
    has_style_drift = bool(re.search(r'Style Drift|风格漂移', text))

    # DNA 宿主文件要求 28 字段；非宿主文件（主 SKILL）要求引用 Style DNA 即可
    dna_pass = (dna_count >= 28) or (dna_count == 0 and 'Style DNA' in text)
    # 角色识别改用内容特征（原先依赖 path.parent.name，换目录名/重命名即失效导致静默跳过检查）
    is_root = (path.name == 'SKILL.md' and bool(re.search(r'Operating Loop|强制触发规则表', text)))
    is_styles = (path.name == 'SKILL.md' and bool(re.search(r'MUST_HAVE:|Style DNA', text)))
    consistency = {
        "绝对承诺词": {"hits": claims, "pass": len(claims) == 0},
        "绝对化规则措辞": {"hits": abs_words, "pass": len(abs_words) == 0, "note": "命中时建议改为条件化表述"},
        "60-30-10硬约束表述": {"hits": hard_601030_hits, "pass": len(hard_601030_hits) == 0, "note": "60/30/10 应为视觉占比参考，非硬比例"},
        "Style DNA 完整性": {"MUST_HAVE字段数": dna_count, "pass": dna_pass, "note": "宿主文件期望≥28字段；非宿主文件检查是否引用DNA"},
        "Design/Render 分离章节": has_design_render if is_root else "SKIP",
        "一致性矩阵章节": has_consistency_matrix if is_root else "SKIP",
        "漂移检测章节": has_style_drift if (is_root or is_styles) else "SKIP",
    }

    return {"skill": str(path.name), "通用": generic, "领域专项": domain, "consistency": consistency}

# === 提示词运行时一致性检查（L2）===
def check_prompt(text, target_style=None):
    low = text.lower()
    out = {}

    # 1. 绝对承诺词 -> FAIL
    claims = _find(low, ABSOLUTE_CLAIMS)
    out["ABSOLUTE_CLAIM"] = "FAIL" if claims else "PASS"
    if claims: out["ABSOLUTE_CLAIM_DETAIL"] = claims

    # 2. 风格身份 + 漂移
    style = (target_style or "").lower()
    if style and style in STYLE_DNA_HINTS:
        dna = STYLE_DNA_HINTS[style]
        core_hits = [w for w in dna["core"] if w in low]
        # 漂移检测排除否定/禁止语境（如配方表"不要水晶灯"→ no crystal chandelier 不算漂移特征）
        drift_hits = []
        for w in dna["drift"]:
            wl = w.lower()
            for ln in low.split('\n'):
                if wl in ln and not re.search(r'禁止|不得|不使用|无绝对|不要|不能|勿|不可|不是|no |without|avoid|never|降低|减少', ln):
                    drift_hits.append(w)
                    break
        out["STYLE_IDENTITY"] = "PASS" if core_hits else "WARN"
        if not core_hits: out["STYLE_IDENTITY_DETAIL"] = f"未命中目标风格核心特征: {dna['core'][:4]}"
        out["STYLE_DRIFT"] = "FAIL" if len(drift_hits) >= 3 else ("WARN" if drift_hits else "PASS")
        if drift_hits: out["STYLE_DRIFT_DETAIL"] = f"漂移特征命中{len(drift_hits)}个(≥3判HIGH): {drift_hits}"
    else:
        out["STYLE_IDENTITY"] = "SKIP" if not style else "WARN"
        out["STYLE_DRIFT"] = "SKIP"

    # 3. 色温冲突：同层级冲突检测（v7.0.1）
    #    同一主照明层 4000K+2700K → FAIL；不同照明层（4000K ambient + 2700K accent）→ PASS（layered lighting 允许）
    k_values = [int(m) for m in re.findall(r'(\d{4})\s*k', low)]
    has_4000 = 4000 in k_values
    has_2700 = 2700 in k_values
    has_3000 = 3000 in k_values
    def _ctx(m):
        # 就近层级窗口：前 25 字符（如 "ambient 4000K"）+ 后 45 字符（如 "4000K linear cove"）
        # 窗口不可过宽，否则相邻色温的层级词互相污染
        return low[max(0, m.start()-25): min(len(low), m.end()+45)]
    k_ctx = {k: [] for k in set(k_values)}
    for m in re.finditer(r'(\d{4})\s*k', low):
        k_ctx.setdefault(int(m.group(1)), []).append(_ctx(m))
    def _in_layer(ctx_list, layer_words):
        return any(any(w in c for w in layer_words) for c in ctx_list)
    layered = False
    if has_4000 and has_2700:
        c4, c7 = k_ctx.get(4000, []), k_ctx.get(2700, [])
        c4_main, c4_acc = _in_layer(c4, LAYER_MAIN), _in_layer(c4, LAYER_ACCENT)
        c7_main, c7_acc = _in_layer(c7, LAYER_MAIN), _in_layer(c7, LAYER_ACCENT)
        # 分层 = 一个在主层 + 另一个在辅助层（双方都需有明确层标记）
        layered = (c4_main and c7_acc) or (c4_acc and c7_main)
    out["LIGHTING_CONSISTENCY"] = "FAIL" if (has_4000 and has_2700 and not layered) else "PASS"
    if layered:
        out["LIGHTING_CONSISTENCY_DETAIL"] = "多层色温（如 4000K ambient + 2700K accent）→ layered lighting，允许"
    # 风格默认色温偏离 >1000K = WARN（用主层色温比较；用户指定优先，不自动 FAIL）
    main_k = [k for k in k_values if _in_layer(k_ctx.get(k, []), LAYER_MAIN)] or k_values
    if style and style in STYLE_DNA_HINTS:
        pref_k = STYLE_DNA_HINTS[style].get("preferred_k")
        if pref_k and main_k and abs(min(main_k) - pref_k) > 1000 and not (has_4000 and pref_k == 4000 and not layered):
            out["LIGHTING_CONSISTENCY"] = "WARN"
            out["LIGHTING_CONSISTENCY_DETAIL"] = f"提示词主层色温 {main_k}K 偏离 {style} 默认 {pref_k}K>1000K——WARN 提示，用户明确指定则用户优先（P0）"

    # 4. 材质-灯光冲突：深暖木 + 高色温
    has_dark_warm_wood = bool(re.search(r'(walnut|teak|dark oak|深(?:暖)?胡桃|柚木)', low))
    has_cool_light = bool(re.search(r'4000\s*k|5000\s*k|冷白光|cool white', low))
    out["MATERIAL_CONSISTENCY"] = "WARN" if (has_dark_warm_wood and has_cool_light) else "PASS"
    if has_dark_warm_wood and has_cool_light:
        out["MATERIAL_CONSISTENCY_DETAIL"] = "深暖木材+高色温冷光 → 木材易发灰，建议协调或提示用户"

    # 5. 色彩一致性：暖色系词 + 冷色系词同现（饱和度冲突）
    warm_colors = bool(re.search(r'(mustard|caramel|terracotta|burnt orange|芥末黄|焦糖)', low))
    cool_colors = bool(re.search(r'(cool gray|icy blue|steel blue|冷灰)', low))
    out["COLOR_CONSISTENCY"] = "WARN" if (warm_colors and cool_colors and not has_4000) else "PASS"

    # 6. 渲染层泄漏
    leak_hits = [w for w in DESIGN_CHANGE_LEAK_WORDS if w.lower() in low]
    out["DESIGN_RENDER_SEPARATION"] = "FAIL" if leak_hits else "PASS"
    if leak_hits: out["DESIGN_RENDER_SEPARATION_DETAIL"] = f"渲染层试图改变设计层: {leak_hits}"

    # 6.5 Material Fidelity 假质感词（v7.0.1）：禁止以"过度纹理词"代替真实材质物理表现
    mf_hits = [w for w in MF_FAKE_WORDS if w in low]
    out["MATERIAL_FIDELITY"] = "FAIL" if mf_hits else "PASS"
    if mf_hits: out["MATERIAL_FIDELITY_DETAIL"] = f"假质感词（应描述物理表现而非堆纹理强度）: {mf_hits}"

    # 7. 渲染词存在性（P5/P6 表现层）
    rl = [w for w in RENDER_LAYER_WORDS if w in low]
    out["RENDER_LAYER"] = "PASS" if rl else "INFO"
    if not rl: out["RENDER_LAYER_DETAIL"] = "未检测到渲染目标词（可选）"

    return out

def _style_from_args(args):
    """解析 --style <风格名>，供 --prompt/--prompt-file 使用"""
    if '--style' in args:
        i = args.index('--style')
        if i + 1 < len(args):
            return args[i + 1]
    return None

def _has_fail(obj):
    """递归检查审计结果里是否存在 FAIL（退出码门禁：有 FAIL 必须退非0）"""
    if isinstance(obj, dict):
        return any(_has_fail(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_has_fail(v) for v in obj)
    return obj == "FAIL"


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == '--prompt':
        style = _style_from_args(args)
        res = check_prompt(args[1], style)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(1 if _has_fail(res) else 0)
    if len(args) >= 2 and args[0] == '--prompt-file':
        style = _style_from_args(args)
        try:
            text = Path(args[1]).read_text(encoding='utf-8')
        except FileNotFoundError:
            print(json.dumps({"error": f"文件不存在: {args[1]}"}, ensure_ascii=False)); sys.exit(1)
        res = check_prompt(text, style)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(1 if _has_fail(res) else 0)
    if len(args) < 1:
        print(json.dumps({"error": "缺少参数", "usage": "python audit.py <SKILL.md路径> | python audit.py --prompt <文本> | python audit.py --prompt-file <文件>"}, ensure_ascii=False))
        sys.exit(2)
    try:
        res = audit(args[0])
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(1 if _has_fail(res) else 0)
    except FileNotFoundError:
        print(json.dumps({"error": "文件不存在", "message": f"找不到: {args[0]}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "脚本异常", "message": str(e)[:200]}, ensure_ascii=False))
        sys.exit(1)
