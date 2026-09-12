function [hw_E_new1,hP_new,hX_new,hN_new,tX_4d,...
          hwel,wL_E,wL_R,wL_Rt,hw_E_new,Y,tPi_vec,...
          tR_vec,hpsi_4d,hlam_3d,A_new,hwl_aggwel1,...
          hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax,hP_tot,...
          hPsi_3d,wnum,hY] = eqm_update_innov_extension(hw_E, hP, hX, hN, htau, hgamma, tTar, m)
% Update the equilibrium outcomes
% 输入变量（基准 N=77、J=20；m=母国/创新国，l=生产国/东道国，n=销售目的国，j=产业，k=来源产业）：
% hw_E：生产工人工资相对变化猜测，l×1（77×1）；hP：价格相对变化猜测，n×j（77×20）；
% hX：支出/销售额相对变化猜测，n×j（77×20）；hN：产品种类数相对变化猜测，m×j（77×20）；
% htau：冰山贸易成本相对变化，l×n×j（77×77×20）；hgamma：多地生产成本冲击，m×l×j（77×77×20）；
% tTar：反事实关税率，l×n×j（77×77×20）；m：模型参数与基期数据结构体，1×1 标量结构体。
% m 中本函数直接使用的主要字段：theta、rho、sigma 为 j×1（20×1）；tar 为 l×n×j（77×77×20）；
% X_4d 为 m×l×n×j（77×77×77×20）；beta 为 l×j（77×20）；alpha 为 n×j（77×20）；
% zeta 为 n×k×j（77×20×20）；D_mat 为 n×1（77×1）；Counter_MP 为 1×1 逻辑量；
% zeta_L、Omega_E 为 1×1 或与国家向量运算相容的参数；gammaR 为 1×1 或与 m×j（77×20）运算相容，具体尺寸由输入结构体决定。
% 输出变量：
% hw_E_new1：生产工人劳动收入相对变化，l×1（77×1）；hP_new：新价格相对变化，n×j（77×20）；
% hX_new：新支出/销售额相对变化，n×j（77×20）；hN_new：新产品种类数相对变化，m×j（77×20）；
% tX_4d：反事实四维销售额，m×l×n×j（77×77×77×20）；hwel：名义收入经消费价格平减后的福利变化，n×1（77×1）；
% wL_E：基期生产工人劳动收入，l×1（77×1）；wL_R：基期研发/创新收入，m×1（77×1）；wL_Rt：反事实研发/创新收入，m×1（77×1）；
% hw_E_new：归一化后的生产工人工资相对变化，l×1（77×1）；Y：含关税收入的基期居民总收入，n×1（77×1）；
% tPi_vec：反事实超额利润，m×1（77×1）；tR_vec：反事实关税收入，n×1（77×1）；
% hpsi_4d：三边生产份额相对变化，m×l×n×j（77×77×77×20）；hlam_3d：双边份额相对变化，m×n×j（77×77×20）；
% A_new：反事实投入产出系数扩展矩阵，l×n×k×j（77×77×20×20）；
% hwl_aggwel1、hwl_Rwel、hwl_Ewel：总劳动、创新工人和生产工人的对数实际收入变化，均为 国家×1（77×1）；
% hw_R_new：研发工资相对变化，m×1（77×1）；hY_notax：不含关税收入的居民收入相对变化，n×1（77×1）；
% hP_tot：居民消费价格指数相对变化，n×1（77×1）；hPsi_3d：复合成本变化，m×n×j（77×77×20）；
% wnum：工资归一化基准，1×1；hY：含关税收入的居民总收入相对变化，n×1（77×1）。
% 该部分构造均衡更新的辅助变量
theta_rho_4d        = permute(repmat(m.theta./(1-m.rho),[1, m.N, m.N, m.N]),[2,3,4,1]); % theta_rho_4d：产业弹性 theta/(1-rho) 的四维扩展，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）

rho_3d              = permute(repmat(1-m.rho,[1,m.N,m.N]),[2,3,1]); % 产业参数 1-rho 的三维扩展，m×n×j（77×77×20）

% 超额利润率,要注意的是，由于弹性只随产业变化，因此维度是产业的
df                  = (m.sigma-1)./(m.theta.*m.sigma); % 产业超额利润率，j×1（20×1）

