import bpy
import datetime

def imageDif(image1, image2):
    print(image1, image2)
    maxDif = 0
    maxTuples = [(0,0,0,0)]
    im1 = bpy.data.images.load(image1)
    im1Array = [v for v in im1.pixels]
    w1,h1 = im1.size[0], im1.size[1]
    print(w1, h1)
    bpy.data.images.remove(im1, do_unlink = True)
    im2 = bpy.data.images.load(image2)
    im2Array = [x for x in im2.pixels]
    w2,h2 = im2.size[0], im2.size[1]
    print(w2,h2)
    bpy.data.images.remove(im2, do_unlink = True)
    if w1 != w2 and h1 != h2:
        print("Error: Dimensions of images must be the same")
    difImArray = [0 for _ in range(w1) for _ in range(h1) for _ in range(4)]
#    for ix in range(w1):
#        for iy in range(h1):
#            difImArray[(iy*w1+ix)*4+3] = 1
    
    for row in range(h1):
        for col in range(w1):
            pix1 = [im1Array[((row*w1)+col)*4], im1Array[((row*w1)+col)*4 + 1], im1Array[((row*w1)+col)*4 + 2]]
            pix2 = [im2Array[((row*w1)+col)*4], im2Array[((row*w1)+col)*4 + 1], im2Array[((row*w1)+col)*4 + 2]]
            #print(pix1, pix2)
            r = (pix2[0] - pix1[0])
            if (r < 0):
                r = pix1[0] - pix2[0]
            g = (pix2[1] - pix1[1])
            if (g < 0):
                g = pix1[1] - pix2[1]
            b = (pix2[2] - pix1[2])
            if (b < 0):
                b = pix1[2] - pix2[2]
            ave = (r + g + b) / 3
            difImArray[((row*w1)+col)*4] = ave;
            difImArray[((row*w1)+col)*4 + 1] = ave;
            difImArray[((row*w1)+col)*4 + 2] = ave;
            difImArray[((row*w1)+col)*4 + 3] = 1;
            if ave > maxDif:
                maxDif = ave
                maxTuples[0] = (col,row,50,50)
    bpy.data.images.new("difImage", w1, h1)
    difIm = bpy.data.images["difImage"]
    difIm.pixels = difImArray
    difIm.save_render("C:/Users/Michael/Documents/Research/src/images/difImageGrey" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png")
    print(maxDif)
    return maxTuples

def main():
    im1 = "C:/Users/Michael/Documents/Research/src/images/render50P_half_size.png"
    im2 = "C:/Users/Michael/Documents/Research/src/images/blurredImage2017_03_01_22_33_12.png"
    tuples = imageDif(im1,im2)
    print(tuples[0][0],tuples[0][1],tuples[0][2],tuples[0][3])

main()
