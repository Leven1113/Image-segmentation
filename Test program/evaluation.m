% function [ P, R, F ] = evaluation(Iseg,Ians)
% Evaluation
%����ԭͼ���Ǹ����Գ���Ȼ��������ָ��ͼ����������ԭͼ����һ����׼�ķָ�������ɫ������ķָ�������ɫ�������غϺã�˵���ָ�����

Iseg = imread('test15.png');
Ians = imread('test1525.png');
Iseg = rgb2gray(Iseg);
Ians = rgb2gray(Ians);
test15 = max(max(Iseg));
test1525 = max(max(Ians));
Iseg = uint8(Iseg/test15);
Ians = uint8(Ians/test1525);
[m,n] = size(Iseg);
c11 = 0; c01 = 0; c10 = 0;
for i = 1:m
    for j = 1:n
        if  (Ians(i,j) == 1 && Iseg(i,j) == 1) 
            c11 = c11 + 1;
        end
        if  (Ians(i,j) == 0 && Iseg(i,j) == 1) 
            c01 = c01 + 1;
        end
         if  (Ians(i,j) == 1 && Iseg(i,j) == 0) 
            c10 = c10 + 1;
         end
    end
end
P = c11 / (c11+c10);
R = c11 / (c11+c01);
F = 2 * P * R / (P + R);

Ians = Ians*255;
Iseg = Iseg*255;
% IansS = zeros(m,n,3);
% IsegS = zeros(m,n,3);
% IansS(:,:,1) = Ians;
% IsegS(:,:,3) = Iseg;
% figure;imshow(uint8(IansS));
% hold on
% imshow(uint8(IsegS));
I = zeros(m,n,3);
I(:,:,1) = Ians;
I(:,:,3) = Iseg;
figure;
imshow(uint8(I));
title('������죨��𣩣��������ǵĽ����');
        
% end