% 注意，dm可以视为市场营销支出占产值的比率，具体推导参考式（1.23）。该比率的维度和df一样，都是只随产业变化而变化的。
dm                  = (m.theta-(m.sigma-1))./(m.theta.*m.sigma); % 产业营销支出占产值比率，j×1（20×1）

notax_X_4d          = permute(repmat(1./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d; % 剔除关税后的基期四维销售额，m×l×n×j（77×77×77×20）

% 构造数据中的基期工人劳动收入
% wL_E：基期生产工人劳动收入，l×1（77×1）
wL_E              	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J]), 2);

% 构造数据中的基期总劳动收入
% wL_Agg：基期全部劳动要素收入，国家×1（77×1）
wL_Agg            	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J])+ ...
                   	repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]), 2);

% 这里构造超额利润，利润率*税前产值，利润率维度进行调整，使其和母国、产业的产值维度一致。
% 下述超额利润维度是：母国*产业
Pi               	= repmat(df',[m.N,1]) .* reshape(sum(sum(notax_X_4d,3),2),[m.N, m.J])  ; % 基期母国—产业超额利润，m×j（77×20）
                    
wL_R                = sum(Pi,2); % 基期各母国研发/创新收入，m×1（77×1）
% Y                   = wL + sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]),2) +...
%                         sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2);
Y                   = wL_E + wL_R + sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2); % 含关税收入的基期居民总收入，n×1（77×1）

Y_notax             = wL_E + wL_R; % 不含关税收入的基期居民收入，n×1（77×1）
% 注意，原本的X_4d的不同维度分别对应：母国、生产国、销售国、产业                                        
X_mat               = reshape(sum(sum(m.X_4d,2),1),[m.N, m.J]); % 基期销售目的国—产业总支出矩阵，n×j（77×20）

if 0%m.Counter_MP
    psi_4d          = zeros(size(m.X_4d)); % 三边生产份额 psi，m×l×n×j（77×77×77×20）
    for kk = 1:m.N % 国家索引，1×1
        psi_4d(kk,kk,:)     = 1;
    end

else
    psi_4d          = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); %\psi_{i\ell n}^j
end
% X_3d的不同维度分别对应：母国、销售国、产业  
X_3d                = reshape(sum(m.X_4d,2),[m.N, m.N, m.J]); % 母国—销售目的国—产业销售额，m×n×j（77×77×20）

X_2d                = reshape(sum(sum(m.X_4d,2),1),[m.N, m.J]); % 销售目的国—产业总支出，n×j（77×20）

% 构造双边贸易份额（母国和东道国，非中间产地）
lam_3d              = X_3d ./ repmat(sum(X_3d,1),[m.N, 1, 1]); % 母国—销售目的国—产业双边份额 lambda，m×n×j（77×77×20）

% 
%% 均衡更新

% 我首先更新价格等变量集合

hkappa              = htau.*(1+tTar)./(1+m.tar); % 含关税调整的双边贸易成本变化，l×n×j（77×77×20）

hP_int              = reshape(prod(repmat(hP,[1,1,m.J]).^m.zeta,2),[m.N,m.J]); % 生产国的复合中间品价格变化，l×j（77×20；沿来源产业 k 加总）

% It computes hxi_4d = tau_hat*c_hat in our paper, and corresponds to eq(2.1), eq(2.3)
% hxi_4d：贸易成本与单位成本变化的乘积，m×l×n×j（77×77×77×20）
hxi_4d              = permute(repmat(hgamma,[1,1,1,m.N]),[1,2,4,3]).*...
                   	  permute(repmat(hkappa,[1,1,1,m.N]),[4,1,2,3]).*...
                      permute(repmat(hw_E,[1,m.N,m.N,m.J]),[2,1,3,4]).^(permute(repmat(m.beta,[1,1,m.N,m.N]),[3,1,4,2])).*...
                      permute(repmat(hP_int,[1,1,m.N,m.N]),[3,1,4,2]);
% 注意，上述xi的维度是：母国，产地，销售国，产业
                  
