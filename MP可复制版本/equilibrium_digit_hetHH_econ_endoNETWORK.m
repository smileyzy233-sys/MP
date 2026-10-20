function [wfL0,wfH0, pf0, PQ,...
          Fp, Pi_prime,...
          ZW2, Snp,...
          hat_c_comp, DP, PF] = equilibrium_digit_hetHH_econ_endoNETWORK(tau_hat,taup,alphas,T,Din,J,N,maxit,tol,VAn,VALn,VAHn,Sn,PQ_init,vfactor,...
                                                                   Gamma_nf_D,Gamma_nf_T,Omega_f_D,Omega_f_T,Omega_T, Omega_f,...
                                                                   Gamma_nf,eta_M,rho_f,No_ProductionNetwork,dummy_ind_digit,A_Prod,Eps_spill,...
                                                                   tech_spillover,EndoDigitTrans,rho_f1,gamma_L)

% 维度约定：基准 N=77、J=20；i=来源国/生产国，n=目的国，j=使用产业，h=来源产业，Jd=数字产业数。
% 输入变量：
% tau_hat：双边冰山贸易成本相对变化，[(j,n) 堆叠行]×i，即 (J*N)×N（1540×77）；taup：同轴的双边含税成本楔子（1540×77）；
% alphas：最终需求产业份额，j×n（20×77）；T：产业贸易弹性参数，j×1（20×1）；Din：基期双边贸易份额，[(j,n) 堆叠行]×i（1540×77）；
% J：产业数，1×1（基准值 20）；N：国家/地区数，1×1（基准值 77）；maxit：最大迭代次数，1×1；tol：收敛容差，1×1；
% VAn：基期总增加值，n×1（77×1）；VALn：基期低技能劳动增加值，n×1（77×1）；VAHn：基期高技能劳动增加值，n×1（77×1）；
% Sn：基期贸易余额/外生净转移，n×1（77×1）；PQ_init：初始产业支出，尺寸由输入决定（本函数未使用）；
% vfactor：迭代调整因子，尺寸由输入决定（本函数未使用）；
% Gamma_nf_D、Gamma_nf_T：数字/传统技术的直接增加值份额，j×n（20×77）；
% Omega_f_D、Omega_f_T：数字/传统技术的中间投入直接消耗份额，h×j×n（20×20×77）；
% Omega_T：传统技术采用份额，j×n（20×77）；Omega_f：不区分技术的中间投入直接消耗份额，h×j×n（20×20×77）；
% Gamma_nf：不区分技术的直接增加值份额，j×n（20×77）；eta_M：中间投入替代弹性，1×1；
% rho_f：劳动与中间投入的替代参数，1×1；No_ProductionNetwork：关闭生产网络的逻辑开关，1×1；
% dummy_ind_digit：数字产业指示向量，j×1（20×1）或 1×j（1×20）；A_Prod：产业—国家生产率，j×n（20×77）；
% Eps_spill：数字产业溢出弹性，d×n（Jd×77）；tech_spillover：是否启用技术溢出的逻辑开关，1×1；
% EndoDigitTrans：是否启用内生数字转型的逻辑开关，1×1；rho_f1：两类技术复合替代参数，1×1；
% gamma_L：传统技术中低技能劳动份额，j×n（20×77）。
% 输出变量：
% wfL0、wfH0：低技能与高技能劳动工资相对变化，均为 n×1（77×1）；pf0：产业价格相对变化，j×n（20×77）；
% PQ：反事实产业支出，j×n（20×77）；Fp：最终需求占比，j×n（20×77）；Pi_prime：反事实双边贸易份额，[(j,n) 堆叠行]×i（1540×77）；
% ZW2：按基期增加值归一化并取负的贸易失衡，n×1（77×1）；Snp：反事实贸易失衡，n×1（77×1）；
% hat_c_comp：最终复合边际成本相对变化，j×n（20×77）；DP：双边总支出分配矩阵，[(j,n) 堆叠行]×i（1540×77）；
% PF：最终需求支出，j×n（20×77）。
              
% 注意，这里的Gamma_nf_k是给定技术k下的增加值份额
% Omega_f_k是给定技术k下的中间品直接消耗系数（分母为中间品总支出）
% Omega_T是“传统”技术的采用份额。

wfL0                =  ones(N,1); % 低技能劳动工资相对变化的初始猜测，n×1（77×1）
wfH0                =  ones(N,1); % 高技能劳动工资相对变化的初始猜测，n×1（77×1）

