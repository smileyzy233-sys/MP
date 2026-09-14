clear
close all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/周老师
%% Current account balance adjustment

load('temp/impute_X_4d.mat') % m：模型参数，1×1 结构体；X_4d：基期四维支出/贸易流，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）
% m.N、m.J：国家数与产业数，均为 1×1 标量（当前为 77、20）；m.tar：双边产业关税率，l×n×j（77×77×20；生产国×销售目的国×产业）
% m.theta、m.rho、m.sigma：产业参数，均为 j×1（20×1）；m.beta：生产国×产业份额，l×j（77×20）；m.alpha：销售目的国×产业最终需求份额，n×j（77×20）；m.zeta：国家×投入产业×产出产业，77×20×20
m.X_4d          = X_4d; % m.X_4d：写入模型结构体的基期四维支出/贸易流，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业）

htau            = ones(m.N,m.N,m.J); % htau：贸易成本的反事实相对变化，l×n×j（77×77×20；生产国×销售目的国×产业）；m.N、m.J 均为 1×1 标量
hgamma          = ones(m.N,m.N,m.J); % hgamma：跨国生产/MP 成本的反事实相对变化，m×l×j（77×77×20；母国/创新国×生产国/东道国×产业）
tTar            = m.tar; % tTar：反事实关税率，l×n×j（77×77×20；生产国×销售目的国×产业），与 m.tar 同维

% innovation input elasticity
m.gammaR        = 0.2; % m.gammaR：创新投入弹性，1×1 标量

% labor supply elasticity
m.zeta_L       	= 2; % m.zeta_L：两类劳动之间的供给弹性，1×1 标量

if 0
    
    % hw：生产国工资相对变化，l×1（77×1）；hP、hX：销售目的国×产业，n×j（77×20）；tX_4d：m×l×n×j（77×77×77×20）
    % hwel：销售目的国福利相对变化，n×1（77×1）；wL、Y、tPi_vec、tR_vec：国家层面结果，均为 77×1
    % hpsi_4d：三边生产份额相对变化，m×l×n×j（77×77×77×20）；hlam_3d：母国×销售目的国×产业，m×n×j（77×77×20）
    [hw, hP, hX, tX_4d, hwel, wL, Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d] = eqm_iter(htau, hgamma, tTar, m);
    
    WZ_hX           = hX; % WZ_hX：保存的产业支出相对变化副本，n×j（77×20；销售目的国×产业），与 hX 同维
    
    m.X_4d          = tX_4d;
    
    save('temp/cab.mat')
    
