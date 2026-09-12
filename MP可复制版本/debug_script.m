%clear
close all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/周老师
load('temp/cab.mat') % m：完成校准的模型参数，1×1 结构体；X_4d 与 m.X_4d：基期四维支出，均为 m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）
% m.N、m.J：国家数与产业数，均为 1×1 标量（当前为 77、20）；m.tar：双边产业关税率，l×n×j（77×77×20；生产国×销售目的国×产业）
% m.theta、m.rho、m.sigma：产业参数，均为 j×1（20×1）；m.beta：l×j（77×20）；m.alpha：n×j（77×20）；m.zeta：国家×投入产业×产出产业（77×20×20）；m.zeta_L：1×1 标量
TRlower_RC=0.8787; % TRlower_RC：其余国家到中国的贸易成本下限情景系数，1×1 标量（本脚本未使用）
TRupper_RC=0.8383; % TRupper_RC：其余国家到中国的贸易成本上限情景系数，1×1 标量（本脚本未使用）
TRlower_CR=0.8787; % TRlower_CR：中国到其余国家的贸易成本下限情景系数，1×1 标量（本脚本未使用）
TRupper_CR=0.8383; % TRupper_CR：中国到其余国家的贸易成本上限情景系数，1×1 标量（本脚本未使用）

MPlower_CR=0.9720; % MPlower_CR：中国到其余国家的 MP 成本下限情景系数，1×1 标量
MPupper_CR=0.9627; % MPupper_CR：中国到其余国家的 MP 成本上限情景系数，1×1 标量（未使用）
MPlower_RC=0.9173; % MPlower_RC：其余国家到中国的 MP 成本下限情景系数，1×1 标量
MPupper_RC=0.8898; % MPupper_RC：其余国家到中国的 MP 成本上限情景系数，1×1 标量（未使用）
%% Liberalization in China: Both trade and MP
N=77; % N：国家数量，1×1 标量（当前为 77）
J=20; % J：产业数量，1×1 标量（当前为 20）
JT=19; % JT：参与自由化设定的产业数量，1×1 标量（当前为 19）

htau = ones(m.N,m.N,m.J); % htau：贸易成本的反事实相对变化，l×n×j（77×77×20；生产国×销售目的国×产业）
hgamma = ones(m.N,m.N,m.J); % hgamma：跨国生产/MP 成本的反事实相对变化，m×l×j（77×77×20；母国/创新国×生产国/东道国×产业）
tTar = m.tar; % tTar：反事实关税率，l×n×j（77×77×20；生产国×销售目的国×产业），与 m.tar 同维；m.N、m.J 为 1×1 标量

%TRADE/MP  Liberalization  CHN13 USA75
%TRADE/MP  Liberalization  CHN13 USA75
for j = 1:JT % j：产业循环索引，1×1 标量
    for n = 1:N % n：国家循环索引，1×1 标量
        htau(n,13,j) =1;  %TRupper_RC(n,1)
       htau(13,n,j) = 1; %TRupper_CR(n,1)
  
         hgamma(n,13,j) =MPlower_RC; %MPupper_RC(n,1)
         hgamma(13,n,j) =MPlower_CR; %MPupper_CR(n,1)


    end 
    htau(13,13,j) = 1;  
   hgamma(13,13,j) = 1;
  
end

m.gammaR        = 0.2; % m.gammaR：创新投入弹性，1×1 标量


m.Counter_MP    = 1; % m.Counter_MP：关闭 MP 份额调整的反事实开关，1×1 逻辑标量


    % hw：生产国工资相对变化，l×1（77×1）；hP、hX：n×j（77×20）；hN_counter：m×j（77×20）
    % tX_4d：m×l×n×j（77×77×77×20）；hwel_counter、wL_E、wL_R、wL_Rt、hw_E_new1、Y、tPi_vec、tR_vec：国家层面结果，均为 77×1
    % hpsi_4d：m×l×n×j（77×77×77×20）；hlam_3d：m×n×j（77×77×20）；A_coeff：第一国别轴×第二国别轴×投入产业 k×产出产业 j（77×77×20×20）
    % hwl_aggwel1、hwl_Rwel、hwl_Ewel、hw_R_new、hY_notax、hP_tot_counter、hY_counter：国家轴×1（77×1）；wnum：1×1 标量
    [hw, hP, hX, hN_counter, tX_4d, hwel_counter, wL_E,wL_R,...
 wL_Rt,hw_E_new1, Y, tPi_vec, tR_vec, hpsi_4d,...
 hlam_3d, A_coeff,hwl_aggwel1,hwl_Rwel,hwl_Ewel,...
 hw_R_new,hY_notax,hP_tot_counter, wnum, hY_counter] = eqm_iter_innov_extension(htau, hgamma, tTar, m);