pf0                 =  ones(J ,N); % 产业价格相对变化的初始猜测，j×n（20×77）

wf0                 = ones(J,N); % 产业复合劳动价格相对变化，j×n（20×77）

wfmax               = 1; % 工资市场迭代误差，1×1

e                   = 1; % 外层工资迭代计数器，1×1

LT                  = zeros(N*(J ),1); % 按产业 j、目的国 n 堆叠的贸易弹性向量，[(j,n) 堆叠行]×1，即 (J*N)×1（1540×1）

po_digit_ind        = find(dummy_ind_digit==1); % 数字产业在全部产业中的索引，d×1（Jd×1）

gamma_H             = 1-gamma_L; % 传统技术中高技能劳动份额，j×n（20×77）

for j	= 1:1:(J ) % 产业索引，1×1

    idx             = 1+(j-1)*N:1:N*j; % 当前产业 j 对应的目的国 n 堆叠行索引，1×N（1×77）

    LT(idx,1)       = ones(N,1)*T(j);
end

Jd                              = length(find(dummy_ind_digit)); % 数字产业数量，1×1

theta_spillover                 = ones(Jd,N); % 数字产业—国家技术溢出调整项，d×n（Jd×77）
 
if tech_spillover == 1
    for h = 1:Jd % 数字产业序号/来源产业索引，1×1
        for n = 1:N % 国家索引，1×1
            theta_spillover(h,n)   	= A_Prod(po_digit_ind(h),n)^Eps_spill(h,n);
        end
    end
end
% 
% Omega_f_couter              = nan(size(Omega_f));
% 
% for n = 1:N
%     Omega_f_couter(:,:,n)   = diag(diag(Omega_f(:,:,n)));
% end

ind_indx_T                  = setdiff(1:J,po_digit_ind); % 非数字（传统）产业索引，1×(J-Jd)（基准最多 1×20）