else

    % Zhou的校准策略，调整alpha使得初始均衡满足
    theta_rho_4d   	= permute(repmat(m.theta./(1-m.rho),[1, m.N, m.N, m.N]),[2,3,4,1]); % theta_rho_4d：产业参数 theta/(1-rho) 的四维扩展，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业）
    
    rho_3d         	= permute(repmat(1-m.rho,[1,m.N,m.N]),[2,3,1]); % rho_3d：产业参数 1-rho 的三维扩展，m×n×j（77×77×20；母国/创新国×销售目的国×产业）
    
    df             	= (m.sigma-1)./(m.theta.*m.sigma); % df：各产业超额利润率，j×1（20×1；产业×1）
    
    dm            	= (m.theta-(m.sigma-1))./(m.theta.*m.sigma); % dm：各产业市场营销支出占产值比率，j×1（20×1；产业×1）
    
    notax_X_4d    	= permute(repmat(1./(1+tTar),[1,1,1,m.N]),[4,1,2,3]).*X_4d; % notax_X_4d：剔除关税后的基期四维支出，m×l×n×j（77×77×77×20；母国×生产国×销售目的国×产业）
    
    Pi            	= repmat(df',[m.N,1]) .* reshape(sum(sum(notax_X_4d,3),2),[m.N, m.J])  ; % Pi：母国—产业超额利润，m×j（77×20；母国/创新国×产业）

    wL_R          	= sum(Pi,2); % wL_R：各母国创新/研发劳动收入，m×1（77×1）

    % wL_agg：各国两类劳动的总收入，国家轴 c×1（77×1）
    wL_agg        	= sum((1-1./repmat(m.sigma',[m.N,1])).*m.beta.*reshape(sum(sum(notax_X_4d,3),1),[m.N, m.J])+...
                   	repmat(dm',[m.N,1]).*reshape(sum(sum(notax_X_4d,2),1),[m.N,m.J])+ ...
                   	repmat(df',[m.N,1]).*reshape(sum(sum(notax_X_4d,3),2),[m.N,m.J]), 2);
    
    m.Omega_E       = (wL_agg - wL_R) ./ wL_agg; % m.Omega_E：生产工人收入占总劳动收入的份额，国家轴 c×1（77×1）
                
    Y              	= wL_agg + sum(reshape(sum(sum(permute(repmat(m.tar./(1+m.tar),[1,1,1,m.N]),[4,1,2,3]).*m.X_4d,2),1),[m.N,m.J]),2); % Y：各销售目的国基期总收入（含关税收入），n×1（77×1）
    
    X_mat_data    	= reshape(sum(sum(m.X_4d,2),1),[m.N, m.J]); % X_mat_data：数据中的销售目的国—产业总支出，n×j（77×20）
    
    % X_mat：由模型方程计算的销售目的国—产业支出，n×j（77×20）
    X_mat         	= m.alpha.*repmat(Y,[1,m.J]) + sum( m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]).*...
                        permute(repmat(reshape(sum(sum(notax_X_4d,3),1),[m.N,m.J]),[1,1,m.J]),[1,3,2]),3 ) ;
    
    % D_mat：各销售目的国经常账户/支出平衡调整项，n×1（77×1）
    D_mat           = sum(( X_mat_data - sum( m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]).*...
                        permute(repmat(reshape(sum(sum(notax_X_4d,3),1),[m.N,m.J]),[1,1,m.J]),[1,3,2]),3 ) ),2);




    I_mat           = Y ; % I_mat：校准迭代中的各销售目的国收入猜测，n×1（77×1）

    loading_fa      = 0.5; % loading_fa：收入校准更新的步长参数，1×1 标量
    
    loading_fa2     = 0.2; % loading_fa2：收入猜测的阻尼权重，1×1 标量


    for ll =1 :1e6 % ll：校准迭代计数器，1×1 标量

        % alpha_recalib：重新校准的最终需求份额，n×j（77×20；销售目的国×产业）
        alpha_recalib   = ( X_mat_data - sum( m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]).*...
                            permute(repmat(reshape(sum(sum(notax_X_4d,3),1),[m.N,m.J]),[1,1,m.J]),[1,3,2]),3 ) )./ repmat(I_mat,[1,m.J]);

        Delta_mat       = (sum(alpha_recalib,2) - 1).*I_mat; % Delta_mat：最终需求份额和偏离 1 对收入的调整量，n×1（77×1）

        I_mat_upate     = I_mat + (1-loading_fa)*Delta_mat; % I_mat_upate：本轮未经二次阻尼的收入更新值，n×1（77×1）

        I_mat           = (1-loading_fa2)*I_mat_upate + loading_fa2*I_mat;

        dist            = norm(Delta_mat); % dist：校准误差范数，1×1 标量

        if dist<1e-8
            break
        end

    end

    D_mat           = I_mat - Y;

    % X_mat_recalib：使用校准份额重构的销售目的国—产业支出，n×j（77×20）
    X_mat_recalib  	= alpha_recalib.*repmat(Y,[1,m.J]) + sum( m.zeta.*permute(repmat(1-1./m.sigma,[1,m.N,m.J]),[2,3,1]).*...
                        permute(repmat(reshape(sum(sum(notax_X_4d,3),1),[m.N,m.J]),[1,1,m.J]),[1,3,2]),3 ) ;
    
    %max(abs(X_mat_recalib(:) - X_mat_data(:)))
    
    m.alpha         = alpha_recalib; % m.alpha：校准后的最终需求支出份额，n×j（77×20；销售目的国×产业）
    
    m.D_mat         = D_mat; % m.D_mat：写入模型结构体的经常账户调整项，n×1（77×1）

     % hN：母国×产业产品种类/创新存量相对变化，m×j（77×20）；wL_E、wL_R、wL_Rt、hw_E_new1：国家层面劳动收入结果，均为 77×1
     % A_new：反事实投入产出系数，第一国别轴×第二国别轴×投入产业 k×产出产业 j（77×77×20×20）；hwl_aggwel1、hwl_Rwel、hwl_Ewel、hw_R_new、hY_notax、hP_tot：均为国家轴×1（77×1）；wnum：1×1 标量
     [hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R,wL_Rt,hw_E_new1,...
          Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d, A_new,hwl_aggwel1,...
          hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax, hP_tot, wnum] = eqm_iter_innov_extension(htau, hgamma, tTar, m); % 输出 Y、tPi_vec、tR_vec、hpsi_4d、hlam_3d 的维度见上方首次说明

    if max(abs(hw(:)-1)) < 1e-8
        disp('校准完成，检测无误')
    end
    
    save('temp/cab.mat')
    
