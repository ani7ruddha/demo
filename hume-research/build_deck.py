#!/usr/bin/env python3
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---- Theme (dark Hume "Creative Performance" language) ----
BG      = RGBColor(0x14,0x16,0x1A)   # charcoal
PANEL   = RGBColor(0x1E,0x21,0x27)   # slightly lighter panel
WHITE   = RGBColor(0xF5,0xF6,0xF8)
MUTE    = RGBColor(0x9A,0xA2,0xAD)   # muted grey
ACCENT  = RGBColor(0x4A,0xDE,0x80)   # mint (positive)
CORAL   = RGBColor(0xFF,0x6B,0x6B)   # risk/negative
AMBER   = RGBColor(0xFF,0xC1,0x4D)   # highlight
LINE    = RGBColor(0x2C,0x31,0x3A)
FONT    = "Arial"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

def slide():
    s = prs.slides.add_slide(BLANK)
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,SW,SH)
    r.fill.solid(); r.fill.fore_color.rgb = BG; r.line.fill.background()
    r.shadow.inherit=False
    s.shapes._spTree.remove(r._element); s.shapes._spTree.insert(2, r._element)
    return s

def box(s,l,t,w,h):
    tb=s.shapes.add_textbox(l,t,w,h); tf=tb.text_frame; tf.word_wrap=True
    return tb,tf

def setp(p,text,size,color=WHITE,bold=False,italic=False,align=PP_ALIGN.LEFT,font=FONT,space_after=6,line=1.05):
    p.alignment=align; p.space_after=Pt(space_after); p.line_spacing=line
    r=p.add_run(); r.text=text; f=r.font
    f.size=Pt(size); f.bold=bold; f.italic=italic; f.name=font; f.color.rgb=color
    return r

def rect(s,l,t,w,h,fill=PANEL,line_color=None,line_w=None):
    sp=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,l,t,w,h)
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb=fill
    if line_color is None: sp.line.fill.background()
    else: sp.line.color.rgb=line_color; sp.line.width=Pt(line_w or 1)
    sp.shadow.inherit=False
    return sp

def header(s,num,label="VOICE OF CUSTOMER  ·  HUME HEALTH POD"):
    # top-left recurring label (mirrors reference header system)
    _,tf=box(s,Inches(0.5),Inches(0.28),Inches(8),Inches(0.4))
    setp(tf.paragraphs[0],label,11,MUTE,bold=True,font=FONT)
    # accent tick
    rect(s,Inches(0.5),Inches(0.66),Inches(0.55),Pt(3),fill=ACCENT)
    # slide number top-right
    _,tf2=box(s,SW-Inches(1.4),Inches(0.28),Inches(0.9),Inches(0.4))
    setp(tf2.paragraphs[0],f"{num} / 17",11,MUTE,bold=True,align=PP_ALIGN.RIGHT)

def title(s,text,top=Inches(0.95),size=30,color=WHITE):
    _,tf=box(s,Inches(0.5),top,SW-Inches(1.0),Inches(1.0))
    setp(tf.paragraphs[0],text,size,color,bold=True)
    return tf

n=0
def N():
    global n; n+=1; return n

# ---------- 1. TITLE ----------
s=slide()
rect(s,0,Inches(2.55),SW,Pt(3),fill=ACCENT)
_,tf=box(s,Inches(0.7),Inches(0.6),Inches(10),Inches(0.5))
setp(tf.paragraphs[0],"VOICE OF CUSTOMER",13,MUTE,bold=True)
_,tf=box(s,Inches(0.7),Inches(2.7),Inches(12),Inches(2.2))
setp(tf.paragraphs[0],"Why People Buy the Hume Pod",46,WHITE,bold=True,line=1.0)
setp(tf.add_paragraph(),"— and what's blocking the sale",30,ACCENT,bold=True,line=1.0)
_,tf=box(s,Inches(0.7),Inches(5.5),Inches(12),Inches(1.4))
setp(tf.paragraphs[0],"Cross-source research:  8,364 Facebook ad comments  ·  Trustpilot  ·  BBB  ·  Reddit  ·  independent reviewers  ·  Amazon",14,MUTE)
setp(tf.add_paragraph(),"Apr 1 – Jun 16, 2026   |   Prepared 2026-06-17",12,MUTE)