m.Counter_MP    = 0;


% hN：基准 MP 机制下的产品种类相对变化，m×j（77×20）；hwel、hP_tot、hY：国家轴×1（77×1）；其余输出维度见上方说明
[hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R,...
 wL_Rt,hw_E_new1, Y, tPi_vec, tR_vec, hpsi_4d,...
 hlam_3d, A_coeff,hwl_aggwel1,hwl_Rwel,hwl_Ewel,...
 hw_R_new,hY_notax,hP_tot, wnum, hY] = eqm_iter_innov_extension(htau, hgamma, tTar, m);


hY_counter(13)

hP_tot_counter(13)

INNOVATION_CHANGES_C_B  = 100*( log(hN_counter(13,:)*m.alpha(13,:)') - log(hN(13,:)*m.alpha(13,:)') ) % INNOVATION_CHANGES_C_B：中国两种 MP 机制间的创新变化差（百分数），1×1 标量


hY(13)

hP_tot(13)

WEL_CHANGES_C_B         = (log(hwel_counter(13)) - log(hwel(13)))*100 % WEL_CHANGES_C_B：中国两种 MP 机制间的福利变化差（百分数），1×1 标量

theta_rho_4d        = permute(repmat(m.theta./(1-m.rho),[1, m.N, m.N, m.N]),[2,3,4,1]); % theta_rho_4d：产业参数 theta/(1-rho) 的四维扩展，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）

rho_3d              = permute(repmat(1-m.rho,[1,m.N,m.N]),[2,3,1]); % rho_3d：产业参数 1-rho 的三维扩展，m×n×j（77×77×20；母国/创新国×销售目的国×产业）

% 超额利润率,要注意的是，由于弹性只随产业变化，因此维度是产业的
df                  = (m.sigma-1)./(m.theta.*m.sigma); % df：各产业超额利润率，j×1（20×1）

% 注意，dm可以视为市场营销支出占产值的比率，具体推导参考式（1.23）。该比率的维度和df一样，都是只随产业变化而变化的。
dm                  = (m.theta-(m.sigma-1))./(m.theta.*m.sigma); % dm：各产业市场营销支出占产值比率，j×1（20×1）

notax_X_4d          = permute(repmat(1./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d; % notax_X_4d：剔除关税后的基期四维支出，m×l×n×j（77×77×77×20）

% 构造数据中的基期工人劳动收入
% wL_E：各生产国工人的基期劳动收入，l×1（77×1）
wL_E              	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J]), 2);

% 构造数据中的基期总劳动收入
% wL_Agg：各国两类劳动的基期总收入，国家轴 c×1（77×1）
wL_Agg            	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J]) + ...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J])+ ...
                   	repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]), 2);

% 这里构造超额利润，利润率*税前产值，利润率维度进行调整，使其和母国、产业的产值维度一致。
% 下述超额利润维度是：母国*产业
Pi               	= repmat(df',[m.N,1]) .* reshape(sum(sum(notax_X_4d,3),2),[m.N, m.J])  ; % Pi：母国—产业超额利润，m×j（77×20）
                    
wL_R                = sum(Pi,2); % wL_R：各母国创新/研发劳动收入，m×1（77×1）
% Y                   = wL + sum(repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]),2) +...
%                         sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2);
Y                   = wL_E + wL_R + sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2); % Y：各销售目的国基期总收入（含关税收入），n×1（77×1）

