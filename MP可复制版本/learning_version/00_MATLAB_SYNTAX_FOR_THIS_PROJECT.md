# 只为这套模型准备的 MATLAB 小白教程

## 怎么使用

这不是通用教材，只解释本项目实际语法。例子优先来自六个学习对象；`length/find/diag/nan` 在六文件中没有执行例，因此引用同项目辅助脚本的真实行，并明确标记。那些辅助文件不属于本轮改写范围。

## 1. 启动、目录和数据

| 语法 | 项目真实例子 | 作用 |
|---|---|---|
| `clear` | `clear`（`2.main...` 第2行） | 清空工作区变量 |
| `close all` | `close all`（第3行） | 关闭图窗，不删除数据 |
| `clc` | `clc`（第4行） | 清空命令窗口显示 |
| `cd` | `cd /Users/summer2025/...` | 改工作目录；这是作者 Mac 绝对路径，当前机器不可移植 |
| `load` | `load('temp/impute_X_4d.mat')` | 把 MAT 文件顶层变量载入工作区 |
| `save` | `save('temp/cab.mat')` | 把工作区保存到 MAT 文件；未列变量时会保存全部变量 |

已确认 `impute_X_4d.mat` 中 `X_4d=[77×77×77×20]`，结构体 `m` 含 `N,J,alpha,beta,zeta,tar,sigma,theta,rho` 等字段。

## 2. 函数、输入、输出与 `end`

```matlab
function [GNF_vec, GOF_vec, GIF_vec, MS_vec, sec_vec, LR_vec] = ...
    wel_decomp(hP, hX, hY_notax, hpsi_4d, hlam_3d, hw, ...
               hw_E_new1, wL_E, hw_R_new, hXf, m)
```

- 右侧圆括号内是输入，左侧方括号内是输出，二者都严格按位置匹配。
- `main...mponly` 的接收列表与当前 `eqm_iter...` 签名有错位风险；MATLAB 不会按相似变量名自动匹配。
- `end` 分别结束 `function`、`if`、`for` 或 `while`。
- 行末 `...` 表示下一物理行仍属于同一条语句。
- 末尾分号 `;` 抑制显示；无分号会把结果打印到命令窗口。

## 3. 条件与循环

```matlab
if dist < 1e-8
    break
else
    ...
end
```

`if/else` 选择分支，`break` 退出最近一层循环。`if 0` 永远不执行真分支；`if 0%m.Counter_MP` 中 `%` 后是注释，所以仍等同 `if 0`。`~` 表示逻辑非，`&&` 表示标量逻辑且。

```matlab
for j = 1:m.J
    ...
end
```

`j` 依次取 `1,2,...,m.J`。福利分解的多层 `for` 对应国家和行业求和指标。

```matlab
while diff > tol && cc < 10000
```

只要误差大于容差且未到次数上限，就继续固定点迭代。`while` 是数值算法，经济均衡条件是 `r=F(r)`。

## 4. 建数组和查看尺寸

| 函数 | 项目真实例子 | 含义 |
|---|---|---|
| `size` | `size(X_4d)`（`main...mponly` 第49行） | 返回各维长度 |
| `length` | `length(vars_2020)`（同项目 `RCA_DVA.m` 第193行） | 返回最大维长度；多维数组更宜用 `size(A,d)` |
| `ones` | `hP=ones(m.N,m.J)` | 全1；hat 初值1表示先猜无变化 |
| `zeros` | `result_iln=zeros(12,3)` | 全0，常用于预分配 |
| `nan` | `hlambda_2d=nan(N,J)`（同项目 `debug_script.m` 第238行） | 全 `NaN`，标记未填或未定义 |
| `eye` | `mask2d=eye(N)==1` | 单位矩阵，再转成对角逻辑掩码 |
| `diag` | `diag(hlam_3d(:,:,ll))`（同项目 `debug_script.m` 第242行） | 矩阵输入取对角线，向量输入建对角矩阵 |
| `find` | `others=find(countryID~=countryID(i))`（同项目 `RCA_DVA.m` 第64行） | 返回条件为真的索引 |

`NaN` 不是经济学上的结构性零，不能为跑通流程而静默填零。

## 5. `()`、`:`、`[]` 与 `'`

- `hP(i,k)`、`hpsi_4d(i,i,i,j)`：圆括号取元素；MATLAB 索引从1开始。
- `X_4d(:,:,:,1:JT)`：单独 `:` 取整维；`1:JT` 生成整数序列。
- `A(:)`：按 MATLAB 列优先顺序拉成列向量。
- `[term1 term2]` 横向拼接，`[hw(:);hP(:)]` 纵向拼接；`[m.N,m.J]` 也可作为尺寸向量。
- `m.sigma'`：把 `[J×1]` 转为 `[1×J]`。`'` 是共轭转置，实数数据下等同普通转置。

固定点把不同形状拼成一个向量：