# ---------- 2. METHOD / SOURCES ----------
s=slide(); header(s,N()); title(s,"What we studied")
cards=[("8,364","Facebook ad comments analyzed (Apr–Jun 2026)"),
       ("6","independent data sources triangulated"),
       ("~50%","of all comments are negative — every week"),
       ("12 wks","of weekly trend data (W14–W25)")]
x=Inches(0.5); w=Inches(2.95); gap=Inches(0.13)
for i,(big,lab) in enumerate(cards):
    L=Emu(int(x)+i*(int(w)+int(gap)))
    rect(s,L,Inches(2.0),w,Inches(1.9),fill=PANEL)
    _,tf=box(s,L+Inches(0.2),Inches(2.2),w-Inches(0.4),Inches(1.6))
    setp(tf.paragraphs[0],big,34,ACCENT,bold=True)
    setp(tf.add_paragraph(),lab,13,WHITE)
_,tf=box(s,Inches(0.5),Inches(4.4),SW-Inches(1.0),Inches(2.4))
setp(tf.paragraphs[0],"Sources & reliability",16,AMBER,bold=True,space_after=8)
for t in ["Facebook ad comments — primary VOC (labeled by theme & sentiment in the export)",
          "BBB — fully verified, dated verbatim complaints (strongest negative evidence)",
          "Trustpilot ~3.6/5 — rating via search snippets (histogram blocked)",
          "Reddit — second-hand via aggregators (Reddit hard-blocked); treat as directional",
          "Independent reviewers (MedGrade/Cybernews) + Amazon India page un-scrapeable"]:
    p=tf.add_paragraph(); setp(p,"•  "+t,12.5,MUTE)

# ---------- 3. BIG TAKEAWAY ----------
s=slide(); header(s,N())
_,tf=box(s,Inches(1.0),Inches(2.2),Inches(11.3),Inches(3.2))
setp(tf.paragraphs[0],"The takeaway",18,ACCENT,bold=True,space_after=14)
setp(tf.add_paragraph(),"Demand is real and emotionally strong — but trust and post-purchase operations are actively killing conversions.",30,WHITE,bold=True,line=1.12,space_after=12)
setp(tf.add_paragraph(),"The comment data runs ~50% negative, every single week.",20,CORAL,bold=True)

# ---------- 4. THREE NUMBERS ----------
s=slide(); header(s,N()); title(s,"The 3 numbers that tell the story")
data=[("4.8  vs  3.6  vs  F",CORAL,"Hume's own site (4.8/5) vs independent Trustpilot (~3.6) vs BBB \"F\" (1.01/5, 263 unanswered complaints). The #1 strategic risk — prospects find it and talk each other out of buying."),
      ("~50% negative",AMBER,"Every week (W14–W25) — structural, not a bad week. Complaints migrate from \"too expensive\" → \"I regret buying\" as units ship."),
      ("#1 driver: the \"anti-scale\"",ACCENT,"For GLP-1 users — \"a regular scale can be so discouraging.\" The most defensible, repeatable ad angle.")]
y=Inches(2.0)
for big,col,body in data:
    rect(s,Inches(0.5),y,SW-Inches(1.0),Inches(1.45),fill=PANEL)
    rect(s,Inches(0.5),y,Pt(5),Inches(1.45),fill=col)
    _,tf=box(s,Inches(0.85),y+Inches(0.14),SW-Inches(1.6),Inches(1.2))
    setp(tf.paragraphs[0],big,22,col,bold=True,space_after=4)
    setp(tf.add_paragraph(),body,13,WHITE,line=1.05)
    y=Emu(int(y)+int(Inches(1.62)))