% 注意，原本的X_4d的不同维度分别对应：母国、生产国、销售国、产业                                        
X_mat               = reshape(sum(sum(m.X_4d,2),1),[m.N, m.J]); % X_mat：销售目的国—产业基期总支出，n×j（77×20）

psi_4d              = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); % psi_4d：基期三边生产份额，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业），即 \psi_{i\ell n}^j

if 0%m.Counter_MP
    psi_4d          = zeros(size(m.X_4d)); %\psi_{i\ell n}^j
    for kk = 1:m.N % kk：国家循环索引，1×1 标量
        psi_4d(kk,kk,:)     = 1;
    end

else
    psi_4d          = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); %\psi_{i\ell n}^j
end

% X_3d的不同维度分别对应：母国、销售国、产业  
X_3d                = reshape(sum(m.X_4d,2),[m.N, m.N, m.J]); % X_3d：母国—销售目的国—产业支出，m×n×j（77×77×20），即 X_{in}^j

% 构造双边贸易份额（母国和东道国，非中间产地）
lam_3d              = X_3d ./ repmat(sum(X_3d,1),[m.N, 1, 1]); % lam_3d：基期双边份额，m×n×j（77×77×20；母国×销售目的国×产业），即 \lambda_{in}^j


hkappa              = htau.*(1+tTar)./(1+m.tar); % hkappa：含关税贸易成本的相对变化，l×n×j（77×77×20；生产国×销售目的国×产业）

%composite intermediate goods price
hP_int              = reshape(prod(repmat(hP,[1,1,m.J]).^m.zeta,2),[m.N,m.J]); % hP_int：复合中间品价格相对变化，l×j（77×20；生产国×产出产业）

% It computes hxi_4d = tau_hat*c_hat in our paper, and corresponds to eq(2.1), eq(2.3)
% hxi_4d：含 MP、贸易、工资和中间品价格的复合成本相对变化，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业）
hxi_4d              = permute(repmat(hgamma,[1,1,1,m.N]),[1,2,4,3]).*...
                   	  permute(repmat(hkappa,[1,1,1,m.N]),[4,1,2,3]).*...
                      permute(repmat(hw,[1,m.N,m.N,m.J]),[2,1,3,4]).^(permute(repmat(m.beta,[1,1,m.N,m.N]),[3,1,4,2])).*...
                      permute(repmat(hP_int,[1,1,m.N,m.N]),[3,1,4,2]);

%psi_4d              = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); %\psi_{i\ell n}^j


hPsi_3d              = reshape(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[m.N, m.N, m.J]).^rho_3d; % hPsi_3d：母国—销售目的国—产业复合成本项相对变化，m×n×j（77×77×20）


% 这里调整一下variety相对变化的维度，填入一个虚拟产地维度
hN_re               = repmat( reshape(hN, [m.N, 1, m.J]), [1, m.N, 1] ); % hN_re：补入销售目的国维度后的产品种类相对变化，m×n×j（77×77×20）

% 基于复合成本Psi，可以更新复合部门产品的价格指标相对变化：
% hP_new：价格指数更新值，n×j（77×20；销售目的国×产业）
hP_new              = ( (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) .* ...
                        reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) ).^(-1./repmat(m.theta',[m.N, 1]));


% hP_tot：最终需求份额加权的居民消费价格指数变化，n×1（77×1）
hP_tot              = prod( hP_new.^(m.alpha), 2);

reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) - ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./ ( (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) )

 ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./  (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) - ...
                        reshape( sum(lam_3d.*hN_re.*hPsi_3d,1), [m.N, m.J] ) 
              
% 上述价格更新完成，接下来更新份额变量

% 首先更新双边份额lambda的相对变化（母国和东道国）
% Note that the relative changes of lambda follows,
% \hat \lambda^j_{in}   = \hat \Psi^j_{in} / ( \sum_k M \Psi^{j\prime}_{kn} / \sum_k M \Psi^{j}_{kn} )
%                       = \hat \Psi^j_{in} / ( \sum \lambda^j_{in} * \hat \Psi^j_{in} )
% Then \hat{lambda}^j_{in} is given by,
%hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]);
hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]); % hlam_3d：双边份额相对变化，m×n×j（77×77×20；母国×销售目的国×产业）

