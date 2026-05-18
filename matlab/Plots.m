
Shift = 0;
f0 = 0;
%while f0<=650 || Shift == 0
    Shift = 0;
    f0 = 0;
%Indlæser lydfil
SNR = -5;
Antal = 1; %Kan gå op til 300
Koer = 2;  %0: ren støj, 1: ren drone, 2: drone med støj, 3: støj med støj
Filter = 1; % 1: Bilinear, 2: Vindue, 3: MatLabs indbyggede Butter, 4: Uden filter

%Til spektrogram
NBid = 6;   %Længden af hann vindue (round(length(y)/6)); 
pOverlap = 0.3;     %Procent overlap


%Til findf0, findpeaks og scorebasedlag0
nSmooth = 10;  %Længden af moving avg - 1 svarer til intet smooth
minFrek = 330;  %Sæt min 
maxDistFrek = 5*minFrek;  %Sæt max dist ml. peaks - husk plads til harmonik
Npeaks = 15;  %Sæt antal pks, ulige, 19, 19, 15, 15
minProm = 0.04;  %Sæt prominence af peaks - MEGET vigtig, hæv den for mere støj, små bidder gør meget 0.0775, 0.068, 0.06, 0.07
tolfreq = 0.15*400;  %Forventer f0 approx 400, så sat til 10% af dette
stovsuger = 0;


%Til DroneFound
%Tolerancer til findpeaks
%Sæt distance, prom og antal til findpeaks funktionen
disttol = 0.2;  %min distance (*f0) tilladt mellem peaks 0.25, 0.2, 0.2, 0.2
PromSpek = 0.085;  %min prominence af peaks 0.11, 0.85, 0.1, 0.0925
Nfind = 30;   %Antal peaks 
%Hvor mange gange højere må det højeste peak være (støvsuger...)
Gange = 3;  %2, 3, 2, 2
%Tolerancer til findMatchedPeaks og shiftOrNor
NrMatch = 5;      %Antal peaks, der skal matche - vælger 5
tol1 = 0.25; %Tolerancen på første peak for match - skal ikke være mindre end disttol/2 0.3, 0.25, 0.25, 0.25
tol2 = 0.2; %Tolerancen på resten af peaks 0.2, 0.2, 0.2, 0.2
Etjek = 1;  %Tjek faldende energi - som udgangspunkt 0, giver ikke mening
tolE = 1; %Hvor mange gange mere energi i de højeste vs laveste

%Beslutning
droneRatio = 0.5;
GnsF0 = 1;   %Tjek for om tidsvinduer giver for forskellige f0'er - som udgangspunkt 1
tolf0 = 0.2;  %Tilladt forskel mellem gennemsnit - kan evt. ændres direkte til Hz 0.25, 0.2, 0.15, 0.15

figbrug = 0;


%Nulstiller DroneFinal
DroneFinal = 0;

%Fortæller om jeg kigger på droner, støj eller blandet
drone = Koer; 
if drone == 1
    navn = "\data\drone";
elseif drone == 0
    navn = "\data\noise";
elseif drone == 2 || drone == 3
    SNRFlag = 1;
end

path = fileparts(mfilename('fullpath'));
if SNRFlag == 0

    %Indlæser og gemmer navne
    folder = path+navn;  % <- din sti
    files = dir(fullfile(folder, '*.wav'));
else
    %Indlæser mappe
    folder1 = path+"\data\drone";  % <- din sti
    files1 = dir(fullfile(folder1, '*.wav'));
    folder2 = path+"\data\noise";  % <- din sti
    files2 = dir(fullfile(folder2, '*.wav'));
    %Bland drone med støj eller støj med støj
        if drone == 2
            folder = folder1;
            files_d = files1;
        elseif drone == 3
            folder = folder2;
            files_d = files2;
        end
end



%Lav signal med ønsket SNR
%Indlæser lydfil
if SNRFlag == 0
    filename = fullfile(folder, files(k).name);
    [yraw, fs] = audioread(filename);
    %Laver om til mono
    yraw = mean(yraw,2);
else
   %Vælg random drone - finder random intergers mellem 1 og
    %length(files)
    droni = randi(length(files_d));
    noisi = randi(length(files2));
    disp(droni)
    disp(noisi)

    filename_drone = fullfile(folder, files_d(198).name); %120 235  129
    [sig_drone, fs_drone] = audioread(filename_drone);
    filename_noise = fullfile(folder2, files2(225).name); %128 37   111
    [sig_noise, fs_noise] = audioread(filename_noise);
    
    %Sætter samplefrekvense
    if fs_drone == fs_noise
        fs = fs_drone;
    else
        disp("Forskellig Fs")
    end

    %Tjekker at signalerne har sammen længde
    if length(sig_noise) < length(sig_drone)
        sig_noise = paddata(sig_noise, length(sig_drone), Side="both");
    else
        sig_noise = sig_noise(1:length(sig_drone));
    end


    % Calculate signal and noise power
    drone_power = mean(sig_drone.^2);
    noise_power = mean(sig_noise.^2);


    %Only add noise if both signal and noise have valid power
    if drone_power > 0 && noise_power > 0
        %Convert SNR from dB to linear
        snr_linear = 10 ^ (SNR / 10);

        %Calculate scaling factor for noise
        noise_scale = sqrt(drone_power / (snr_linear * noise_power + eps));

        %Mix signal with scaled noise
        sig = sig_drone + noise_scale * sig_noise;

        %Normalize to prevent clipping
        max_val = max(abs(sig));
        if max_val > 0 
            sig = sig ./ max_val;
        end

        %Ensure no NaN values
        yraw = rmmissing(sig);
    else
        disp("Invalid")
    end

    %Laver om til mono
    yraw = mean(yraw,2);
    yraw = fillmissing(yraw,'linear');
