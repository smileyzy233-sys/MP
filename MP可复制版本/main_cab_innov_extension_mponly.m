
%导入MP和TR自由化的数据
clear
close all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/周老师
load('temp/cab.mat') % m：模型参数与基期数据结构体，1×1 struct；X_4d：基期四维流量，母国 m×生产国 l×目的国 n×产业 j（77×77×77×20）
TRlower_RC=0.8787;% 从其他国家到中国的贸易成本下降下限；标量（1×1）
TRupper_RC=0.8383;% 从其他国家到中国的贸易成本下降上限；标量（1×1，本脚本未用于计算）
TRlower_CR=0.8787;% 从中国到其他国家的贸易成本下降下限；标量（1×1）
TRupper_CR=0.8383;% 从中国到其他国家的贸易成本下降上限；标量（1×1，本脚本未用于计算）

MPlower_CR=0.9720;% 从中国到其他国家的 MP 成本下降下限；标量（1×1）
MPupper_CR=0.9627;% 从中国到其他国家的 MP 成本下降上限；标量（1×1，本脚本未用于计算）
MPlower_RC=0.9173;% 从其他国家到中国的 MP 成本下降下限；标量（1×1）
MPupper_RC=0.8898;% 从其他国家到中国的 MP 成本下降上限；标量（1×1，本脚本未用于计算）
%% Liberalization in China: Both trade and MP
N=77; % 经济体数量；标量（1×1）
J=20; % 原始产业数量；标量（1×1）
JT=19; % 后续结果汇总保留的产业数量；标量（1×1）

htau = ones(m.N,m.N,m.J); % 双边贸易成本的反事实相对变化；生产国 l×目的国 n×产业 j（77×77×20）
hgamma = ones(m.N,m.N,m.J); % 双边 MP 成本的反事实相对变化；母国 m×生产国 l×产业 j（77×77×20）
tTar = m.tar; % 反事实关税率；生产国 l×目的国 n×产业 j（77×77×20，与 m.tar 同维）

%TRADE/MP  Liberalization  CHN13 USA75
for j = 3:JT % j：产业索引；标量（1×1，取值 3:19）
    for n = 1:N % n：经济体索引；标量（1×1，取值 1:77）
        htau(n,13,j) =1;  %TRupper_RC(n,1)
       htau(13,n,j) = 1; %TRupper_CR(n,1)
  
         hgamma(n,13,j) =0.9; %MPupper_RC(n,1)
         hgamma(13,n,j) =1; %新增


    end 
    htau(13,13,j) = 1;  
   hgamma(13,13,j) = 1;
  
end

% 前八个输出：hw 为生产国工资变化，l×1（77×1）；hP、hX 分别为目的国价格与支出变化，n×j（77×20）；hN 为母国产品种类数变化，m×j（77×20）；tX_4d 为反事实流量，m×l×n×j（77×77×77×20）；hwel 为目的国福利变化，n×1（77×1）；wL_E 为生产国基期生产工人收入，l×1（77×1）；wL_R 为母国基期研发收入，m×1（77×1）。
% 接口提示：当前 eqm_iter_innov_extension 在第 9、10 位新增了 wL_Rt 和 hw_E_new1，本调用未同步增加接收变量，故第 9 项起按当前函数实际位置依次绑定如下。
% 实际错位绑定及具体维度：Y←wL_Rt（反事实研发收入，m×1（77×1））；tPi_vec←hw_E_new1（生产工人收入变化，l×1（77×1））；tR_vec←Y（基期总收入，n×1（77×1））；hpsi_4d←tPi_vec（反事实利润，m×1（77×1））；hlam_3d←tR_vec（反事实关税收入，n×1（77×1））；A_coeff←hpsi_4d（三边生产份额变化，m×l×n×j（77×77×77×20））；hwl_aggwel1←hlam_3d（双边份额变化，m×n×j（77×77×20））；hwl_Rwel←A_new（投入产出系数扩展矩阵，l×n×k×j（77×77×20×20），k=来源产业）；hwl_Ewel←hwl_aggwel1（国家×1（77×1））；hw_R_new←hwl_Rwel（m×1（77×1））；hY_notax←hwl_Ewel（l×1（77×1））；hP_tot←hw_R_new（m×1（77×1））。
[hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R, Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d, A_coeff,hwl_aggwel1,hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax,hP_tot] = eqm_iter_innov_extension(htau, hgamma, tTar, m);


