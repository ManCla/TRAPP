
A = csvread('average_overhead_2021-03-09 23:40:50.896417.csv',...
            1,0);

histogram(A(:,2),100)