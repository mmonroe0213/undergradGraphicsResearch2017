from PIL import Image
import datetime

def gaussianBlur(image, kernel):
    myImage = Image.open(image)
    blurredImage = Image.open(image)
    for row in range(3, myImage.height-2):
        for col in range(3, myImage.width-2):
            pixels = [[], [], [], [], []]
            for i in range(-2, 3):
                for j in range(-2, 3):
                    pixels[i + 2].append(myImage.getpixel((col+j,row+i)))
            r = 0
            g = 0
            b = 0
            for i in range(5):
                for j in range(5):
                    r += pixels[i][j][0] * kernel[i][j]
                    g += pixels[i][j][1] * kernel[i][j]
                    b += pixels[i][j][2] * kernel[i][j]
            blurredPixel = (int(r), int(g), int(b))
            blurredImage.putpixel((col,row),blurredPixel)
    blurredImage.save("./blurredImage" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png")

def main():
##    image = input("Enter image name:")
    image = "render50P_half_size.png"
    kernel = [[0.003765, 0.015019, 0.023792, 0.015019, 0.003765],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.023792, 0.094907, 0.150342, 0.094907, 0.023792],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.003765, 0.015019, 0.023792, 0.015019, 0.003765]]
    gaussianBlur(image, kernel)

main()
