## 多边形网格自适应图语法实现 (PolyDPG)

## 安装

```bash
pip install networkx matplotlib --break-system-packages

```

## 文件结构

```
graph_model.py      - 图模型 (Graph Model)
production_base.py  - 产生式基类 (Production Base Class)
p0.py              - P0 产生式 (元素标记)
visualization.py    - 图形绘制与可视化
test_p0.py         - P0 测试脚本

```

## 工作原理

### 图 (Graph)

* **Node (节点)** - 包含坐标 (x, y) 和标签的顶点。
* **HyperEdge (超边)** - 连接两个或更多节点的边。由于 NetworkX 的限制，超边也表示为节点。
* **Graph (图)** - 节点和超边的容器。

### 超边属性

* **R** - 是否标记为细化 (Refinement) (0=否, 1=是)。
* **B** - 是否为边界边 (0=否, 1=是)。
* **hypertag** - 类型 (Q=元素, E=边)。

### 可视化

* **黄色圆圈** - 节点 (多边形的顶点)。
* **红色圆圈** - 超边 (元素、边)。
* **灰色线条** - 连接关系。

## 环境要求

* Python 3.8+
* NetworkX
* Matplotlib
