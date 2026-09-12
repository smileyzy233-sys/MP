close all
clear all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/复刻DVA
%读取数据
%77经济体 45个部门=3465
z2020=xlsread('2020_SML.xlsx','2020_SML','B2:ECH3466');% 2020 年中间投入产出矩阵；供给方 country×sector 堆叠单元 r×使用方 country×sector 堆叠单元 q（3465×3465，即 77×45 对 77×45）
F2020=xlsread('2020_SML.xlsx','2020_SML','ECI2:EUB3466');% 2020 年最终需求；供给方 country×sector 堆叠单元 r ×（目的经济体 country×6 类最终用途）（3465×462=3465×(77×6)）
y2020=xlsread('2020_SML.xlsx','2020_SML','EUC2:EUC3466');% 2020 年总产出；country×sector 堆叠单元 r ×1（3465×1）
v2020=xlsread('2020_SML.xlsx','2020_SML','B3467:ECH3468');% 2020 年增加值投入；增加值类别×country×sector 堆叠单元 r（2×3465）
vv2020=sum(v2020,1) % 2020 年各 country×sector 单元增加值合计；1×堆叠单元 r（1×3465）
save(['mat2020.mat'],'z2020','F2020','y2020','vv2020');

%中国13 美国74
close all
clear all
clc
cd /Users/summer2025/Desktop/2024新论文/MP论文2024/最新版结果77/复刻DVA
load 'mat2020.mat'

%%%需要哪些数据：直接消耗系数A 总产出X 增加值：X-sum(A,2).*X 最终使用（区分国别）X-sum(A,1).*X

J=77; % 经济体数量（此独立脚本以 J 表示 country 数，而非主模型产业数）；标量（1×1）
S=45; % 每个经济体的部门数量；标量（1×1）
JS=J*S; % country×sector 堆叠单元总数（77×45=3465）；标量（1×1）
FF2020=zeros(JS,J) % 合并六类最终用途后的 2020 年最终需求；供给方 country×sector 堆叠单元 r ×目的经济体 country（3465×77）
for i=1:size(F2020,1) % i：供给方 country×sector 堆叠单元 r 的行索引；标量（1×1，取值 1:3465）
    for j=1:6:(size(F2020,2)-5) % j：某目的经济体六类最终用途的起始列索引；标量（1×1，取值 1,7,...,457）
        FF2020(i, ceil((j-1)/6)+1)=sum(F2020(i, j:j+5));
    end
end
check=y2020-sum(z2020,2)-sum(FF2020,2) ; % country×sector 单元供需平衡核对残差；堆叠单元 r×1（3465×1）


XXi=z2020; % 当前年份中间投入产出矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
FFdi=FF2020; % 当前年份最终需求；供给方堆叠单元 r×目的经济体 country（3465×77）
YY=y2020; % 当前年份总产出；country×sector 堆叠单元 r×1（3465×1）
VV=vv2020; % 当前年份增加值；1×country×sector 堆叠单元 r（1×3465）
vas=VV./YY' % 各 country×sector 单元增加值率；1×堆叠单元 r（1×3465）
 vas(find(isnan(vas)))=0.000001;
 
Vhat=diag(vas);  % 增加值率对角矩阵；堆叠单元 r×堆叠单元 r（3465×3465）
I=eye(J*S); % country×sector 堆叠空间的单位矩阵；堆叠单元 r×堆叠单元 r（3465×3465）

%%投入系数矩阵
 YY1=repmat(YY,1,JS); % 按列复制的总产出矩阵；供给方堆叠单元 r×复制列 q（3465×3465）
A=XXi./YY1'; % 直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
    A(find(isnan(A)))=0;
    A(A == inf) = 0; 
%%投入系数矩阵
%对角线国家国内元素提取
A_in=zeros(JS,JS); % 仅保留各经济体国内 45×45 投入块的直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
for i=1:J %% i：经济体 country 索引；标量（1×1，取值 1:77）
A_in([S*(i-1)+1:S*i],[S*(i-1)+1:S*i])=A([S*(i-1)+1:S*i],[S*(i-1)+1:S*i]);
end
A_out=A-A_in; % 跨境直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）

