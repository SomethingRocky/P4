

function [Procent, Succeser, Ialt, Gnsf0Vec, FigureAuto, FigureMatch] = detektionsFunc(Koer, SNR, Antal, Filter, fig)


%Tolerancer defineres her!

%Til spektrogram
NBid = 6;   %Længden af hann vindue (round(length(y)/6)); 
pOverlap = 0.3;     %Procent overlap


%Til findf0, findpeaks og scorebasedlag0
nSmooth = 5;  %Længden af moving avg - 1 svarer til intet smooth
minFrek = 330;  %Sæt min 
maxDistFrek = 5*minFrek;  %Sæt max dist ml. peaks - husk plads til harmonik
Npeaks = 15;  %Sæt antal pks, ulige
minProm = 0.05;  %Sæt prominence af peaks
tolfreq = 0.15*400;  %Forventer f0 approx 400, så sat til 15% af dette


%Til DroneFound
%Tolerancer til findpeaks
%Sæt distance, prom og antal til findpeaks funktionen
disttol = 0.2;  %min distance tilladt mellem peaks
PromSpek = 0.05;  %min prominence af peaks
Nfind = 30;   %Antal peaks 
%Hvor mange gange højere må det højeste peak være (støvsuger...)
Gange = 5;  
%Tolerancer til findMatchedPeaks og shiftOrNor
NrMatch = 5;      %Antal peaks, der skal matche 
tol1 = 0.3; %Tolerancen på første peak for match
tol2 = 0.2; %Tolerancen på resten af peaks
Etjek = 1;  %Tjek faldende energi - som udgangspunkt 0



%Beslutning
droneRatio = 0.6;
GnsF0 = 1;   %Tjek for om tidsvinduer giver for forskellige f0'er - som udgangspunkt 1
tolf0 = 0.2;  %Tilladt forskel mellem gennemsnit - kan evt. ændres direkte til Hz



Succeser = 0;
Ialt = 0;
Procent = zeros(1,length(Koer));
loops = 0;


for Koer = Koer
    loops = loops + 1;
    SNRFlag = 0;



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


    %Initializing
    SuccesKoer = 0;
    nValid = 0;
    Gnsf0Vec = zeros(Antal,1);
    %Kører en fil af gangen
    for k = 1:Antal

        %Nulstiller DroneFinal
        DroneFinal = 0;


        %Sikre, at der først bliver lavet figurer på sidste k
        figbrug = 0;
        if fig == 1 && k == Antal
            figbrug = 1;
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
    
            filename_drone = fullfile(folder, files_d(droni).name);
            [sig_drone, fs_drone] = audioread(filename_drone);
            filename_noise = fullfile(folder2, files2(noisi).name);
            [sig_noise, fs_noise] = audioread(filename_noise);
            
            %Sætter samplefrekvense
            if fs_drone == fs_noise
                fs = fs_drone;
            else
                disp("Forskellig Fs")
                continue
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
                %disp("Invalid")
                continue
            end
    
            %Laver om til mono
            yraw = mean(yraw,2);
        end
        

        %Filtrerer
        if Filter == 1

        elseif Filter == 2

        elseif Filter == 3

        else
            yraw = fillmissing(yraw,'linear');
            %Filtrerer med et N ordens butterworth filter
            Nbut = 4;  %OBS! hvis ordenen hæves til noget for højt risikerer man ustabilitet
            Wn = [150 2500] / (fs/2);                                                                   %CUT-OFF FREKVENSERNE ER MEGET VIGTIGE
            [b,a] = butter(Nbut, Wn, 'bandpass');
            %Filtrerer
            y = filtfilt(b,a,yraw);

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
           for itid = 1:NWindows
               %Definerer data
                H = abs(s(:,itid));
                H = normalize(H,'range');

                %Bestemmer f0
                [f0,nf0,FigureAuto] = findf0(H,Deltaf,nSmooth,minFrek,maxDistFrek,Npeaks,minProm,tolfreq,figbrug);

                %Kører detektion så længe f0 ikke er nan
                if isnan(f0) 
                    DroneFlag = 0;  
                else 
                    %Detektion
                    [DroneFlag,FigureMatch] = DroneFound(H,f,f0,nf0,disttol,Nfind,PromSpek,Gange,NrMatch, Npeaks, tol1, tol2, Etjek, figbrug);
                end

                %Gemmer DroneFlag og f0
                DroneFundet(itid) = DroneFlag;
                f0Vec(itid) = f0;
            end


            %Undersøger, hvis angivet, om der er overensstemmelse i gennemsnit
            f0Vec = f0Vec(logical(DroneFundet));
            if GnsF0 == 1
                if isempty(f0Vec)
                    DroneFinal = 0;
                    Gnsf0Vec(k) = mean(f0Vec);  %Hvis f0Vec er tom bliver dette element NaN
                else
                    [DroneFinal, Gnsf0El] = Tjekf0(f0Vec,NWindows,tolf0,droneRatio);
                    Gnsf0Vec(k) = Gnsf0El;
                end
            %Hvis ikke angivet
            else
                %1 hvis drone, 0 hvis støj
                DroneFinal = nnz(DroneFundet) >= NWindows*droneRatio;
                Gnsf0Vec(k) = mean(f0Vec);  
            end

        end
            
        %Succes eller ikke succes
        if drone == 1 || drone == 2
            SuccesFlag = DroneFinal;
        else
            SuccesFlag = ~DroneFinal;
        end
        
        nValid = nValid + 1;
        SuccesKoer = SuccesKoer + SuccesFlag;

    end
    
    

    %Tjekker hvor god jeg har været
    if nValid > 0
        Procent(loops) = SuccesKoer/nValid;
    else
        Procent(loops) = nan;
    end
    Succeser = Succeser + SuccesKoer;
    Ialt = Ialt + nValid;

end










