clear classes
close all
mod = py.importlib.import_module('degen9bus');
py.importlib.reload(mod);
load('IfesSolcastPT15M.mat');
load('UCloads');

%% Meteorological data
IfesSolcastPT15M.PeriodStart = datetime(IfesSolcastPT15M.PeriodStart, 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
startDate = datetime('2022-08-12 00:00:00', 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
endDate = datetime('2022-08-12 23:45:00', 'InputFormat', 'yyyy-MM-dd HH:mm:ss');

filteredData = IfesSolcastPT15M(IfesSolcastPT15M.PeriodStart >= startDate & IfesSolcastPT15M.PeriodStart <= endDate, :);

%% Load data
startLoadDate = datetime('2016-08-10 00:00:00', 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
endLoadDate = datetime('2016-08-10 23:45:00', 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
filteredLoad = UCloads(UCloads.Timestamp >= startLoadDate & UCloads.Timestamp <= endLoadDate, :);

Load1 = interp1(0:23,filteredLoad.UC8,0:0.25:23, 'linear');
Load2 = interp1(0:23,filteredLoad.UC2,0:0.25:23, 'linear');
Load3 = interp1(0:23,filteredLoad.UC3,0:0.25:23, 'linear');
Load1(end+1:96) = Load1(end);
Load2(end+1:96) = Load2(end);
Load3(end+1:96) = Load3(end);

%% PV Genrators data
Npv = zeros(1,2);
Vmpp = zeros(1,2);
Impp = zeros(1,2);
Voc = zeros(1,2);
Isc = zeros(1,2);
Kv = zeros(1,2);
Ki = zeros(1,2);
Area = zeros(1,2);
Efficiency = zeros(1,2);
tilt = zeros(1,2);
azimuth = zeros(1,2);

%PV1
Npv(1) = 296;            % number of modules
Efficiency(1) = 0.204;   % module efficiency
tilt(1) = 18;            % Tilt angle
azimuth(1) = 7;          % Azimuth angle
%Module data
Vmpp(1) = 41.1; 
Impp(1) = 10.96;
Voc(1) = 49.1;
Isc(1) = 11.60;
Kv(1) = -0.27;
Ki(1) = 0.05;

%PV2
Npv(2) = 420;           % number of PV modules
Efficiency(2) = 0.214;  % module efficiency
tilt(2) = 12;           % Tilt angle
azimuth(2) = 44;        % Azimuth angle
Vmpp(2) = 39.5; 
Impp(2) = 10.1;
Voc(2) = 48.1;
Isc(2) = 10.9;
Kv(2) = -0.28;
Ki(2) = 0.037;

%% Aerogenerator data
Nt = 5;                  %Number of generators
Vi = 3;                  %cut-in velocity
Vo = 20;                 %cut-out velocity
GP = 9;                  % polinomial order                                                      
PRT = [2.5, 8.5, 16.6, 28.7, 43.2, 55.1, 59.6, 59.9, 59.9, 59.9, 59.9, 59.9, 59.9, 57.5, 55.0, 52.0, 49.1, 46.8];
VT =  [3  ,  4 ,   5 ,  6  ,   7 ,  8  ,  9  ,  10 ,  11 ,  12 ,  13 ,  14 ,  15 ,  16 ,  17 ,  18 ,  19 ,  20 ]; 
PolT = polyfit(VT,PRT,GP);

size_ = size(filteredData.PeriodStart);
dayOfYear = zeros(1,size_(1));

%% Solar Irradiance calculations (POA) and PV Power Outputs
for i=1:2
    dayOfYear = day(filteredData.PeriodStart(1), 'dayofyear');    
    POA(i,:) = calculate_POA(filteredData.Ghi, tilt(i), azimuth(i), dayOfYear, -19.39);
end

for i=1:2
    dayOfYear = day(filteredData.PeriodStart(1), 'dayofyear');    
    PVGen(i,:) = PVGeneration(Npv(i),filteredData.AirTemp,POA(i,:)/1000, Vmpp(i),Impp(i), Voc(i),Isc(i),Kv(i),Ki(i));
end

%% Wind Power Output
WindGen = WindGeneration(Nt,filteredData.WindSpeed10m,PolT,GP);

%% Load case and run OPF
mpc = loadcase('./case9');
define_constants;

for h=1:size(PVGen(1,:)')
	mpopt = mpoption('verbose', 0, 'out.all', 0);
	mpc.gen(2, PG) = PVGen(1,h);
    mpc.gen(3, PG) = PVGen(2,h);
    mpc.gen(4, PG) = WindGen(h);
    mpc.bus(5, PD) = Load1(h);
    mpc.bus(7, PD) = Load2(h);
    mpc.bus(9, PD) = Load3(h);

    results{h} = runpf(mpc, mpopt);
	gen_power_kW(:,h) = results{h}.gen(:,PG);
	gen_power_kVAr(:,h) = results{h}.gen(:,QG);
	buses_voltage(:,h) = results{h}.bus(:,VM);
    Grid(:,h) = results{h}.branch(:, PF);
end

%% Plot Results
figure(1)
plot(filteredData.PeriodStart,gen_power_kW')
legend('Main Grid', 'PV1 - Bus 2', 'PV2 - Bus 3', 'WG - Bus 6')
title('Generators Power Flow')
ylabel('Power (kW)')
xlabel('Time (h)')

figure(2)
plot(filteredData.PeriodStart,buses_voltage')
title('9 Bus Voltages ')
ylabel('Voltage (pu)')
xlabel('Time (h)')

data = table(filteredData.PeriodStart, gen_power_kW(1,:)',gen_power_kW(2,:)',gen_power_kW(3,:)',Load1',Load2',Load3', 'VariableNames', {'DataHora', 'Gen-01', 'Gen-02', 'Gen-03', 'Load-01','Load-02','Load-03'});
%save('PowerData.mat','data');

DLEMcontract(data(:,{'Gen-01','Gen-02','Gen-03'}), filteredLoad.UC1, filteredLoad.UC2, filteredLoad.UC9)

function POA = calculate_POA(GHI, tilt, azimuth, dayOfYear, latitude)
    % Convert degrees to radians
    tilt_rad = deg2rad(tilt);
    azimuth_rad = deg2rad(azimuth);
    latitude_rad = deg2rad(latitude);
    
    % Declination solar angle
        solarDeclination = 0.409 * sin(2 * pi * (dayOfYear - 81) / 368);
    % Inicialização do array POA
    POA = zeros(1, 96); % 96 intervals of 15 minutes in a day

    for i = 1:96
        
        % convert index to hour
        hour = mod(i-1, 4) * 0.25 + floor((i-1) / 4);

        hourAngle = deg2rad(15 * (hour - 12));  % Subtract 12 to centralize mid-day

        % Solar Elevation angle calculation
        solarElevationAngle = asin(sin(latitude_rad) * sin(solarDeclination) + cos(latitude_rad) * cos(solarDeclination) * cos(hourAngle));

        % Incidence Angle calculation
        cosIncidenceAngle = sin(solarElevationAngle) * cos(tilt_rad) + cos(solarElevationAngle) * sin(tilt_rad) * cos(azimuth_rad - hourAngle);

        % Plane of Array (POA) for the actual interval
        POA(i) = GHI(i) * max(cosIncidenceAngle, 0); % using max to avoid negative values
    end
end

function [Ppv] = PVGeneration(Npv,Ta,Gg,Vmpp,Impp,Voc,Isc,Kv,Ki)
    
    FF = (Vmpp*Impp)/(Voc*Isc);
    Not = 42;
        
    for i = 1:length(Ta)
        Tc(i) = Ta(i) + Gg(i)*(Not - 20)/0.8;
        V(i) = Voc *(1 + Kv*(Tc(i) - 25)/100);
        I(i) = (Gg(i))*Isc*(1 + Ki*(Tc(i) - 25)/100);
        Ppv(i) = 0.9*Npv*V(i)*I(i)*FF/1000;       
    end
end      

function [Pwg] = WindGeneration(Nt,Ws,PolT,GP)

            
    Vi = 3;                  %cut-in
    Vo = 20;                 %cut-out
    
    for i = 1:length(Ws) 
        if Ws(i) < Vi
            Pwg(i) = 0;
        else if (Vi <= Ws(i) && Ws(i) < Vo)
                Pwg(i) = 0;
                for k = 1:(GP+1)
                    Pwg(i) = Pwg(i)+ Nt*(PolT(k)*Ws(i)^(GP+1-k));
                end
                if Pwg(i) < 0
                    Pwg(i) = 0;
                end
            else  Pwg(i) = 0;
            end
        end       
    end
end
    