while (e <= maxit) && (wfmax > tol)
    
    pfmax               = 1; % 价格内层迭代误差，1×1
    
    it                  = 1; % 价格内层迭代计数器，1×1

    %%Calculating marginal cost
    if ~No_ProductionNetwork
        
        while (it <= maxit) && (pfmax > tol)
            
            if EndoDigitTrans
                hat_c_nf_T                  = zeros(J ,N); % 传统技术的复合劳动成本相对变化，j×n（20×77）
                hat_c_nf_D                  = zeros(J ,N); % 数字技术的高技能劳动成本相对变化，j×n（20×77）
                % we first compute marginal cost due to labor factor
                % hat_c_nf(n,j) = ( Omega^L_nf(j,n) * w(n)^(1-eta_nf) + sum_k Omega^k_nf_n * p(k,n)^(1-eta_nf) )^(1/(1-eta_nf))
                for j = 1:(J )
                    for n = 1:N
                        wf0(j,n)            = wfL0(n)^gamma_L(j,n) * wfH0(n)^gamma_H(j,n);
                        hat_c_nf_T(j,n)     = wf0(j,n); %( Omega_L_nf(j,n) * wf0(n)^(1-eta_nf) + sum(p_nf_aux) )^(1/(1-eta_nf))  ;
                        hat_c_nf_D(j,n)     = wfH0(n);
                    end
                end
                
                %% 首先计算数智技术的复合中间品价格以及该技术下的产品边际成本
                hat_c_f_D                       = zeros(J ,N); % 数字技术的复合中间品价格相对变化，j×n（20×77）
                p_f_D_aux                       = zeros(J,1); % 数字技术各来源产业中间品价格加总项，h×1（20×1）
                % we next compute the marginal cost regarding intermediate inputs
                % hat_c_f(n,j) = ( sum_k Omega^hj_f_n * (p(h,n) * policy_shock) ^(1-eta_f) )^(1/(1-eta_f))
                for j = 1:J
                    for n = 1:N
                        for h = 1:J
                            if dummy_ind_digit(h) == 1
                                temp_digit_po  	= find(po_digit_ind == h); % 当前数字产业在数字产业子集中的位置，1×1
                                % if source ind is digitial ind
                                p_f_D_aux(h)    = Omega_f_D(h,j,n) * ( pf0(h,n)/theta_spillover(temp_digit_po,n) ).^(1-eta_M);
                                if isnan(p_f_D_aux(h))
                                    aa= 1; % 数值异常调试标记，1×1
                                end
                            else
                                p_f_D_aux(h)  	= Omega_f_D(h,j,n) * ( pf0(h,n) ).^(1-eta_M);
                            end
                        end
                        hat_c_f_D(j,n)         	= ( sum(p_f_D_aux) ).^(1/(1-eta_M))  ;
                    end
                end
                
                hat_c_D_comp      = zeros(J ,N); % 数字技术下的产品边际成本相对变化，j×n（20×77）
                % finally calculate composited marginal cost
                % hat_c_comp(n,j) = ( Omega_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Omega_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f))
                for n = 1:1:N
                    for j = 1:(J )
                        hat_c_D_comp(j,n) = A_Prod(j,n)^(-1) * ( Gamma_nf_D(j,n) * hat_c_nf_D(j,n)^(1-rho_f) + (1-Gamma_nf_D(j,n)) * hat_c_f_D(j,n)^(1-rho_f) )^(1/(1-rho_f)) ;
                    end
                end
                
                %% 进一步计算传统技术的复合中间品价格以及该技术下的产品边际成本
                hat_c_f_T                  	= zeros(J ,N); % 传统技术的复合中间品价格相对变化，j×n（20×77）
                hat_c_f_T_alt              	= zeros(J ,N); % 按传统产业筛选口径计算的复合中间品价格，j×n（20×77）
                p_f_T_aux                 	= zeros(J,1); % 传统技术各来源产业中间品价格加总项，h×1（20×1）
                p_f_T_aux_alt             	= zeros(J,1); % 筛选传统产业后的中间品价格加总项，h×1（20×1）
                % we next compute the marginal cost of traditional intermediate inputs
                % hat_c_f(n,j) = ( sum_k Omega^hj_f_n * (p(h,n) * policy_shock) ^(1-eta_f) )^(1/(1-eta_f))
                for j = 1:J
                    for n = 1:N
                        for h = 1:J % 传统技术，我们可以直接遍历所有来源产业，因为数智类的投入份额为零，因此不影响
                            % 如果觉得不合适，可以采用如下命令：
                            if ~isempty(find(h == ind_indx_T)) || ~isempty(find(j == po_digit_ind))
                                p_f_T_aux_alt(h) 	= Omega_f_T(h,j,n) * ( pf0(h,n) ).^(1-eta_M);
                            end
                            p_f_T_aux(h)  	= Omega_f_T(h,j,n) * ( pf0(h,n) ).^(1-eta_M);
                            
                        end
                        
                        if norm(p_f_T_aux_alt-p_f_T_aux)>1e-12
                            aa = 1;
                        end
                        
                        hat_c_f_T(j,n)      = ( sum(p_f_T_aux) ).^(1/(1-eta_M))  ;
                        hat_c_f_T_alt(j,n)  = ( sum(p_f_T_aux_alt) ).^(1/(1-eta_M))  ;
                    end
                    p_f_T_aux_alt         	= zeros(J,1);
                end
                
                hat_c_T_comp                = zeros(J ,N); % 传统技术下的产品边际成本相对变化，j×n（20×77）
                % finally calculate composited marginal cost
                % hat_c_comp(n,j) = ( Omega_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Omega_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f))
                for n = 1:1:N
                    for j = 1:(J )
                        hat_c_T_comp(j,n)   = A_Prod(j,n)^(-1) * ( Gamma_nf_T(j,n) * hat_c_nf_T(j,n)^(1-rho_f) + (1-Gamma_nf_T(j,n)) * hat_c_f_T(j,n)^(1-rho_f) )^(1/(1-rho_f)) ;
                    end
                end
                
                
                %% 计算最终复合的边际成本
                hat_c_comp          = zeros(J ,N); % 数字与传统技术复合后的边际成本相对变化，j×n（20×77）
                % finally calculate composited marginal cost
                % hat_c_comp(n,j) = ( Omega_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Omega_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f))
                for n = 1:1:N
                    for j = 1:(J )
                        hat_c_comp(j,n)     = ( (1-Omega_T(j,n)) * hat_c_D_comp(j,n)^(1-rho_f1) + Omega_T(j,n) * hat_c_T_comp(j,n)^(1-rho_f1) )^(1/(1-rho_f1)) ;
                    end
                end
            else
                hat_c_nf                    = zeros(J ,N); % 不区分技术时的劳动成本相对变化，j×n（20×77）
                % we first compute marginal cost due to labor factor
                % hat_c_nf(n,j) = ( Omega^L_nf(j,n) * w(n)^(1-eta_nf) + sum_k Omega^k_nf_n * p(k,n)^(1-eta_nf) )^(1/(1-eta_nf))
                for j = 1:(J )
                    for n = 1:N
                        hat_c_nf(j,n)       = wf0(n);%( Omega_L_nf(j,n) * wf0(n)^(1-eta_nf) + sum(p_nf_aux) )^(1/(1-eta_nf))  ;
                    end
                end
                
                hat_c_f                     = zeros(J ,N); % 不区分技术时的复合中间品价格相对变化，j×n（20×77）
                p_f_aux                     = zeros(J,1); % 各来源产业中间品价格加总项，h×1（20×1）
                % we next compute the marginal cost regarding intermediate inputs
                % hat_c_f(n,j) = ( sum_k Omega^hj_f_n * (p(h,n) * policy_shock) ^(1-eta_f) )^(1/(1-eta_f))
                for j = 1:J
                    for n = 1:N
                        for h = 1:J
                            if dummy_ind_digit(h) == 1
                                temp_digit_po  	= find(po_digit_ind == h);
                                % if source ind is digitial ind
                                p_f_aux(h)  	= Omega_f(h,j,n) * ( pf0(h,n)/theta_spillover(temp_digit_po,n) ).^(1-eta_M);
                                
                            else
                                p_f_aux(h)  	= Omega_f(h,j,n) * ( pf0(h,n) ).^(1-eta_M);
                            end
                        end
                        hat_c_f(j,n)            = ( sum(p_f_aux) ).^(1/(1-eta_M))  ;
                    end
                end
                
                hat_c_comp      = zeros(J ,N);
                % finally calculate composited marginal cost
                % hat_c_comp(n,j) = ( Omega_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Omega_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f))
                for n = 1:1:N
                    for j = 1:(J )
                        hat_c_comp(j,n) = A_Prod(j,n)^(-1) * ( Gamma_nf(j,n) * (wf0)^(1-rho_f) + (1-Gamma_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f)) ;
                    end
                end
            end
            
            %% calculating phat
            Din_om = Din.*( tau_hat.^(-1./(LT*ones(1,N)))); % 经贸易成本冲击调整的基期贸易份额项，[(j,n) 堆叠行]×i（1540×77）
            
            phat1 = nan(J ,n); % 更新后的产业价格相对变化，j×n（完成态 20×77；初始化第二维取当前循环变量 n）
            
            for j = 1:1:(J )
                
                for n = 1:1:N
                    phat1(j , n) = Din_om( n + (j-1)*N , :)*( hat_c_comp(j,:).^( - 1 / T( j )) )';
                    
                    % this happens because of sectors with zero VA
                    % Note that we do not want logs of zero
                    if  phat1(j , n) == 0
                        phat1(j , n) = 1;
                    else
                        phat1(j , n) = phat1(j , n)^( - T( j ) );
                    end
                end
            end
            
            pfdev    = abs(phat1 - pf0); % 价格迭代逐元素偏差，j×n（20×77）
            pf0      = phat1;
            pfmax    = max(max(pfdev));
            it       = it + 1;
        end
        
    else
        pfmax = 1;
        while (it <= maxit) && (pfmax > tol)
            
            hat_c_nf                    = zeros(J ,N);
            % we first compute marginal cost due to labor factor
            % hat_c_nf(n,j) = ( Omega^L_nf(j,n) * w(n)^(1-eta_nf) + sum_k Omega^k_nf_n * p(k,n)^(1-eta_nf) )^(1/(1-eta_nf))
            for j = 1:(J )
                for n = 1:N
                    hat_c_nf(j,n)       = wf0(n);%( Omega_L_nf(j,n) * wf0(n)^(1-eta_nf) + sum(p_nf_aux) )^(1/(1-eta_nf))  ;
                end
            end
            
            hat_c_f                     = pf0;
            % It should be noted that the composite intermediate input
            % prices completely degenerates.
            
            hat_c_comp                  = zeros(J ,N);
            % finally calculate composited marginal cost
            % hat_c_comp(n,j) = ( Omega_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Omega_nf(j,n)) * hat_c_f(j,n)^(1-rho_f) )^(1/(1-rho_f))
            for n = 1:1:N
                for j = 1:(J )
                    %hat_c_comp(j,n)     = A_Prod(j,n)^(-1) * ( Gamma_nf(j,n) * hat_c_nf(j,n)^(1-rho_f) + (1-Gamma_nf(j,n))* pf0(j,n)^(1-rho_f) )^(1/(1-rho_f)) ;
                    hat_c_comp(j,n)     = A_Prod(j,n)^(-1) * hat_c_nf(j,n) ;
                end
            end
            
            
            %% calculating phat
            Din_om = Din.*( tau_hat.^(-1./(LT*ones(1,N))));
            
            phat1 = nan(J ,n);
            
            for j = 1:1:(J )
                
                for n = 1:1:N
                    phat1(j , n) = Din_om( n + (j-1)*N , :)*( hat_c_comp(j,:).^( - 1 / T( j )) )';
                    
                    % this happens because of sectors with zero VA
                    % Note that we do not want logs of zero
                    if  phat1(j , n) == 0
                        phat1(j , n) = 1;
                    else
                        phat1(j , n) = phat1(j , n)^( - T( j ) );
                    end
                end
            end
            
            pfdev    = abs(phat1 - pf0); % Checking tolerance
            pf0      = phat1;
            pfmax    = max(max(pfdev));
            it       = it + 1;
        end
    end
    
    %% calculating Pi_prime
    Pi_hat = nan(size(Din)); % 双边贸易份额相对变化，[(j,n) 堆叠行]×i（1540×77）
    
    for j = 1:1:(J ) % within ind j
        for n = 1:1:N % destination ind
            for i = 1:N % 来源国索引，1×1
                Pi_hat( n + (j-1)*N , i ) = ( tau_hat( n + (j-1)*N , i )*hat_c_comp(j,i)/phat1(j,n) )^(- 1/T( j ));
            end
        end
    end
    
    Pi_hat_re       = permute(reshape(Pi_hat,[N,J,N]), [1,3,2]); % 重排后的贸易份额相对变化，n×i×j（77×77×20；目的国×来源国×产业）
    
    Pi_prime        = Din.*Pi_hat; % 反事实双边贸易份额，[(j,n) 堆叠行]×i（1540×77）
    
    for j = 1:1:(J )
        irow        = 1+N*(j-1):1:N*j; % 当前产业 j 在堆叠贸易矩阵中的目的国行索引，1×n（1×77）
        Fp(j,:)     = sum((Pi_prime(irow,:)./taup(irow,:)),2)'; % 最终需求占比，j×n（20×77；此处写入第 j 行）
    end
    
    if ~EndoDigitTrans
        %%Calculating Expenditure MATRIX
        IA                      = zeros((J )*N,(J )*N); % 最终需求分配矩阵，[(n,j) 国家内产业堆叠行]×[(n,j) 国家内产业堆叠列]（1540×1540）
        I_F                     = 1 - Fp; % 中间需求占比的互补项，j×n（20×77）
        
        for n = 1:1:N
            IA(1 + (n-1)*(J ) : n*(J ), 1 + (n-1)*(J ) : n*(J )) = kron(alphas(:,n),I_F(:,n)');
        end
        
        Pit                     = Pi_prime./(taup); % 剔除贸易成本楔子后的反事实贸易份额，[(j,n) 堆叠行]×i（1540×77）
        
        H_comp                  = nan(N*(J ), N*(J )); % 生产网络中间需求传导矩阵，[(n,h) 国家内来源产业堆叠行]×[(n,j) 国家内使用产业堆叠列]（1540×1540）
        
        Phi_prime_f            	= nan( J,(J ),N ); % 反事实中间投入成本份额，h×j×n（20×20×77；来源产业×使用产业×国家）
        
        Phi_f                   = nan( J,(J ),N ); % 基期中间投入成本份额，h×j×n（20×20×77；来源产业×使用产业×国家）
        
        for ii = 1:N  % 销售/目的国索引，1×1
            for n = 1:N % source country
                for k = 1:(J ) % 使用产业索引，1×1
                    for j = 1:(J )%  source ind
                        
                        Phi_f(j,k,n)                                = Omega_f(j,k,n) * (1-Gamma_nf(k,n));
                        
                        if dummy_ind_digit(j) == 1
                            temp_digit_po                           = find(po_digit_ind == j);
                            % if source ind is digitial ind
                            Phi_prime_f(j,k,n)                   	= A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/theta_spillover(temp_digit_po,n)/hat_c_f(k,n))^(1-eta_M)) ...
                                                                    * ( (hat_c_f(k,n)/hat_c_comp(k,n) )^(1-rho_f) ) * Phi_f(j,k,n);
                            
                        else
                            Phi_prime_f(j,k,n)                    	= A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/hat_c_f(k,n))^(1-eta_M)) ...
                                                                    * ( (hat_c_f(k,n)/hat_c_comp(k,n) )^(1-rho_f) ) * Phi_f(j,k,n);
                        end
                        
                        %share_prime_L(k,n)                          = A_Prod(k,n)^(rho_f-1) * ((wf0(n)/hat_c_comp(j,n))^(1 - rho_f)) .* share_L_temp;
                        
                        H_comp( (n-1)*(J) + j , (ii-1)*(J ) + k)    = Phi_prime_f(j,k,n) * Pit( ii + (k-1)*N , n );
                        
                        
                    end
                    
                    
                end
            end
        end
        
    else
        
        %%Calculating Expenditure MATRIX
        IA                      = zeros((J )*N,(J )*N);
        I_F                     = 1 - Fp;
        
        for n = 1:1:N
            IA(1 + (n-1)*(J ) : n*(J ), 1 + (n-1)*(J ) : n*(J )) = kron(alphas(:,n),I_F(:,n)');
        end
        
        Pit                     = Pi_prime./(taup);
        
        H_comp                  = nan(N*(J ), N*(J ));
        
        % 传统技术的份额
        Phi_prime_f_T         	= nan( J,(J ),N ); % 传统技术反事实中间投入成本份额，h×j×n（20×20×77）
        
        % 传统技术的份额
        Phi_f_T               	= nan( J,(J ),N ); % 传统技术基期中间投入成本份额，h×j×n（20×20×77）
        
        % 数字技术的份额
        Phi_prime_f_D          	= nan( J,(J ),N ); % 数字技术反事实中间投入成本份额，h×j×n（20×20×77）
        
        % 数字技术的份额
        Phi_f_D               	= nan( J,(J ),N ); % 数字技术基期中间投入成本份额，h×j×n（20×20×77）
        
        Phi_prime_f         	= nan( J,(J ),N );
        
        h_idx_temp             	= 1; % 数字技术非数字来源项的临时行索引，1×1
        
        for ii = 1:N  % detination country
            for n = 1:N % source country
                for k = 1:(J ) % destination ind
                    for j = 1:(J )%  source ind
                        
                        Phi_f_T(j,k,n)                    	= Omega_f_T(j,k,n) * (1-Gamma_nf_T(k,n));
                        
                        Phi_f_D(j,k,n)                    	= Omega_f_D(j,k,n) * (1-Gamma_nf_D(k,n));
                        
                        Phi_prime_f_T(j,k,n)             	= A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/hat_c_f_T(k,n))^(1-eta_M)) * ( (hat_c_f_T(k,n)/hat_c_T_comp(k,n) )^(1-rho_f) )...
                                                            * ( (hat_c_T_comp(k,n)/hat_c_comp(k,n) )^(1-rho_f1) ) * Phi_f_T(j,k,n);

                        if dummy_ind_digit(j) == 1
                            temp_digit_po                  	= find(po_digit_ind == j);
                            % if source ind is digitial ind
                            % Phi_prime_f(j,k,n)            = A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/theta_spillover(temp_digit_po,n)/hat_c_f(k,n))^(1-eta_M)) * ( (hat_c_f(k,n)/hat_c_comp(k,n) )^(1-rho_f) )...
                            %                               * Phi_f(j,k,n);
                            %
                            Phi_prime_f_D(j,k,n)         	= A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/theta_spillover(temp_digit_po,n)/hat_c_f_D(k,n))^(1-eta_M)) * ( (hat_c_f_D(k,n)/hat_c_D_comp(k,n) )^(1-rho_f) )...
                                                            * ( (hat_c_D_comp(k,n)/hat_c_comp(k,n) )^(1-rho_f1) ) * Phi_f_D(j,k,n);
                            
                            
                        else
                            % Phi_prime_f(j,k,n)            = A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/hat_c_f(k,n))^(1-eta_M)) * ( (hat_c_f(k,n)/hat_c_comp(k,n) )^(1-rho_f) )...
                            %                               * Phi_f(j,k,n);
                            %
                            Phi_prime_f_D(j,k,n)         	= A_Prod(k,n)^(rho_f-1) * ((phat1(j,n)/hat_c_f_D(k,n))^(1-eta_M)) * ( (hat_c_f_D(k,n)/hat_c_D_comp(k,n) )^(1-rho_f) )...
                                                           	* ( (hat_c_D_comp(k,n)/hat_c_comp(k,n) )^(1-rho_f1) ) * Phi_f_D(h_idx_temp,k,n);
                            
                        end                        
                        
                        %Phi_prime_f_D(j,k,n)            	= ((phat1(j,n)/hat_c_f_D(k,n))^(1-eta_M)) * ( (hat_c_f_D(k,n)/hat_c_D_comp(k,n) )^(1-rho_f) )...
                        %                                  	* ( (hat_c_D_comp(k,n)/hat_c_comp(k,n) )^(1-rho_f) ) * Phi_f_D(j,k,n);
                        
                        Phi_prime_f(j,k,n)                  = Omega_T(k,n) * Phi_prime_f_T(j,k,n) + (1-Omega_T(k,n)) * Phi_prime_f_D(j,k,n);
                        
                        H_comp( (n-1)*(J ) + j , (ii-1)*(J ) + k)   = Phi_prime_f(j,k,n) * Pit( ii + (k-1)*N , n );
                        
                        h_idx_temp                                  = h_idx_temp + 1;
                        
                    end
                    
                    h_idx_temp = 1;
                    
                end
            end
        end
        
    end
    
    OM              = eye((J )*N,(J )*N) - ((H_comp + IA)); % 均衡线性系统系数矩阵 I-H-IA，[(n,j) 国家内产业堆叠]×[(n,j) 国家内产业堆叠]（1540×1540）
    
    Total_Income    = (ones((J ),1)*(wfL0.*VALn + wfH0.*VAHn - Sn)'); % 各产业复制的国家可支配收入，j×n（20×77）
    
    PQ              = OM\reshape(alphas.*Total_Income,[(J )*N,1]); % 线性系统求得的产业支出堆叠向量，[vec(j×n)]×1，即 (J*N)×1（1540×1）
    
    PQ              = reshape(PQ,J ,N);
    
    PQ_vec          = reshape(PQ',1,(J )*N)'; % 按国家 n、产业 j 顺序堆叠的产业支出，[(n,j) 堆叠行]×1（1540×1）
    %%calculating trade balance
    for n = 1:1:N
        DP(:,n)     = Pit(:,n).*PQ_vec; % 双边总支出分配矩阵，[(j,目的国) 堆叠行]×来源国 i（1540×77；此处写入第 n 列）
    end
    LHS             = sum(DP)'; % 各来源国出口总额，i×1（77×1）
    
    
    DP_prime                  	= nan(J,N); % 按产业汇总的国家总产出/支出，j×n（20×77）
    for j = 1:1:(J)
        DP_prime(j,:)           = sum(DP(1+(j-1)*N:j*N,:),1);
    end

    
    share_prime_L_T           	= nan(size(DP_prime)); % 传统技术反事实劳动增加值份额，j×n（20×77）
    share_prime_L_D           	= nan(size(DP_prime)); % 数字技术反事实劳动增加值份额，j×n（20×77）
    share_prime_L             	= nan(size(DP_prime)); % 不区分技术的反事实劳动增加值份额，j×n（20×77）
    VAjn_prime                  = nan(size(DP_prime)); % 反事实产业—国家总增加值，j×n（20×77）
    VALjn_prime                 = nan(size(DP_prime)); % 反事实产业—国家低技能劳动增加值，j×n（20×77）
    VAHjn_prime                 = nan(size(DP_prime)); % 反事实产业—国家高技能劳动增加值，j×n（20×77）
    
    if EndoDigitTrans
        for j = 1:(J)
            for n = 1:N
                share_L_T_temp        	= Gamma_nf_T(j,n) ; % 当前产业国家的传统技术基期劳动份额，1×1
                
                share_L_D_temp        	= Gamma_nf_D(j,n); % 当前产业国家的数字技术基期劳动份额，1×1
                
                share_prime_L_T(j,n)  	= A_Prod(j,n)^(rho_f-1) * ((wf0(n)/hat_c_T_comp(j,n))^(1 - rho_f))  .* share_L_T_temp;
                
                share_prime_L_D(j,n)  	= A_Prod(j,n)^(rho_f-1) * ((wfH0(n)/hat_c_D_comp(j,n))^(1 - rho_f))  .* share_L_D_temp;
                
                VAjn_prime(j,n)         = DP_prime(j,n) * ( Omega_T(j,n)* ( (hat_c_T_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_T(j,n) ...
                                                       + (1-Omega_T(j,n))* ( (hat_c_D_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_D(j,n) );
                
                VALjn_prime(j,n)        = DP_prime(j,n) * ( Omega_T(j,n)* ( (hat_c_T_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_T(j,n) * gamma_L(j,n) + 0 );
                
                VAHjn_prime(j,n)        = DP_prime(j,n) * ( Omega_T(j,n)* ( (hat_c_T_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_T(j,n) * gamma_H(j,n) ...
                                                       + (1-Omega_T(j,n))* ( (hat_c_D_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_D(j,n) * 1 ) ;
                

                share_prime_L_T(j,n) + sum(Phi_prime_f_T(:,j,n),1) - 1;
                
                share_prime_L_D(j,n) + sum(Phi_prime_f_D(:,j,n),1) - 1;
                
                % test_temp：成本份额加总为一的检验残差，1×1
                test_temp               = ( Omega_T(j,n)* ( (hat_c_T_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_T(j,n) ...
                                        + (1-Omega_T(j,n))* ( (hat_c_D_comp(j,n)/hat_c_comp(j,n) )^(1-rho_f1) ) .* share_prime_L_D(j,n)) ...
                                        + sum( Phi_prime_f(:,j,n),1) - 1;
                
%                 if abs(test_temp) > 1e-5
%                     disp('Something wrong!')
%                 end
%                 
            end
        end
    else
        for j = 1:(J)
            for n = 1:N
                share_L_temp            = Gamma_nf(j,n) ; % 当前产业国家的不分技术基期劳动份额，1×1
                
                share_prime_L(j,n)      = A_Prod(j,n)^(rho_f-1) * ((wf0(n)/hat_c_comp(j,n))^(1 - rho_f)) .* share_L_temp;
                
                VAjn_prime(j,n)         = DP_prime(j,n) * share_prime_L(j,n);
                
                test_temp               = share_prime_L(j,n) + sum( Phi_prime_f(:,j,n),1) - 1;
                
                if abs(test_temp) > 1e-5
                    disp('Something wrong!')
                end
                
            end
        end
    end
    
    VAn_prime                   = sum( VAjn_prime, 1)'; % 反事实各国总增加值，n×1（77×1）
    VALn_prime                  = sum( VALjn_prime, 1)'; % 反事实各国低技能劳动增加值，n×1（77×1）
    VAHn_prime                  = sum( VAHjn_prime, 1)'; % 反事实各国高技能劳动增加值，n×1（77×1）
    
    Pce_prime                   = prod(phat1.^(alphas)); % 各国最终消费价格指数相对变化，1×n（1×77）
    
    VAn_real_prime              = sum( VAjn_prime, 1)'./Pce_prime'; % 反事实各国实际增加值，n×1（77×1）
    
    % calculating RHS (Imports) trade balance
    PF                          = PQ.*Fp; % 各产业—国家最终需求支出，j×n（20×77）
    
    RHS                         = sum(PF)'; % 各目的国进口/最终需求总额，n×1（77×1）
    
    % excess function (trade balance)
    Snp                         = (RHS - LHS + Sn); % 反事实贸易失衡，n×1（77×1）
    
    ZW2                         = -(RHS - LHS + Sn)./(VAn); % 按基期增加值归一化并取负的贸易失衡，n×1（77×1）
    %Iteration factor prices
        
    Lab_mkt_L_check             = norm(VALn_prime./VALn - wfL0); % 低技能劳动市场更新误差范数，1×1
        
    Lab_mkt_H_check             = norm(VAHn_prime./VAHn - wfH0); % 高技能劳动市场更新误差范数，1×1
    
    if (mod(e,20)) == 0
        wfmax       = abs(Lab_mkt_L_check) + abs(Lab_mkt_H_check)
    end
    
    wfL0            = VALn_prime./VALn;

    wfH0            = VAHn_prime./VAHn;
    
    %wfL0(1)         = 1;
    
    e               = e+1;
end


aa = 1;
