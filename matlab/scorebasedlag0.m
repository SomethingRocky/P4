
function [lag0] = scorebasedlag0(idxSpring,pksDistSort,tollags)

%Undersøger biderne mellem hvert spring en ad gangen
        %Giver score efter hvor mange der er i hver bid, og om de
        %indeholder multiplum

        antl = zeros(length(idxSpring)+1,1);
        suml = zeros(length(idxSpring)+1,1);
        gnsl = zeros(length(idxSpring)+1,1);
        prvIdx = [0;idxSpring(1:end)]+1;
        idxEnd = [idxSpring(1:end);numel(pksDistSort)];
        for i = 1:length(antl)
            antl(i) = length(pksDistSort(prvIdx(i):idxEnd(i)));
            suml(i) = sum(pksDistSort(prvIdx(i):idxEnd(i)));
            gnsl(i) = mean(pksDistSort(prvIdx(i):idxEnd(i)));
        end
        Santl = antl/sum(antl);
         
        %Ser om der er nogle gennemsnit, der er multiplum af de andre (alle
        %frekvenser er 1 multiplum af sig selv)
        n = zeros(length(antl));
        jaMulti = zeros(length(antl));
        for i=1:length(antl)
            n(i:end,i) = round(gnsl(i:end)/gnsl(i));
            jaMulti(i:end,i) = abs(gnsl(i:end) - n(i:end,i)*gnsl(i)) <= (n(i:end,i)*(tollags));
        end
        % jaMulti(jaMulti<0)=0;
        % jaMulti(~isfinite(jaMulti)) = 0;
        % n(~isfinite(n)) = 0;
        Smulti = sum(jaMulti,1)/length(antl);
        Smulti = Smulti';


        %Vægter antal højest og vælger den bid med højest score, hvis der
        %er flere ens tages gennemsnit
        Score = (3/8)*Santl + (5/8)*Smulti;  %Vægter små med multis lidt højere
        %disp([antl,Santl,sum(jaMulti,1)',Smulti,Score])
        idxScore = find(Score == max(Score));
        if isempty(idxScore)
            lag0 = nan;
        elseif isscalar(idxScore)
            %Hvis der ikke er nogle multiplum
            if Smulti(idxScore) == 1/length(antl)
                lag0 = gnsl(idxScore);
            %Hvis der er multiplum
            else
                multis = jaMulti(:,idxScore).*n(:,idxScore);
                idxnz = logical(multis>0);
                multis = multis(idxnz);
                gnslNorm = gnsl(idxnz) ./ multis;
                antlVaegt = antl(idxnz) .* multis;
                %Bestemmer den nye lag0
                lag0 = sum(gnslNorm .* antlVaegt) / sum(antlVaegt);
            end
        %Hvis der er flere bidder med samme score tag den med størst antal
        else
            antalsc = antl(idxScore);
            idxantal = find(antalsc == max(antalsc));
            %Hvis der er en med max antal
            if isscalar(idxantal)
                Smultisc = Smulti(idxScore);
                gnslsc = gnsl(idxScore);
                jaMultisc = jaMulti(:,idxScore);
                nsc = n(:,idxScore);
                %Hvis der ikke er nogle multiplum (udover i sin egen)
                if Smultisc(idxantal) == 1/length(antl)
                    lag0 = gnslsc(idxantal);
                %Hvis der er multiplum
                else
                    multis = jaMultisc(:,idxantal).*nsc(:,idxantal);
                    idxnz = logical(multis>0);
                    multis = multis(idxnz);
                    gnslNorm = gnsl(idxnz) ./ multis;
                    antlVaegt = antl(idxnz) .* multis;
                    %Bestemmer den nye lag0
                    lag0 = sum(gnslNorm .* antlVaegt) / sum(antlVaegt);
                end
            %Hvis der er flere med samme antal tages det laveste gennemsnit
            else
                %disp("Så' det så'n det er")
                gnslsc = gnsl(idxScore);
                lag0 = min(gnslsc);
                %lag0 = mean(gnslsc);
                %lag0 = nan;
            end
        end

        