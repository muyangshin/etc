function [] = SunEarthMoon(years,framerate)
%% Clean Up
close all
clc

%% Initializaion
x_earth = 147300000000; % dist from sun to earth [m]
x_mercury = 57910000000; % dist from sun to mercury [m]
v_earth = 30257; % orbital speed [m/s]
v_mercury = 47360; % orbital speed [m/s]
r_sat = 384748000; % dist from earth to the moon [m]
% r_earth = 6367000; % earth radius [m]
% r_mercury = 2440000; % mercury radius [m]
v_sat = 1023; % relative velocity from earth [m/s]
a = 5.145; % Angle to vertical (y) axis 
b = 90; % Angle to horizontal (x) axis in xz plane

x_earth_o = [x_earth; 0; 0];
x_sun_o = [0; 0; 0];
x_sat_o = [x_earth+r_sat; 0; 0];
x_mercury_o = [x_mercury; 0; 0];
v_earth_o = [0; v_earth; 0];
v_sun_o = [0; 0; 0];
v_sat_o = v_sat*[cos(pi/180*b)*sin(pi/180*a); cos(pi/180*a); sin(pi/180*b)*sin(pi/180*a)] + v_earth_o;
v_mercury_o = [0; v_mercury; 0];
interval = years*[0 31536000];

%% Error Control
h = [0.01 36000];
tol = 100000;
Options.AbsTol = tol;
Options.MaxStep = h(2);
Options.InitialStep = h(1);

%% Analysis
ao = [x_earth_o; v_earth_o; x_sun_o; v_sun_o; x_sat_o; v_sat_o; x_mercury_o; v_mercury_o]; 
[t, x] = ode45(@earthfinal,interval,ao,Options);

%% Plots
q = framerate;
scrsz = get(0,'ScreenSize');
figure('position', [0.05*scrsz(3) 0.05*scrsz(4) 0.75*scrsz(3) 0.45*scrsz(4)])
set(gcf,'name','Sun, Earth, and Moon Orbits')
for i = 1:length(t)/q
    subplot(1,2,1)
    plot3(x(1:i*q,1),x(1:i*q,2),x(1:i*q,3),'g',x(1:i*q,7),x(1:i*q,8),x(1:i*q,9),'r',x(1:i*q,13),x(1:i*q,14),x(1:i*q,15),'b')
    axis(1.1*[min(x(:,1)) max(x(:,1)) min(x(:,2)) max(x(:,2)) 2*min(x(:,15)) 2*max(x(:,15))])
    xlabel('Universal X Coordinate (m)')
    ylabel('Universal Y Coordinate (m)')
    zlabel('Universal Z Coordinate (m)')
    title('Relative Orbits: Moon, Earth, Sun')
    legend('Earth','Sun','Moon')
    hold on
    plot3(x(i*q,1),x(i*q,2),x(i*q,3),'g-o',x(i*q,7),x(i*q,8),x(i*q,9),'r-o',x(i*q,13),x(i*q,14),x(i*q,15),'b-o')
    hold off
    
    subplot(1,2,2)
    plot3(x(1:i*q,1),x(1:i*q,2),x(1:i*q,3),'g',x(1:i*q,19),x(1:i*q,20),x(1:i*q,21),'m',x(1:i*q,7),x(1:i*q,8),x(1:i*q,9),'r')
    axis(1.1*[min(x(:,1)) max(x(:,1)) min(x(:,2)) max(x(:,2)) 2*min(x(:,15)) 2*max(x(:,15))])
    xlabel('Universal X Coordinate (m)')
    ylabel('Universal Y Coordinate (m)')
    zlabel('Universal Z Coordinate (m)')
    title('Relative Orbits: Earth, Mercury, Sun')
    legend('Earth','Mercury','Sun')
    hold on
    plot3(x(i*q,1),x(i*q,2),x(i*q,3),'g-o',x(i*q,19),x(i*q,20),x(i*q,21),'m-o',x(i*q,7),x(i*q,8),x(i*q,9),'r-o')
    hold off
    
    drawnow
end
end

%% Differential Equation Function
function [udot]= earthfinal(t,u)
m_earth = 5.9742e24; % [kg]
m_sun = 1.98892e30; % [kg]
m_sat = 11110; % [kg]
m_mercury = 3.285e23; % [kg]
G = 6.67300e-11; %[(m)^3(kg)^-1(s)^-2];

