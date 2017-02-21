from PIL import Image

def imageDif(image1, image2):
    im1 = Image.open(image1)
    im2 = Image.open(image2)
    difIm = Image.new(im1.mode, (im1.width, im1.height))
    if im1.width != im2.width and im1.height != im2.height:
        print("Error: Dimensions of images must be the same")
    for row in range(im1.height):
        for col in range(im1.width):
            pix1 = im1.getpixel((col,row))
            pix2 = im2.getpixel((col,row))
            r = (pix2[0] - pix1[0])**2
            g = (pix2[1] - pix1[1])**2
            b = (pix2[2] - pix1[2])**2
            ave = (r + g + b) // 3
            difIm.putpixel((col,row),(ave,ave,ave))
    difIm.save("./difImageGrey.png")

def main():
    im1 = "render50P_small.png"
    im2 = "blurredImage.png"
    imageDif(im1,im2)

main()
