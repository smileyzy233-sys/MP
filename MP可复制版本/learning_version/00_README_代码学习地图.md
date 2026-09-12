# MATLAB 量化贸易/跨国生产代码学习地图

## 先看结论：这套程序在做什么

这套代码用 **exact hat algebra（精确帽子代数）** 求政策冲击后的反事实一般均衡。它不是直接重新估计所有水平值，而是求

$$
\hat x=\frac{x'}{x}.
$$

其中 $x$ 是基期，$x'$ 是反事实均衡。`hat=1` 表示没有变化，`hat>1` 表示上升，`hat<1` 表示下降。例如 `hgamma=0.9173` 表示反事实跨国投资成本为基期的 91.73%，即下降 8.27%。代码中以 `h` 开头的变量通常是 hat variable；以 `t` 开头的变量通常是反事实水平量，但这只是本项目的命名习惯，不是 MATLAB 语法。

程序主线是：

```text
基期数据 X_4d 与参数 m
        ↓
校准 alpha、贸易差额 D_mat、劳动收入份额 Omega_E
        ↓
设定贸易成本 htau、跨国投资成本 hgamma、反事实关税 tTar
        ↓
固定点迭代 eqm_iter
        ↓
单次均衡映射 eqm_update：价格 → 份额 → 销售额 → 工资/利润/创新 → 收入/支出
        ↓
比较新旧猜测，阻尼更新，直到 diff < tol
        ↓
反事实均衡与福利分解
```

## 整套学习版的文件

| 顺序 | 学习版文件                                            | 对应原文件                             | 作用                                                         |
| ---: | ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------ |
|    0 | `00_VARIABLE_DICTIONARY.md`                         | MAT 元数据与六个原文件                 | 查变量含义、维度与状态                                       |
|    0 | `00_MATLAB_SYNTAX_FOR_THIS_PROJECT.md`              | 六个原文件，少量例子来自同项目辅助脚本 | 只学本项目实际用到的 MATLAB                                  |
|    0 | `00_EQUATION_CODE_MAPPING.md`                       | 论文式 (16)–(41)                      | 从论文公式跳到变量和代码模块                                 |
|    1 | `01_main_calibration_and_counterfactual_LEARNING.m` | `2.main_cab_innov_extension.m`       | 加载、校准、基期检验、设置政策冲击并调用求解器               |
|    2 | `02_equilibrium_iterator_LEARNING.m`                | `eqm_iter_innov_extension.m`         | 固定点迭代、收敛误差与阻尼                                   |
|    3 | `03_equilibrium_update_LEARNING.m`                  | `eqm_update_innov_extension.m`       | 一次完整的一般均衡更新，是最核心文件                         |
|    4 | `04_mp_only_counterfactual_LEARNING.m`              | `main_cab_innov_extension_mponly.m`  | 只改变 MP 成本的情景及结果整理                               |
|    5 | `05_recompute_equilibrium_LEARNING.m`               | `Recompute_Equ.m`                    | 给定候选均衡变量重新计算关键恒等式，帮助核对                 |
|    6 | `06_welfare_decomposition_LEARNING.m`               | `wel_decomp.m`                       | 产品种类、离岸外包、创新、市场规模、投入产出、劳动再配置分解 |

原文件没有被覆盖；学习版的目标是解释和展开，不是改变模型或修复作者代码。

## 必须先记住的索引和维度

实证数据确认 `m.N=77`、`m.J=20`、`m.JT=19`。文档继续用符号 `N`、`J`，这样同一逻辑也适用于别的数据规模。

### 四维销售额的统一约定

```text
X_4d(m,l,n,j)
第1维 m：母国 / 创新国 / 企业所有权国
第2维 l：生产国 / 东道国
第3维 n：销售目的国 / 消费国
第4维 j：行业
```

因此，`X_4d(m,l,n,j)` 是“母国 `m` 的 `j` 行业企业，在 `l` 国生产并向 `n` 国销售的销售额”。`X_4d`、`notax_X_4d`、`tX_4d`、`notax_tX_4d`、`hxi_4d`、`psi_4d`、`hpsi_4d` 都沿用这个次序。

常见加总可以直接翻译为：

| MATLAB          | 消掉的维度  | 留下的经济对象           |
| --------------- | ----------- | ------------------------ |
| `sum(X_4d,1)` | 母国`m`   | 生产国 × 销售国 × 行业 |
| `sum(X_4d,2)` | 生产国`l` | 母国 × 销售国 × 行业   |
| `sum(X_4d,3)` | 销售国`n` | 母国 × 生产国 × 行业   |
| `sum(X_4d,4)` | 行业`j`   | 母国 × 生产国 × 销售国 |

MATLAB 会保留被加总维度为长度 1，所以代码还会使用 `reshape` 或 `squeeze`。这些操作只改变数组形状，不是新的经济方程。

## 建议学习顺序

### 第一阶段：数组和 hat algebra

先读变量字典与语法教程，只需要掌握：

1. `A(i,j)` 是取元素，`A(:,j)` 是取第 `j` 列；
2. `.*`、`./`、`.^` 是逐元素运算；
3. `sum(A,d)` 沿第 `d` 维加总；
4. `reshape` 改形状、`repmat` 复制、`permute` 换维度顺序、`squeeze` 删除长度为 1 的维度；
5. `hX=1` 是“先猜没有相对变化”，不是“支出水平等于 1”。

第一次阅读可以暂时跳过：校准循环的阻尼细节、所有结果导出、MP 双边变化的事后统计、`A_new` 的四维扩展。

### 第二阶段：读主程序 `01_main...`

目标是回答：数据从哪里来？`m` 中有什么？哪些是理论参数，哪些是政策冲击，哪些是数值算法参数？

重点看：

- `load('temp/impute_X_4d.mat')` 后 `m.X_4d=X_4d`；
- `htau=1`、`hgamma=1`、`tTar=m.tar` 定义“无冲击”基准；
- `alpha_recalib` 与 `D_mat` 的校准循环；
- 调用 `eqm_iter_innov_extension` 的输入与输出顺序。

第一次可以跳过 `Tests` 后用于论文特定情景和 Excel 输出的代码。

### 第三阶段：读迭代器 `02_equilibrium_iterator...`

把它当成数值算法，不要把 `tol=1e-6`、`ww=0.5` 当成经济参数。

```text
old guess r = [hw; hP; hX; hN]
        ↓ 代入均衡方程
new implied value rr = F(r)
        ↓
diff = max(abs(r-rr))
        ↓
new stored guess = ww*rr + (1-ww)*r
```

均衡要求 `r=F(r)`；因此 `diff→0` 表示固定点收敛。阻尼会让收敛更稳，但也可能更慢。

### 第四阶段：精读 `03_equilibrium_update...`

建议分三遍：

1. 第一遍只读每个模块的“经济问题”，忽略长的 `repmat/permute`；
2. 第二遍在纸上写每个数组的维度，逐个检查 `sum(...,d)` 消掉谁；
3. 第三遍对照论文式 (34)–(41)，区分“理论方程”“维度对齐”“数值保护”。

一次更新的顺序是：基期收入和份额 → 冲击后的成本 → 复合成本与价格 → `lambda/psi` → 四维销售额 → 工资与利润 → 研发工资和产品种类 → 家庭收入 → 产品市场出清 → 价格基准化和福利。

第一次可以暂时跳过：`MP_bilat_hat`、`GO_my` 等辅助诊断，`A_new` 的投入产出网络扩展，以及 `isreal` 调试分支。不要跳过 `notax_tX_4d`、`hw_E_new1`、`hPi_new`、`hw_R_new`、`hN_new`、`hY`、`hX_new`。

### 第五阶段：读 `04_mp_only...` 与 `05_recompute...`

`04` 展示怎样把一个理论冲击写进三维政策数组。例如 `hgamma(n,13,j)=0.9` 是“母国/生产国/行业”哪个方向，必须结合 `hxi_4d` 中的维度展开检查，不能只看注释猜测。其后统计代码把四维流量沿不同维度加总。

`05` 是核对工具：给定 `hw,hP,hX,hN`，重算 `hPsi_3d`、`hP_new`、`hlam_3d`、`hpsi_4d` 和 `tX_4d`。它不是完整求解器。

### 第六阶段：读 `06_welfare...`

先理解每个分项是对数变化，再理解其系数。`GNF_vec+GOF_vec+GIF_vec+MS_vec+sec_vec+LR_vec` 是否精确等于总福利，需要在依赖数据齐全时另做数值核对；函数本身未实现该总和检验。

## 如何逐行读复杂数组表达式

遇到下面一类代码时：

```matlab
reshape(sum(sum(notax_X_4d,3),1),[m.N,m.J])
```

按从内到外读：

1. `sum(notax_X_4d,3)`：对销售国 `n` 加总，形状 `[m×l×1×j]`；
2. 再 `sum(...,1)`：对母国 `m` 加总，形状 `[1×l×1×j]`；
3. `reshape(...,[N,J])`：删除两个单例维度，得到“生产国 `l` × 行业 `j`”。

每次都先问“还剩哪些经济索引”，再看数值运算。`repmat/permute` 通常只是把低维参数扩展到同一个索引空间，不能单独解释成经济机制。

## 三类代码要分开看

| 类别             | 典型例子                                 | 解释方式                             |
| ---------------- | ---------------------------------------- | ------------------------------------ |
| A. 理论/经济方程 | `hN_new=(hPi_new./hw_R_new).^m.gammaR` | 利润相对研发工资决定产品种类变化     |
| B. 数组维度操作  | `permute(repmat(...),...)`             | 复制低维对象并把维度放到正确索引位置 |
| C. 数值求解算法  | `ww=0.5`、`max(1e-6,...)`            | 阻尼或数值下界，不是论文结构参数     |

## 当前证据边界与学习提醒

- MAT 元数据已经确认：`X_4d=[77×77×77×20]`；`alpha,beta=[77×20]`；`zeta=[77×20×20]`；`tar=[77×77×20]`；`sigma,theta,rho=[20×1]`。`cab.mat` 的关键求解结果维度也与变量字典所列一致。
- 六个原始文件内部使用的函数名与文件名总体相符，但主脚本仍含作者机器的绝对 `cd` 路径；跨机器运行前需改工作目录或从正确目录启动。这是可移植性问题，不是经济学问题。
- `eqm_update_innov_extension.m` 先执行 `isempty(m.Counter_MP)`。如果结构体没有该字段，MATLAB 会在 `isempty` 之前就报“字段不存在”；当前 `impute_X_4d.mat` 元数据未确认该字段存在。
- `main_cab_innov_extension_mponly.m` 第 42 行接收输出的顺序/数量与 `eqm_iter_innov_extension` 当前函数签名不一致，可能造成变量错位；学习版保留原行为并警示，不能把该调用当成已验证接口。
- `wel_decomp.m` 读取 `m.df`、`m.notax_tX_4d`、`m.notax_X_4d`，但在所审阅六个文件中未见这些字段被写入 `m`。这三个依赖需要调用者补齐。
- `Recompute_Equ.m` 中 `hxi_4d` 对 `hw`、`m.beta`、`hP_int` 的扩展次序与更新函数写法不同；在没有运行时逐元素核对前，不应宣称两者等价。
- 当前文档只完成静态映射与 MAT 尺寸核对，不代表学习版和原版已经完成运行时数值一致性验证。

## 推荐的验收方式

当基期数据和 MATLAB 环境可运行时，分别保存原版与学习版结果，逐项检查：

```matlab
max(abs(hw_original(:)       - hw_learning(:)))
max(abs(hP_original(:)       - hP_learning(:)))
max(abs(hX_original(:)       - hX_learning(:)))
max(abs(hN_original(:)       - hN_learning(:)))
max(abs(tX_4d_original(:)    - tX_4d_learning(:)))
max(abs(hpsi_4d_original(:)  - hpsi_4d_learning(:)))
max(abs(hlam_3d_original(:)  - hlam_3d_learning(:)))
max(abs(hwel_original(:)     - hwel_learning(:)))
```

只有这些差异接近机器误差，并且两边都确实由当前输入重新运行，才能称为“数值等价”。