d_earth_sun = sqrt((u( 7,1)-u(1,1))^2+(u( 8,1)-u(2,1))^2+(u( 9,1)-u(3,1))^2);
d_earth_sat = sqrt((u(13,1)-u(1,1))^2+(u(14,1)-u(2,1))^2+(u(15,1)-u(3,1))^2);
d_earth_mercury = sqrt((u(19,1)-u(1,1))^2+(u(20,1)-u(2,1))^2+(u(21,1)-u(3,1))^2);
d_sun_sat =   sqrt((u(13,1)-u(7,1))^2+(u(14,1)-u(8,1))^2+(u(15,1)-u(9,1))^2);
d_sun_mercury = sqrt((u(19,1)-u(7,1))^2+(u(20,1)-u(8,1))^2+(u(21,1)-u(9,1))^2);
d_sat_mercury = sqrt((u(13,1)-u(19,1))^2+(u(14,1)-u(20,1))^2+(u(15,1)-u(21,1))^2);


% Earth motion
udot( 1,1) = u(4,1);
udot( 2,1) = u(5,1);
udot( 3,1) = u(6,1);
udot( 4,1) = m_sun*G*(u(7,1)-u(1,1))/d_earth_sun^3 + m_sat*G*(u(13,1)-u(1,1))/d_earth_sat^3 + m_mercury*G*(u(19,1)-u(1,1))/d_earth_mercury^3;
udot( 5,1) = m_sun*G*(u(8,1)-u(2,1))/d_earth_sun^3 + m_sat*G*(u(14,1)-u(2,1))/d_earth_sat^3 + m_mercury*G*(u(20,1)-u(2,1))/d_earth_mercury^3;
udot( 6,1) = m_sun*G*(u(9,1)-u(3,1))/d_earth_sun^3 + m_sat*G*(u(15,1)-u(3,1))/d_earth_sat^3 + m_mercury*G*(u(21,1)-u(3,1))/d_earth_mercury^3;
% Sun Motion
udot( 7,1) = u(10,1);
udot( 8,1) = u(11,1);
udot( 9,1) = u(12,1);
udot(10,1) = m_earth*G*(u(1,1)-u(7,1))/d_earth_sun^3 + m_sat*G*(u(13,1)-u(7,1))/d_sun_sat^3 + m_mercury*G*(u(19,1)-u(7,1))/d_sun_mercury^3;
udot(11,1) = m_earth*G*(u(2,1)-u(8,1))/d_earth_sun^3 + m_sat*G*(u(14,1)-u(8,1))/d_sun_sat^3 + m_mercury*G*(u(20,1)-u(8,1))/d_sun_mercury^3;
udot(12,1) = m_earth*G*(u(3,1)-u(9,1))/d_earth_sun^3 + m_sat*G*(u(15,1)-u(9,1))/d_sun_sat^3 + m_mercury*G*(u(21,1)-u(9,1))/d_sun_mercury^3;
% Satellite Motion
udot(13,1) = u(16,1);
udot(14,1) = u(17,1);
udot(15,1) = u(18,1);
udot(16,1) = m_earth*G*(u(1,1)-u(13,1))/d_earth_sat^3 + m_sun*G*(u(7,1)-u(13,1))/d_sun_sat^3 + m_mercury*G*(u(19,1)-u(13,1))/d_sat_mercury^3;
udot(17,1) = m_earth*G*(u(2,1)-u(14,1))/d_earth_sat^3 + m_sun*G*(u(8,1)-u(14,1))/d_sun_sat^3 + m_mercury*G*(u(20,1)-u(14,1))/d_sat_mercury^3;
udot(18,1) = m_earth*G*(u(3,1)-u(15,1))/d_earth_sat^3 + m_sun*G*(u(9,1)-u(15,1))/d_sun_sat^3 + m_mercury*G*(u(21,1)-u(15,1))/d_sat_mercury^3;
% Mercury Motion
udot(19,1) = u(22,1);
udot(20,1) = u(23,1);
udot(21,1) = u(24,1);
udot(22,1) = m_earth*G*(u(1,1)-u(19,1))/d_earth_mercury^3 + m_sun*G*(u(7,1)-u(19,1))/d_sun_mercury^3 + m_sat*G*(u(13,1)-u(19,1))/d_sat_mercury^3;
udot(23,1) = m_earth*G*(u(2,1)-u(20,1))/d_earth_mercury^3 + m_sun*G*(u(8,1)-u(20,1))/d_sun_mercury^3 + m_sat*G*(u(14,1)-u(20,1))/d_sat_mercury^3;
udot(24,1) = m_earth*G*(u(3,1)-u(21,1))/d_earth_mercury^3 + m_sun*G*(u(9,1)-u(21,1))/d_sun_mercury^3 + m_sat*G*(u(15,1)-u(21,1))/d_sat_mercury^3;
end