end

%% Tests

% Test for current account balance
load('temp/cab.mat')

htau                = ones(m.N,m.N,m.J);
hgamma              = ones(m.N,m.N,m.J);
tTar                = m.tar;

%% 校准检验程序

% 我先检验贸易份额计算方法是否正确
% 母国从不同产地生产并出口到销售国的份额
psi_4d              = m.X_4d./repmat(sum(m.X_4d,2),[1,m.N,1,1]); % psi_4d：基期三边生产份额，m×l×n×j（77×77×77×20；母国/创新国×生产国/东道国×销售目的国×产业），即 \psi_{i\ell n}^j
% X_3d的不同维度分别对应：母国、销售国、产业  
X_3d                = reshape(sum(m.X_4d,2),[m.N, m.N, m.J]); % X_3d：母国—销售目的国—产业支出，m×n×j（77×77×20），即 X_{in}^j

% lam_3d代表了销售国从不同生产国进口的份额，不同维度分别对应：母国、销售国、产业  
lam_3d              = X_3d ./ repmat(sum(X_3d,1),[m.N, 1, 1]); % lam_3d：基期双边份额，m×n×j（77×77×20；母国×销售目的国×产业），即 \lambda_{in}^j

%那么
Pi_3d               = squeeze(sum( psi_4d .* permute(repmat(lam_3d,[1,1,1,m.N]),[1,4,2,3]), 1)); % Pi_3d：生产国—销售目的国—产业贸易份额，l×n×j（77×77×20）

check_error4        = 1 - squeeze(sum(Pi_3d,1)); % check_error4：按生产国加总后的贸易份额偏差，n×j（77×20；销售目的国×产业）；下一行归约为 1×1 标量范数
check_error4        = norm(check_error4(:));

trshare_alt         = squeeze(sum(m.X_4d,1)) ./  repmat(reshape(squeeze(sum(sum(m.X_4d,1),2)), [1, m.N, m.J]), [m.N, 1, 1, 1]); % trshare_alt：由四维支出直接计算的生产国—销售目的国—产业贸易份额，l×n×j（77×77×20）

mp_3d               = reshape(sum(m.X_4d,3),[m.N, m.N, m.J]); % mp_3d：母国—生产国—产业的跨国生产流量，m×l×j（77×77×20）
tr_3d               = reshape(sum(m.X_4d,1),[m.N, m.N, m.J]); % tr_3d：生产国—销售目的国—产业贸易流量，l×n×j（77×77×20）

mpshare_sim1        = mp_3d./repmat(sum(mp_3d,1),[m.N,1,1]); % mpshare_sim1：跨国生产流量按母国归一化后的份额，m×l×j（77×77×20；母国×生产国×产业）
trshare_sim1        = tr_3d./repmat(sum(tr_3d,1),[m.N,1,1]); % trshare_sim1：贸易流量按生产国归一化后的份额，l×n×j（77×77×20；生产国×销售目的国×产业）

check_error1        = norm(trshare_sim1(:)-trshare_alt(:)); % check_error1：两种贸易份额算法之差的范数，1×1 标量
check_error2        = norm(Pi_3d(:)-trshare_alt(:)); % check_error2：分解贸易份额与直接贸易份额之差的范数，1×1 标量

if check_error1 + check_error2 >1e-10
    error('something wrong')
end


% 我再检验中间品份额计算方法是否正确

check_error3        = 1 - (squeeze( sum( m.zeta, 2) ) + m.beta); % check_error3：中间投入份额与劳动份额加总偏差，l×j（77×20；生产国×产出产业）；下一行归约为 1×1 标量范数

check_error3        = norm(check_error3(:));

if check_error3 >1e-10
    error('something wrong')
end

  [hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R,wL_Rt,hw_E_new1,...
          Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d, A_new,hwl_aggwel1,...
          hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax, hP_tot, wnum] = eqm_iter_innov_extension(htau, hgamma, tTar, m);
