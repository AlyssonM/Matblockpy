function DLEMcontract(Power_gen,load1,load2,load3)

%pyenv("Version","D:\MATLAB\.gridenv\Scripts\python.exe"); 
% mod = py.importlib.import_module('ipfs');
% py.importlib.reload(mod);

%dados de entrada
% - preço do kW/h de energia tatifa branca
a = 0.56634; %FP
b = 0.81626; %INT
c = 1.22498; %P

% - Custo variável durante o dia, tarifa TOU(Time-Of-use): tarifa branca
TOU= [a  a  a  a  a  a  c  c  c  b   b   b   a    a    a    b    b   c    c    c    b     b    a    a];
%horasDoDia = [1  2  3  4  5  6  7  8  9  10  11  12  13   14  15   16   17   18   19   20   21   22   23   24];
TFI = 0.47;

Rp = py.numpy.array([]);
for i=1:24
    Rp = py.numpy.append(Rp,TOU(i));
end
py.ipfs.startLEM(Rp);

P1_gen = py.numpy.array([]);
P1_price = py.numpy.array([]);
P2_gen = py.numpy.array([]);
P2_price = py.numpy.array([]);
P3_gen = py.numpy.array([]);
P3_price = py.numpy.array([]);
C1_load = py.numpy.array([]);
C1_price = py.numpy.array([]);
C2_load = py.numpy.array([]);
C2_price = py.numpy.array([]);
C3_load = py.numpy.array([]);
C3_price = py.numpy.array([]);

Prosumer1_gen = interp1(0:0.25:23.75,table2array(Power_gen(:,1))',0:23, 'linear');
Prosumer1_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.5*rand - 0.5);
Prosumer2_gen = interp1(0:0.25:23.75,table2array(Power_gen(:,2))',0:23, 'linear');
Prosumer2_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.5*rand - 0.5);
Prosumer3_gen = interp1(0:0.25:23.75,table2array(Power_gen(:,3))',0:23, 'linear');
Prosumer3_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.5*rand - 0.5);

for i=1:24
    P1_gen = py.numpy.append(P1_gen,Prosumer1_gen(i));
    P1_price = py.numpy.append(P1_price,Prosumer1_price(i));
    P2_gen = py.numpy.append(P2_gen,Prosumer2_gen(i));
    P2_price = py.numpy.append(P2_price,Prosumer2_price(i));
    P3_gen = py.numpy.append(P3_gen,Prosumer3_gen(i));
    P3_price = py.numpy.append(P3_price,Prosumer3_price(i));
end

% client1 = [table2array(Power_gen(:,1))', P1_price];
% client2 = [table2array(Power_gen(:,1))', P2_price];


py.ipfs.Register('client1','PV-1',1);
py.ipfs.Register('client2','PV-2',1);
py.ipfs.Register('client3','PV-3',1);
py.ipfs.Register('client4','CU-1',0);
py.ipfs.Register('client5','CU-2',0);
py.ipfs.Register('client6','CU-3',0);
py.ipfs.DLEMbid('client1', P1_gen, P1_price);
py.ipfs.DLEMbid('client2', P2_gen, P2_price);
py.ipfs.DLEMbid('client3', P3_gen, P3_price);

Consumer1_load = load1/5;
Consumer1_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.3*rand - 0.3);
Consumer2_load = load2/5;
Consumer2_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.3*rand - 0.3);
Consumer3_load = load3/5;
Consumer3_price = ((TFI + TOU)/2) + ((TFI + TOU)/16)*(1.3*rand - 0.3);

for i=1:24
    C1_load = py.numpy.append(C1_load,(-1*Consumer1_load(i)));
    C1_price = py.numpy.append(C1_price,Consumer1_price(i));
    C2_load = py.numpy.append(C2_load,(-1*Consumer2_load(i)));
    C2_price = py.numpy.append(C2_price,Consumer2_price(i));
    C3_load = py.numpy.append(C3_load,(-1*Consumer3_load(i)));
    C3_price = py.numpy.append(C3_price,Consumer3_price(i));
end
py.ipfs.DLEMbid('client4', C1_load, C1_price);
py.ipfs.DLEMbid('client5', C2_load, C2_price);
py.ipfs.DLEMbid('client6', C3_load, C3_price);

disp("Clear Local Energy Post-Market");
py.ipfs.MarketData()
py.ipfs.getTransactions()
%py.ipfs.Demand_response();
%py.ipfs.TradeEnergyMatched();
%BidsLength = py.ipfs.getBidsLength();
%Bids = py.ipfs.getBids();
end