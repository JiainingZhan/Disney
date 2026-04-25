# ✨ Disney Project Suite

> Intelligent theme park experience optimizer with modular architecture and extensible design

---

English summary: This repository contains two Disney-themed projects: (1) an intelligent park itinerary planner MVP and (2) a Disney IP content recommender, with runnable CLIs, tests, and extensible architecture.

这个仓库实现了两个 Disney 主题项目：

- 主项目：**迪士尼乐园行程智能规划平台（MVP）**
- 辅项目：**迪士尼 IP 内容推荐系统**

设计目标：模块化架构、可演示的业务逻辑、清晰的测试覆盖。

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

- 游乐设施：按"偏好得分 / 预计耗时"计算优先级，贪心选择
- 演出项目：固定时间窗，若时间可达则优先插入
- 最终输出：按时间排序的结构化行程

### 运行演示

```bash
python -m projects.itinerary_planner.cli \
  --family 0.7 --thrill 0.8 --photo 0.4 \
  --start 09:00 --hours 8
```

---

## 辅项目：迪士尼 IP 内容推荐系统

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

## 业务设计说明

- **行程规划核心价值**：自动化解析用户偏好与时空约束，生成可执行的行程安排
- **技术实现策略**：采用可解释的规则+评分模型（MVP 阶段），便于调试与迭代
- **量化指标示例**：行程生成耗时、偏好匹配度、演出覆盖率

---

## 后续可扩展方向

- 接入真实排队与演出 API
- 行程规划从贪心升级为动态规划/启发式搜索
- 推荐系统从标签规则升级为协同过滤/向量召回
- 增加 Web 前端与可视化看板
