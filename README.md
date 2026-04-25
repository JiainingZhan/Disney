

English summary: This repository contains two portfolio-ready Disney-themed projects: (1) an intelligent park itinerary planner MVP and (2) a Disney IP content recommender, with runnable CLIs, tests, and project documentation.

这个仓库实现了一个可直接展示给面试官的项目组合：

- 主项目：**迪士尼乐园行程智能规划平台（MVP）**
- 小项目：**迪士尼 IP 内容推荐系统**

目标：体现业务理解 + 工程实现能力，支持快速演示与二次扩展。

---

## 目录结构

```text
projects/
  itinerary_planner/
    data.py
    planner.py
    cli.py
  ip_recommender/
    data.py
    recommender.py
    cli.py
tests/
  test_itinerary_planner.py
  test_ip_recommender.py
```

---

## 主项目：迪士尼乐园行程智能规划平台（MVP）

### 已实现能力

- 用户偏好输入（亲子/刺激/拍照）
- 入园时间与可用时长
- 基于排队时间、人流因子、偏好得分的行程自动生成
- 演出（固定开场时间）自动插入行程
- 结果输出为时间轴（timeline）

### 核心思路

- 游乐设施：按“偏好得分 / 预计耗时”计算优先级，贪心选择
- 演出项目：固定时间窗，若时间可达则优先插入
- 最终输出：按时间排序的结构化行程

### 运行演示

```bash
python -m projects.itinerary_planner.cli \
  --family 0.7 --thrill 0.8 --photo 0.4 \
  --start 09:00 --hours 8
```

---

## 小项目：迪士尼 IP 内容推荐系统

### 已实现能力

- 用户输入喜欢的 IP（如 Frozen, Marvel）
- 基于标签重叠与类别匹配的候选打分
- 输出 Top-N 推荐内容（电影/角色/商品/乐园体验）

### 核心思路

- 建立统一标签体系（角色、风格、年龄段、类型等）
- 计算用户喜好标签与候选内容标签重叠得分
- 使用类别轻度加权，避免推荐结果过于单一

### 运行演示

```bash
python -m projects.ip_recommender.cli \
  --likes Frozen Marvel \
  --top-n 5
```

---

## 测试

```bash
python -m unittest discover -s tests -v
```

---

## 面试讲述建议（可直接复用）

- 业务目标：减少游客规划成本，提升游玩效率和体验
- 技术取舍：先做可解释、可复现的规则+评分模型（MVP），后续可升级 ML
- 可量化指标（示例）：行程规划时间下降、偏好命中率提升、推荐点击率提升

---

## 后续可扩展方向

- 接入真实排队与演出 API
- 行程规划从贪心升级为动态规划/启发式搜索
- 推荐系统从标签规则升级为协同过滤/向量召回
- 增加 Web 前端与可视化看板
