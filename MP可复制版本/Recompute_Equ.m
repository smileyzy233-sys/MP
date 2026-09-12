% 外部工作区输入（本模型 m.N=77、m.J=20）：m 为模型参数与基期数据结构体，1×1 struct；htau、tTar 为生产国 l×目的国 n×产业 j（77×77×20）；hgamma 为母国 m×生产国 l×产业 j（77×77×20）；hP、hX、hN 为经济体×产业（77×20，其中具体经济体轴随变量经济含义而异）；hw 为生产国 l×1（77×1）。四维流量统一按母国 m×生产国 l×目的国 n×产业 j 排列。
theta_rho_4d        = permute(repmat(m.theta./(1-m.rho),[1, m.N, m.N, m.N]),[2,3,4,1]); % theta_rho_4d：产业参数 theta/(1-rho) 的四维扩展，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）

rho_3d              = permute(repmat(1-m.rho,[1,m.N,m.N]),[2,3,1]); % 部门参数 1-rho 在母国—目的国维度上的扩展；m×n×j（77×77×20）

% 超额利润率,要注意的是，由于弹性只随产业变化，因此维度是产业的
df                  = (m.sigma-1)./(m.theta.*m.sigma); % 部门超额利润率；产业 j×1（20×1，与 m.sigma、m.theta 同维）

% 注意，dm可以视为市场营销支出占产值的比率，具体推导参考式（1.23）。该比率的维度和df一样，都是只随产业变化而变化的。
dm                  = (m.theta-(m.sigma-1))./(m.theta.*m.sigma); % 市场营销支出占产值比率；产业 j×1（20×1，与 df 同维）

notax_X_4d          = permute(repmat(1./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d; % 剔除关税后的基期四维流量；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）

% 构造数据中的基期生产工人劳动收入；wL_E 为经济体×1（77×1）
wL_E              	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J]), 2);

% 构造数据中的基期总劳动收入；wL_Agg 为经济体×1（77×1）
wL_Agg            	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J])+ ...
                   	repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]), 2);

% 这里构造超额利润，利润率*税前产值，利润率维度进行调整，使其和母国、产业的产值维度一致。
% 下述超额利润维度是：母国*产业
Pi               	= repmat(df',[m.N,1]) .* reshape(sum(sum(notax_X_4d,3),2),[m.N, m.J])  ; % 基期母国—产业超额利润；m×j（77×20）
                    
wL_R                = sum(Pi,2); % 各母国超额利润（研发）收入；母国 m×1（77×1）
% Y                   = wL + sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]),2) +...
%                         sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2);
Y                   = wL_E + wL_R + sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2); % 各经济体总收入（劳动收入、利润和关税收入之和）；目的国/经济体 n×1（77×1）

% 注意，原本的X_4d的不同维度分别对应：母国、生产国、销售国、产业                                        
X_mat               = reshape(sum(sum(m.X_4d,2),1),[m.N, m.J]); % 基期目的国—产业总支出；n×j（77×20）

psi_4d              = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); % 三边生产份额 psi_{mln}^j；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）

% X_3d的不同维度分别对应：母国、销售国、产业  
X_3d                = reshape(sum(m.X_4d,2),[m.N, m.N, m.J]); % 基期母国—目的国—产业流量 X_{mn}^j；m×n×j（77×77×20）

% 构造双边贸易份额（母国和东道国，非中间产地）
lam_3d              = X_3d ./ repmat(sum(X_3d,1),[m.N, 1, 1]); % 基期双边贸易份额 lambda_{mn}^j；母国 m×目的国 n×产业 j（77×77×20）


hkappa              = htau.*(1+tTar)./(1+m.tar); % 含关税贸易成本的相对变化；生产国 l×目的国 n×产业 j（77×77×20）

%composite intermediate goods price
hP_int              = reshape(prod(repmat(hP,[1,1,m.J]).^m.zeta,2),[m.N,m.J]); % 复合中间品价格变化；生产国 l×使用产业 j（77×20）

% It computes hxi_4d = tau_hat*c_hat in our paper, and corresponds to eq(2.1), eq(2.3)
% hxi_4d：三边综合成本变化 tau_hat*c_hat；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）
hxi_4d              = permute(repmat(hgamma,[1,1,1,m.N]),[1,2,4,3]).*...
                   	  permute(repmat(hkappa,[1,1,1,m.N]),[4,1,2,3]).*...
                      repmat(hw,[1,m.N,m.N,m.J]).^(permute(repmat(m.beta,[1,1,m.N,m.N]),[1,3,4,2])).*...
                      permute(repmat(hP_int,[1,1,m.N,m.N]),[1,3,4,2]);


psi_4d              = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); % 三边生产份额 psi_{mln}^j；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）


hPsi_3d              = reshape(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[m.N, m.N, m.J]).^rho_3d; % 母国—目的国复合成本指数的相对变化；m×n×j（77×77×20）


% 这里调整一下variety相对变化的维度，填入一个虚拟产地维度
hN_re               = repmat( reshape(hN, [m.N, 1, m.J]), [1, m.N, 1] ); % 在目的国维扩展后的母国产品种类数变化；m×n×j（77×77×20）

% 基于复合成本Psi，可以更新复合部门产品的价格指标相对变化：
% hP_new：更新后的部门价格变化；目的国 n×产业 j（77×20）
hP_new              = ( (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) .* ...
                        reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) ).^(-1./repmat(m.theta',[m.N, 1]));


hP_tot              = prod( hP_new.^(m.alpha), 2); % 各目的国总价格指数变化；目的国 n×1（77×1）

reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) - ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./ ( (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) )

 ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./  (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) - ...
                        reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) ;
              
% 上述价格更新完成，接下来更新份额变量

% 首先更新双边份额lambda的相对变化（母国和东道国）
% Note that the relative changes of lambda follows,
% \hat \lambda^j_{in}   = \hat \Psi^j_{in} / ( \sum_k M \Psi^{j\prime}_{kn} / \sum_k M \Psi^{j}_{kn} )
%                       = \hat \Psi^j_{in} / ( \sum \lambda^j_{in} * \hat \Psi^j_{in} )
% Then \hat{lambda}^j_{in} is given by,
%hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]);
hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]); % 双边贸易份额 lambda 的相对变化；母国 m×目的国 n×产业 j（77×77×20）


%接下来更新三边生产份额psi的相对变化（母国、生产国和东道国）
% computes psi^j_{nlm} in the paper for eq.(2.3)
hpsi_4d             = hxi_4d.^(-theta_rho_4d)./repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]); % 三边生产份额 psi 的相对变化；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）

% 基于上述份额变化，计算事后的分配（基于猜测的产值相对变化）
% One can show that:
% X^j_{iln} = \psi^j_{iln} * \lambda^j_{in} * X^j_n
% \hat X^j_{iln} = \hat \psi^j_{iln} * \hat \lambda^j_{in} * \hat X^j_n
% X^{j \prime}_{iln} = X^j_{iln} * \hat X^j_{iln}
% 这一步在利用猜测的X_2d_prime的相对变化计算方程（2.4）右侧的X_4d_prime，并用于更新“新的”X_2d_prime
% tX_4d：反事实含税四维流量；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）
tX_4d               = m.X_4d .* hpsi_4d .* permute(repmat(hlam_3d,[1,1,1,m.N]),[1,4,2,3]) .* ...
                    permute(repmat(hX,[1,1,m.N,m.N]),[3,4,1,2]);

%补上税，进一步对应到（2.4）式右侧
notax_tX_4d         = permute(repmat(1./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*tX_4d; % 剔除反事实关税后的四维流量；母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）