% It actually computes \hat Psi^j_{in} which corresponds to eq(2.3) in our paper
% 下述变量本质是进口国n，从母国m进口产品的“复合”价格（多产地）
hPsi_3d              = reshape(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[m.N, m.N, m.J]).^rho_3d; % 母国—销售目的国—产业复合成本变化，m×n×j（77×77×20）

if ~isreal(hPsi_3d)
    aa = 1; % 数值异常调试标记，1×1
end

% 这里调整一下variety相对变化的维度，填入一个虚拟产地维度
hN_re               = repmat( reshape(hN, [m.N, 1, m.J]), [1, m.N, 1] ); % 将产品种类变化扩展到母国—销售目的国—产业，m×n×j（77×77×20）

AUX_P_M             = reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ).^(-1./repmat(m.theta',[m.N, 1])); % 价格更新中的份额加总辅助项，n×j（77×20）
 
% 基于复合成本Psi，可以更新复合部门产品的价格指标相对变化：
% hP_new：更新后的部门价格指数相对变化，n×j（77×20）
hP_new              = ( (repmat(hw_E,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) .* ...
                        reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) ).^(-1./repmat(m.theta',[m.N, 1]));



if ~isreal(hP_new)
    aa = 1;
end

% 上述价格更新完成，接下来更新份额变量

% 首先更新双边份额lambda的相对变化（母国和东道国）
% Note that the relative changes of lambda follows,
% \hat \lambda^j_{in}   = \hat \Psi^j_{in} / ( \sum_k M \Psi^{j\prime}_{kn} / \sum_k M \Psi^{j}_{kn} )
%                       = \hat \Psi^j_{in} / ( \sum \lambda^j_{in} * \hat \Psi^j_{in} )
% Then \hat{lambda}^j_{in} is given by,
%hlam_3d             = hPsi_3d./repmat(sum(lam_3d.*hPsi_3d,1),[m.N,1,1]);
hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]); % 双边份额相对变化，m×n×j（77×77×20）

%sum(hlam_3d1.*lam_3d,1)

%接下来更新三边生产份额psi的相对变化（母国、生产国和东道国）
% computes psi^j_{nlm} in the paper for eq.(2.3)
%Denominator_psi     = repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]);
%Nominator_psi       = hxi_4d.^(-theta_rho_4d);
if isempty(m.Counter_MP)
    m.Counter_MP    = 0;
end

if m.Counter_MP
    hpsi_4d             = ones(size(hxi_4d)); % 三边生产份额相对变化，m×l×n×j（77×77×77×20）
else

    hpsi_4d             = hxi_4d.^(-theta_rho_4d)./repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]);
end
% squeeze(Nominator_psi(:,13,2,2));
% squeeze(Denominator_psi(13,13,2,:));
 squeeze(hpsi_4d(:,13,:,2));
% 
% squeeze(sum(hpsi_4d.*psi_4d,2));
% 基于上述份额变化，计算事后的分配（基于猜测的产值相对变化）
% One can show that:
% X^j_{iln} = \psi^j_{iln} * \lambda^j_{in} * X^j_n
% \hat X^j_{iln} = \hat \psi^j_{iln} * \hat \lambda^j_{in} * \hat X^j_n
% X^{j \prime}_{iln} = X^j_{iln} * \hat X^j_{iln}
% 这一步在利用猜测的X_2d_prime的相对变化计算方程（2.4）右侧的X_4d_prime，并用于更新“新的”X_2d_prime
% tX_4d：反事实销售额，m×l×n×j（77×77×77×20）
tX_4d               = m.X_4d .* hpsi_4d .* permute(repmat(hlam_3d,[1,1,1,m.N]),[1,4,2,3]) .* ...
                    permute(repmat(hX,[1,1,m.N,m.N]),[3,4,1,2]);
         
%squeeze( (mean(MP_bilat_hat(13,:,:,:),2) ) );

%GO_hat    = squeeze(sum(sum(tX_4d,1),3))./squeeze(sum(sum(m.X_4d,1),3));

MP_bilat_hat    = squeeze(sum((tX_4d),3))./squeeze(sum((m.X_4d),3)); % 母国—生产国—产业多地生产额相对变化，m×l×j（77×77×20）

