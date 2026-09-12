function [hw, hP, hX, hN, tX_4d, hwel, wL_E,wL_R,wL_Rt,hw_E_new1,...
          Y, tPi_vec, tR_vec, hpsi_4d, hlam_3d, A_new,hwl_aggwel1,...
          hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax, hP_tot, wnum,hY] = eqm_iter_innov_extension(htau, hgamma, tTar, m);
% Compute the equilibrium changes by iteration
% 输入变量（基准 N=77、J=20；m=母国/创新国，l=生产国/东道国，n=销售目的国，j=产业）：
% htau：冰山贸易成本的相对变化，l×n×j（77×77×20）；hgamma：多地生产成本冲击，m×l×j（77×77×20）；
% tTar：反事实关税率，l×n×j（77×77×20）；m：模型参数与基期数据结构体，1×1 标量结构体（其中 m.N、m.J 均为 1×1）。
% 输出变量：
% hw：生产工人工资相对变化，l×1（77×1）；hP：部门价格指数相对变化，n×j（77×20）；
% hX：部门支出/销售额相对变化，n×j（77×20）；hN：产品种类数相对变化，m×j（77×20）；
% tX_4d：反事实四维销售额，m×l×n×j（77×77×77×20）；
% hwel：名义总收入经价格指数平减后的福利变化，n×1（77×1）；wL_E：基期生产工人劳动收入，l×1（77×1）；
% wL_R：基期研发/创新收入，m×1（77×1）；wL_Rt：反事实研发/创新收入，m×1（77×1）；
% hw_E_new1：生产工人劳动收入相对变化，l×1（77×1）；Y：含关税收入的基期居民总收入，n×1（77×1）；
% tPi_vec：反事实超额利润，m×1（77×1）；tR_vec：反事实关税收入，n×1（77×1）；
% hpsi_4d：三边生产份额相对变化，m×l×n×j（77×77×77×20）；hlam_3d：双边份额相对变化，m×n×j（77×77×20）；
% A_new：反事实投入产出系数扩展矩阵，l×n×k×j（77×77×20×20；k=来源产业，j=使用产业）；
% hwl_aggwel1：总劳动收入的对数实际变化，国家×1（77×1）；hwl_Rwel：创新工人收入的对数实际变化，m×1（77×1）；
% hwl_Ewel：生产工人收入的对数实际变化，l×1（77×1）；hw_R_new：研发工资相对变化，m×1（77×1）；
% hY_notax：不含关税收入的居民收入相对变化，n×1（77×1）；hP_tot：居民消费价格指数相对变化，n×1（77×1）；
% wnum：工资归一化基准，1×1；hY：含关税收入的居民总收入相对变化，n×1（77×1）。

hw          = ones(m.N,1);      % 均衡迭代中的生产工人工资变化猜测，l×1（77×1）
hP          = ones(m.N,m.J);    % 均衡迭代中的价格变化猜测，n×j（77×20）
hX          = ones(m.N,m.J);    % 均衡迭代中的支出/销售额变化猜测，n×j（77×20）
hN          = ones(m.N,m.J);    % 均衡迭代中的产品种类变化猜测，m×j（77×20）

diff        = 1;                % 当前迭代最大绝对误差，1×1
tol         = 1e-6;             % 均衡迭代收敛容差，1×1
cc          = 0;                % 均衡迭代次数计数器，1×1
ww          = 0.5;              % 阻尼更新权重，1×1

while diff > tol && cc < 10000

     % hw_new：新生产工人工资变化，l×1（77×1）；hP_new、hX_new：新价格和支出，n×j（77×20）；hN_new：新种类数，m×j（77×20）；
     % hPsi_3d：母国—销售国—产业复合成本变化，m×n×j（77×77×20）；其余变量的含义与同名输出一致。
     [hw_new,hP_new,hX_new,hN_new,tX_4d,...
      hwel,wL_E,wL_R,wL_Rt,hw_E_new1,Y,tPi_vec,...
      tR_vec,hpsi_4d,hlam_3d,A_new,hwl_aggwel1,...
      hwl_Rwel,hwl_Ewel,hw_R_new,hY_notax,hP_tot,...
      hPsi_3d,wnum,hY] = eqm_update_innov_extension(hw, hP, hX, hN, htau, hgamma, tTar, m);
% [hw_E_new,hP_new,hX_new,hN_new,tX_4d,hwel,wL_E,wL_R,Y,tPi_vec,tR_vec,hpsi_4d,hlam_3d,A_new,hwl_aggwel1,hwl_Rwel,hwl_Ewel,hw_R_new] = eqm_update_innov_extension(hw_E, hP, hX, hN, htau, hgamma, tTar, m)
% Update the equilibrium outcomes

    r       = [hw(:); hP(:); hX(:); hN(:)];                 % 本轮旧猜测拼接向量，[l；vec(n×j)；vec(n×j)；vec(m×j)]，N(1+3J)×1（4697×1）
    rr      = [hw_new(:); hP_new(:); hX_new(:); hN_new(:)]; % 本轮新解拼接向量，轴顺序同 r，N(1+3J)×1（4697×1）
    
    diff    = max(abs(r-rr));
    cc      = cc+1;
    
    disp(diff)
    disp(cc)
      
    hw      = ww*hw_new + (1-ww)*hw;
    hP      = ww*hP_new + (1-ww)*hP;
    hX      = ww*hX_new + (1-ww)*hX;  
    hN      = ww*hN_new + (1-ww)*hN;  
    
end

% we still need to check hatY_n = hat(1-zeta_N)^(-1/varphi)

end

