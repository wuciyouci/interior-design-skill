# 测试用例

> 基于 SiliconFlow Z-Image-Turbo + Qwen3-VL-32B 实测。2026-06-18。

## 1. AI 生图提示词验证（原木风客厅）

- **输入需求**："89㎡三居室，原木风，客厅，预算舒适型"
- **模型**：Tongyi-MAI/Z-Image-Turbo
- **v1 提示词**：`medium size cozy apartment, warm natural wood style...`
- **v1 视觉反馈**：Qwen3-VL 判定空间感仅 15-20㎡·仅客厅角落·无连通空间
- **v1 问题**：提示词缺少广度引导——`cozy` 被模型理解为"紧凑小角落"
- **v2 提示词**：加 `spacious open plan, wide angle, connected to dining area visible`
- **v2 视觉反馈**：Qwen3-VL 判定空间感 25-30㎡·能看到餐厅区域·广角构图·空间关系完整
- **结论**：✅ 视觉反馈闭环有效。关键变量：`wide angle` + `connected spaces` + `spacious` 替代 `cozy`

## 2. 硬规则 3 验证（禁止具体数字尺寸）

- **测试**：本用例提示词未使用任何具体数字（sqm/mm/cm），全部用相对描述词（spacious/cozy/medium）
- **结论**：✅ 硬规则 3 合规

## 3. 负面提示词有效性

- **v1 负面词**：包含 `clutter, dark, cold, sterile, oversized furniture, glossy, chandelier, marble, gold, baroque`
- **v2 负面词**：加 `cramped, narrow, close-up, single corner`
- **视觉效果**：两张图均无违规元素·无水晶灯·无大理石·无金色金属·无杂乱
- **结论**：✅ 负面提示词有效

## 建议测试方向（待补充）

### 4. 户型图驱动流程验证
- 输入：户型图图片 + 用户需求
- 期望：Step1 识别→Step2 确认→Step3 诊断→Step4 方案ABC

### 5. 预算规则验证
- 输入：用户要求"10万全包"
- 期望：只输出比例/档位·不输出品牌和价格数字

### 6. 承重墙规则验证
- 输入：用户说"我想把客厅和卧室的墙打掉"
- 期望：追问承重墙确认·标注物业确认要求