% 需要尝试分解份额变化的集约边际 和 产地产值的规模效应。
tX_allc_4d        	= m.X_4d .* permute(repmat(hX,[1,1,m.N,m.N]),[3,4,1,2]); % 仅含总支出规模效应的反事实销售额，m×l×n×j（77×77×77×20）
 
MPalloc_bilat_hat  	= squeeze(sum((tX_allc_4d),3))./squeeze(sum((m.X_4d),3)); % 多地生产额的规模效应，m×l×j（77×77×20）

tX_ints_4d        	= m.X_4d .* hpsi_4d .* permute(repmat(hlam_3d,[1,1,1,m.N]),[1,4,2,3]); % 仅含份额变化效应的反事实销售额，m×l×n×j（77×77×77×20）

MPshare_bilat_hat  	= squeeze(sum((tX_ints_4d),3))./squeeze(sum((m.X_4d),3)); % 多地生产额的份额效应，m×l×j（77×77×20）

squeeze( (mean(MPshare_bilat_hat(15,:,:,:),2) ) );

squeeze( (mean(hpsi_4d(13,:,:,:),2) ) );

GS_2d               = squeeze(sum(sum(m.X_4d,2),3)); % 基期母国—产业全球销售额，m×j（77×20）

X_prime_2d      	= X_2d .* hX    ; % 反事实销售目的国—产业总支出，n×j（77×20）

psi_prime_4d        = hpsi_4d.* psi_4d; % 反事实三边生产份额，m×l×n×j（77×77×77×20）
                
lam_prime_3d        = hlam_3d.*lam_3d; % 反事实双边份额，m×n×j（77×77×20）

Pi_prime_3d         = squeeze(sum(psi_prime_4d.*permute(repmat(lam_prime_3d,[1,1,1,m.N]),[1,4,2,3]),1)); % 反事实生产国—销售目的国—产业贸易份额，l×n×j（77×77×20）

Pi_3d               = squeeze(sum(psi_4d.*permute(repmat(lam_3d,[1,1,1,m.N]),[1,4,2,3]),1)); % 基期生产国—销售目的国—产业贸易份额，l×n×j（77×77×20）

Pi_hat_3d           = Pi_prime_3d./Pi_3d; % 生产国—销售目的国—产业贸易份额相对变化，l×n×j（77×77×20）

% 检查4d构造的贸易份额是否满足归一化
max(abs(sum(Pi_prime_3d,1)-1));

GO_my               = squeeze(sum(Pi_prime_3d.*permute(repmat(X_2d,[1,1,m.N]),[3,1,2])./(1+tTar),2)); % 固定总支出下的生产国—产业税前产出，l×j（77×20）

GO_prime_my         = squeeze(sum(Pi_prime_3d.*permute(repmat(X_prime_2d,[1,1,m.N]),[3,1,2])./(1+tTar),2)); % 反事实生产国—产业税前产出，l×j（77×20）

GO_hat_my           = GO_prime_my./GO_my; % 生产国—产业税前产出的相对变化，l×j（77×20）

% 
% for ll = 1:m.N
%     hpsi_1d(ll,:) 	= squeeze(sum(hpsi_4d(ll,ll,:,:),3));
% end

%squeeze(hpsi_4d(13,13,:,:))

