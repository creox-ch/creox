"""Original soundtrack for the Creox promo (synthesised, no samples). 20 s, 120 BPM. Sparse, no whooshes."""
import numpy as np, wave, sys
SR=48000; DUR=20.0; N=int(SR*DUR); fps=30
out=np.zeros((N,2)); t=np.arange(N)/SR
def env(n,a=0.005,d=0.3):
    x=np.arange(n)/SR; return np.minimum(1,x/a)*np.exp(-x/d)
def add(sig,at,gain=1.0,pan=0.0):
    i=int(at*SR); n=min(len(sig),N-i)
    if n<=0: return
    out[i:i+n,0]+=sig[:n]*gain*(1-max(pan,0)); out[i:i+n,1]+=sig[:n]*gain*(1+min(pan,0))
def tone(f,dur,d=0.3,harm=(1,.5,.25)):
    n=int(dur*SR); x=np.arange(n)/SR
    return sum(h*np.sin(2*np.pi*f*(k+1)*x) for k,h in enumerate(harm))*env(n,0.004,d)
def kick(dur=0.35):
    n=int(dur*SR); x=np.arange(n)/SR; f=50+90*np.exp(-x*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*9)
def tick(dur=0.05,seed=1):
    n=int(dur*SR); return np.random.default_rng(seed).standard_normal(n)*np.exp(-np.arange(n)/SR*90)*0.5
note=lambda m:440*2**((m-69)/12)
F=lambda fr: fr/fps
T=dict(drop=25,chips=[48,56,64],click=82,soc=95,web=215,nl=290,brief=365,poster=450,end=535)
# pad
pad=np.zeros(N)
for m in (57,64,71,72): pad+=np.sin(2*np.pi*note(m)*t)*0.05+np.sin(2*np.pi*note(m)*1.003*t)*0.035
sw=np.clip(t/1.2,0,1)*np.clip((DUR-t)/1.0,0,1); out+=np.stack([pad*sw,pad*sw],1)
add(tone(note(45),0.6,0.35,(1,.3)),F(T['drop']),0.55)
for fr in T['chips']: add(tick(),F(fr),0.3,0.3)
add(tick(0.04,2),F(T['click']),0.9); add(tone(note(69),0.25,0.08,(1,.2)),F(T['click']),0.35)
# groove from approval to end, bass follows the scenes
beat=0.5; k=0; st=F(T['click'])
roots={0:33,1:36,2:31,3:33}
while st+k*beat<DUR-0.8:
    tt=st+k*beat; add(kick(),tt,0.65)
    add(tone(note(roots[(k//8)%4]),0.45,0.2,(1,.15)),tt,0.32)
    if k%2==1: add(tick(0.03,3),tt,0.16,-0.2)
    k+=1
# social: plucks on cards and tiles
scale=[69,72,74,76,79,81,84,86,88]
for i in range(5): add(tone(note(scale[i]),0.45,0.16,(1,.4,.15)),F(T['soc']+6+i*8+12),0.28,(-0.4 if i%2 else 0.4))
for i in range(8): add(tone(note(scale[i]+12),0.2,0.07,(1,.3)),F(T['soc']+52+i*6+8),0.12,(0.3 if i%2 else -0.3))
# website, newsletter: soft two-note chime when done
for fr in (T['web']+44, T['nl']+50): add(tone(note(76),0.6,0.3,(1,.3)),F(fr),0.25); add(tone(note(81),0.8,0.4,(1,.3)),F(fr)+0.1,0.22)
add(tone(note(79),0.3,0.12,(1,.2)),F(T['nl']+16),0.18)
# brief: flap and stamp = short low thuds
add(tone(note(40),0.25,0.08,(1,.5)),F(T['brief']+50),0.4); add(tone(note(38),0.3,0.1,(1,.6)),F(T['brief']+52),0.55)
# poster: two thuds when pasted
for d in (15,31): add(tone(note(36),0.3,0.1,(1,.6,.2)),F(T['poster']+d),0.6)
# end chord
for m in (57,64,69,72,76): add(tone(note(m),2.2,1.0,(1,.3,.1)),F(T['end']),0.15)
out/=np.max(np.abs(out))*1.12
out*=np.clip((DUR-t)/0.6,0,1)[:,None]
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
print("ok")
