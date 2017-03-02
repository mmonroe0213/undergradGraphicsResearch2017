import bpy
import datetime

image = "C:/Users/Michael/Documents/Research/src/images/render50P_half_size.png"
myImage = bpy.data.images.load(image)
w,h = myImage.size[0], myImage.size[1]

def gaussianBlur(kernel):
    global w,h, myImage
    pix = [v for v in myImage.pixels]
    blur_pix = [v for v in myImage.pixels]
    bpy.data.images.remove(myImage, do_unlink = True)
    for row in range(3, h-2):
        for col in range(3, w-2):
            pixels = [[], [], [], [], []]
            for i in range(-2, 3):
                for j in range(-2, 3):
                    pixels[i + 2].append([pix[(((row+i)*w)+(col+j))*4], 
                                          pix[(((row+i)*w)+(col+j))*4 + 1], 
                                          pix[(((row+i)*w)+(col+j))*4 + 2]])
            new_pixel = [0, 0, 0]
            for i in range(5):
                for j in range(5):
                    for k in range(3):
                        new_pixel[k] += pixels[i][j][k] * kernel[i][j]
            #print(pix[row * w + col], new_pixel)
            for i in range(3):
                blur_pix[((row * w) + col)*4 + i] = new_pixel[i]
    return blur_pix
    
def main():
##    image = input("Enter image name:")
    global w, h
    kernel = [[0.003765, 0.015019, 0.023792, 0.015019, 0.003765],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.023792, 0.094907, 0.150342, 0.094907, 0.023792],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.003765, 0.015019, 0.023792, 0.015019, 0.003765]]
    bpy.data.images.new("blurredImage", w, h)
    blurredImage = bpy.data.images["blurredImage"]
    blurredImage.pixels = gaussianBlur(kernel)
    blurredImage.save_render("C:/Users/Michael/Documents/Research/src/images/blurredImage" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png")

main()