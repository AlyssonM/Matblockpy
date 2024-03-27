%pyenv("Version","D:\MATLAB\.gridenv\Scripts\python.exe"); 
clear classes
mod = py.importlib.import_module('contract_interface');
py.importlib.reload(mod);

mpc = loadcase('IEEE4bus');
py.contract_interface.setGeneratorPower(int32(0),int32(0));
Power = py.contract_interface.getGenerator();
GenPower = double(py.array.array('d', py.numpy.nditer(Power)));

mpopt = mpoption('verbose', 0, 'out.all', 0);
define_constants;
for h=1:24
    if(h == 3)
        py.contract_interface.setGeneratorPower(int32(50),int32(0));
    end
    if(h == 5)
        py.contract_interface.setGeneratorPower(int32(25),int32(10));
    end
    
    if(h > 10)
        py.contract_interface.setGeneratorPower(int32(25+5*(h-10)),int32(-50));
    end
    Power = py.contract_interface.getGenerator();
    GenPower = double(py.array.array('d', py.numpy.nditer(Power)));
	mpc.gen(1, PG) = GenPower(1);
    mpc.gen(1, QG) = GenPower(2);
    results{h} = runpf(mpc, mpopt);
	gen_power_kW(:,h) = results{h}.gen(:,PG);
	gen_power_kVAr(:,h) = results{h}.gen(:,QG);
	buses_voltage(:,h) = results{h}.bus(:,VM);
    Grid(:,h) = sum(results{h}.branch(1:2, PF));
end

initial_time = datetime('today', 'Format', 'yyyy-MM-dd HH:mm:ss');
% Cria um vetor datetime com incrementos de uma hora
simulation_time = initial_time + hours(0:23);
figure(1)
hold on 
plot(simulation_time,gen_power_kW(1,:))
plot(simulation_time,gen_power_kVAr(1,:))
legend('Active Power (kW)', 'Reactive Power (kVAr)')
xlabel('Time (h)')
ylabel('Power')

