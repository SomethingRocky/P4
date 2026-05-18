

function [nf0new, Shift] = ShiftOrNot(nf0, pksSort, locsSort,f0,tol1,tol2)
    %En funktion der tjekker, om der ligger et tidligere harmoniske peak
    %før den forventede f0, og shifter om nødvendigt
    idexes = locsSort <= f0*(1-tol1);  
    pksLow = pksSort(idexes);
    locsLow = locsSort(idexes);
    locsHigh = locsSort(~idexes);


    %Hvis der ligger et peak inden for tol1 af fundamental frekvensen som
    %er højere eller lig med dem under f0 OG som har en harmonisk frekvens, så shifter jeg ikke
    [dist3min,idx3min] = mink(abs(locsSort-f0),3);
    idxmvalid = dist3min <= tol1*f0;
    idxmvalid = idx3min(idxmvalid);
    mxOf0 = max(pksSort(idxmvalid));
    if isempty(mxOf0) || isnan(mxOf0)
        mxOf0 = 0;
    end
    %Det jeg skal bruge til at tjekke for harmonisk peak
    nypksSort = pksSort;
    nypksSort(~idxmvalid) = 0;
    nyIndex = nypksSort == mxOf0;
    nytalindex = find(nyIndex,1,"first");
    nyLocsSort = locsSort(nytalindex+1:end);
    if ~isempty(pksLow) && ~isempty(nyLocsSort) && mxOf0 >= max(pksLow) && min(abs(nyLocsSort-(locsSort(nytalindex)+f0))) < tol2*f0
        %disp("Intet Shift")
        Shift = 0;
        nf0new = nf0;
    else
    %Tjekker om de tre største (virker også selvom der er færre end 3 eller
    %ingen) har harmoniske frekvenser
    [pks3,idx3] = maxk(pksLow,3);
    locs3 = locsLow(idx3);
    %Definerer tolerance
    valid = zeros(length(locs3),1);
    for k = 1:length(locs3)
        %Tjekker om der er harmoniske frekvenser inden for tolerancen
        harm1 = abs(locsHigh-(locs3(k)+f0))<tol2*f0;
        if sum(harm1) > 0
            valid(k) = 1;
        end
    end
    %Hvis der er valid peaks shiftes til den største, ellers shiftes ikke
    if sum(valid) > 0
        valid = logical(valid);
        [~,idxmax] = max(pks3(valid));
        nf0new = nf0 - (f0 - locs3(idxmax));
        Shift = 1;
    else
        %disp("Intet Shift")
        nf0new = nf0;
        Shift = 0;
    end
    end