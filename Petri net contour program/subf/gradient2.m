function [xx,yy] = grad(a,xax,yax)
%就是用差分法求梯度矩阵
%GRADIENT Approximate gradient.
%	[PX,PY] = GRADIENT(Z,DX,DY) returns the numerical partial derivatives(微分)
%	of matrix Z in matrices PX = dZ/dx and PY = dZ/dy.   DX and DY
%	may be scalars containing the sample spacing in the X and Y
%	directions, or they may be vectors containing all the explicit
%	locations.
%
%	[PX,PY] = GRADIENT(Z) assumes DX = DY = 1.
%
%	If Y is a vector, GRADIENT(Y) and GRADIENT(Y,DX) return the one
%	dimensional numerical derivative dY/dX.
%
%	For example, try
%	   [x,y] = meshgrid(-2:.2:2, -2:.2:2);
%	   z = x .* exp(-x.^2 - y.^2);
%	   [px,py] = gradient(z,.2,.2);
%	   contour(z),hold on, quiver(px,py), hold off
%
%	See also DIFF, DEL2, QUIVER, CONTOUR.

%	Charles R. Denham, MathWorks 3-20-89
%	Copyright (c) 1984-94 by The MathWorks, Inc.
%   本程序就是求梯度，采用办法和我《水平集研究记录》中有关求梯度的办法介绍是一样的。先求行，但是在求列时，而是把图像反转，用的还是求行的方式，有点
%   巧妙。
[m,n] = size(a); %a is the blured image
if nargin == 1, xax = 1; yax = 1; end %nargin参数个数
if nargin == 2, yax = xax; end
if length(xax) == 1, xax = xax .* (0:n-1); end %这行和下行要做什么
if length(yax) == 1, yax = yax .* (0:m-1); end

y = [];
ax = xax(:).';
for i = 1:2
   x = y;
   [m,n] = size(a);
   y = zeros(m, n);
   j = 1:m;
   if n > 1
      d = ax(2) - ax(1);
      y(j, 1) = (a(j, 2) - a(j, 1)) ./ d;     % Left edge.
      d = ax(n) - ax(n-1);
      y(j, n) = (a(j, n) - a(j, n-1)) ./ d;   % Right edge.
   end
   if n > 2
      k = 1:n-2;
      d = ones(m, 1) * (ax(k+2) - ax(k));
      y(j, k+1) = (a(j, k+2) - a(j, k)) ./ d;   % Middle.
   end
   a = a.';
   ax = yax(:).';
end
z = (x + sqrt(-1) .* y.');   %由于在求列的梯度的时候是把列转为行来求的，得到y，所以在表示一个点的梯度时，要把y进行转置，这样才符合实际情况
if nargout < 2
   xx = z;
 else
   xx = real(z); yy = imag(z);
end

