
function [f0,nf0,FigurAuto] = findf0(Hraw,Deltaf,nSmooth, minFrek,maxDistFrek,Npeaks,minProm,tolfreq,stovsuger,figbrug)

FigurAuto = [];

AntalMinPeaks = 3; %minimum antal peaks i autokorrelationen for at den godkendes, >1, ulige

%Autokorrelation klargøring
Hm = Hraw - mean(Hraw);  %Fjerner "skrå envelope" for at kunne lave autocorrelation
H = normalize(Hm,'range');

%Laver autokorrelation, normaliserer og smoother
[HkorRaw,lags] = xcorr(H,H);  
%HkorRaw = sqrt(abs(HkorRaw)); %bedre på støj, samlet lidt værre - prom i stedet
Hkorsmooth = smoothdata(HkorRaw,'movmean',nSmooth);
Hkor = normalize(Hkorsmooth,'range');

%Finder peaks
%Laver et overslag på en min./max. lag mellem peaks
minLag = minFrek/Deltaf; 
maxDistLag = maxDistFrek/Deltaf;
[pks,locs] = findpeaks(Hkor,SortStr="descend", MinPeakDistance=minLag,NPeaks=Npeaks,MinPeakProminence=minProm*max(Hkor)); 

if stovsuger == 1
    %Tjekker for støvsugere...
    maxpks = maxk(pks,2);
    if ~isempty(pks) && length(maxpks)== 2 && maxpks(1) > 2*maxpks(2)
        %disp("autoStøvsuger")
        %Fjerner støvsugerpeaket
        clipLevel = maxpks(2);
        above = Hkor > clipLevel;
        d = diff([false; above(:); false]);
        startIdx = find(d == 1);
        endIdx   = find(d == -1) - 1;
        highestLoc = locs(1);
        k = find(highestLoc >= startIdx & highestLoc <= endIdx, 1);
        if ~isempty(k)
            i1 = startIdx(k);
            i2 = endIdx(k);
            n = i2 - i1 + 1;
            x = linspace(-1, 1, n);
            epsilon = 2*minProm * max(abs(Hkor));
            cap = clipLevel + epsilon * (1 - x.^2);
            Hkor(i1:i2) = cap;
        end
        %Normaliserer igen
        Hkorsmooth = smoothdata(Hkor,'movmean',nSmooth);
        Hkor = normalize(Hkorsmooth,'range');
        %Finder peaks
        [pks,locs] = findpeaks(Hkor,SortStr="descend", MinPeakDistance=minLag,NPeaks=Npeaks,MinPeakProminence=minProm*max(Hkor));      %VIGTIG SÆT MIN.DIST OG ANTAL PEAKS
    end
end


%Sikre, at jeg finder mere end 3 peaks, hvis muligt
locsNew = locs;
pksNew = pks;
smooth = 1;
prom = 1;
i = 3;
while length(locsNew)<=AntalMinPeaks && i > 0
    %Kigger uden smooth, hvis der kun er lavet en autokorrelation
    if smooth == 1
        %disp("Uden smooth")
        HkorNew = normalize(HkorRaw,'range');
        [pksNew,locsNew] = findpeaks(HkorNew,SortStr="descend", MinPeakDistance=minLag,NPeaks=Npeaks,MinPeakProminence=minProm*max(HkorNew));
        smooth = 0;
        i = i-1;
    %Sænker prominence m. 50% på smoothed resultater
    elseif prom == 1
        %disp("Mindre Prominence")
        PromNew = minProm-minProm*0.5;
        HkorNew = Hkor;
        [pksNew,locsNew] = findpeaks(HkorNew,SortStr="descend", MinPeakDistance=minLag,NPeaks=Npeaks,MinPeakProminence=PromNew*max(HkorNew));
        prom = 0;
        i = i-1;
    %Uden smooth med lavere prominence
    else
        %disp("Big Guns")
        HkorNew = normalize(HkorRaw,'range');
        PromNew = minProm*0.5;
        [pksNew,locsNew] = findpeaks(HkorNew,SortStr="descend", MinPeakDistance=minLag,NPeaks=Npeaks,MinPeakProminence=PromNew*max(HkorNew));
        i = i-1;
    end
end

%Sætter de nye lokationer - hvis while-loopet ikke har kørt ændres bare
%tilbage
locs = locsNew;
pks = pksNew;

%Laver figur, hvis ønsket
if figbrug == 1
    %Gemmer resultatet i en figur
    FigurAuto = figure('Visible','off');
        plot(lags,Hkor)
        hold on
        scatter(locs-locs(pks==max(pks)),pks)
        hold off
end

%Fjerne peaks med afstand mellem som er meget for store
pksDist = abs(diff(sort(locs)));
pksDistSort = sort(pksDist);
pksDistSort(pksDistSort>maxDistLag) = [];

%Hvis stadig ikke nok peaks slutter programmet
if length(pksDistSort) <= AntalMinPeaks-1
    %disp("Ingen Harmonisk Adfærd")
    lag0 = nan;

%Hvis der er peaks nok bruges disse til at finde f0
else
    
    %Undersøger om peaks ligger tæt på eller langt fra hinanden
    tollags = tolfreq/Deltaf;
    idxEnsV = diff(pksDistSort)<=tollags;
    idxForV = ~idxEnsV;
    idxSpring = find(idxForV);

    %Hvis de alle ligge inden for tolerancen bestemmes gennemsnittet.
    %Ellers undersøges, om der er afstande i multiplum af andre
    if isempty(idxSpring)
        lag0 = mean(pksDistSort);

    else 
        %Benytter hjælpefunktion
        lag0 = scorebasedlag0(idxSpring,pksDistSort,tollags);

    end

end

%På baggrund af de fundne lag0 bestemmes f0
f0 = lag0*Deltaf;
nf0 = (1:(Npeaks-1)/2)*f0;