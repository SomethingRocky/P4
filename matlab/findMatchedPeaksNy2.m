
function [found, matchedPeaks, pksSzFound,nf0mVec,nf0LoopVec] = findMatchedPeaksNy2(nf0, pksSig2, pksSig2Sort, locsSig2, locsSig2Sort, Npeaks,f0,tol1,tol2)
    %Tjekker hvilke af de 20 fundne peaks i spektret, som matcher med de
    %forventede harmoniske peaks med en givet tolerance
    %Når jeg finder peaks, så gør jeg det ved at give hver peak en score
    %baseret på distance (lokal, global, harmonisk) amplitude overensstemmelse og så
    %vælge den bedste 
    tol3 = 2*tol2;
    
    %Definerer vægte
    w_dist = ones(3,1)*(2/9);
    w_amp = ones(3,1)*(1/9);
    %Uden en af disse [nf0Loop,nf0m,nf0(k)]
    % w_dist(1) = 0;
    % w_amp(1) = 0;

    %Initialising 
    found = zeros((Npeaks-1)/2,1);
    matchedPeaks = nan((Npeaks-1)/2,1);
    Npks = (Npeaks-1)/2;
    nf0mVec = zeros((Npeaks-1)/2,1);
    nf0LoopVec = zeros((Npeaks-1)/2,1);
    nf0m = nf0(1);
    nf0Loop = nf0(1);
    nf0mVec(1) = nf0m;
    nf0LoopVec(1) = nf0Loop;

    for k = 1:Npks
        if k == 1
            tol = tol1;
        else
            tol = tol2;
        end

        %Giver hvert peak en distance score fra 0 til 1, negativ når dist>tol.
        %Når de ligger længere væk end tolerancen sættes score 0.
        dist1 = abs(locsSig2Sort-nf0Loop);
        dist2 = abs(locsSig2Sort-nf0m);
        dist3 = abs(locsSig2Sort-nf0(k));
        dist = [dist1,dist2,dist3];
        freqs = [nf0Loop,nf0m,nf0(k)];

        %For hver af de tre frekvenser
        Score = zeros(length(locsSig2Sort),1);
        Samp = zeros(length(locsSig2Sort),3);
        Sdist = zeros(length(locsSig2Sort),3);
        for i = 1:length(freqs)
        %Scorer distancen
        SdistEl = 1 - dist(:,i)/(tol*f0);
        SdistEl(SdistEl<0) = 0;
        Sdist(:,i) = SdistEl;
        
        %Hvis der er valide peaks scores amplituden
        if nnz(Sdist(:,i))> 0
            SampEl = pksSig2Sort;
            %Giver hvert peak en amplitude score fra 0 til 1, igen kun af de
            %tilladte
            SampEl(~logical(Sdist(:,i))) = 0;
            SampEl = SampEl/max(SampEl);
            Samp(:,i) = SampEl;
        else
            SampEl = zeros(length(locsSig2Sort),1);
            Samp(:,i) = SampEl;
        end

        %Finder scoren
        Score = Score + w_dist(i)*Sdist(:,i) + w_amp(i)*SampEl;

        end

                
     %Hvis der er gyldige peaks vælges det bedste
     if nnz(Score)>0
        %Finder tilhørende idxer 
        [~,idx] = max(Score);
        found(k) = 1;
        matchedPeaks(k) = locsSig2Sort(idx);
        nf0Loop = matchedPeaks(k) + f0;
        [~,idxmin] = min([dist1(idx),dist2(idx),dist3(idx)]);
        if length(idxmin) > 1
            nfOld = mean(freqs(idxmin));
        else
            nfOld = freqs(idxmin);
        end           
        nf0m = nfOld + f0;
    %Hvis der ikke er nogen gyldige peaks sættes
    else
        nf0Loop = nf0Loop + f0;
        nf0m = nf0m + f0;
     end

    %Tjekker helt til sidst, at mine forventede frekvenser ikke kommer
    %for langt fra hinanden
    if k < Npks
        while abs(nf0m-nf0(k+1))>= tol3*f0
            nf0m = 0.8*nf0m + 0.2*nf0(k+1);
        end
        while abs(nf0Loop-nf0(k+1))>= tol3*f0
            nf0Loop = 0.8*nf0Loop + 0.2*nf0(k+1);
        end
        nf0mVec(k+1) = nf0m;
        nf0LoopVec(k+1) = nf0Loop;
    end
    end

    %Slutter af med at definerer det sidste
    [tf, idxMatch] = ismember(matchedPeaks, locsSig2);
    idxMatch(tf == 0) = [];
    pksSzFound = pksSig2(idxMatch);


   


    