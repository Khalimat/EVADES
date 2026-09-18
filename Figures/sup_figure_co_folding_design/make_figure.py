import os
OUT = os.path.dirname(os.path.abspath(__file__))
import math
W, H = 482, 556
FONT = "Helvetica, Arial, 'Liberation Sans', sans-serif"
INK, CAP, DOT      = "#33393E", "#97A1A8", "#AEBCC4"
ADP_F, ADP_S       = "#C96F5A", "#9A4630"          # phage protein - warm
PL_BIG             = "#EAF1F6"                      # host system - cool
PL_F,  PL_F2, PL_S = "#D3E4EC", "#E3EEF3", "#3F7B95"
SUM_F, SUM_S, SUM_T= "#EAF2F6", "#3F7B95", "#2E6079"
OK_F,  OK_S,  OK_T = "#E7F2EF", "#3E8A78", "#2F6E5E"

s=[]
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def txt(x,y,t,size=8,fill=INK,anchor="middle",weight="normal"):
    s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
             f'text-anchor="{anchor}" font-weight="{weight}">{esc(t)}</text>')
def circ(cx,cy,r,fill,strk=None,sw=1.4):
    st=f' stroke="{strk}" stroke-width="{sw}"' if strk else ''
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{st}/>')
def dots(x1,y1,x2,y2):
    s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{DOT}" '
             f'stroke-width="1.1" stroke-dasharray="1.8 3" stroke-linecap="round"/>')
def wof(lines,size,pad): return max(len(l) for l in lines)*size*0.545 + pad*2
def pill(cx,cy,lines,fill,strk,tc,size=9.2,pad=16,lh=12):
    w=wof(lines,size,pad); h=len(lines)*lh+13
    s.append(f'<rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" '
             f'fill="{fill}" stroke="{strk}" stroke-width="1.7"/>')
    y0=cy-(len(lines)-1)*lh/2+size*0.36
    for i,l in enumerate(lines): txt(cx,y0+i*lh,l,size,tc,weight="bold")
    return w,h
def label(x,y,l,t):
    txt(x,y,l.upper(),11.5,"#000000",anchor="start",weight="bold"); txt(x+18,y,t,9.2,INK,anchor="start",weight="bold")

LX, RX = 92, 288
label(14,26,"a","Each ADP is co-folded with every protein of the system it inhibits")
txt(LX,54,"ADP with uncharacterised",7.8,CAP); txt(LX,64,"mechanism",7.8,CAP)
txt(RX,54,"All proteins of the defence system",7.8,CAP); txt(RX,64,"it is reported to inhibit",7.8,CAP)

def row(cy,R,n,rr,pr,adp,sysname,npro):
    circ(RX,cy,R,PL_BIG)
    pts=[]
    for i in range(n):
        a=math.radians(-100+360*i/n)
        x,y=RX+rr*math.cos(a), cy+rr*math.sin(a)
        circ(x,y,pr,PL_F if i%2 else PL_F2,PL_S,1.3); pts.append((x,y))
    w,h=pill(LX,cy,[adp],ADP_F,ADP_S,"#FFFFFF",8.8,pad=15)
    for (x,y) in pts: dots(LX+w/2+4, cy, x-pr-1, y)
    txt(RX+R+12,cy-2,sysname,7.8,SUM_T,anchor="start",weight="bold")
    txt(RX+R+12,cy+9,f"{npro} proteins → {npro} pairs",7.4,CAP,anchor="start")

row(130,50,13,34,7.0,"AcrIA1","type I-A CRISPR–Cas",13)
row(240,37,6,22,8.5,"ORF46","BREX type I",6)
row(322,26,2,13,9.5,"Gad2","Gabija",2)

for x in (LX,RX):
    for i in range(3): circ(x,362+i*7,1.7,"#C4C4C4")
txt(LX,398,"93 ADPs",8.6,ADP_S,weight="bold")
txt(LX,409,"uncharacterised mechanism",7.4,CAP)
txt(RX,398,"19 defence systems",8.6,SUM_T,weight="bold")
txt(RX,409,"166 defence proteins",7.4,CAP)
pill(241,442,["433 ADP–defence protein pairs"],SUM_F,SUM_S,SUM_T,9.6,pad=18)

label(14,486,"b","Co-folding and confidence filtering")
yc=524
steps=[(["433 pairs"],"#FFFFFF",SUM_S,SUM_T,None),
       (["AlphaFold co-folding","5 models × 4 seeds"],"#FFFFFF",SUM_S,SUM_T,"8,660 structures"),
       (["mean ipTM ≥ 0.6"],"#FFFFFF",SUM_S,SUM_T,"across models and seeds"),
       (["candidate","interaction pairs"],OK_F,OK_S,OK_T,None)]
ws=[wof(l,8.6,14) for l,_,_,_,_ in steps]
GAP=20; x=(W-(sum(ws)+GAP*(len(ws)-1)))/2; prev=None
for (lines,f,st,tc,note),w in zip(steps,ws):
    cx=x+w/2
    if prev is not None: dots(prev+6,yc,x-6,yc)
    _,h=pill(cx,yc,lines,f,st,tc,8.6,pad=14,lh=11)
    if note: txt(cx,yc+h/2+12,note,7.2,CAP)
    prev=x+w; x+=w+GAP

svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="170mm" height="{H/W*170:.1f}mm" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#FFFFFF"/>
{chr(10).join(s)}
</svg>'''
open(os.path.join(OUT,'SuppFig_cofolding_screen.svg'),'w').write(svg)
import cairosvg
cairosvg.svg2pdf(bytestring=svg.encode(),write_to=os.path.join(OUT,'SuppFig_cofolding_screen.pdf'))
cairosvg.svg2png(bytestring=svg.encode(),write_to=os.path.join(OUT,'SuppFig_cofolding_screen.png'),scale=4)
print("ok")
