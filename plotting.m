
A = csvread('average_overhead_2021-03-09 23:40:50.896417.csv',...
            1,0);

histogram(A(:,2),100)


l = size(A,1);
maxima = zeros(1,l);
maxima(1)=A(1,2);

for i = 2:l 
    if maxima(i-1)>A(i,2)
        maxima(i)=maxima(i-1);
    else
        maxima(i)=A(i,2);
    end
end

figure
stairs(maxima)