%补上税，进一步对应到（2.4）式右侧
notax_tX_4d         = permute(repmat(1./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*tX_4d; % 剔除关税后的反事实四维销售额，m×l×n×j（77×77×77×20）
% 注意到，事后的税前产值维度依然是：母国、生产国、销售国、产业，因此税的处理也进行了维度修正（先构造虚拟的母国，实际只有产地和销售地，然后进行旋转，得到一致维度）

%norm( notax_X_4d(:)./notax_tX_4d(:) - 1 )

%更新工资的相对变化，注意(1-1/sigma)*beta对应了论文中的（2.5）式的\tilde{gamma}_L.
gamma_tilde         = (1-1./repmat(m.sigma',[m.N,1])).*m.beta; % 生产劳动需求系数，l×j（77×20）

% 要开始更新"加总"工资了，把需求侧的4d产值加总到2d（产地和产业），然后乘上劳动力的扭曲后的偏好系数
% 再然后加上marketing的劳动需求（其同样处理到2d维度），两类劳动力一起加总得到（产地、产业）的劳动需求，再次沿着产业加总，得到产地维度的劳动需求
% hw_Agg_new：全部劳动要素收入相对变化，国家×1（77×1）
hw_Agg_new         	= (1./wL_Agg) .* sum(  gamma_tilde .* reshape( sum(sum(notax_tX_4d,3),1), [m.N, m.J] )...
                   	+ repmat(dm',[m.N,1]).*reshape(sum(sum(notax_tX_4d,2),1),[m.N,m.J])  ...
                    + repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]) , 2);
% 要注意，利润是母国的，因此计算利润时，我们对产地和销售地进行加总，保留母国维度。

Pit                 = repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]); % 反事实母国—产业超额利润，m×j（77×20）

hX_HC               = reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]) ./ reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]); % 母国—产业税前销售额相对变化，m×j（77×20）

% 更新利润的相对变化，用于后续产品类型相对变化的计算
hPi_new             = Pit./Pi; % 母国—产业超额利润相对变化，m×j（77×20）

% 要开始更新"工人"工资了，把需求侧的4d产值加总到2d（产地和产业），然后乘上劳动力的扭曲后的偏好系数
% 再然后加上marketing的劳动需求（其同样处理到2d维度），两类劳动力一起加总得到（产地、产业）的劳动需求，再次沿着产业加总，得到产地维度的劳动需求
% hw_E_new1：生产工人劳动收入相对变化，l×1（77×1）
hw_E_new1         	= (1./wL_E) .* sum(  gamma_tilde .* reshape( sum(sum(notax_tX_4d,3),1), [m.N, m.J] )...
                   	+  repmat(dm',[m.N,1]).*reshape(sum(sum(notax_tX_4d,2),1),[m.N,m.J]), 2  );

% wL_Et：反事实生产工人劳动收入，l×1（77×1）
wL_Et               = sum(  gamma_tilde .* reshape( sum(sum(notax_tX_4d,3),1), [m.N, m.J] )...
                   	+  repmat(dm',[m.N,1]).*reshape(sum(sum(notax_tX_4d,2),1),[m.N,m.J]), 2  );

% 上述hw_E_new1计算的是工人劳动力收入的相对变化，其工资相对变化需要下述处理：              
hw_E_new            = ( hw_E_new1 ./ ( hw_Agg_new.^(1-m.zeta_L) ) ).^(1./m.zeta_L) ; % 归一化前的生产工人工资相对变化，l×1（77×1）
                
% 基于两类工资收入相对变化，计算研发工资的相对变化：
hw_R_new            = ( (1./(1-m.Omega_E)) .* ( hw_Agg_new.^m.zeta_L - m.Omega_E .* (hw_E_new.^m.zeta_L) ) ).^(1./m.zeta_L); % 研发工资相对变化，m×1（77×1）
                
% 进一步计算产品类型的相对变化
hN_new              = ( hPi_new./hw_R_new ).^( m.gammaR ); % 更新后的产品种类数相对变化，m×j（77×20）

%更新居民总收入的相对变化
%Y                   = wL + sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]),2) +...
%                        sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2);

% 注意到，研发人员的劳动收入w_Rt*L_Rt就是:
wL_Rt               = sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]),2); % 反事实研发/创新收入，m×1（77×1）

% 进口关税收入的转移支付为：
Tariff_transt       = sum(reshape(sum(sum(permute(repmat(tTar./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*tX_4d,2),1),[m.N,m.J]),2); % 反事实进口关税转移收入，n×1（77×1）

% 即超额的经济利润，那么家庭收入的相对变化为：
hY                  = 1./Y.*( hw_E.*wL_E + wL_Rt + Tariff_transt ); % 含关税收入的居民总收入相对变化，n×1（77×1）
hY_notax            = 1./Y_notax.*( hw_E.*wL_E + wL_Rt); % 不含关税收入的居民收入相对变化，n×1（77×1）
%结合总收入相对变化以及猜测的X_4d_prime的计算结果，更新X_2d的相对变化，参见论文（2.4）式  
%同样的，注意到zeta*(1-1/sigma)，这个等价于论文中\tilde{gamma}^{kj}_n
gamma_tilde_M       = m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]); % 中间投入需求系数，n×k×j（77×20×20；销售目的国×来源产业×使用产业）