%%%%计算中国作为i的变化
N=77; % 经济体数量；标量（1×1）
J=20; % 截取前的产业数量；标量（1×1）
JT=19; % 截取后的产业数量；标量（1×1）
size(X_4d)

X_4d=X_4d(:,:,:,1:JT) % 截取产业后的基期四维流量；母国 m×生产国 l×目的国 n×产业 j（77×77×77×19）
tX_4d=tX_4d(:,:,:,1:JT) % 截取产业后的反事实四维流量；母国 m×生产国 l×目的国 n×产业 j（77×77×77×19）
size(X_4d)

m.J=JT % 将结构体内产业数量改为 19；标量（1×1）
J=JT % 当前产业数量；标量（1×1，值为 19）

%预处理  这里的做法是把本国-本国的设定为0
mask2d = eye(N)==1; % 同一经济体配对元素的逻辑掩码；经济体×经济体（77×77）
mask3d = repmat(mask2d, [1, 1, J]); % 按产业复制的同一经济体配对掩码；经济体×经济体×产业 j（77×77×19）
% 加总i
X_lnj =squeeze(sum(X_4d,1)) % 基期流量对母国 m 维加总；生产国 l×目的国 n×产业 j（77×77×19）
X_lnj(mask3d) = 0 
tX_lnj =squeeze(sum(tX_4d,1)) % 反事实流量对母国 m 维加总；生产国 l×目的国 n×产业 j（77×77×19）
tX_lnj(mask3d) = 0
%加总n
X_inj=squeeze(sum(X_4d,2)); % 基期流量对生产国 l 维加总；母国 m×目的国 n×产业 j（77×77×19）
X_inj(mask3d) = 0
tX_inj=squeeze(sum(tX_4d,2)); % 反事实流量对生产国 l 维加总；母国 m×目的国 n×产业 j（77×77×19）
tX_inj(mask3d) = 0
% 加总n
X_ilj =squeeze(sum(X_4d,3)) % 基期流量对目的国 n 维加总；母国 m×生产国 l×产业 j（77×77×19）
X_ilj(mask3d) = 0
tX_ilj =squeeze(sum(tX_4d,3)) % 反事实流量对目的国 n 维加总；母国 m×生产国 l×产业 j（77×77×19）
tX_ilj(mask3d) = 0


result_iln=zeros(12,3); % 汇总结果表；指标×结果列（12×3）
%%%%%%%%%%%%1.作为母国i加总变化%%%%i%%%%%%%%
%%%X_ij
X_ij  = reshape(squeeze(sum(X_ilj,2)),[N,J]); % 基期母国—产业总流量；母国 m×产业 j（77×19）
tX_ij = reshape(squeeze(sum(tX_ilj,2)),[N,J]); % 反事实母国—产业总流量；母国 m×产业 j（77×19）
%1.整体  这里是1-20行业 其实不太合理就加制造业 3-19
AS = [9 32 41 43 50 51 58 65 69 75] % 选定经济体编号；经济体编号序列（1×10）
ind_all = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]; % 纳入汇总的制造业产业编号；产业编号序列（1×17）

change_Xi=sum(tX_ij(:,ind_all)-X_ij(:,ind_all),2)./sum(X_ij(:,ind_all),2) % 各母国制造业总流量的相对变化；母国 m×1（77×1）
result_iln(1,1)=change_Xi(13,1)*100; %中国
disp(result_iln(1,1))
