#!/usr/bin/env python3
"""Compute answers for ex3–ex20. Print LaTeX."""
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "engine" / "lib")]
import sympy as sp
from sympy import sqrt, simplify, Eq, solve, Matrix, N, pi, cos, sin, tan, atan, radsimp
import geometry_kernel as gk

def out(name, expr):
    e = simplify(expr)
    print(f"{name}: {e}    tex={gk.tex(e)}")
    return e

# ---------- 例题4 cuboid N dist ----------
print("===== ex4 =====")
# A=0, AB=3 x, BC=1 y, AA1=2 z. M mid A1B1=(3/2,0,2)
# N on surface, |N-B|=|N-M|=|N-D|
x,y,z = sp.symbols('x y z')
B = gk.V(3,0,0); D=gk.V(0,1,0); M=gk.V(sp.Rational(3,2),0,2)
N = gk.V(x,y,z)
eqs = [sp.Eq(sp.simplify((N-B).dot(N-B)-(N-M).dot(N-M)),0),
       sp.Eq(sp.simplify((N-B).dot(N-B)-(N-D).dot(N-D)),0)]
print("planes", [sp.factor(e.lhs) for e in eqs])
# y=3x-4, z=(12x-11)/16
# surface: x=0|3 or y=0|1 or z=0|2, with 0<=x<=3,0<=y<=1,0<=z<=2
cands=[]
for face, val in [("x",0),("x",3),("y",0),("y",1),("z",0),("z",2)]:
    if face=="x":
        sol = solve(eqs+[Eq(x,val)], [x,y,z], dict=True)
    elif face=="y":
        sol = solve(eqs+[Eq(y,val)], [x,y,z], dict=True)
    else:
        sol = solve(eqs+[Eq(z,val)], [x,y,z], dict=True)
    for s in sol:
        xx,yy,zz=[s[x],s[y],s[z]]
        if 0<=xx<=3 and 0<=yy<=1 and 0<=zz<=2:
            cands.append((xx,yy,zz,zz))  # dist to z=0 is zz
print("cands", cands)

# ---------- 例题13 prism ----------
print("===== ex13 =====")
# unfolding min: E=(0,0,2), F=(2,0,0)
E=gk.V(0,0,2); F=gk.V(2,0,0); B1=gk.V(6,0,4); C1=gk.V(0,2,4)
# Cayley-Menger R
def circum_R(A,B,C,D):
    # R = |OA||OB||OC| / |6V * 2?|
    # formula: R = |a||b||c| / (4K) analog
    #  | (A-D)·((B-D)×(C-D)) | / 6  = V
    # R^2 = |a|^2 |n|^2 / (4 |n·(something)|
    u,v,w = B-A, C-A, D-A
    V6 = sp.Abs(u.dot(v.cross(w)))  # 6V
    # circumcenter: solve |X-A|=|X-B|=|X-C|=|X-D|
    # 2(B-A)·X = |B|^2-|A|^2 etc with A origin relative
    M = Matrix([
        [2*u[0],2*u[1],2*u[2]],
        [2*v[0],2*v[1],2*v[2]],
        [2*w[0],2*w[1],2*w[2]],
    ])
    rhs = Matrix([u.dot(u), v.dot(v), w.dot(w)])
    o = A + M.solve(rhs)  # from A
    R = simplify((o-A).norm())
    return R, o
R, O = circum_R(B1,C1,E,F)
out("ex13 R", R)