%导入MP和TR自由化的数据
clear
close all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/周老师
load('temp/cab.mat') % m：完成校准的模型参数，1×1 结构体；其字段尺寸由 cab.mat 中输入决定
TRlower_RC=0.8787; % TRlower_RC：其余国家到中国的贸易成本下限情景系数，1×1 标量
TRupper_RC=0.8383; % TRupper_RC：其余国家到中国的贸易成本上限情景系数，1×1 标量（本段未使用）
TRlower_CR=0.8787; % TRlower_CR：中国到其余国家的贸易成本下限情景系数，1×1 标量
TRupper_CR=0.8383; % TRupper_CR：中国到其余国家的贸易成本上限情景系数，1×1 标量（本段未使用）

MPlower_CR=0.9720; % MPlower_CR：中国到其余国家的 MP 成本下限情景系数，1×1 标量
MPupper_CR=0.9627; % MPupper_CR：中国到其余国家的 MP 成本上限情景系数，1×1 标量（本段未使用）
MPlower_RC=0.9173; % MPlower_RC：其余国家到中国的 MP 成本下限情景系数，1×1 标量
MPupper_RC=0.8898; % MPupper_RC：其余国家到中国的 MP 成本上限情景系数，1×1 标量（本段未使用）
%% Liberalization in China: Both trade and MP
N=77; % N：国家数量，1×1 标量（当前为 77）
J=20; % J：产业数量，1×1 标量（当前为 20）
JT=19; % JT：参与自由化设定的产业数量，1×1 标量（当前为 19）

htau = ones(m.N,m.N,m.J); % htau：贸易成本的反事实相对变化，l×n×j（77×77×20；生产国×销售目的国×产业）
hgamma = ones(m.N,m.N,m.J); % hgamma：跨国生产/MP 成本的反事实相对变化，m×l×j（77×77×20；母国/创新国×生产国/东道国×产业）
tTar = m.tar; % tTar：反事实关税率，l×n×j（77×77×20；生产国×销售目的国×产业），与 m.tar 同维

%TRADE/MP  Liberalization  CHN13 USA75
for j = 1:JT % j：产业循环索引，1×1 标量
    for n = 1:N % n：国家循环索引，1×1 标量
        htau(n,13,j) =TRlower_RC;  %TRupper_RC(n,1)
       htau(13,n,j) = TRlower_CR; %TRupper_CR(n,1)
  
         hgamma(n,13,j) =MPlower_RC; %MPupper_RC(n,1)
         hgamma(13,n,j) =MPlower_CR; %MPupper_CR(n,1)


    end 
    htau(13,13,j) = 1;  
   hgamma(13,13,j) = 1;
  
end
          % hw：生产国工资相对变化，l×1（77×1）；hP、hX：n×j（77×20）；hN：m×j（77×20）；tX_4d：m×l×n×j（77×77×77×20）
          % hwel、wL_E、wL_R、wL_Rt、hw_E_new1、Y、tPi_vec、tR_vec：国家层面结果，均为 77×1；hpsi_4d：m×l×n×j（77×77×77×20）；hlam_3d：m×n×j（77×77×20）
          % A_new：第一国别轴×第二国别轴×投入产业 k×产出产业 j（77×77×20×20）；hwl_aggwel1、hwl_Rwel、hwl_Ewel、hw_R_new、hY_notax、hP_tot：均为 77×1；wnum：1×1 标量
          [hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R,wL_Rt,hw_E_new1,...
          Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d, A_new,hwl_aggwel1,...
          hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax, hP_tot, wnum] = eqm_iter_innov_extension(htau, hgamma, tTar, m);

save('temp/result_TTMMlower.mat')

%%%%%%%%%
clear
close all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/周老师
load('temp/result_TTMMlower.mat') % 加载上段保存的均衡结果；各变量尺寸与保存时一致
%%%%%福利评估%%%
%term1 总福利变化
term1  =log(hwel) % term1：各国对数总福利变化，国家轴 c×1（77×1）
%term2 总实际工资收入变化
term2  =hwl_aggwel1 % term2：各国总实际劳动收入变化，国家轴 c×1（77×1）
%term3 创新工人实际工资收入变化
term3  =hwl_Rwel % term3：各国创新工人实际收入变化，母国轴 m×1（77×1）
%term4 劳动工人实际工资收入变化
term4  =hwl_Ewel % term4：各国生产工人实际收入变化，生产国轴 l×1（77×1）

result_welfare=[term1 term2 term3 term4] % result_welfare：福利分解结果矩阵，国家轴×4 个福利指标（77×4）
writematrix(result_welfare, 'result/区分创新工人和生产工人的福利.xlsx')