end


%Filtrerer
if Filter == 1   %Bilinear
    %Dette er et fjerde ordens Butterworth filter
    pad = zeros(4,1);
    x = [pad;yraw;pad];
    yf = zeros(length(x),1);
    for n = length(pad)+1:length(pad)+length(yraw)
        yf(n) = 2.69136*yf(n-1)-2.70948*yf(n-2)+1.29657*yf(n-3)-0.28040*yf(n-4)+0.12584*x(n)-0.25168*x(n-2)+0.12584*x(n-4);
    end
    y = yf(length(pad)+1:length(pad)+length(yraw));

elseif Filter == 2   %Vinduesmetoden
    %Benytter 200 orden hann filter (på det ideelle båndpas filter)
    L = 201;
    n = (0:L-1)';
    alpha = (L-1)/2;
    w1 = 2*pi*150/fs; w2 = 2*pi*2500/fs; 
    h_ideel = (1/pi) * (w2*sinc((w2/pi)*(n-alpha)) - w1*sinc((w1/pi)*(n-alpha)));
    h_hann = 0.5 - 0.5*cos(n*(2*pi/(200-1)));
    h = h_ideel .* h_hann;
    %Filtrerer med convolve
    y = conv(yraw,h,'same');

elseif Filter == 3
    %Filtrerer med et N ordens butterworth filter
    Nbut = 4;  %OBS! hvis ordenen hæves til noget for højt risikerer man ustabilitet
    Wn = [150 2500] / (fs/2);                                                                   %CUT-OFF FREKVENSERNE ER MEGET VIGTIGE
    [b,a] = butter(Nbut, Wn, 'bandpass');
    %Filtrerer
    y = filtfilt(b,a,yraw);

else
    %Uden filter
    y = yraw;

end



% Laver spektrogram 
%Specifiere at jeg vil lave ca. 8 bidder med 30% overlap 
NSTFT = round(length(y)/NBid); 
[s,fraw,~,~] = spectrogram(y,hann(NSTFT),round(pOverlap*NSTFT));  
f = fs*fraw/(2*pi);   %Laver frekvensvektor i Hz i stedet for radianer
Deltaf = (fs/2)/length(f);  %Frekvensopløsning
NWindows = size(s,2);


%Tjekker allerførst at der rent faktisk er et signal
signal = 1;
if sum(sum(s))==0 
    signal = 0;
    DroneFinal = 0;
    Gnsf0Vec(k) = nan;
end