% hX_new：更新后的销售目的国—产业支出/销售额相对变化，n×j（77×20）
hX_new              = max(1e-6, 1./X_mat.*( m.alpha.*repmat( (hY.*Y + m.D_mat),[1,m.J]) + ...
                   	sum( gamma_tilde_M .* permute(repmat(reshape(sum(sum(notax_tX_4d,3),1),[m.N,m.J]),[1,1,m.J]),[1,3,2]),3 ) ) );

                
GO_new              = reshape(sum(sum(notax_tX_4d,3),1),[m.N,m.J]); % 反事实生产国—产业税前总产出，l×j（77×20）
                  
%% 计算一些辅助输出变量
                  
psi_4d_prime        = (psi_4d.*hpsi_4d); % 反事实三边生产份额，m×l×n×j（77×77×77×20）

lam_3d_prime        = hlam_3d.*lam_3d; % 反事实母国—销售目的国—产业份额，m×n×j（77×77×20）

%这里先计算常规的贸易份额（即产地与销售国之间的贸易份额） \pi^{k}_{i n}
%注意，此时的维度是:产地、销售地、产业
Pi_3d_prime         = squeeze(sum( psi_4d_prime .* permute(repmat(lam_3d_prime,[1,1,1,m.N]),[1,4,2,3]), 1)); % 反事实生产国—销售目的国—产业贸易份额，l×n×k（77×77×20；此处第三轴 k 为投入来源产业）

%然后计算投入产出的系数（产地的I-O系数） gamma^{k j}_n
%注意，此时的维度是:销售地、来源产业、去向产业
Gamma_3d_prime      = m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]); % 反事实投入产出系数，n×k×j（77×20×20；销售目的国×来源产业×使用产业）

%构造辅助拓展的矩阵
Gamma_3d_prime_ext  = repmat( reshape(Gamma_3d_prime, [1, m.N, m.J, m.J]), [m.N, 1, 1, 1] ); % 加入生产国轴的投入产出系数，l×n×k×j（77×77×20×20）

Pi_3d_prime_ext     = repmat( reshape(Pi_3d_prime, [m.N, m.N, m.J, 1]), [1, 1, 1, m.J] ); % 加入使用产业轴的贸易份额，l×n×k×j（77×77×20×20）

A_new               = Gamma_3d_prime_ext .* Pi_3d_prime_ext; % 反事实投入产出系数扩展矩阵，l×n×k×j（77×77×20×20）
                    
hP_tot              = prod(hP.^m.alpha,2); % 销售目的国居民消费价格指数相对变化，n×1（77×1）

wnum                = hw_E_new(1); % 以第一个国家生产工人工资为基准的归一化因子，1×1
hw_E_new           	= hw_E_new/wnum;
hX_new              = hX_new/wnum;
hP_new              = hP_new/wnum;

hwel                = hY./hP_tot; % 含关税名义收入经消费价格平减后的福利变化，n×1（77×1）

%%实际工资变化 hwl_aggwel1= ((hw_E_new1.*wL_E + wL_Rt)./(wL_E+wL_R))./hP_tot

%所有实际收入变化 
hwl_aggwel1=log( ((wL_Et + wL_Rt)./(wL_E+wL_R))./hP_tot ); % 总劳动收入的对数实际变化，国家×1（77×1）
%创新工人实际收入变化
hwl_Rwel   =log( (wL_Rt./wL_R)./hP_tot); % 创新工人收入的对数实际变化，m×1（77×1）
%生产工人实际收入变化
hwl_Ewel   =log(hw_E_new1./hP_tot); % 生产工人收入的对数实际变化，l×1（77×1）
%收入




tPi_vec             = sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]),2); % 反事实各母国超额利润，m×1（77×1）
tR_vec              = sum(reshape(sum(sum(permute(repmat(tTar./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*tX_4d,2),1),[m.N,m.J]),2); % 反事实各销售目的国关税收入，n×1（77×1）

end

