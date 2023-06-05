# %%
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from tqdm import tqdm
from joblib import Parallel, delayed

# %%
locs = []

# file = open("input/city_locators.txt","r")
# contents = file.read().splitlines()
# file.close()
# for line in range(8, len(contents)-4, 6):
#     ids = int(contents[line].split("=")[1])
#     temp = contents[line+1].split(" ")[1:-1]
#     locs.append([float(temp[0])/2, (6144-float(temp[2]))/2])

file = open("input/port_locators.txt","r")
contents = file.read().splitlines()
file.close()
for line in range(8, len(contents)-4, 6):
    ids = int(contents[line].split("=")[1])
    temp = contents[line+1].split(" ")[1:-1]
    locs.append([float(temp[0])/2, (4096-float(temp[2]))/2])

#old
#image = np.array(Image.open(r"input/example.png","r").convert('L'))

maxpixelx = int(8192/2)
maxpixely = int(4096/2)
image = np.zeros((2048, 4096)).astype(np.uint8)

# %%
ncells = 256
mapped = [[[] for _ in range(ncells)] for _ in range(ncells)]
for elem in locs:
    xindex = int(round(elem[0]/maxpixelx*(ncells-1)))
    yindex = int(round(elem[1]/maxpixely*(ncells-1)))
    mapped[xindex][yindex].append(elem)


# %%
def inner_loop(y0, mapped):
    minval = 5
    temp = []
    for x0 in range(maxpixelx):
        xindex = int(round(x0/maxpixelx*(ncells-1)))
        yindex = int(round(y0/maxpixely*(ncells-1)))

        search = []
        search.extend(mapped[xindex][yindex])

        xlims = [max(0,xindex-1),min(ncells-1,xindex+1)]
        ylims = [max(0,yindex-1),min(ncells-1,yindex+1)]
        search.extend(mapped[xlims[0]][yindex])
        search.extend(mapped[xlims[1]][yindex])
        search.extend(mapped[xindex][ylims[0]])
        search.extend(mapped[xindex][ylims[1]])

        search.extend(mapped[xlims[0]][ylims[0]])
        search.extend(mapped[xlims[1]][ylims[0]])
        search.extend(mapped[xlims[0]][ylims[1]])
        search.extend(mapped[xlims[1]][ylims[1]])

        if len(search)==0:
            temp.append(0)
            continue

        dist = np.sqrt(min([(elem[0]-x0)**2+(elem[1]-y0)**2 for elem in search]))
        dist = int((1-min(minval,dist)/minval)*255)
        temp.append(dist)
    return temp

# %%
result = Parallel(n_jobs=-2)(delayed(inner_loop)(y0, mapped) for y0 in tqdm(range(maxpixely)))

for y0, temp in enumerate(result):
    for x0, value in enumerate(temp):
        image[y0,x0] = value

Image.fromarray(image).save('output/nightLight.png')



# %%