%Hvis der er et signal undersøges hvert tidsvindue
if signal == 1 

    %Initializing
   DroneFundet = zeros(NWindows,1);
   f0Vec = zeros(NWindows,1);
   for itid = 3
       %Definerer data
        H = abs(s(:,itid));
        Hraw = normalize(H,'range');

        AntalMinPeaks = 5; %minimum antal peaks i autokorrelationen for at den godkendes, >1, ulige

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
            if ~isempty(pks) && length(maxpks)== 2 && maxpks(1) > 1.5*maxpks(2)
                disp("autoStøvsuger")
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
        while length(locsNew)<=3 && i > 0
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
        
        figure(1);
        plot(lags*Deltaf,Hkor)
        hold on
        scatter((locs-(length(lags)-1)/2)*Deltaf,pks)
        hold off


        %Fjerne peaks med afstand mellem som er meget for store
        pksDist = abs(diff(sort(locs)));
        pksDistSort = sort(pksDist);
        pksDistSort(pksDistSort>maxDistLag) = [];
        
        %Hvis stadig ikke nok peaks slutter programmet
        if length(pksDistSort) < AntalMinPeaks-1
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


        %Kører detektion så længe f0 ikke er nan
        if isnan(f0) 
            DroneFlag = 0;  
        else 
            %Detektion
            %Finder de 20 største peaks i spektrummet 
            [pksSig2,locsSig2] = findpeaks(H,f,SortStr="descend",MinPeakDistance=disttol*f0,NPeaks=Nfind, MinPeakProminence=PromSpek*max(H)); 
            %Sortere efer rækkefølge af frekvenser
            mat = [locsSig2,pksSig2]; matSort = sortrows(mat,"ascend");
            locsSig2Sort = matSort(:,1);
            pksSig2Sort = matSort(:,2); 
            
            
            %Tjekker for støvsugere...
            maxPks = maxk(pksSig2,2);
            if ~isempty(pksSig2) && length(maxPks)== 2 && maxPks(1) > Gange*maxPks(2)
                %Fjerner støvsugerpeaket
                disp("Støvsuger")
                clipLevel = maxPks(2);
                above = H > clipLevel;
                d = diff([false; above(:); false]);
                startIdx = find(d == 1);
                endIdx   = find(d == -1) - 1;
                highestLoc = locsSig2(1);
                k = find(highestLoc >= startIdx & highestLoc <= endIdx, 1);
                if ~isempty(k)
                    i1 = startIdx(k);
                    i2 = endIdx(k);
                    n = i2 - i1 + 1;
                    x = linspace(-1, 1, n);
                    epsilon = PromSpek * max(abs(H));
                    cap = clipLevel + epsilon * (1-x.^2);
                    H(i1:i2) = cap;
                end
                %Normaliserer igen
                H = normalize(H,'range');
                %Bestemmer en ny f0 
                [f0new,nf0new,~] = findf0(H,Deltaf,nSmooth,minFrek,maxDistFrek,Npeaks,minProm,tolfreq,stovsuger,figbrug);
                if isfinite(f0new)
                    f0 = f0new;
                    nf0 = nf0new;
                end
                %Finder peaks
                [pksSig2,locsSig2] = findpeaks(H,f,SortStr="descend",MinPeakDistance=disttol*f0,NPeaks=Nfind, MinPeakProminence=PromSpek*max(H));       %VIGTIG SÆT MIN.DIST OG ANTAL PEAKS
                %Sortere efer rækkefølge
                mat = [locsSig2,pksSig2]; matSort = sortrows(mat,"ascend");
                locsSig2Sort = matSort(:,1);
                pksSig2Sort = matSort(:,2); 
            end
            
            
            %Undersøger om jeg kan finde peaks som matcher min f0
            [found, matchedPeaks, pksSzFound, nf0mVec,nf0LoopVec] = findMatchedPeaksNy2(nf0, pksSig2, pksSig2Sort, locsSig2, locsSig2Sort, Npeaks,f0,tol1,tol2);
            
            
            %Tjekker om mine frekvenser kan shiftes
            [nf0shift, Shift] = ShiftOrNot(nf0, pksSig2Sort, locsSig2Sort,f0,tol1,tol2);
            %Hvis ja, ser om jeg får bedre resultater
            if Shift == 1
                [foundSh, matchedPeaksSh, pksSzFoundSh,nf0mVecSh,nf0LoopVecSh] = findMatchedPeaksNy2(nf0shift, pksSig2, pksSig2Sort, locsSig2, locsSig2Sort, Npeaks,f0,tol1,tol2);
                %Hvis begge finder 5 eller flere matches vælges den med de
                %største matchende peaks
                if sum(foundSh) >= NrMatch && sum(found) >= NrMatch
                    if sum(pksSzFoundSh(1:NrMatch)) > sum(pksSzFound(1:NrMatch))
                        Shift = 1;
                    else
                        Shift = 0;
                    end
                elseif sum(foundSh) >= NrMatch && sum(found) < NrMatch
                    Shift = 1;
                else
                    Shift = 0;
                end
                %Sætter nye værdier
                % if Shift == 1
                %     disp("Shift")
                %     found = foundSh;
                %     matchedPeaks = matchedPeaksSh;
                %     pksSzFound = pksSzFoundSh;
                %     nf0 = nf0shift;
                %     nf0mVec = nf0mVecSh;
                %     nf0LoopVec = nf0LoopVecSh;
                % end
            end
            
            
            %Tjekker, om der er fundet peaks nok
            if sum(found)>=NrMatch  
                if Etjek == 1
                    %Tjekker om energi af peaks er faldende
                    E_low  = sum(pksSzFound(1:3));
                    E_high = sum(pksSzFound(end-2:end)); 
                    DroneFlag = E_low > tolE*E_high;
                else
                    DroneFlag = 1;
                end
            else
                DroneFlag = 0;                
            end
            
            %Laver figur, hvis ønsket
            figure(2);
            plot(f,H,LineWidth=0.9)
            hold on
            scatter(locsSig2,pksSig2,"v","filled", "MarkerFaceColor","b","MarkerEdgeColor","b")
            hold on
            %Indexer for de matchende peaks
            [tf, idxMatch] = ismember(matchedPeaks, locsSig2);
            idxMatch(tf == 0) = [];
            scatter(locsSig2(idxMatch),pksSig2(idxMatch),"v","filled", "MarkerFaceColor","g","MarkerEdgeColor","g")
            ylim([0,1.1])
            %xlim([0,4000])
            hold on
            %xline(nf0,Color="r",LineWidth=1)
            hold on
            %xline(nf0mVec,Color='k')
            hold on
            %xline(nf0LoopVec,Color="m")
            hold off
        
        
        
        end



        %Gemmer DroneFlag og f0
        DroneFlag;
        f0
        pksDistSort';
   end

end
%end



