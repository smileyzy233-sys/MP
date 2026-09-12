% GNF gains from New varieties; GOF gains from offshoring.
% GIF gains from Innovation; MS gains from Market Size.
% LR Labor Reallocation; SEC sectoral input-output effect.
% 索引约定：m=母国/创新国，l=生产国，n=销售目的国，i=福利归属国，j/k=产业；当前 N=77、J=20。
% 变量及维度（均在函数接口首次出现处说明）：
%   hP, hX          销售目的国 n×产业 j 的价格与支出/规模变化（77×20）。
%   hY_notax        福利归属国 i×1 的不含税收入变化（77×1）；hpsi_4d 为 m×l×n×j（77×77×77×20）。
%   hlam_3d         母国 m×销售目的国 n×产业 j 的贸易/品种份额变化（77×77×20）；hw 为国家 i×1（77×1）。
%   hw_E_new1       生产/营销工人工资变化，国家 i×1（77×1）；wL_E 为国家 i×1 的基期收入（77×1；两者当前未使用）。
%   hw_R_new        研发要素工资变化，母国 m×1（77×1）；hXf 为母国 m×产业 j 的企业销售额变化（77×20；当前未使用）。
%   m               模型参数与基期数据结构体，1×1 struct；m.N、m.J 均为 1×1 标量（当前 77、20）。
%   GNF_vec, GOF_vec, GIF_vec, MS_vec, sec_vec, LR_vec 均为福利归属国 i×1（77×1）。
function [GNF_vec, GOF_vec, GIF_vec, MS_vec, sec_vec, LR_vec] = wel_decomp( hP, hX,  hY_notax, hpsi_4d, hlam_3d, hw, hw_E_new1, wL_E, hw_R_new, hXf, m)
% Decomposing the welfare effects
%term1 ok 产品种类效应
% GNF_mat：福利归属国 i×产业 j 的新品种福利贡献（77×20）。
GNF_mat = ones(m.N,m.J);
for i = 1:m.N  % i：福利归属国索引，1×1 标量，取值 1,…,77。
    for j = 1:m.J  % j：产业索引，1×1 标量，取值 1,…,20。
        GNF_mat(i,j) = -m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*log(hlam_3d(i,i,j));        
    end
end
GNF_vec = sum(GNF_mat,2);

%term2 ok 离岸外包效应
% GOF_mat：福利归属国 i×产业 j 的离岸外包福利贡献（77×20）。
GOF_mat = ones(m.N,m.J);
for i = 1:m.N
    for j = 1:m.J
        GOF_mat(i,j) = -m.alpha(i,j)*(1-m.rho(j))/(m.theta(j)*m.beta(i,j))*log(hpsi_4d(i,i,i,j));
    end
end
GOF_vec = sum(GOF_mat,2);


%term3 check？？？ 创新效应
% Pit：反事实情景下按 m.df 加权的母国 m×产业 j 利润（77×20）。
Pit                 = repmat(m.df',[m.N,1]).*reshape(sum(sum(m.notax_tX_4d,3),2),[m.N,m.J]);
% Pi：基准情景下按 m.df 加权的母国 m×产业 j 利润（77×20）。
Pi               	= repmat(m.df',[m.N,1]).*reshape(sum(sum(m.notax_X_4d,3),2),[m.N, m.J])  ;                  
% 更新利润的相对变化，用于后续产品类型相对变化的计算
% hPi_new：母国 m×产业 j 的利润反事实/基准比率（77×20）。
hPi_new             = Pit./Pi;


%Pit1  =repmat(1,[m.N,1]).*reshape(sum(sum(tX_4d,3),2),[m.N,m.J])
%Pi1   =repmat(1,[m.N,1]).*reshape(sum(sum(X_4d,3),2),[m.N, m.J])
%hPi_new1             = Pit1./Pi1;


% GIF_mat：福利归属国 i×产业 j 的创新福利贡献（77×20）。
GIF_mat = ones(m.N,m.J);
for i = 1:m.N
    for j = 1:m.J
           GIF_mat(i,j) = m.alpha(i,j)/(m.theta(j) * m.beta(i,j))*m.gammaR*log(hPi_new(i,j)/hw_R_new(i));        
    end
end
GIF_vec = sum(GIF_mat,2);

%term4 check？？？ 市场规模效应 
% MS_mat：福利归属国 i×产业 j 的市场规模福利贡献（77×20）。
MS_mat = ones(m.N, m.J);
for i = 1:m.N
    for j = 1:m.J
              MS_mat(i,j) = m.alpha(i,j)/m.beta(i,j)*((m.theta(j) - (m.sigma(j) - 1)) / (m.theta(j) * (m.sigma(j) - 1)))*log(hX(i,j)/hw(i));
    end
end
MS_vec = sum(MS_mat,2); 

%term5 ok 投入产出效应
% sec_3d：福利归属国 i×投入产业 k×产出产业 j 的投入产出福利贡献（77×20×20）。
sec_3d = ones(m.N,m.J,m.J);
for i = 1:m.N
    for k = 1:m.J  % k：投入产业索引，1×1 标量，取值 1,…,20。
        for j = 1:m.J
            sec_3d(i,k,j) = -m.alpha(i,j)*m.zeta(i,k,j)/m.beta(i,j)*log(hP(i,k)/hP(i,j));            
        end
    end
end
sec_vec = sum(sum(sec_3d,3),2);

%term6 check？？？ 劳动再配置效应
%这里得是收入 不是工资
LR_vec     = log(hY_notax./(hw));
end