```matlab
r  = [hw(:); hP(:); hX(:); hN(:)];
rr = [hw_new(:); hP_new(:); hX_new(:); hN_new(:)];
```

## 6. `*` 与 `.*`、`/` 与 `./`、`^` 与 `.^`

| 运算符 | 含义 | 项目真实例子 |
|---|---|---|
| `*` | 矩阵乘法；标量间也是普通乘法 | `m.theta(j)*m.beta(i,j)`；项目另有行向量乘列向量 `hN(13,:)*m.alpha(13,:)'` |
| `.*` | 对应元素相乘 | `m.X_4d.*hpsi_4d` |
| `/` | 右矩阵除法；标量间是普通除法 | `m.alpha(i,j)/m.beta(i,j)` |
| `./` | 对应元素相除 | `hPi_new=Pit./Pi` |
| `^` | 矩阵幂；标量间是普通幂 | 六文件核心数组没有执行态 `^` 例，不应为凑例子把 `.^` 改成 `^` |
| `.^` | 每个元素分别乘方 | `hxi_4d.^(-theta_rho_4d)` |

经济学上的“每格份额 × 每格销售额”通常用 `.*`，与线性代数矩阵乘法 `*` 不同。

## 7. `sum/prod/mean/max/abs/norm/log`

```matlab
sum(notax_X_4d,3)
```

`sum(A,d)` 沿第 `d` 维加总并把该维保留为长度1。上式消掉销售国 `n`。`sum(sum(notax_X_4d,3),1)` 要从内向外读：先消销售国，再消母国，留下生产国×行业。

```matlab
hP_tot = prod(hP.^m.alpha,2);
```

`prod` 沿行业维连乘，构造 Cobb–Douglas 最终价格指数。`hP_int` 中的 `prod(...,2)` 沿投入行业连乘。

```matlab
mean(hpsi_4d(13,:,:,:),2)
```

`mean` 沿第2维生产国取算术平均；这是更新函数中的诊断表达式，不是核心均衡条件。

```matlab
diff = max(abs(r-rr));
dist = norm(Delta_mat);
```

`abs` 逐项取绝对值，`max` 取最大误差；向量 `norm` 默认给欧氏范数。二者是不同数值误差口径。

```matlab
log(hlam_3d(i,i,j))
```

`log` 是自然对数。小变化时 `100*log(hat)` 近似百分比变化。

## 8. 四个关键维度函数

### `reshape`：改形状，不改元素顺序

```matlab
X_3d = reshape(sum(m.X_4d,2),[m.N,m.N,m.J]);
```

`sum(...,2)` 后是 `[m×1×n×j]`；`reshape` 去掉单例维成为 `[m×n×j]`。元素数必须不变。

### `repmat`：复制

```matlab
repmat(df',[m.N,1])
```

把只随行业变化的 `[1×J]` 利润率复制为 `[N×J]`。复制只是维度匹配，不增加经济异质性。

### `permute`：重新排列维度

```matlab
permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3])
```

`tar=[l×n×j]`，先复制为 `[l×n×j×m]`，再排为 `[m×l×n×j]`，才能逐元素乘 `X_4d`。

### `squeeze`：删除长度为1的维度

```matlab
MP_bilat_hat = squeeze(sum(tX_4d,3))./squeeze(sum(m.X_4d,3));
```

沿销售国加总后为 `[m×l×1×j]`，`squeeze` 得 `[m×l×j]`。若真实维长为1，它可能删得比预期更多；固定接口更适合显式 `reshape`。

## 9. 结构体 `m`

```matlab
m.N
m.J
m.alpha
m.X_4d = X_4d;
```

点号后是字段。读取不存在字段会报错；因此 `isempty(m.Counter_MP)` 不能处理“字段根本不存在”，因为必须先读取字段。学习版可警示，但不能在未授权时改原行为。

## 10. 同时识别 MATLAB 和经济学

```matlab
tX_4d = m.X_4d .* hpsi_4d .* ...
         permute(repmat(hlam_3d,[1,1,1,m.N]),[1,4,2,3]) .* ...
         permute(repmat(hX,[1,1,m.N,m.N]),[3,4,1,2]);
```

`[MATLAB]`：将 `[m×n×j]` 的 `hlam_3d` 和 `[n×j]` 的 `hX` 扩成 `[m×l×n×j]` 后逐元素乘。

`[经济学]`：$X_{mln}^{j\prime}=X_{mln}^j\hat\psi_{mln}^j\hat\lambda_{mn}^j\hat X_n^j$。

## 11. 五个常见误解

1. `ones(...)` 不是经济变量水平等于1，而是 hat 初猜为1。
2. `sum(A,2)` 是沿第2维加总。
3. `reshape` 不做经济加总；真正聚合发生在 `sum`。
4. `A*B` 与 `A.*B` 不可互换。
5. 函数输入输出按位置匹配，不按变量名匹配。