# ---------- 例题19 tetra volume from x-coords ----------
print("===== ex19 =====")
# Regular tetrahedron, x-coords 2,3,5,7. Volume.
# For regular tetra edge a, the 4 x-coordinates are projections on a line.
# Variance of projections: for regular tetra, centroid 0, vertices
# Regular tetra in standard position then rotate.
# Known: sum of squares of coords on an axis...
# Let xs = 2,3,5,7. Mean = 17/4. 
# For regular tetra edge a, the RMS of projections of vertices onto a unit vector u:
# vertices from centroid: |vi|=(√6/4)*a * √(3/2 wait) circumradius R=√6/4 a
# Four vertices: sum vi=0, |vi|=R, vi·vj = -R^2/3 = -a^2/8
# Sum of (vi·u)^2 = u^T (sum vi vi^T) u
# sum_i vi vi^T = (4 R^2 / 3) I  because isotropic: trace = 4 R^2, 3 equal eigenvalues.
# R^2 = 6 a^2 / 16 = 3 a^2 / 8
# sum (xi - mean)^2 = (4 R^2 / 3) = 4*(3 a^2/8)/3 = a^2/2
xs=[2,3,5,7]
mean=sp.Rational(sum(xs),4)
s2=sum((sp.Integer(x)-mean)**2 for x in xs)
print("sum sq", s2, "mean", mean)
# s2 = a^2 / 2  => a^2 = 2 s2
a2 = 2*s2
a=sqrt(a2)
V = simplify(a**3 / (6*sqrt(2)))  # regular tetra V=a^3 √2 / 12 = a^3 / (6√2)
out("ex19 V", V)

# ---------- 例题14 hemisphere ----------
print("===== ex14 =====")
a=sp.symbols('a', positive=True)
# r=sin a, cos(2a)= sin^2 a - 1/2 cos^2 a from earlier
# u=sin^2 a = r^2
u=sp.symbols('u', positive=True)
eq = Eq(u - sp.Rational(1,2)*(1-u), 1-2*u)
print(solve(eq,u))
eq2 = Eq(u - sp.Rational(1,2)*(1-u), 2*(1-u)-1)  # cos2a=2c^2-1
print('alt', solve(eq2,u))
out("ex14 r", sqrt(sp.Rational(3,7)))

# ---------- 例题8 tetra CD min ----------
print("===== ex8 =====")
ax,ay,c,d = sp.symbols('ax ay c d', real=True)
# ax^2+ay^2=3, B=(0,0,1), A=(ax,ay,0), C=(c,0,0), D=(d,0,0), M=(c/2,0,0)
A=gk.V(ax,ay,0); Bb=gk.V(0,0,1); C=gk.V(c,0,0); D=gk.V(d,0,0); Mm=gk.V(c/2,0,0)
def area(P,Q,R):
    return (Q-P).cross(R-P).norm()/2
eqs=[Eq(ax**2+ay**2,3), Eq(area(A,Bb,D),1), Eq(area(A,Bb,Mm),1)]
# expand
nD=(A-Bb).cross(D-Bb).dot((A-Bb).cross(D-Bb))
nM=(A-Bb).cross(Mm-Bb).dot((A-Bb).cross(Mm-Bb))
eqs=[Eq(ax**2+ay**2,3), Eq(nD,4), Eq(nM,4)]
print(eqs)
# nD = ay^2 + (ax-d)^2 + ay^2 d^2 = 4
# nM = ay^2 + (ax-c/2)^2 + ay^2 (c/2)^2 = 4
# ay^2 = 3-ax^2
# (3-ax^2)(1+d^2) + (ax-d)^2 = 4
# (3-ax^2)(1+d^2) + ax^2 -2 ax d + d^2 = 4
sols=[]
axv=sp.symbols('ax')
# try ay != 0
# I'll solve numerically-symbolically
fD = (3-ax**2)*(1+d**2) + (ax-d)**2 - 4
fM = (3-ax**2)*(1+(c/2)**2) + (ax-c/2)**2 - 4
# c<=0<=d or d<=0<=c, CD=Abs(d-c) min, H=0 on segment
vars_s = solve([fD,fM],[c,d], dict=True)
print('n sols', len(vars_s))
for s in vars_s[:8]:
    print(simplify(s), 'CD', simplify(sp.Abs(s[d]-s[c])))

print("done batch header")
