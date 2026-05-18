

function [DroneFinal, Gnsf0El] = Tjekf0(f0Vec,NWindows,tolf0,droneRatio)

f0Sort = sort(f0Vec);
difff0 = diff(f0Sort);
idxSpring = find(difff0>tolf0*f0Sort(1));
%Tjekker, hvor mange, der er i hver bid
antf0 = zeros(length(idxSpring)+1,1);
sumf0 = zeros(length(idxSpring)+1,1);
gnsf0 = zeros(length(idxSpring)+1,1);
prvIdx = [0;idxSpring(1:end)]+1;
idxEnd = [idxSpring(1:end);numel(f0Sort)];
for i = 1:length(antf0)
    antf0(i) = length(f0Sort(prvIdx(i):idxEnd(i)));
    sumf0(i) = sum(f0Sort(prvIdx(i):idxEnd(i)));
    gnsf0(i) = mean(f0Sort(prvIdx(i):idxEnd(i)));
end
%Hvis der er en bid med antal stort nok
if any(antf0>=NWindows*droneRatio)
    DroneFinal = 1;
    idxNok = antf0>=NWindows*droneRatio;
    if nnz(idxNok) == 1
        Gnsf0El = gnsf0(idxNok);
    %Kommer aldrig til at være mere end to, så vælg mindste
    else
        Gnsf0El = gnsf0(find(idxNok,1,'first'));
    end
%Ellers tjek for multiplum
else
    n = zeros(length(antf0));
    jaMulti = zeros(length(antf0));
    sumantf0 = zeros(length(antf0));
    for i=1:length(antf0)
        n(i:end,i) = round(gnsf0(i:end)/gnsf0(i));
        jaMulti(i:end,i) = abs(gnsf0(i:end) - n(i:end,i)*gnsf0(i)) <= (n(i:end,i)*tolf0*f0Sort(1));
        sumantf0(:,i) = antf0 .* jaMulti(:,i);
    end
    %Ser om det hjalp
    if any(sum(sumantf0,1)>=NWindows*droneRatio)
        idxNok = sum(sumantf0,1)>=NWindows*droneRatio;
        Gnsf0El = gnsf0(find(idxNok,1,'first'));
        DroneFinal = 1;
    else
        DroneFinal = 0;
        Gnsf0El = mean(f0Vec);  
    end
end

