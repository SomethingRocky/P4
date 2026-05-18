

function [DroneFlag,FigureMatch] = DroneFound(H,f,f0,nf0,disttol,Nfind,PromSpek,Gange,NrMatch, Npeaks, tol1, tol2, tolE, Etjek, Deltaf,nSmooth,minFrek,maxDistFrek,minProm,tolfreq,stovsuger,figbrug)

FigureMatch = [];

%Finder de 20 største peaks i spektrummet 
[pksSig2,locsSig2] = findpeaks(H,f,SortStr="descend",MinPeakDistance=disttol*f0,NPeaks=Nfind, MinPeakProminence=PromSpek*max(H)); 
%Sortere efer rækkefølge af frekvenser
mat = [locsSig2,pksSig2]; matSort = sortrows(mat,"ascend");
locsSig2Sort = matSort(:,1);
pksSig2Sort = matSort(:,2); 


%  %Tjekker for støvsugere...
% maxPks = maxk(pksSig2,2);
% if ~isempty(pksSig2) && length(maxPks)== 2 && maxPks(1) > Gange*maxPks(2)
%     %Fjerner støvsugerpeaket
%     %disp("Støvsuger")
%     clipLevel = maxPks(2);
%     above = H > clipLevel;
%     d = diff([false; above(:); false]);
%     startIdx = find(d == 1);
%     endIdx   = find(d == -1) - 1;
%     highestLoc = locsSig2(1);
%     k = find(highestLoc >= startIdx & highestLoc <= endIdx, 1);
%     if ~isempty(k)
%         i1 = startIdx(k);
%         i2 = endIdx(k);
%         n = i2 - i1 + 1;
%         x = linspace(-1, 1, n);
%         epsilon = PromSpek * max(abs(H));
%         cap = clipLevel + epsilon * (1-x.^2);
%         H(i1:i2) = cap;
%     end
%     %Normaliserer igen
%     H = normalize(H,'range');
%     %Bestemmer en ny f0 
%     [f0new,nf0new,~] = findf0(H,Deltaf,nSmooth,minFrek,maxDistFrek,Npeaks,minProm,tolfreq,stovsuger,figbrug);
%     if isfinite(f0new)
%         f0 = f0new;
%         nf0 = nf0new;
%     end
%     %Finder peaks
%     [pksSig2,locsSig2] = findpeaks(H,f,SortStr="descend",MinPeakDistance=disttol*f0,NPeaks=Nfind, MinPeakProminence=PromSpek*max(H));       %VIGTIG SÆT MIN.DIST OG ANTAL PEAKS
%     %Sortere efer rækkefølge
%     mat = [locsSig2,pksSig2]; matSort = sortrows(mat,"ascend");
%     locsSig2Sort = matSort(:,1);
%     pksSig2Sort = matSort(:,2); 
% end


%Tjekker for støvsugere...
maxPks = maxk(pksSig2,2);
if ~isempty(pksSig2) && length(maxPks)== 2 && maxPks(1) > Gange*maxPks(2)
    %Fjerner støvsugerpeaket
    H(H>maxPks(2)) = maxPks(2);
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
[found, matchedPeaks, pksSzFound,~,~] = findMatchedPeaksNy2(nf0, pksSig2, pksSig2Sort, locsSig2, locsSig2Sort, Npeaks,f0,tol1,tol2);


%Tjekker om mine frekvenser kan shiftes
[nf0shift, Shift] = ShiftOrNot(nf0, pksSig2Sort, locsSig2Sort,f0,tol1,tol2);
%Hvis ja, ser om jeg får bedre resultater
if Shift == 1
    [foundSh, matchedPeaksSh, pksSzFoundSh,~,~] = findMatchedPeaksNy2(nf0shift, pksSig2, pksSig2Sort, locsSig2, locsSig2Sort, Npeaks,f0,tol1,tol2);
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
    if Shift == 1
        %disp("Shift")
        found = foundSh;
        matchedPeaks = matchedPeaksSh;
        pksSzFound = pksSzFoundSh;
        nf0 = nf0shift;
    end
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
if figbrug == 1
    %Gemmer resultatet i en figur
    FigureMatch = figure('Visible','off');
    plot(f,H)
    hold on
    scatter(locsSig2,pksSig2,"v","filled", "MarkerFaceColor","b","MarkerEdgeColor","b")
    hold on
    %Indexer for de matchende peaks
    [tf, idxMatch] = ismember(matchedPeaks, locsSig2);
    idxMatch(tf == 0) = [];
    scatter(locsSig2(idxMatch),pksSig2(idxMatch),"v","filled", "MarkerFaceColor","g","MarkerEdgeColor","g")
    xline(nf0,Color="r")
    hold off
else
    FigureMatch = [];
end