# ---------- 5. CROSS-SOURCE AGREEMENT TABLE ----------
s=slide(); header(s,N()); title(s,"What every source agrees on")
rows=[["Theme","FB","Trustpilot","BBB","Reddit","Indep."],
["Strong appeal (anti-scale / rich metrics)","✓","✓","–","✓","✓"],
["Customer service / refund failures","✓","✓","Severe","✓","–"],
["Accuracy doubt vs DEXA","✓","✓","✓","✓","Severe"],
["Trust / scam / legitimacy doubt","✓","✓","✓","FitTrack","–"],
["Price & hidden subscription friction","✓","✓","✓","✓","✓"]]
tl,tt=Inches(0.5),Inches(2.0); tw=SW-Inches(1.0); th=Inches(4.6)
tbl=s.shapes.add_table(len(rows),6,tl,tt,tw,th).table
tbl.columns[0].width=Inches(5.1)
for c in range(1,6): tbl.columns[c].width=Inches(1.446)
for ri,row in enumerate(rows):
    tbl.rows[ri].height=Inches(0.76)
    for ci,val in enumerate(row):
        cell=tbl.cell(ri,ci); cell.fill.solid()
        cell.fill.fore_color.rgb = (RGBColor(0x1F,0x4E,0x78) if ri==0 else (PANEL if ri%2 else RGBColor(0x17,0x19,0x1E)))
        cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.margin_left=Inches(0.12); cell.margin_top=Inches(0.02); cell.margin_bottom=Inches(0.02)
        tf=cell.text_frame; p=tf.paragraphs[0]; p.alignment=(PP_ALIGN.LEFT if ci==0 else PP_ALIGN.CENTER)
        r=p.add_run(); r.text=val; f=r.font; f.name=FONT; f.size=Pt(13 if ci==0 else 13)
        if ri==0: f.bold=True; f.color.rgb=WHITE
        elif ci==0: f.color.rgb=WHITE
        elif val=="✓": f.color.rgb=ACCENT; f.bold=True
        elif val in ("Severe","FitTrack"): f.color.rgb=CORAL; f.bold=True
        else: f.color.rgb=MUTE

# ---------- 6. DIVIDER: WHY THEY BUY ----------
def divider(num,word,sub):
    s=slide(); header(s,num)
    rect(s,Inches(0.5),Inches(3.05),Inches(1.1),Pt(6),fill=ACCENT)
    _,tf=box(s,Inches(0.5),Inches(3.2),Inches(12),Inches(2.0))
    setp(tf.paragraphs[0],word,54,WHITE,bold=True)
    setp(tf.add_paragraph(),sub,18,MUTE)
    return s
divider(N(),"WHY THEY BUY","Purchase drivers, ranked by signal")

# ---------- 7. WHY THEY BUY ----------
s=slide(); header(s,N()); title(s,"Why they buy")
drivers=[("1  Progress tracking & motivation","GLP-1 / weight-loss users — the \"anti-scale\""),
         ("2  Detailed metrics","\"learn about my body\" — fat, muscle, HRV, sleep"),
         ("3  At-home convenience","\"body-composition scanner at home,\" <60s scan"),
         ("4  Preventative peace of mind","catch problems early (esp. Band buyers)"),
         ("5  Gifting","Mother's / Father's Day recurring")]
y=Inches(1.9)
for h,sub in drivers:
    rect(s,Inches(0.5),y,Inches(6.0),Inches(0.92),fill=PANEL)
    _,tf=box(s,Inches(0.7),y+Inches(0.1),Inches(5.7),Inches(0.8))
    setp(tf.paragraphs[0],h,15,ACCENT,bold=True,space_after=2)
    setp(tf.add_paragraph(),sub,11.5,MUTE)
    y=Emu(int(y)+int(Inches(1.0)))
# verbatim panel
rect(s,Inches(6.8),Inches(1.9),Inches(6.0),Inches(4.92),fill=RGBColor(0x17,0x19,0x1E),line_color=LINE,line_w=1)
_,tf=box(s,Inches(7.05),Inches(2.1),Inches(5.5),Inches(4.6))
setp(tf.paragraphs[0],"In their words",14,AMBER,bold=True,space_after=10)
for q in ['"My husband got me one for Mother\'s Day as I am on a GLP-1 weight loss journey and a regular scale can be so discouraging — it educates me AND helps my mental health."',
          '"I didn\'t expect to learn so much about my body — the sleep and HRV insights are really accurate."',
          '"It\'s like having your own body composition scanner at home."']:
    p=tf.add_paragraph(); setp(p,q,12.5,WHITE,italic=True,line=1.08,space_after=12)

