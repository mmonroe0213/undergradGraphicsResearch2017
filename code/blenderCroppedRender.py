import bpy
import math
import random

print('-'*50)

# gather data
scene = bpy.context.scene
render = scene.render
rw,rh,rp = render.resolution_x,render.resolution_y,render.resolution_percentage
rw,rh = int(rw * rp / 100), int(rh * rp / 100)

if 'combined' in bpy.data.images:
    bpy.data.images.remove(bpy.data.images['combined'], do_unlink=True)
bpy.data.images.new('combined', rw, rh)
cimg = bpy.data.images['combined']
cpix = [0 for _ in range(rw) for _ in range(rh) for _ in range(4)]
ctot = [0 for _ in range(rw) for _ in range(rh) for _ in range(4)]
counts = [0 for _ in range(rw) for _ in range(rh)]

# set alpha
for ix in range(rw):
    for iy in range(rh):
        cpix[(iy*rw+ix)*4+3] = 1
        ctot[(iy*rw+ix)*4+3] = 1

def renderRegion(x,y,w,h,s, fn):
    global rw,rh,rwp,rhp
    global cimg,cpix,ctot,counts
    
    # ensure we're only working with ints
    x,y,w,h,s = map(int,[x,y,w,h,s])
    
    print('rendering: (%d,%d)x(%d,%d)@%d' % (x,y,w,h,s))
    
    # set up render borders to focus render on specific region
    rl,rr = x - math.floor(w/2), x + math.ceil(w/2)
    rb,rt = y - math.floor(h/2), y + math.ceil(h/2)
    rl,rr = max(0, min(rw-1, rl)),max(0, min(rw-1, rr))
    rb,rt = max(0, min(rh-1, rb)),max(0, min(rh-1, rt))
    render.use_border = True            # tell renderer to use border (below)
    render.use_crop_to_border = False   # keep same size (do not crop)
    # note: render border is [0,1]x[0,1], not [0,width)x[0,height)
    render.border_min_x = rl / rw
    render.border_min_y = 1 - rt / rh
    render.border_max_x = rr / rw
    render.border_max_y = 1 - rb / rh
    
    # set the correct number of samples per pixel
    scene.cycles.samples = s     # not s2
    scene.cycles.aa_samples = s
    scene.cycles.use_square_samples = False
    
    # ensure (probabilistically) that the PRNG uses a different seed
    # for each render 
    scene.cycles.seed = random.randint(0,100000)
    
    # tell blender to render to file located in same folder
    render.filepath = bpy.path.abspath('//%s' % fn)
    
    # do the render!
    bpy.ops.render.render(write_still=True)
    
    # load render into new image (do be deleted)
    img = bpy.data.images.load('//%s' % fn)
    pix = [v*s for v in img.pixels]
    bpy.data.images.remove(img, do_unlink=True) # delete render image
    
    # aggregate
    print('aggregating partial render')
    # leaving a small border...
    for ix in range(rl+1,rr-1):
        for iy in range((rh-1)-rt+1,(rh-1)-rb-1):
            idx,idx4 = iy*rw+ix,(iy*rw+ix)*4
            counts[idx] += s
            for ic in range(3):
                ctot[idx4+ic] += pix[idx4+ic]
                cpix[idx4+ic] = math.pow(ctot[idx4+ic] / counts[idx], 0.5)
    

# render full low-res
renderRegion(rw//2,rh//2,rw,rh,4, 'full.exr')

# render partial high-res
x,y,w,h,s = 400,400,200,100,40
renderRegion(x,y,w,h,s, 'partial.exr')

# update combined (aggregate) image
cimg.pixels = cpix
print('finished')
