import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

x = np.linspace(0,30,1001)

a = np.sin(x)
atext = "sin(x)"

b = np.sin(x+np.pi)
btext = "sin(x+π)"

c = np.sin(2*x)
ctext = "sin(2x)"

#constructive interference
aa = a+a
aatext = atext + " + " + atext

#destructive interference
ab = a+b
abtext = atext + " + " + btext

#Inteference of different frequencies
ac = a+c
actext = atext + " + " + ctext


fig, ax = plt.subplots(nrows= 3, ncols=3, constrained_layout=True, figsize= (10,6))
fig.set_constrained_layout_pads(w_pad=0.0001, h_pad=0.0001, wspace=0.0001, hspace=0.0001) # type: ignore

ax[0,0].plot(x,a, label=atext)
ax[0,0].set_title("Constructive interference")
ax[1,0].plot(x,a, label=atext)
ax[2,0].plot(x,aa, label=abtext)


ax[0,1].plot(x,a,label= atext, color="r")
ax[0,1].set_title("Destructive interference")
ax[1,1].plot(x,b, label=btext, color="r")
ax[2,1].plot(x,ab, label=abtext, color="r")

ax[0,2].plot(x,a, label=atext, color= "orange")
ax[0,2].set_title("Different frequencies")
ax[1,2].plot(x,c, label=ctext, color= "orange")
ax[2,2].plot(x,ac, label=actext, color= "orange")


ymin, ymax = -2.1, 2.1
for list in ax:
    for axes in list:
        axes.legend(loc="upper right")
        # Remove everything else
        axes.set_xticks([])
        axes.set_yticks([])
        for spine in axes.spines.values():
            spine.set_visible(False)
        axes.set_xlabel("")
        axes.set_ylabel("")
        axes.set_ylim(ymin,ymax)
        axes.grid(False)



        
plt.show()