hlam_3d_1             = (hN_re.*1)./repmat(sum(lam_3d.*hN_re.*1,1),[m.N,1,1]); % hlam_3d_1：仅保留产品种类项的双边份额相对变化，m×n×j（77×77×20）
hlam_3d_2             = (1.*hPsi_3d)./repmat(sum(lam_3d.*1.*hPsi_3d,1),[m.N,1,1]); % hlam_3d_2：仅保留复合成本项的双边份额相对变化，m×n×j（77×77×20）

%接下来更新三边生产份额psi的相对变化（母国、生产国和东道国）
% computes psi^j_{nlm} in the paper for eq.(2.3)
if ~m.Counter_MP
    hpsi_4d         = hxi_4d.^(-theta_rho_4d)./repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]); % hpsi_4d：三边生产份额相对变化，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业）
else
    hxi_4d          = ones(size(m.X_4d));
end

% 基于上述份额变化，计算事后的分配（基于猜测的产值相对变化）
% One can show that:
% X^j_{iln} = \psi^j_{iln} * \lambda^j_{in} * X^j_n
% \hat X^j_{iln} = \hat \psi^j_{iln} * \hat \lambda^j_{in} * \hat X^j_n
% X^{j \prime}_{iln} = X^j_{iln} * \hat X^j_{iln}
% 这一步在利用猜测的X_2d_prime的相对变化计算方程（2.4）右侧的X_4d_prime，并用于更新“新的”X_2d_prime
% tX_4d：反事实四维支出，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业）
tX_4d               = m.X_4d .* hpsi_4d .* permute(repmat(hlam_3d,[1,1,1,m.N]),[1,4,2,3]) .* ...
                    permute(repmat(hX,[1,1,m.N,m.N]),[3,4,1,2]);

