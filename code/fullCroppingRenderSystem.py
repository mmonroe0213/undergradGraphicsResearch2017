import bpy
import math
import random
import datetime


bpy.data.scenes[0].render.engine = 'CYCLES'

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
    render.filepath = bpy.path.abspath('//../../images/%s' % fn)
    
    # do the render!
    bpy.ops.render.render(write_still=True)
    
    # load render into new image (do be deleted)
    img = bpy.data.images.load('//../../images/%s' % fn)
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
                cpix[idx4+ic] = math.pow(ctot[idx4+ic] / counts[idx], 1.0)


def gaussianBlur(kernel):
    global cpix
    global rw, rh
    blur_pix = [v for v in cpix]
    for row in range(3, rh-2):
        for col in range(3, rw-2):
            pixels = [[], [], [], [], []]
            for i in range(-2, 3):
                for j in range(-2, 3):
                    pixels[i + 2].append([cpix[(((row+i)*rw)+(col+j))*4], 
                                          cpix[(((row+i)*rw)+(col+j))*4 + 1], 
                                          cpix[(((row+i)*rw)+(col+j))*4 + 2]])
            new_pixel = [0, 0, 0]
            for i in range(5):
                for j in range(5):
                    for k in range(3):
                        new_pixel[k] += pixels[i][j][k] * kernel[i][j]
            #print(pix[row * w + col], new_pixel)
            for i in range(3):
                blur_pix[((row * rw) + col)*4 + i] = new_pixel[i]
    return blur_pix

def imageDif(im1, im2):
    #print(image1, image2)
    global rw, rh
    maxDif = 0
    maxTuples = [(0,0,0,0)]
    difImArray = [0 for _ in range(rw) for _ in range(rh) for _ in range(4)]
#    for ix in range(rw):
#        for iy in range(rh):
#            difImArray[(iy*rw+ix)*4+3] = 1
    
    for row in range(rh):
        for col in range(rw):
            pix1 = [im1[((row*rw)+col)*4], im1[((row*rw)+col)*4 + 1], im1[((row*rw)+col)*4 + 2]]
            pix2 = [im2[((row*rw)+col)*4], im2[((row*rw)+col)*4 + 1], im2[((row*rw)+col)*4 + 2]]
            #print(pix1, pix2)
            r = (pix2[0] - pix1[0]) ** 2
            g = (pix2[1] - pix1[1]) ** 2
            b = (pix2[2] - pix1[2]) ** 2
            ave = (r + g + b) / 3
            difImArray[((row*rw)+col)*4] = ave;
            difImArray[((row*rw)+col)*4 + 1] = ave;
            difImArray[((row*rw)+col)*4 + 2] = ave;
            difImArray[((row*rw)+col)*4 + 3] = 1;
            if ave > maxDif:
                #print("Average: ", ave)
                #print("Max Dif: ", maxDif)
                maxDif = ave
                maxTuples[0] = (col,row,50,50)
                #print(col, row)
    bpy.data.images.new("difImage", rw, rh)
    difIm = bpy.data.images["difImage"]
    difIm.pixels = difImArray
    difIm.save_render("//../../images/difImageGrey" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png")
    bpy.data.images.remove(difIm, do_unlink=True)
    return maxTuples
    
    
# render full low-res
renderRegion(rw//2,rh//2,rw,rh,4, 'full.png')

kernel = [[0.003765, 0.015019, 0.023792, 0.015019, 0.003765],
          [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
          [0.023792, 0.094907, 0.150342, 0.094907, 0.023792],
          [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
          [0.003765, 0.015019, 0.023792, 0.015019, 0.003765]]

for _ in range(2):
    bpy.data.images.new("blurredImage", rw, rh)
    blurredImage = bpy.data.images["blurredImage"]
    blurredImage.pixels = gaussianBlur(kernel)
    blurredImage.save_render("//../../images/blurredImage.png")

    maxTuple = imageDif(cpix, blurredImage.pixels)
    bpy.data.images.remove(blurredImage, do_unlink=True)

    # render partial high-res
    x,y,w,h,s = maxTuple[0][0],maxTuple[0][1],maxTuple[0][2],maxTuple[0][3],40
    renderRegion(x,y,w,h,s, 'partial.png')

    # update combined (aggregate) image
    cimg.pixels = cpix
    cimg.save_render("//../../images/combined.png")

print('finished')