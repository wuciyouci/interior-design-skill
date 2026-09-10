# Regression Cases [v7.0.0 新增]

> 一致性升级回归测试：验证 Style DNA、漂移检测、色温规则、用户优先原则的执行正确性。
> 运行：`python scripts/audit.py --prompt "<提示词>"` 可辅助判定（结合本表人工预期）。
> 每跑一次 SKILL 升级，必须重跑本表 6 例，全部符合预期才算通过。

---

## CASE 1：现代简约 + light oak + 4000K（不漂移）

**输入**：Modern Minimalist + light oak + 4000K

**预期**：
- STYLE_IDENTITY: PASS（modern minimalist 核心特征命中）
- STYLE_DRIFT: PASS（不得漂移到 Japandi / Mid-Century）
- LIGHTING_CONSISTENCY: PASS（4000K 与风格一致，现代简约允许 3500-4000K）

**通过标准**：`audit.py --prompt` 输出 STYLE_IDENTITY=PASS 且 STYLE_DRIFT=PASS。

---

## CASE 2：中古风 + walnut + leather + rattan + 3000K（正确中古）

**输入**：Mid-Century Modern + walnut + leather + rattan + 3000K

**预期**：
- STYLE_IDENTITY: PASS（walnut/rattan/leather 命中中古核心）
- STYLE_DRIFT: PASS（无古典/工业/霓虹特征）
- MATERIAL_CONSISTENCY: PASS（深暖木 + 3000K 暖光协调）

**通过标准**：输出 STYLE_IDENTITY=PASS 且 STYLE_DRIFT=PASS 且 MATERIAL_CONSISTENCY=PASS。

---

## CASE 3：现代简约 + walnut + rattan + caramel leather + brass + mustard + 2700K（HIGH DRIFT）

**输入**：Modern Minimalist 却出现 walnut + rattan + caramel leather + brass + mustard + 2700K Edison

**预期**：
- STYLE_DRIFT: **FAIL**（漂移特征 ≥3 → HIGH STYLE DRIFT → Mid-Century Modern）
- 系统必须提示"风格漂移"，不得静默通过

**通过标准**：audit 输出 STYLE_DRIFT=FAIL 且 DETAIL 列出漂移特征。

---

## CASE 4：现代简约 + 4000K + warm white + light oak（warm white 不误判）

**输入**：Modern Minimalist + 4000K + warm white + light oak

**预期**：
- COLOR_CONSISTENCY: PASS（warm white 是中性暖白，不构成暖色风格判定）
- LIGHTING_CONSISTENCY: PASS
- **不得**因为出现 "warm white" 而误判为暖风格（侘寂/复古等）

**通过标准**：输出全部 PASS，无暖风格误判 WARN。

---

## CASE 5：Wabi-Sabi + 4000K（WARN 而非自动 FAIL）

**输入**：Wabi-Sabi 风格 + 4000K

**预期**：
- LIGHTING_CONSISTENCY: WARN（色温偏离风格默认 2700K 暖调，但**不自动 FAIL**）
- 如果用户明确指定 4000K → 用户要求优先（P0），WARN 提示后按用户执行

**通过标准**：输出 WARN 而非 FAIL；方案交付时带提示"与风格默认色温不一致，用户要求优先"。

---

## CASE 6：用户指定"现代简约，但我要深胡桃木"（用户优先）

**输入**：用户明确要求"现代简约，但我要深胡桃木"

**预期**：
- **允许执行用户要求**（P0 用户明确要求 > P2 风格 DNA）
- 同时提示："材质方向会使视觉更接近深色现代/中古倾向，但用户要求优先"
- MATERIAL_CONSISTENCY: WARN 提示，不阻止执行

**通过标准**：输出最终方案采用深胡桃木，且附用户优先提示语。

---

## CASE 7：分层灯光（v7.0.1 新增）

**输入**：Modern Minimalist + 4000K linear cove main illumination + 2700K floor lamp accent

**预期**：
- LIGHTING_CONSISTENCY: **PASS**（4000K 主层 + 2700K 辅助层 = 允许的 layered lighting）
- 同主层版本（4000K main ceiling + 2700K main ceiling）→ **FAIL**

**通过标准**：`audit.py --prompt` 分层版 LIGHTING=PASS、同层版 LIGHTING=FAIL。

## CASE 8：Material Fidelity 假质感词（v7.0.1 新增）

**输入**：出现 ultra detailed material / maximum texture / hyper-detailed wood grain

**预期**：MATERIAL_FIDELITY: FAIL（假质感词，应描述物理表现）

**通过标准**：audit 输出 MATERIAL_FIDELITY=FAIL 且 DETAIL 列出命中词。

---

## 运行记录

| 日期 | 版本 | CASE1 | CASE2 | CASE3 | CASE4 | CASE5 | CASE6 | CASE7 | CASE8 | 结果 |
|------|------|-------|-------|-------|-------|-------|-------|-------|-------|------|
| 2026-08-12 | v7.0.0 | ✅PASS | ✅PASS | ✅FAIL(漂移) | ✅PASS | ✅WARN | 行为规则·人工 | — | — | **全部通过** |
| 2026-08-12 | v7.0.1 | ✅PASS | ✅PASS | ✅FAIL(漂移) | ✅PASS | ✅WARN | 行为规则·人工 | ✅PASS | ✅FAIL(假质感词) | **全部通过** |

> CASE6 验证记录：用户指定"现代简约但深胡桃木" → 执行用户要求（P0 优先），附提示"材质方向使视觉更接近深色现代/中古倾向，用户要求优先"——由运行 SKILL 时人工确认，audit 脚本不做硬性拦截。
