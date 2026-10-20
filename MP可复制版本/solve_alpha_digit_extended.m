% This function calculates the Omega matrix in Caliendo - Parro (2009).
% 索引约定：n/ii=来源国/目的国，j/h/k=产业；当前基准 N=77、J=20。
% 变量及维度（均在函数接口首次出现处说明）：
%   alphas_init  初始最终需求份额，j×n（20×77）；PQ 为产业—国家堆叠支出向量，(J*N)×1（1540×1）。
%   B            beta 参数矩阵，j×n（20×77）；Omega_f 为投入产业 h×产出产业 k×国家 n（20×20×77）。
%   Gamma_nf     增加值份额，k×n（20×77）；Dinp 为“产业 k—目的国 ii”堆叠行×来源国 n，1540×77。
%   taup         与 Dinp 同轴的贸易成本楔子，1540×77；Fp 为产业 j×国家 n 的加权关税份额，20×77。
%   VAn          国家 n×1 的增加值（77×1）；Sn 为国家 n×1 的贸易余额/净转移项（77×1）。
%   J, N         产业数与国家数，均为 1×1 标量（当前为 20、77）；eta_M, rho_f 为 1×1 CES 参数。
%   alphas_update 更新后最终需求份额，j×n（20×77）；OM 为堆叠产业—国家线性系统矩阵，1540×1540。

function [alphas_update, OM] = solve_alpha_digit_extended(alphas_init,PQ,B,Omega_f,Gamma_nf,Dinp,taup,Fp,VAn,Sn,J,N,eta_M,rho_f)


% IA：国际贸易税收形成的支出反馈矩阵，堆叠产业—国家×堆叠产业—国家（1540×1540）。
IA                          = zeros( (J)*N,(J)*N);
% I_F：关税收入留存份额（1-Fp），产业 j×国家 n（20×77）。
I_F                         = 1 - Fp;

for n = 1:1:N  % n：国家索引，1×1 标量，取值 1,…,77。
    IA(1 + (n-1)*(J) : n*(J), 1 + (n-1)*(J) : n*(J)) = kron(alphas_init(:,n),I_F(:,n)');
end

% Pit：剔除贸易成本楔子后的贸易份额，“产业 k—目的国 ii”堆叠行×来源国 n（1540×77）。
Pit                         = Dinp./(taup);
% Bt：1-beta 的补份额，产业 j×国家 n（20×77；当前函数后续未使用）。
Bt                          = 1-B;
% I write an simplified loop used for constructing the matrix GP
% row represents the source and col is the destination
    
% wf0：基准工资/要素价格向量，国家 n×1（77×1）。
wf0                         = ones(N,1);                               

% pf0：基准产业价格矩阵，产业 j×国家 n（20×77；当前函数后续未使用）。
pf0                         = ones(J,N);                            

% H_comp：投入产出与贸易份额合成矩阵，来源“国家 n—产业 j”×目的“国家 ii—产业 k”（1540×1540）。
H_comp                      = nan(N*(J ), N*(J ));

% Phi_prime_f：价格调整后的中间投入系数，投入产业 h×产出产业 k×来源国 n（20×20×77）。
Phi_prime_f                 = nan( J,(J ),N );

% Phi_f：中间投入直接消耗系数，投入产业 h×产出产业 k×来源国 n（20×20×77）。
Phi_f                       = nan( J,(J ),N );

% Phi_prime_nf：价格调整后的非中间投入系数占位数组，h×k×n（20×20×77；当前函数未使用）。
Phi_prime_nf                = nan( J,(J ),N );

% Phi_nf：非中间投入系数占位数组，h×k×n（20×20×77；当前函数未使用）。
Phi_nf                      = nan( J,(J ),N );

% phat1：产业价格变化占位矩阵，产业 j×国家 n（20×77；当前函数未使用）。
phat1                       = ones(J,N);

% j_idx_temp：临时产业索引，1×1 标量（当前函数未使用）。
j_idx_temp                  = 1;
% h_idx_temp：中间投入来源产业 h 的临时索引，1×1 标量，取值 1,…,20。
h_idx_temp                  = 1;

for ii = 1:N  % ii：目的国索引，1×1 标量，取值 1,…,77。
    for n = 1:N % n：来源国索引，1×1 标量（已在上方首次说明）。
        for k = 1:(J ) % k：使用投入的产出产业索引，1×1 标量，取值 1,…,20。
            for j = 1:(J )% j：提供投入的来源产业索引，1×1 标量，取值 1,…,20。
                
                    Phi_f(h_idx_temp,k,n)                    	= Omega_f(h_idx_temp,k,n) * (1-Gamma_nf(k,n));
                    
                    Phi_prime_f(h_idx_temp,k,n)                	= ((1/1)^(1-eta_M)) * ( (1/1)^(1-rho_f) ) * Phi_f(h_idx_temp,k,n);
                    
                    H_comp( (n-1)*(J) + j , (ii-1)*(J) + k)     = Phi_prime_f(h_idx_temp,k,n) * Pit( ii + (k-1)*N , n );
                    
                    h_idx_temp                                  = h_idx_temp + 1;
                    
                %end
            end
            
            h_idx_temp = 1;
            
        end
    end
end

% aa：中间投入与增加值份额的加总校验数组，单例轴×产出产业 k×国家 n（1×20×77）。
aa = sum(Phi_prime_f,1) + reshape(Gamma_nf,[1 J N]);
%sum(aa(:,1,1))

% OM 的维度已在函数输出说明中给出。
OM                      = eye((J)*N,(J)*N) - (H_comp + IA);

% Total_Income：按产业复制后以“产业 j—国家 n”堆叠的可支配收入向量，1540×1。
Total_Income            = reshape((ones((J),1)*(wf0.*VAn - Sn)'),[(J)*N,1]);

%(I - GP - IA)*PQ = alphas*Total_Income
% alphas_vec：以“产业 j—国家 n”堆叠的更新后最终需求份额，1540×1。
alphas_vec              = (OM*PQ)./Total_Income;

alphas_update           = reshape(alphas_vec,(J),N);

