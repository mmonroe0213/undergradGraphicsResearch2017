from PIL import Image

def gaussianBlur(image, kernel):
    myImage = Image.open(image)
    blurredImage = Image.new(myImage.mode, (myImage.width, myImage.height))
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
    blurredImage.save("./blurredImage1.png")

def main():
##    image = input("Enter image name:")
    image = "render1000P_small.png"
    kernel = [[0.003765, 0.015019, 0.023792, 0.015019, 0.003765],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.023792, 0.094907, 0.150342, 0.094907, 0.023792],
              [0.015019, 0.059912, 0.094907, 0.059912, 0.015019],
              [0.003765, 0.015019, 0.023792, 0.015019, 0.003765]]
    gaussianBlur(image, kernel)

main()
