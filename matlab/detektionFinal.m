%% Detektion af drone

close all





nForsoeg = 3000;
SNR = [20,5,2,0.5,-2,-5,-10,-20];
%SNR = [20,0.5,-20];
Antal = 1; %Kan gå op til 300
Koer = [3,2];  %0: ren støj, 1: ren drone, 2: drone med støj, 3: støj med støj
fig = 0;   %Vil jeg have dannet figure? Som udgangspunkt sat til 0!!!
Filter = 1; % 1: Bilinear, 2: Vindue, 3: MatLabs indbyggede Butter, 4: Uden filter


ProcentMatSam = [];
ProcentTotGns = zeros(length(nForsoeg),1);
GnsMat = [];
for i = 1:nForsoeg
ProcentMat = zeros(length(SNR),length(Koer)+1);
SucceserSam = 0;
IaltSam = 0;
Gnsf0 = [];
for n = 1:length(SNR)

    Snr = SNR(n);
    [Procent, Succeser, Ialt, Gnsf0Vec, FigureAuto, FigureMatch] = detektionsFunc(Koer, Snr, Antal, Filter, fig);

    SucceserSam = SucceserSam + Succeser;
    IaltSam = IaltSam + Ialt;
    ProcentMat(n,:) = [Procent,Succeser/Ialt];
    Gnsf0 = cat(2,Gnsf0,Gnsf0Vec);
    
end

ProcentSamlet = SucceserSam/IaltSam;
ProcentTotGns(i) = ProcentSamlet;
ProcentMatSam = cat(3,ProcentMatSam,ProcentMat);
GnsMat = cat(3,GnsMat,Gnsf0);

end


ProcentGns = mean(ProcentMatSam,3,'omitmissing');
ProcentStd = std(ProcentMatSam,0,3,'omitmissing');
TotProcentGns = mean(ProcentTotGns);
TotProcentStd = std(ProcentTotGns);

Gnsf01 = mean(GnsMat,1,'omitmissing');
Gnsf0Fin = mean(Gnsf01,3,'omitmissing');




%Vis figurer 
if fig == 1
set(FigureAuto, 'Visible', 'on')
set(FigureMatch, 'Visible', 'on')
end











