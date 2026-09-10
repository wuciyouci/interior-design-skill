#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布局审查脚本 · 校验 Blender 白模是否与设计方案一致

用法：
  方式1（推荐，Blender 内执行）：
    在 Blender MCP 里执行本文件的核心函数，或粘贴执行
  方式2（独立运行）：
    blender --background --python verify_layout.py

方案配置说明（JSON 内置，可按项目修改）：
  - furniture: 家具组 {name, 期望中心, 容差, 最小尺寸}
  - clearances: 间距要求 {between: [组A, 组B], min, axis}
  - 越界检查基于墙体范围自动计算
"""

import json
import sys
from mathutils import Vector

# ================= 方案配置（可修改） =================
PLAN = {
    "name": "20㎡多功能房间·奶油风",
    "room": {"x_min": 0.0, "x_max": 5.0, "y_min": -0.15, "y_max": 4.15},
    "furniture": [
        {"name": "Bed_00",        "label": "床",         "target": [1.45, 1.05], "tol": 0.8,
         "min_size": [1.8, 1.9],  "note": "1.8×2.0 双人床，靠左墙"},
        {"name": "Nightstand_02", "label": "床头柜",     "target": [2.65, 1.05], "tol": 0.4,
         "min_size": None,        "note": "贴床右侧"},
        {"name": "Wardrobe_01",   "label": "衣柜",       "target": [4.35, 3.6],  "tol": 0.8,
         "min_size": None,        "note": "右上角"},
        {"name": "Desk_04",       "label": "书桌+电脑",  "target": [4.35, 1.8],  "tol": 0.8,
         "min_size": None,        "note": "靠右墙，含显示器/椅子",
         "exclude": ["PC_ChairSeat", "PC_ChairBack", "PC_ChairPole"]},  # 椅子在桌前方属正常，不参与间距计算
        {"name": "Sofa_01",       "label": "沙发",       "target": [0.9, 3.4],   "tol": 0.8,
         "min_size": None,        "note": "左下角"},
    ],
    "clearances": [
        {"between": ["Bed_00", "Wardrobe_01"], "min": 0.6, "axis": "x",
         "note": "床侧走道 ≥0.6m (GB 50096)"},
        {"between": ["Bed_00", "Desk_04"],     "min": 0.6, "axis": "x",
         "note": "床右→书桌 ≥0.6m 走道"},
    ],
}

# ================= 核心函数 =================

def get_group_bbox(obj, exclude=None):
    """获取物体组（含子级）的世界包围盒，可排除指定子级"""
    if obj is None:
        return None
    exclude = exclude or []
    all_v = []
    for o in [obj] + list(obj.children):
        if o.name in exclude:
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        all_v.extend(bb)
    if not all_v:
        return None
    mn = Vector(tuple(min(v[i] for v in all_v) for i in range(3)))
    mx = Vector(tuple(max(v[i] for v in all_v) for i in range(3)))
    return mn, mx


def get_room_bounds():
    """从墙体自动计算房间范围"""
    import bpy
    room_v = []
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith('Wall'):
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            room_v.extend(bb)
    if not room_v:
        return None
    return (Vector(tuple(min(v[i] for v in room_v) for i in range(3))),
            Vector(tuple(max(v[i] for v in room_v) for i in range(3))))


def verify(plan=None, verbose=True):
    """执行审查，返回 (通过项数, 总项数, 结果列表)"""
    import bpy
    plan = plan or PLAN
    results = []
    total = 0
    passed = 0

    # 0. 家具存在性
    total += 1
    missing = [f["name"] for f in plan["furniture"] if bpy.data.objects.get(f["name"]) is None]
    if not missing:
        passed += 1
        results.append(("家具存在性", True, "全部存在"))
    else:
        results.append(("家具存在性", False, f"缺失: {missing}"))

    # 1. 各家具位置 + 尺寸
    for f in plan["furniture"]:
        obj = bpy.data.objects.get(f["name"])
        total += 1
        if obj is None:
            results.append((f["label"], False, "物体不存在"))
            continue
        bb = get_group_bbox(obj)
        if bb is None:
            results.append((f["label"], False, "无包围盒"))
            continue
        mn, mx = bb
        center = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2))
        target = Vector(f["target"])
        dist = (center - target).length
        ok = dist <= f["tol"]
        # 尺寸检查（+0.01 容差避免浮点边界误判）
        size_ok = True
        size_str = ""
        if f.get("min_size"):
            w, d = mx.x - mn.x, mx.y - mn.y
            if w + 0.01 < f["min_size"][0] or d + 0.01 < f["min_size"][1]:
                size_ok = False
            size_str = f" 尺寸{w:.2f}x{d:.2f}m (要求≥{f['min_size'][0]}x{f['min_size'][1]})"
        if ok:
            passed += 1
        results.append((f["label"], ok,
                        f"中心({center.x:.2f},{center.y:.2f}) 目标{f['target']} 偏差{dist:.2f}m"))
        if f.get("min_size"):
            total += 1  # 尺寸检查独立计分
            if size_ok:
                passed += 1
            results.append((f"{f['label']}尺寸", size_ok, size_str.strip()))

    # 2. 间距检查（使用家具配置的 exclude）
    f_by_name = {f["name"]: f for f in plan["furniture"]}
    for c in plan["clearances"]:
        total += 1
        fa, fb = f_by_name.get(c["between"][0]), f_by_name.get(c["between"][1])
        bb_a = get_group_bbox(bpy.data.objects.get(c["between"][0]),
                              fa.get("exclude") if fa else None)
        bb_b = get_group_bbox(bpy.data.objects.get(c["between"][1]),
                              fb.get("exclude") if fb else None)
        if bb_a is None or bb_b is None:
            results.append((f"{c['between']} 间距", False, "物体缺失"))
            continue
        axis = c["axis"]
        if axis == "x":
            gap = bb_b[0].x - bb_a[1].x
        else:
            gap = bb_b[0].y - bb_a[1].y
        ok = gap >= c["min"]
        if ok:
            passed += 1
        results.append((f"{c['between'][0]}→{c['between'][1]} 间距",
                        ok, f"{gap:.2f}m (要求≥{c['min']}m) {c.get('note','')}"))

    # 3. 越界检查（所有 MESH 必须在房间内）
    total += 1
    room = get_room_bounds()
    out = []
    if room:
        rmin, rmax = room
        for o in bpy.data.objects:
            if o.type != 'MESH':
                continue
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            for v in bb:
                if (v.x < rmin.x - 0.1 or v.x > rmax.x + 0.1 or
                        v.y < rmin.y - 0.1 or v.y > rmax.y + 0.1):
                    out.append(o.name)
                    break
    ok = not out
    if ok:
        passed += 1
    results.append(("越界检查", ok, f"房间X[{room[0].x:.2f}-{room[1].x:.2f}] Y[{room[0].y:.2f}-{room[1].y:.2f}] "
                                       + ("全部在房间内 ✅" if ok else f"越界: {out[:10]}")))

    # 输出
    if verbose:
        print(f"\n=== 布局审查: {plan['name']} ===")
        for label, ok, detail in results:
            mark = "✅ PASS" if ok else "❌ FAIL"
            print(f"{mark}  {label}: {detail}")
        print(f"\n结果: {passed}/{total} 通过  ({'全部通过' if passed == total else '有 FAIL，需修正'})")

    return passed, total, results


# ================= 入口 =================
if __name__ == "__main__":
    passed, total, _ = verify()
    sys.exit(0 if passed == total else 1)
