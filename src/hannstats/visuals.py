# Custom plotting functions styled for the Hannibal video project

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


color_palette = ['#860307', #Deep Red
                 '#C51C14', #Bright Blood
                 '#E83A36', #Pomegranite
                 '#D6AB7F', # Beige
                 '#191212'  #Black
                 ]
plt.style.use(['dark_background', 'seaborn-talk', 'seaborn-dark-palette'])

def get_color_palette():
    return color_palette

def bar(x,y, ax=None, **plt_kwargs):
    if ax is None:
        ax = plt.gca()
    # Check for user-defined color; else use default
    color = plt_kwargs.pop('color', color_palette[0])
    ax.bar(x, y, color=color, **plt_kwargs)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    sns.despine(right=True, top=True)
    return(ax)

def line(x,y, ax=None, **plt_kwargs):
    if ax is None:
        ax = plt.gca()
    color = plt_kwargs.pop('color', color_palette[0])
    ax.plot(x, y, color=color, **plt_kwargs)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    return(ax)

def barh(x,y,ax=None, **plt_kwargs):
    if ax is None:
        ax = plt.gca()
    # Check for user-defined color; else use default
    color = plt_kwargs.pop('color', color_palette[0])
    ax.barh(x, y, color=color, **plt_kwargs)
    sns.despine(right=True, top=True)
    return(ax)



if __name__ == "__main__":
    # Lil Demo
    import statsmodels.api as sm
    prestige = sm.datasets.get_rdataset("Duncan", "carData", cache=True).data

    b = bar(prestige.type, prestige.prestige)
    b.set_xlabel("Profession")
    b.set_ylabel("Prestige")
    plt.show()
    plt.clf()

    l = line(prestige.type, prestige.prestige)
    l.set_xlabel("Profession")
    l.set_ylabel("Prestige")
    plt.show()