%补上税，进一步对应到（2.4）式右侧
notax_tX_4d         = permute(repmat(1./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*tX_4d; % notax_tX_4d：剔除关税后的反事实四维支出，m×l×n×j（77×77×77×20）
% 注意到，事后的税前产值维度依然是：母国、生产国、销售国、产业，因此税的处理也进行了维度修正（先构造虚拟的母国，实际只有产地和销售地，然后进行旋转，得到一致维度）

%norm( notax_X_4d(:)./notax_tX_4d(:) - 1 )

%更新工资的相对变化，注意(1-1/sigma)*beta对应了论文中的（2.5）式的\tilde{gamma}_L.
gamma_tilde         = (1-1./repmat(m.sigma',[m.N,1])).*m.beta; % gamma_tilde：生产劳动的收入份额系数，l×j（77×20；生产国×产业）

% 要开始更新"加总"工资了，把需求侧的4d产值加总到2d（产地和产业），然后乘上劳动力的扭曲后的偏好系数
% 再然后加上marketing的劳动需求（其同样处理到2d维度），两类劳动力一起加总得到（产地、产业）的劳动需求，再次沿着产业加总，得到产地维度的劳动需求
% hw_Agg_new：总劳动收入的更新比率，国家轴 c×1（77×1）
hw_Agg_new         	= (1./wL_Agg) .* sum(  gamma_tilde .* reshape( sum(sum(notax_tX_4d,3),1), [m.N, m.J] )...
                   	+ repmat(dm',[m.N,1]).*reshape(sum(sum(notax_tX_4d,2),1),[m.N,m.J])  ...
                    + repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]) , 2);
% 要注意，利润是母国的，因此计算利润时，我们对产地和销售地进行加总，保留母国维度。

Pit                 = repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]); % Pit：反事实母国—产业超额利润，m×j（77×20）
% 更新利润的相对变化，用于后续产品类型相对变化的计算
hPi_new             = Pit./Pi; % hPi_new：母国—产业利润相对变化，m×j（77×20）

% 要开始更新"工人"工资了，把需求侧的4d产值加总到2d（产地和产业），然后乘上劳动力的扭曲后的偏好系数
% 再然后加上marketing的劳动需求（其同样处理到2d维度），两类劳动力一起加总得到（产地、产业）的劳动需求，再次沿着产业加总，得到产地维度的劳动需求
% hw_E_new1：生产工人劳动收入相对变化，l×1（77×1；生产国×1）
hw_E_new1         	= (1./wL_E) .* sum(  gamma_tilde .* reshape( sum(sum(notax_tX_4d,3),1), [m.N, m.J] )...
                   	+  repmat(dm',[m.N,1]).*reshape(sum(sum(notax_tX_4d,2),1),[m.N,m.J]), 2  );

% 上述hw_E_new1计算的是工人劳动力收入的相对变化，其工资相对变化需要下述处理：              
hw_E_new            = ( hw_E_new1 ./ ( hw_Agg_new.^(1-m.zeta_L) ) ).^(1./m.zeta_L) ; % hw_E_new：生产工人工资相对变化，l×1（77×1）

%wnum                = hw_E_new(1);
%hP_new              = hP_new/wnum;  
%hP_new - hP


hlam_3d             = (hN_re.*hPsi_3d)./repmat(sum(lam_3d.*hN_re.*hPsi_3d,1),[m.N,1,1]);

N = m.N; % N：从模型结构体读取的国家数量，1×1 标量（当前为 77）
J = m.J; % J：从模型结构体读取的产业数量，1×1 标量（当前为 20）

AUX_VAR1            = ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./  (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) ; % AUX_VAR1：价格方程隐含的市场规模复合项，n×j（77×20；销售目的国×产业）


Aux_var             = repmat(reshape(( hP_new.^(-repmat(m.theta',[N,1])) .* ( hX./ repmat(hw,[1,J]) ).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) ),[1,N, J]) , [ N, 1 , 1]); % Aux_var：将市场规模复合项扩展至母国维度，m×n×j（77×77×20；母国×销售目的国×产业）

AUX_VAR1            = ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./  (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) ;

%hlam_3d             - (hN_re.*hPsi_3d)./repmat( reshape(AUX_VAR1, [1 , m.N, m.J] ),[m.N,1,1])


%hlam_3d - hN_re .* hPsi_3d ./ Aux_var

hlambda_2d              = nan(N,J); % hlambda_2d：贸易份额相对变化的国内对角项，国家×产业 c×j（77×20）
hlambda_2d1             = nan(N,J); % hlambda_2d1：同一国内对角项的复核副本，国家×产业 c×j（77×20）

for ll = 1:J % ll：产业循环索引，1×1 标量
    hlambda_2d(:,ll)    = diag(hlam_3d(:,:,ll));
end

PsiAUX_4d               = repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]); % PsiAUX_4d：生产份额归一化分母的四维扩展，m×l×n×j（77×77×77×20）

hpsi_2d                  = nan(N,J); % hpsi_2d：三边生产份额相对变化的国内对角项，国家×产业 c×j（77×20）
hPsi_2d                  = nan(N,J); % hPsi_2d：复合成本相对变化的国内对角项，国家×产业 c×j（77×20）
hxi_2d                   = nan(N,J); % hxi_2d：四维复合成本相对变化的全国内对角项，国家×产业 c×j（77×20）

PsiAUX_2d                = nan(N,J); % PsiAUX_2d：生产份额归一化分母的全国内对角项，国家×产业 c×j（77×20）

for ll = 1:N
    hpsi_2d(ll,:)        = squeeze(hpsi_4d(ll,ll,ll,:));
    hlambda_2d1(ll,:)    = squeeze(hlam_3d(ll,ll,:));
    hPsi_2d(ll,:)        = squeeze(hPsi_3d(ll,ll,:));

    hxi_2d(ll,:)        = squeeze(hxi_4d(ll,ll,ll,:));

    PsiAUX_2d(ll,:)           = PsiAUX_4d(ll,ll,ll,:);

end

hP_int              = reshape(prod(repmat(hP,[1,1,m.J]).^m.zeta,2),[m.N,m.J]); % The matrix of intermediate prices: dim1 i, dim2 j

hP_AUX              = squeeze(prod( repmat(hP,[1,1,m.J]).^(-repmat(reshape(m.theta,[1,1,J]),[N,J,1]).*m.zeta), 2 )); % hP_AUX：投入产出价格联结的复合项，国家×产出产业 c×j（77×20）

hc_AUX              = squeeze(prod( repmat(hP,[1,1,m.J]).^(m.zeta), 2 )) .* ( repmat(hw, [1,J]) ).^( m.beta ); % hc_AUX：工资与中间品价格合成的单位成本相对变化，生产国×产业 l×j（77×20）


%( hpsi_2d) -  hc_AUX.^(-squeeze(theta_rho_4d(1,1,:,:))) ./PsiAUX_2d 

%hpsi_4d             - hxi_4d.^(-theta_rho_4d)./repmat(sum(psi_4d.*hxi_4d.^(-theta_rho_4d),2),[1,m.N,1,1]);


%( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) ) - hN./AUX_VAR1 .* hc_AUX.^(-repmat(m.theta',[N,1]))

%( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) ) ./ ( repmat(hw, [1,J]) ).^( -repmat(m.theta',[N,1]).*m.beta ) - ...
%  hN./AUX_VAR1 .* (squeeze(prod( repmat(hP,[1,1,m.J]).^(m.zeta), 2 )) ).^(-repmat(m.theta',[N,1]))

%( repmat(hw, [1,J]) ).^( repmat(m.theta',[N,1]) .* m.beta ) - ...
%    hN./AUX_VAR1 .* hP_AUX ./ ( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) )


% guanjian fangcheng


( repmat(hw, [1,J]) ./ hP_new ).^( repmat(m.theta',[N,1]) .* m.beta ) - ...
    hN./AUX_VAR1 .* ( hP_AUX./ hP_new.^( repmat(m.theta',[N,1]) .* m.beta ) ) ./ ( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) )



hP_new.^(-m.alpha)              - repmat(hw, [1,J]).^(-m.alpha) .* ( hN./AUX_VAR1 .* ( hP_AUX./ hP_new.^( repmat(m.theta',[N,1]) .* m.beta ) ) ...
                                    ./ ( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) ) ).^( m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) );

% hP_C_AUX：福利价格分解方程右端的产业项，国家×产业 c×j（77×20）
hP_C_AUX            = repmat(hw, [1,J]).^(-m.alpha) .* ( hN./AUX_VAR1 .* ( hP_AUX./ hP_new.^( repmat(m.theta',[N,1]) .* m.beta ) ) ...
                                    ./ ( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) ) ).^( m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) );


 %AUX_VAR1            = ( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ./  (repmat(hw,[1,m.J])./hX).^(1-repmat(m.theta'./(m.sigma'-1),[m.N,1])) ;

%hP_new - repmat(hw, [1,J]).*( hN./AUX_VAR1 .* ( hP_AUX./ hP_new.^( repmat(m.theta',[N,1]) .* m.beta ) ) ...
%                                    ./ ( hlambda_2d .* hpsi_2d.^(1- repmat(m.rho',[N,1])) ) ).^( -1 ./ ( repmat(m.theta',[N,1]) .* m.beta ) );



% innovation term

Innov_effects       = hN.^( m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) ); % Innov_effects：创新/产品种类效应，国家×产业 c×j（77×20）

Variety_effects     = hlambda_2d.^( - m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) ); % Variety_effects：国内贸易份额（广延边际）效应，国家×产业 c×j（77×20）

IOLinkage_effects   = ( hP_AUX./ hP_new.^( repmat(m.theta',[N,1]) .* m.beta ) ./( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ).^( m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) ); % IOLinkage_effects：投入产出联结效应，国家×产业 c×j（77×20）

Offshoring_effects  = ( hpsi_2d.^(1- repmat(m.rho',[N,1])) ).^( -m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) ); % Offshoring_effects：离岸生产/外包效应，国家×产业 c×j（77×20）

MktSize_effects     = ( AUX_VAR1./( hP_new.^(-repmat(m.theta',[m.N, 1])) ) ).^( -m.alpha ./ ( repmat(m.theta',[N,1]) .* m.beta ) ); % MktSize_effects：市场规模效应，国家×产业 c×j（77×20）

LabAlloc_effects    = (hY_notax./(hw)); % LabAlloc_effects：劳动收入再配置效应，国家轴 c×1（77×1）

hP_C_AUX./repmat(hw, [1,J]).^(-m.alpha) - Innov_effects.*Variety_effects.*IOLinkage_effects.*Offshoring_effects.*MktSize_effects;

%sum(log(Innov_effects),2) + sum(log(Variety_effects),2) + sum(log(IOLinkage_effects),2) + sum(log(Offshoring_effects),2) + sum(log(MktSize_effects),2)  - sum(log(hP_C_AUX./repmat(hw, [1,J]).^(-m.alpha)),2);
hwel1               = hY_notax./hP_tot; % hwel1：不含关税收入的福利相对变化，国家轴 c×1（77×1）

Decomp_Ptot         = sum(log(Innov_effects),2) + sum(log(Variety_effects),2) + sum(log(IOLinkage_effects),2) + sum(log(Offshoring_effects),2) + sum(log(MktSize_effects),2) + sum(log(repmat(hw, [1,J]).^(-m.alpha) ),2); % Decomp_Ptot：对数总价格/福利分解项之和，国家轴 c×1（77×1）

%Decomp_Ptot  - (-log(hP_tot) );
%log(hY_notax) + Decomp_Ptot - log(hwel1)
%Decomp_Ptot - sum(log(repmat(hw, [1,J]).^(-m.alpha) ),2) + LR_vec - log(hwel1)


sum(log(Innov_effects),2) + sum(log(Variety_effects),2) + sum(log(IOLinkage_effects),2) + sum(log(Offshoring_effects),2) + sum(log(MktSize_effects),2) + log( LabAlloc_effects ) - log(hwel1)


%hP_new  - hP_C_AUX.^(-1./m.alpha)


GNF_mat = ones(m.N,m.J); % GNF_mat：各国各产业广延边际效应的对数贡献，国家×产业 c×j（77×20）
for i = 1:m.N % i：国家循环索引，1×1 标量
    for j = 1:m.J
        GNF_mat(i,j) = -m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*log(hlam_3d(i,i,j));        
    end
end
GNF_vec = sum(GNF_mat,2); % GNF_vec：各国广延边际效应的产业加总，国家轴 c×1（77×1）

GNF_mat1 = ones(m.N,m.J); % GNF_mat1：仅含产品种类渠道的广延边际贡献，国家×产业 c×j（77×20）
for i = 1:m.N
    for j = 1:m.J
        GNF_mat1(i,j) = -m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*log(hlam_3d_1(i,i,j));        
    end
end
GNF_vec1 = sum(GNF_mat1,2); % GNF_vec1：各国产品种类渠道贡献的产业加总，国家轴 c×1（77×1）


GNF_mat2 = ones(m.N,m.J); % GNF_mat2：仅含复合成本渠道的广延边际贡献，国家×产业 c×j（77×20）
for i = 1:m.N
    for j = 1:m.J
        GNF_mat2(i,j) = -m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*log(hlam_3d_2(i,i,j));        
    end
end
GNF_vec2 = sum(GNF_mat2,2); % GNF_vec2：各国复合成本渠道贡献的产业加总，国家轴 c×1（77×1）


norm(GNF_vec-sum(log(Variety_effects),2))

%term2 ok 离岸外包效应
GOF_mat = ones(m.N,m.J); % GOF_mat：各国各产业离岸外包效应的对数贡献，国家×产业 c×j（77×20）
for i = 1:m.N
    for j = 1:m.J
        GOF_mat(i,j) = -m.alpha(i,j)*(1-m.rho(j))/(m.theta(j)*m.beta(i,j))*log(hpsi_4d(i,i,i,j));
    end
end
GOF_vec = sum(GOF_mat,2); % GOF_vec：各国离岸外包效应的产业加总，国家轴 c×1（77×1）
norm(GOF_vec-sum(log(Offshoring_effects),2))

%term3 check？？？ 创新效应
Pit                 = repmat(df',[m.N,1]).*reshape(sum(sum(notax_tX_4d,3),2),[m.N,m.J]);
Pi               	= repmat(df',[m.N,1]) .* reshape(sum(sum(notax_X_4d,3),2),[m.N, m.J])  ;                  
% 更新利润的相对变化，用于后续产品类型相对变化的计算
hPi_new             = Pit./Pi;

hXf = squeeze(sum(sum(tX_4d, 2), 3)) ./squeeze(sum(sum(X_4d, 2), 3)); % hXf：母国—产业总产值相对变化，m×j（77×20）

GIF_mat = ones(m.N,m.J); % GIF_mat：各母国各产业创新效应的对数贡献，m×j（77×20）
for i = 1:m.N
    for j = 1:m.J
        GIF_mat(i,j) = m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*m.gammaR*log(hPi_new(i,j)/hw_R_new(i));        
    end
end
GIF_vec = sum(GIF_mat,2); % GIF_vec：各母国创新效应的产业加总，m×1（77×1）
norm(GIF_vec-sum(log(Innov_effects),2))

%term4 check？？？ 市场规模效应 
MS_mat = ones(m.N, m.J); % MS_mat：各国各产业市场规模效应的对数贡献，国家×产业 c×j（77×20）
for i = 1:m.N
    for j = 1:m.J
         MS_mat(i,j) = m.alpha(i,j)/m.beta(i,j)*((m.theta(j) - (m.sigma(j) - 1)) / (m.theta(j) * (m.sigma(j) - 1)))*log(hX(i,j)/hw(i));
    end
end
MS_vec = sum(MS_mat,2); % MS_vec：各国市场规模效应的产业加总，国家轴 c×1（77×1）
norm(MS_vec-sum(log(MktSize_effects),2))

%term5 ok 投入产出效应 hP_new 还是hP
sec_3d = ones(m.N,m.J,m.J); % sec_3d：国家×来源产业 k×去向产业 j 的投入产出联结贡献，c×k×j（77×20×20）
for i = 1:m.N
    for k = 1:m.J % k：来源产业循环索引，1×1 标量
        for j = 1:m.J
            sec_3d(i,k,j) = -m.alpha(i,j)*m.zeta(i,k,j)/m.beta(i,j)*log(hP_new(i,k)/hP_new(i,j));            
        end
    end
end
sec_vec = sum(sum(sec_3d,3),2); % sec_vec：各国投入产出联结效应的产业加总，国家轴 c×1（77×1）
norm(sec_vec-sum(log(IOLinkage_effects),2) )

% we still need to check hatY_n = hat(1-zeta_N)^(-1/varphi)
%term6 check？？？ 劳动再配置效应
%这里得是收入 不是工资
LabAlloc_effects    = (hY_notax./(hw));
LR_vec=LabAlloc_effects % LR_vec：各国劳动再配置效应，国家轴 c×1（77×1）
gap1 = GNF_vec + GOF_vec + GIF_vec + MS_vec + sec_vec + log(LabAlloc_effects) - log(hwel1); % gap1：福利分解恒等式的国家层面残差，国家轴 c×1（77×1）

disp(max(abs(gap1)))


welfare_dec = [log(hwel1) GNF_vec sec_vec GOF_vec  GIF_vec MS_vec  log(LR_vec) gap1]; % welfare_dec：福利及六项分解与残差汇总，国家轴×8 个指标（77×8）


m.notax_X_4d        = notax_X_4d; % m.notax_X_4d：写入结构体的税前基期四维支出，m×l×n×j（77×77×77×20）
m.df                = df; % m.df：写入结构体的产业超额利润率，j×1（20×1）
m.notax_tX_4d       = notax_tX_4d; % m.notax_tX_4d：写入结构体的税前反事实四维支出，m×l×n×j（77×77×77×20）

% %%check
% [GNF_vec1, GOF_vec1, GIF_vec1, MS_vec1, sec_vec1, LR_vec1] = wel_decomp( hP, hX, hY_notax, hpsi_4d, hlam_3d, hw, hw_E_new1, wL_E, hw_R_new, hXf, m);
% 
% norm(GNF_vec1 - GNF_vec)
% 
% norm(GOF_vec1 - GOF_vec)
% 
% norm(GIF_vec1 - GIF_vec)
% 
% norm(MS_vec1 - MS_vec)
% 
% norm(sec_vec1 - sec_vec)
% 
% norm(LR_vec1 - LR_vec)
% 
