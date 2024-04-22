function [MCQ,lambda] = DoubleAuction(Ns, Nb, Ps, Pb, Ct)
    prob = optimproblem;
    N = Ns + Nb;
    P = [Ps Pb];
    x = optimvar('x',N);
    % Minimize cost of electricity from the grid
    prob.ObjectiveSense = 'minimize';
%     prob.Objective = sum(C(1:Ns)'.*x(1:Ns)) - sum(C(Ns+1:N)'.*x(Ns+1:N));
    prob.Objective = Ct*x;
    % Constraints
    constr1 = x(1:N) >= 0;
    constr2 = x(1:N) <= P';
    constr3 = sum(x(1:Ns)) == sum(x(Ns+1:N));
    
    prob.Constraints.constr1 = constr1;
    prob.Constraints.constr2 = constr2;
    %prob.Constraints.constr3 = constr3;

    
    % Solve the linear program
    options = optimoptions(prob.optimoptions,'Display','None');
    [values,~,exitflag] = solve(prob,'Options',options);
    
    MCQ = values.x;
    lambda = Ct;

end