# ---------- 8. DIVIDER: BLOCKERS ----------
divider(N(),"WHAT'S BLOCKING THE SALE","Objections, ranked by comment volume")

# ---------- 9. CORE OBJECTIONS ----------
s=slide(); header(s,N()); title(s,"Core objections (of 4,696 negative comments)")
objs=[("Customer service / returns / refunds","13%",CORAL),
      ("Price confusion  ($199 ad → $249 cart)","7%",CORAL),
      ("Shipping / delivery delays","7%",AMBER),
      ("Scam / legitimacy doubt  (FitTrack + \"FAKE\" videos)","5%",CORAL),
      ("Hidden subscription / membership fee","5%",AMBER),
      ("App / Bluetooth / connectivity","5%",AMBER),
      ("Accuracy / BIA limitations vs DEXA","4%",MUTE)]
y=Inches(1.95); maxp=13
for label,pct,col in objs:
    rect(s,Inches(0.5),y,Inches(8.4),Inches(0.6),fill=PANEL)
    barw=Emu(int(Inches(8.4))*int(pct.strip('%'))//maxp)
    rect(s,Inches(0.5),y,barw,Inches(0.6),fill=col)
    _,tf=box(s,Inches(0.7),y+Inches(0.08),Inches(8.0),Inches(0.45))
    setp(tf.paragraphs[0],label,13,WHITE,bold=True)
    _,tf=box(s,Inches(9.05),y+Inches(0.04),Inches(1.2),Inches(0.5))
    setp(tf.paragraphs[0],pct,17,col,bold=True)
    y=Emu(int(y)+int(Inches(0.7)))
_,tf=box(s,Inches(10.4),Inches(1.95),Inches(2.6),Inches(4.8))
setp(tf.paragraphs[0],"Note",13,AMBER,bold=True,space_after=8)
setp(tf.add_paragraph(),"#1–#4 are trust & operations problems — not product problems. No creative outruns a refund queue.",13,WHITE,line=1.12)

# ---------- 10. OBJECTION VERBATIM ----------
s=slide(); header(s,N()); title(s,"The objections, in their words")
cols=[("Customer service / refunds",CORAL,['"22 emails to initiate the return process."','BBB: "required to pay return shipping despite the devices being clearly defective… still awaiting a full refund."','"live-chat is turned off… I want my money back from this fraudulent company."']),
      ("Price & subscription",AMBER,['"Your ad states $199 but at checkout $249 was the only price available."','"Says $199 then when you click it adds another $50. Very sheepish."','"the app is free but only basic — to unlock the full app it is $99/year… deceiving."']),
      ("Scam doubt & accuracy",MUTE,['"Right after I placed the order I saw a YouTube video \'FAKE\'."','Reddit: "using FitTrack as a cover to scam investors."','"wildly inaccurate vs DEXA — scale showed 10.8% while DEXA showed 15%."'])]
x=Inches(0.5); w=Inches(4.07); gap=Inches(0.06)
for i,(h,col,qs) in enumerate(cols):
    L=Emu(int(x)+i*(int(w)+int(gap)))
    rect(s,L,Inches(1.95),w,Inches(4.9),fill=RGBColor(0x17,0x19,0x1E),line_color=LINE,line_w=1)
    rect(s,L,Inches(1.95),w,Inches(0.55),fill=col)
    _,tf=box(s,L+Inches(0.18),Inches(2.0),w-Inches(0.36),Inches(0.45))
    setp(tf.paragraphs[0],h,13.5,BG,bold=True)
    _,tf=box(s,L+Inches(0.18),Inches(2.65),w-Inches(0.36),Inches(4.1))
    for q in qs:
        p=tf.add_paragraph(); setp(p,q,11.5,WHITE,italic=True,line=1.08,space_after=11)

# ---------- 11. DIVIDER: FAQs ----------
divider(N(),"FAQs","The questions buyers ask before purchase")

# ---------- 12. FAQs ----------
s=slide(); header(s,N()); title(s,"Frequently asked questions (of 1,667 questions)")
faqs=[("Price / where to buy / membership cost","Most-asked. \"$199 or $249? what does Hume+ cost?\""),
      ("Do I need a phone / the app? Which OS?","\"Do I need my phone with me to use it?\""),
      ("How accurate vs DEXA / how does it work?","\"I thought bone density needed a hospital DEXA.\""),
      ("Safety: pacemaker / implants / pregnancy?","HIGHEST-ENGAGEMENT question — currently UNANSWERED"),
      ("Multiple users / family / weight limit?","\"Can my mom & dad share one device?\""),
      ("Shipping to UK / Canada / Australia / India?","duties & availability"),
      ("Warranty / returns / trial / data privacy?","\"who has access to my data?\"")]
y=Inches(1.95)
for q,sub in faqs:
    col = CORAL if q.startswith("Safety") else WHITE
    rect(s,Inches(0.5),y,SW-Inches(1.0),Inches(0.62),fill=(RGBColor(0x2A,0x1E,0x1E) if col==CORAL else PANEL))
    _,tf=box(s,Inches(0.7),y+Inches(0.07),Inches(7.5),Inches(0.5))
    setp(tf.paragraphs[0],q,14,col,bold=True)
    _,tf=box(s,Inches(8.3),y+Inches(0.1),Inches(4.6),Inches(0.5))
    setp(tf.paragraphs[0],sub,11.5,(AMBER if col==CORAL else MUTE),italic=True)
    y=Emu(int(y)+int(Inches(0.7)))

# ---------- 13. WEEKLY TREND ----------
s=slide(); header(s,N()); title(s,"The weekly view: ~50% negative, structurally")
wk=[("W14","51"),("W15","55"),("W16","47"),("W17","52"),("W18","57"),("W19","51"),("W20","50"),("W21","49"),("W22","50"),("W23","46"),("W24","39"),("W25","46")]
base=Inches(5.7); chart_h=Inches(3.0); x=Inches(0.7); bw=Inches(0.78); gap=Inches(0.21)
for i,(lab,val) in enumerate(wk):
    v=int(val); h=Emu(int(chart_h)*v//60)
    L=Emu(int(x)+i*(int(bw)+int(gap)))
    rect(s,L,Emu(int(base)-int(h)),bw,h,fill=(CORAL if v>=50 else AMBER))
    _,tf=box(s,L-Inches(0.05),base+Inches(0.05),bw+Inches(0.1),Inches(0.3))
    setp(tf.paragraphs[0],lab,10,MUTE,align=PP_ALIGN.CENTER)
    _,tf=box(s,L-Inches(0.05),Emu(int(base)-int(h)-int(Inches(0.32))),bw+Inches(0.1),Inches(0.3))
    setp(tf.paragraphs[0],val+"%",10,WHITE,bold=True,align=PP_ALIGN.CENTER)
_,tf=box(s,Inches(0.7),Inches(1.85),SW-Inches(1.4),Inches(0.8))
setp(tf.paragraphs[0],"% of weekly comments that are negative. Complaints shift over time from \"too expensive\" (early) → service/refund regret (as units ship).",13,MUTE)

# ---------- 14. DIVIDER: ACTIONS ----------
divider(N(),"ACTIONS","What to do — impact-ranked")

# ---------- 15. TOP 5 MOVES ----------
s=slide(); header(s,N()); title(s,"Top 5 moves (impact-ranked)")
moves=[("Fix support visibly","Publish a working contact + refund SLA; stop charging return shipping on defectives. Kills the loudest objection."),
       ("Put real price + subscription cost in the ad","Kills the price and \"deceiving\" objections at once."),
       ("Lead creative with the anti-scale / GLP-1 angle","Trend + fat-vs-muscle — not accuracy claims you can't defend."),
       ("Pre-empt the scam doubt","Founder / clinician explainer of how BIA works and what it can't do."),
       ("Ship an always-on FAQ","Price, app/phone, pacemaker safety, multi-user, shipping countries.")]
y=Inches(1.9)
for i,(h,sub) in enumerate(moves,1):
    rect(s,Inches(0.5),y,SW-Inches(1.0),Inches(0.92),fill=PANEL)
    c=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(0.7),y+Inches(0.21),Inches(0.5),Inches(0.5))
    c.fill.solid(); c.fill.fore_color.rgb=ACCENT; c.line.fill.background(); c.shadow.inherit=False
    ctf=c.text_frame; cp=ctf.paragraphs[0]; cp.alignment=PP_ALIGN.CENTER
    rr=cp.add_run(); rr.text=str(i); rr.font.bold=True; rr.font.size=Pt(18); rr.font.color.rgb=BG; rr.font.name=FONT
    _,tf=box(s,Inches(1.45),y+Inches(0.11),Inches(11.2),Inches(0.78))
    setp(tf.paragraphs[0],h,15,WHITE,bold=True,space_after=2)
    setp(tf.add_paragraph(),sub,12,MUTE)
    y=Emu(int(y)+int(Inches(1.0)))

# ---------- 16. CREDIBILITY GAP ----------
s=slide(); header(s,N()); title(s,"The #1 strategic risk: the credibility gap")
gg=[("Hume.com","4.8/5",ACCENT,"company-curated"),("Trustpilot","3.6/5",AMBER,"~4,100–4,800 reviews"),("BBB","F · 1.01/5",CORAL,"263 unanswered complaints")]
x=Inches(0.9); w=Inches(3.6); gap=Inches(0.4)
for i,(src,score,col,sub) in enumerate(gg):
    L=Emu(int(x)+i*(int(w)+int(gap)))
    rect(s,L,Inches(2.3),w,Inches(2.6),fill=PANEL)
    rect(s,L,Inches(2.3),w,Pt(6),fill=col)
    _,tf=box(s,L+Inches(0.2),Inches(2.55),w-Inches(0.4),Inches(2.2))
    setp(tf.paragraphs[0],src,16,MUTE,bold=True,align=PP_ALIGN.CENTER,space_after=8)
    setp(tf.add_paragraph(),score,40,col,bold=True,align=PP_ALIGN.CENTER,space_after=8)
    setp(tf.add_paragraph(),sub,12,WHITE,align=PP_ALIGN.CENTER)
_,tf=box(s,Inches(0.9),Inches(5.4),Inches(11.5),Inches(1.4))
setp(tf.paragraphs[0],"Prospects find the independent reviews and talk each other out of buying in the comments. Closing this gap (support + transparency) is the single highest-ROI lever.",16,WHITE,line=1.15)

# ---------- 17. APPENDIX ----------
s=slide(); header(s,N()); title(s,"Appendix · sources & caveats")
_,tf=box(s,Inches(0.5),Inches(2.0),SW-Inches(1.0),Inches(4.8))
for t in ["Full data & verbatim quotes: Hume Pod Research workbook (7 tabs) + Google Sheet.",
          "Detailed report: REPORT.md / Hume_Pod_Full_Report.docx.",
          "",
          "Caveats:",
          "•  Amazon India page un-scrapeable — no India price/reviews (a 4.8/48,252 figure surfaced but is UNVERIFIED).",
          "•  Trustpilot blocked direct scraping (403) — rating via snippets; star histogram unavailable.",
          "•  Reddit hard-blocked — quotes second-hand via aggregators; treat as directional.",
          "•  BBB quotes are fully verified & dated (strongest negative evidence).",
          "•  The FB page mixes Pod (scale) + Band (heart-attack wearable); Band issues bleed onto the Pod."]:
    p=tf.add_paragraph()
    if t=="Caveats:": setp(p,t,15,AMBER,bold=True,space_after=6)
    elif t=="": setp(p,"",6)
    else: setp(p,t,13,WHITE if not t.startswith("•") else MUTE,line=1.1,space_after=6)

prs.save("Hume_Pod_VOC_Deck.pptx")
print("slides:",len(prs.slides._sldIdLst))