%%%%%%%%%%%出口%%%%%%%%%%%%%%%
% 为每个行业单元赋国家编号（重复每个国家S次）
countryID = repelem((1:J)', S);  % 每个 country×sector 堆叠单元所属的经济体编号；堆叠单元 r×1（3465×1）
EXPO = zeros(JS, 1); % 各 country×sector 单元的中间品出口；堆叠单元 r×1（3465×1）
%中间品
for i = 1:JS
    others = find(countryID ~= countryID(i)); % 外国使用方的 country×sector 堆叠索引；(3465-45)×1（3420×1）
    EXPO(i) = EXPO(i) + sum(XXi(i, others));
end
%最终品
EXPF = zeros(JS, 1); % 各 country×sector 单元的最终品出口；堆叠单元 r×1（3465×1）
for i = 1:JS
    for j = 1:J  % j 表示目的地国家
        if countryID(i) ~= j
            EXPF(i) = EXPF(i) + FFdi(i, j);
        end
    end
end
 

%加总
EXP=EXPO+EXPF;  % 各 country×sector 单元总出口；堆叠单元 r×1（3465×1）
e_ir=EXP ; % RCA 计算中的 country×sector 出口额；堆叠单元 r×1（3465×1）
%出口总值
EXP_all=sum(EXP,1) % 世界出口总额；标量（1×1）
%各国出口总值
export_mat = reshape(EXP, S, J);  % 按部门×经济体重排的出口矩阵；sector×country（45×77）
country_export = sum(export_mat, 1)'; % 各经济体出口总额；country×1（77×1）
%%%%%%%%%%%出口%%%%%%%%%%%%

%%%%%计算DVA
L=I/(I-A_in); % 国内投入关联的 Leontief 逆矩阵；来源堆叠单元 r×使用堆叠单元 q（3465×3465）
L1=pinv(I-A_in); % 用广义逆计算的 Leontief 逆矩阵（核对/备用）；来源堆叠单元 r×使用堆叠单元 q（3465×3465）
DVA=Vhat*L*diag(EXP) % 各来源 country×sector 单元对各出口单元的国内增加值贡献；来源堆叠单元 r×出口堆叠单元 q（3465×3465）

%%%%%%%%%DVA_F%%%%%%%
DVA_F=Vhat*L*EXP  % 前向关联口径的国内增加值出口；来源 country×sector 堆叠单元 r×1（3465×1）
%%%%%%%%%DVA_B%%%%%%%
DVA_B=vas*L*diag(EXP) % 后向关联口径的国内增加值出口；1×出口 country×sector 堆叠单元 q（1×3465）

%%%%%%%%%%%%%%%%%%%%%%%%CVA （7）%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%DVA_B./EXP%%%%
dvas_ir=DVA_B'./e_ir   % country×sector 出口的国内增加值率；堆叠单元 r×1（3465×1）
  dvas_ir(find(isnan(dvas_ir)))=0;
  dvas_ir(dvas_ir == inf) = 0;
  %（6）计算 dva_s_r
%国家层面的总值 （6-1） 
DVA_B_gj = repelem(sum(reshape(DVA_B, S, J), 1)', S); % 各经济体 DVA_B 总额复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
e_ir_gj = repelem(sum(reshape(e_ir, S, J), 1)', S); % 各经济体出口总额复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
dvas_r=DVA_B_gj./e_ir_gj % 经济体层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
%行业层面的总值 （6-2）
DVA_B_hy = repmat(sum(reshape(DVA_B, S, J), 2), J, 1); % 各部门全球 DVA_B 总额复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
e_ir_hy = repmat(sum(reshape(e_ir, S, J), 2), J, 1); % 各部门全球出口总额复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
dvas_i=DVA_B_hy./e_ir_hy % 部门层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
%世界层面的总值  国家行业加总 （6-3）
DVA_B_all=repmat(sum(DVA_B,2),JS,1); % 世界 DVA_B 总额复制向量；country×sector 堆叠单元 r×1（3465×1）
e_ir_all=repmat(sum(e_ir',2),JS,1); % 世界出口总额复制向量；country×sector 堆叠单元 r×1（3465×1）
dvas=DVA_B_all./e_ir_all; % 世界层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
dvas_check = sum(DVA_B) / sum(e_ir); % 世界国内增加值率核对值；标量（1×1）
%%%%%%%%%计算CVA_ir%%%%%%%%%%%%%%%（7）
CVA_ir=(dvas_ir./dvas_r)./(dvas_i./dvas) % country×sector 国内增加值率比较优势指数；堆叠单元 r×1（3465×1）
  CVA_ir(find(isnan(CVA_ir)))=0;
  CVA_ir(CVA_ir== inf) = 0;
%中国13 美国74  到这里了

%%%%%求dir_bi  dir_fi
dirdva_ir=vas.*EXP' % country×sector 直接国内增加值出口；1×堆叠单元 r（1×3465）
dir_bir=dirdva_ir./DVA_B % 后向口径直接增加值占比；1×出口堆叠单元 r（1×3465）
dir_fir=dirdva_ir./DVA_F' % 前向口径直接增加值占比；1×来源堆叠单元 r（1×3465）

%%%%%%%%%%%%%%%%%%%%%%%%Cd_b_ir (10)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  dir_bir(find(isnan(dir_bir)))=0;
  dir_bir(dir_bir== inf) = 0;
%dir_br 国家层面的总值    根据（8）式来的
DVA_B_gj = repelem(sum(reshape(DVA_B, S, J), 1)', S);          %分母
dirdva_ir_gj = repelem(sum(reshape(dirdva_ir, S, J), 1)', S); % 各经济体直接增加值出口复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
dir_br=dirdva_ir_gj./DVA_B_gj % 经济体层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_bi 行业层面的总值    根据（8）式来的
DVA_B_hy = repmat(sum(reshape(DVA_B, S, J), 2), J, 1);         %分母
dirdva_ir_hy = repmat(sum(reshape(dirdva_ir, S, J), 2), J, 1); % 各部门全球直接增加值出口复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
dir_bi =dirdva_ir_hy./DVA_B_hy % 部门层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_b 世界层面的总值  国家行业加总 
DVA_B_all=repmat(sum(DVA_B,2),JS,1);  %分母
dirdva_ir_all=repmat(sum(dirdva_ir,2),JS,1); % 世界直接增加值出口总额复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_b=dirdva_ir_all./DVA_B_all; % 世界层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_b_check = sum(dirdva_ir) / sum(DVA_B); % 世界后向直接增加值占比核对值；标量（1×1）
%%%%%%%%%计算Cd_b_ir%%%%%%%%%%%%%%%（10）
Cd_b_ir=(dir_bir'./dir_br)./(dir_bi./dir_b) % 后向直接增加值占比的比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_b_ir(find(isnan(Cd_b_ir)))=0;
Cd_b_ir(Cd_b_ir== inf) = 0;

%%%%%%%%%%%%%%%%%%%%%%%%Cd_f_ir (11)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  dir_fir(find(isnan(dir_fir)))=0;
  dir_fir(dir_fir== inf) = 0;
%dir_fr 国家层面的总值    根据（9）式来的
DVA_F_gj = repelem(sum(reshape(DVA_F', S, J), 1)', S); % 各经济体 DVA_F 总额复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_gj = repelem(sum(reshape(dirdva_ir, S, J), 1)', S);  %分子
dir_fr=dirdva_ir_gj./DVA_F_gj % 经济体层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_fi 行业层面的总值    根据（9）式来的
DVA_F_hy = repmat(sum(reshape(DVA_F', S, J), 2), J, 1); % 各部门全球 DVA_F 总额复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_hy = repmat(sum(reshape(dirdva_ir, S, J), 2), J, 1); %分子
dir_fi =dirdva_ir_hy./DVA_F_hy % 部门层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_f 世界层面的总值  国家行业加总 
DVA_F_all=repmat(sum(DVA_F',2),JS,1); % 世界 DVA_F 总额复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_all=repmat(sum(dirdva_ir,2),JS,1);   %分子
dir_f=dirdva_ir_all./DVA_F_all; % 世界层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_f_check = sum(dirdva_ir) / sum(DVA_F); % 世界前向直接增加值占比核对值；标量（1×1）
%%%%%%%%%计算Cd_f_ir%%%%%%%%%%%%%%%（11）
Cd_f_ir=(dir_fir'./dir_fr)./(dir_fi./dir_f) % 前向直接增加值占比的比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_f_ir(find(isnan(Cd_f_ir)))=0;
Cd_f_ir(Cd_f_ir== inf) = 0;

%%%%%%%%%%%%(3)RCA_G基于增加值测算的RCA%%%%%%%%%e_ir
RCA_G=(e_ir./e_ir_gj)./(e_ir_hy./e_ir_all); % 基于总出口的显示性比较优势指数；country×sector 堆叠单元 r×1（3465×1）
%%%%%%%%%%%%(4)RCA_VA基于增加值测算的RCA%%%%%%%%%DVA_F
RCA_VA=(DVA_F./DVA_F_gj)./(DVA_F_hy./DVA_F_all); % 基于国内增加值出口的显示性比较优势指数；country×sector 堆叠单元 r×1（3465×1）

%%%%%%%%%%%%%核对%%%%%%%%%
check=RCA_VA-(RCA_G.*CVA_ir.*Cd_b_ir./Cd_f_ir) % RCA 恒等式逐 country×sector 单元核对残差；堆叠单元 r×1（3465×1）
max_err = max(abs(check)); % RCA 恒等式核对的最大绝对误差；标量（1×1）
disp(max_err)
% 给变量加上年份后缀
Cd_b_ir_2020 = Cd_b_ir; % 2020 年后向直接增加值占比比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_f_ir_2020 = Cd_f_ir; % 2020 年前向直接增加值占比比较优势分项；country×sector 堆叠单元 r×1（3465×1）
CVA_ir_2020  = CVA_ir; % 2020 年国内增加值率比较优势指数；country×sector 堆叠单元 r×1（3465×1）
RCA_G_2020   = RCA_G; % 2020 年总出口 RCA；country×sector 堆叠单元 r×1（3465×1）
RCA_VA_2020  = RCA_VA; % 2020 年增加值出口 RCA；country×sector 堆叠单元 r×1（3465×1）
e_ir_2020    = e_ir; % 2020 年 country×sector 出口额；堆叠单元 r×1（3465×1）
DVA_F_2020   = DVA_F; % 2020 年前向国内增加值出口；来源堆叠单元 r×1（3465×1）
DVA_B_2020   = DVA_B; % 2020 年后向国内增加值出口；1×出口堆叠单元 r（1×3465）
% vars_2020：待执行缺失值、无穷值、零值和负值检查的变量名；变量列表（1×8 cell）
vars_2020 = { ...
    'Cd_b_ir_2020','Cd_f_ir_2020','CVA_ir_2020', ...
    'RCA_G_2020','RCA_VA_2020','e_ir_2020', ...
    'DVA_F_2020','DVA_B_2020'};

for k = 1:length(vars_2020) % k：待检查变量列表索引；标量（1×1，取值 1:8）
    v = eval(vars_2020{k}); % 当前接受检查的数值变量；堆叠单元 r×1（3465×1），唯 DVA_B_2020 为 1×堆叠单元 r（1×3465）
    fprintf('%s: NaN=%d, Inf=%d, Zero=%d, Neg=%d\n', vars_2020{k}, ...
        sum(isnan(v)), sum(isinf(v)), sum(v==0), sum(v<0));
end
% 保存到带年份的文件
save('result_2020.mat', ...
    'Cd_b_ir_2020', 'Cd_f_ir_2020', 'CVA_ir_2020', 'RCA_G_2020', ...
    'RCA_VA_2020', 'e_ir_2020', 'DVA_F_2020', 'DVA_B_2020');


%%%%%%%1995
close all
clear all
clc
cd C:\Users\ZHR\OneDrive\Desktop\代码核对
%读取数据
%77经济体 45个部门=3465
z1995=xlsread('1995_SML.xlsx','1995_SML','B2:ECH3466');% 1995 年中间投入产出矩阵；供给方 country×sector 堆叠单元 r×使用方 country×sector 堆叠单元 q（3465×3465，即 77×45 对 77×45）
F1995=xlsread('1995_SML.xlsx','1995_SML','ECI2:EUB3466');% 1995 年最终需求；供给方 country×sector 堆叠单元 r×（目的经济体 country×6 类最终用途）（3465×462）
y1995=xlsread('1995_SML.xlsx','1995_SML','EUC2:EUC3466');% 1995 年总产出；country×sector 堆叠单元 r×1（3465×1）
v1995=xlsread('1995_SML.xlsx','1995_SML','B3467:ECH3468');% 1995 年增加值投入；增加值类别×country×sector 堆叠单元 r（2×3465）
vv1995=sum(v1995,1) % 1995 年各 country×sector 单元增加值合计；1×堆叠单元 r（1×3465）
save(['mat1995.mat'],'z1995','F1995','y1995','vv1995');

%中国13 美国74
close all
clear all
clc
cd C:\Users\ZHR\OneDrive\Desktop\代码核对
load 'mat1995.mat'
J=77; % 经济体数量（此独立脚本以 J 表示 country 数）；标量（1×1）
S=45; % 每个经济体的部门数量；标量（1×1）
JS=J*S; % country×sector 堆叠单元总数（77×45=3465）；标量（1×1）
FF1995=zeros(JS,J) % 合并六类最终用途后的 1995 年最终需求；供给方 country×sector 堆叠单元 r×目的经济体 country（3465×77）
for i=1:size(F1995,1) % i：供给方 country×sector 堆叠单元 r 的行索引；标量（1×1，取值 1:3465）
    for j=1:6:(size(F1995,2)-5) % j：某目的经济体六类最终用途的起始列索引；标量（1×1，取值 1,7,...,457）
        FF1995(i, ceil((j-1)/6)+1)=sum(F1995(i, j:j+5));
    end
end
check=y1995-sum(z1995,2)-sum(FF1995,2) ; % country×sector 单元供需平衡核对残差；堆叠单元 r×1（3465×1）


XXi=z1995; % 当前年份中间投入产出矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
FFdi=FF1995; % 当前年份最终需求；供给方堆叠单元 r×目的经济体 country（3465×77）
YY=y1995; % 当前年份总产出；country×sector 堆叠单元 r×1（3465×1）
VV=vv1995; % 当前年份增加值；1×country×sector 堆叠单元 r（1×3465）
vas=VV./YY' % 各 country×sector 单元增加值率；1×堆叠单元 r（1×3465）
 vas(find(isnan(vas)))=0.000001;
 
Vhat=diag(vas);  % 增加值率对角矩阵；堆叠单元 r×堆叠单元 r（3465×3465）
I=eye(J*S); % country×sector 堆叠空间的单位矩阵；堆叠单元 r×堆叠单元 r（3465×3465）

%%投入系数矩阵
 YY1=repmat(YY,1,JS); % 按列复制的总产出矩阵；供给方堆叠单元 r×复制列 q（3465×3465）
A=XXi./YY1'; % 直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
    A(find(isnan(A)))=0;
    A(A == inf) = 0; 
%%投入系数矩阵
%对角线国家国内元素提取
A_in=zeros(JS,JS); % 仅保留各经济体国内 45×45 投入块的直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）
for i=1:J %% i：经济体 country 索引；标量（1×1，取值 1:77）
A_in([S*(i-1)+1:S*i],[S*(i-1)+1:S*i])=A([S*(i-1)+1:S*i],[S*(i-1)+1:S*i]);
end
A_out=A-A_in; % 跨境直接消耗系数矩阵；供给方堆叠单元 r×使用方堆叠单元 q（3465×3465）

%%%%%%%%%%%出口%%%%%%%%%%%%%%%
% 为每个行业单元赋国家编号（重复每个国家S次）
countryID = repelem((1:J)', S);  % 每个 country×sector 堆叠单元所属的经济体编号；堆叠单元 r×1（3465×1）
EXPO = zeros(JS, 1); % 各 country×sector 单元的中间品出口；堆叠单元 r×1（3465×1）
%中间品
for i = 1:JS
    others = find(countryID ~= countryID(i)); % 外国使用方的 country×sector 堆叠索引；外国堆叠单元 q×1（3420×1）
    EXPO(i) = EXPO(i) + sum(XXi(i, others));
end
%最终品
EXPF = zeros(JS, 1); % 各 country×sector 单元的最终品出口；堆叠单元 r×1（3465×1）
for i = 1:JS
    for j = 1:J  % j 表示目的地国家
        if countryID(i) ~= j
            EXPF(i) = EXPF(i) + FFdi(i, j);
        end
    end
end
 

%加总
EXP=EXPO+EXPF;  % 各 country×sector 单元总出口；堆叠单元 r×1（3465×1）
e_ir=EXP ; % RCA 计算中的 country×sector 出口额；堆叠单元 r×1（3465×1）
%出口总值
EXP_all=sum(EXP,1) % 世界出口总额；标量（1×1）
%各国出口总值
export_mat = reshape(EXP, S, J);  % 按部门×经济体重排的出口矩阵；sector×country（45×77）
country_export = sum(export_mat, 1)';      % 各经济体出口总额；country×1（77×1）
%%%%%%%%%%%出口%%%%%%%%%%%%

%%%%%计算DVA
L=I/(I-A_in); % 国内投入关联的 Leontief 逆矩阵；来源堆叠单元 r×使用堆叠单元 q（3465×3465）
L1=pinv(I-A_in); % 用广义逆计算的 Leontief 逆矩阵（核对/备用）；来源堆叠单元 r×使用堆叠单元 q（3465×3465）
DVA=Vhat*L*diag(EXP) % 各来源 country×sector 单元对各出口单元的国内增加值贡献；来源堆叠单元 r×出口堆叠单元 q（3465×3465）

%%%%%%%%%DVA_F%%%%%%%
DVA_F=Vhat*L*EXP  % 前向关联口径的国内增加值出口；来源 country×sector 堆叠单元 r×1（3465×1）
%%%%%%%%%DVA_B%%%%%%%
DVA_B=vas*L*diag(EXP) % 后向关联口径的国内增加值出口；1×出口 country×sector 堆叠单元 q（1×3465）

%%%%%%%%%%%%%%%%%%%%%%%%CVA （7）%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%DVA_B./EXP%%%%
dvas_ir=DVA_B'./e_ir   % country×sector 出口的国内增加值率；堆叠单元 r×1（3465×1）
  dvas_ir(find(isnan(dvas_ir)))=0;
  dvas_ir(dvas_ir == inf) = 0;
  %（6）计算 dva_s_r
%国家层面的总值 （6-1） 
DVA_B_gj = repelem(sum(reshape(DVA_B, S, J), 1)', S); % 各经济体 DVA_B 总额复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
e_ir_gj = repelem(sum(reshape(e_ir, S, J), 1)', S); % 各经济体出口总额复制至其 45 个部门；country×sector 堆叠单元 r×1（3465×1）
dvas_r=DVA_B_gj./e_ir_gj % 经济体层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
%行业层面的总值 （6-2）
DVA_B_hy = repmat(sum(reshape(DVA_B, S, J), 2), J, 1); % 各部门全球 DVA_B 总额复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
e_ir_hy = repmat(sum(reshape(e_ir, S, J), 2), J, 1); % 各部门全球出口总额复制至 77 个经济体；country×sector 堆叠单元 r×1（3465×1）
dvas_i=DVA_B_hy./e_ir_hy % 部门层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
%世界层面的总值  国家行业加总 （6-3）
DVA_B_all=repmat(sum(DVA_B,2),JS,1); % 世界 DVA_B 总额复制向量；country×sector 堆叠单元 r×1（3465×1）
e_ir_all=repmat(sum(e_ir',2),JS,1); % 世界出口总额复制向量；country×sector 堆叠单元 r×1（3465×1）
dvas=DVA_B_all./e_ir_all; % 世界层面国内增加值率复制向量；country×sector 堆叠单元 r×1（3465×1）
dvas_check = sum(DVA_B) / sum(e_ir); % 世界国内增加值率核对值；标量（1×1）
%%%%%%%%%计算CVA_ir%%%%%%%%%%%%%%%（7）
CVA_ir=(dvas_ir./dvas_r)./(dvas_i./dvas) % country×sector 国内增加值率比较优势指数；堆叠单元 r×1（3465×1）
  CVA_ir(find(isnan(CVA_ir)))=0;
  CVA_ir(CVA_ir== inf) = 0;
%中国13 美国74  到这里了

%%%%%求dir_bi  dir_fi
dirdva_ir=vas.*EXP' % country×sector 直接国内增加值出口；1×堆叠单元 r（1×3465）
dir_bir=dirdva_ir./DVA_B    % 后向口径直接增加值占比；1×出口堆叠单元 r（1×3465）
dir_fir=dirdva_ir./DVA_F'  % 前向口径直接增加值占比；1×来源堆叠单元 r（1×3465）

%%%%%%%%%%%%%%%%%%%%%%%%Cd_b_ir (10)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  dir_bir(find(isnan(dir_bir)))=0;
  dir_bir(dir_bir== inf) = 0;
%dir_br 国家层面的总值    根据（8）式来的
DVA_B_gj = repelem(sum(reshape(DVA_B, S, J), 1)', S);          % 国家层面 DVA_B 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_gj = repelem(sum(reshape(dirdva_ir, S, J), 1)', S);  % 国家层面直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_br=dirdva_ir_gj./DVA_B_gj % 经济体层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_bi 行业层面的总值    根据（8）式来的
DVA_B_hy = repmat(sum(reshape(DVA_B, S, J), 2), J, 1);         % 部门层面 DVA_B 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_hy = repmat(sum(reshape(dirdva_ir, S, J), 2), J, 1); % 部门层面直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_bi =dirdva_ir_hy./DVA_B_hy % 部门层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_b 世界层面的总值  国家行业加总 
DVA_B_all=repmat(sum(DVA_B,2),JS,1);  % 世界 DVA_B 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_all=repmat(sum(dirdva_ir,2),JS,1);   % 世界直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_b=dirdva_ir_all./DVA_B_all; % 世界层面后向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_b_check = sum(dirdva_ir) / sum(DVA_B); % 世界后向直接增加值占比核对值；标量（1×1）
%%%%%%%%%计算Cd_b_ir%%%%%%%%%%%%%%%（10）
Cd_b_ir=(dir_bir'./dir_br)./(dir_bi./dir_b) % 后向直接增加值占比的比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_b_ir(find(isnan(Cd_b_ir)))=0;
Cd_b_ir(Cd_b_ir== inf) = 0;

%%%%%%%%%%%%%%%%%%%%%%%%Cd_f_ir (11)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  dir_fir(find(isnan(dir_fir)))=0;
  dir_fir(dir_fir== inf) = 0;
%dir_fr 国家层面的总值    根据（9）式来的
DVA_F_gj = repelem(sum(reshape(DVA_F', S, J), 1)', S);          % 国家层面 DVA_F 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_gj = repelem(sum(reshape(dirdva_ir, S, J), 1)', S);  % 国家层面直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_fr=dirdva_ir_gj./DVA_F_gj % 经济体层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_fi 行业层面的总值    根据（9）式来的
DVA_F_hy = repmat(sum(reshape(DVA_F', S, J), 2), J, 1);         % 部门层面 DVA_F 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_hy = repmat(sum(reshape(dirdva_ir, S, J), 2), J, 1); % 部门层面直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_fi =dirdva_ir_hy./DVA_F_hy % 部门层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
%dir_f 世界层面的总值  国家行业加总 
DVA_F_all=repmat(sum(DVA_F',2),JS,1);  % 世界 DVA_F 分母复制向量；country×sector 堆叠单元 r×1（3465×1）
dirdva_ir_all=repmat(sum(dirdva_ir,2),JS,1);   % 世界直接增加值分子复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_f=dirdva_ir_all./DVA_F_all; % 世界层面前向直接增加值占比复制向量；country×sector 堆叠单元 r×1（3465×1）
dir_f_check = sum(dirdva_ir) / sum(DVA_F); % 世界前向直接增加值占比核对值；标量（1×1）
%%%%%%%%%计算Cd_f_ir%%%%%%%%%%%%%%%（11）
Cd_f_ir=(dir_fir'./dir_fr)./(dir_fi./dir_f) % 前向直接增加值占比的比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_f_ir(find(isnan(Cd_f_ir)))=0;
Cd_f_ir(Cd_f_ir== inf) = 0;

%%%%%%%%%%%%(3)RCA_G基于增加值测算的RCA%%%%%%%%%e_ir
RCA_G=(e_ir./e_ir_gj)./(e_ir_hy./e_ir_all); % 基于总出口的显示性比较优势指数；country×sector 堆叠单元 r×1（3465×1）
%%%%%%%%%%%%(4)RCA_VA基于增加值测算的RCA%%%%%%%%%DVA_F
RCA_VA=(DVA_F./DVA_F_gj)./(DVA_F_hy./DVA_F_all); % 基于国内增加值出口的显示性比较优势指数；country×sector 堆叠单元 r×1（3465×1）

%%%%%%%%%%%%%核对%%%%%%%%%
check=RCA_VA-(RCA_G.*CVA_ir.*Cd_b_ir./Cd_f_ir) % RCA 恒等式逐 country×sector 单元核对残差；堆叠单元 r×1（3465×1）
max_err = max(abs(check)); % RCA 恒等式核对的最大绝对误差；标量（1×1）
disp(max_err)
% 给变量加上年份后缀
Cd_b_ir_1995 = Cd_b_ir; % 1995 年后向直接增加值占比比较优势分项；country×sector 堆叠单元 r×1（3465×1）
Cd_f_ir_1995 = Cd_f_ir; % 1995 年前向直接增加值占比比较优势分项；country×sector 堆叠单元 r×1（3465×1）
CVA_ir_1995  = CVA_ir; % 1995 年国内增加值率比较优势指数；country×sector 堆叠单元 r×1（3465×1）
RCA_G_1995   = RCA_G; % 1995 年总出口 RCA；country×sector 堆叠单元 r×1（3465×1）
RCA_VA_1995  = RCA_VA; % 1995 年增加值出口 RCA；country×sector 堆叠单元 r×1（3465×1）
e_ir_1995    = e_ir; % 1995 年 country×sector 出口额；堆叠单元 r×1（3465×1）
DVA_F_1995   = DVA_F; % 1995 年前向国内增加值出口；来源堆叠单元 r×1（3465×1）
DVA_B_1995   = DVA_B; % 1995 年后向国内增加值出口；1×出口堆叠单元 r（1×3465）

% 保存到带年份的文件
save('result_1995.mat', ...
    'Cd_b_ir_1995', 'Cd_f_ir_1995', 'CVA_ir_1995', 'RCA_G_1995', ...
    'RCA_VA_1995', 'e_ir_1995', 'DVA_F_1995', 'DVA_B_1995');

%%%%%%%%%%%14式%%%%%%继续编写 这里是一个分解的结果，需要两期的数据 
close all
clear all
clc
% 导入两个年份的计算结果
load('result_2020.mat');
load('result_1995.mat');
J=77; % 经济体数量（此独立脚本以 J 表示 country 数）；标量（1×1）
S=45; % 每个经济体的部门数量；标量（1×1）
JS=J*S; % country×sector 堆叠单元总数（77×45=3465）；标量（1×1）

% ========= ΔRCA_VA =========
delta_RCA_VA_ir = RCA_VA_2020 - RCA_VA_1995; % 1995—2020 年增加值出口 RCA 变化；country×sector 堆叠单元 r×1（3465×1）
%%%%这里是否需要把位于分母的变量，是零或缺失值的替换成极小值

% ========= ΔRCA_G, ΔCVA, ΔCd_b, ΔCd_f =========
delta_RCA_G  = RCA_G_2020  - RCA_G_1995; % 1995—2020 年总出口 RCA 变化；country×sector 堆叠单元 r×1（3465×1）
delta_CVA_ir    = CVA_ir_2020 - CVA_ir_1995; % 1995—2020 年 CVA 分项变化；country×sector 堆叠单元 r×1（3465×1）
delta_Cd_b_ir   = Cd_b_ir_2020 - Cd_b_ir_1995; % 1995—2020 年后向分项变化；country×sector 堆叠单元 r×1（3465×1）
delta_Cd_f_ir   = Cd_f_ir_2020 - Cd_f_ir_1995; % 1995—2020 年前向分项变化；country×sector 堆叠单元 r×1（3465×1）


% ========= 四个分项计算 =========
% term1：RCA_G 变化对 RCA_VA 变化的分解贡献；country×sector 堆叠单元 r×1（3465×1）
term1 = 0.5 .* ( (Cd_b_ir_2020./Cd_f_ir_2020).*CVA_ir_2020 + ...
                 (Cd_b_ir_1995./Cd_f_ir_1995).*CVA_ir_1995 ) .* delta_RCA_G;

% term2：CVA 变化对 RCA_VA 变化的分解贡献；country×sector 堆叠单元 r×1（3465×1）
term2 = 0.5 .* ( RCA_G_1995 .* (Cd_b_ir_2020./Cd_f_ir_2020) + ...
                 RCA_G_2020 .* (Cd_b_ir_1995./Cd_f_ir_1995) ) .* delta_CVA_ir;

% term3：Cd_b 变化对 RCA_VA 变化的分解贡献；country×sector 堆叠单元 r×1（3465×1）
term3 = 0.5 .* ( RCA_G_1995 .* (CVA_ir_1995./Cd_f_ir_2020) + ...
                 RCA_G_2020 .* (CVA_ir_2020./Cd_f_ir_1995) ) .* delta_Cd_b_ir;

% term4：Cd_f 倒数变化对 RCA_VA 变化的分解贡献；country×sector 堆叠单元 r×1（3465×1）
term4 = 0.5 .* ( RCA_G_2020 .* CVA_ir_2020 .* Cd_b_ir_2020 + ...
                 RCA_G_1995 .* CVA_ir_1995 .* Cd_b_ir_1995 ) .* ...
                ( 1./Cd_f_ir_2020 - 1./Cd_f_ir_1995 );     %%这是修改过后的

%%term4 = 0.5 .* ( RCA_G_2020 .* CVA_ir_2020 .* Cd_b_ir_2020./ delta_Cd_f_ir + ...
                %%RCA_G_1995 .* CVA_ir_1995 .* Cd_b_ir_1995 ./ delta_Cd_f_ir) ;  %%这是文献的分解方式
% ========= 合并 =========
SDA_sum = term1 + term2 + term3 + term4; % 四个结构分解贡献之和；country×sector 堆叠单元 r×1（3465×1）

% ========= 检查 =========
max_diff = max(abs(delta_RCA_VA_ir - SDA_sum)); % SDA 分解恒等式的最大绝对误差；标量（1×1）
disp(['SDA 分解误差最大值 = ', num2str(max_diff)]);
