import image
path = "/home/mlenka/images/"
def test_filters():
    # original image
    img = image.Image(path+"board.jpg")
    kernel = [4.5,0,0,0,0,0,0,0,0,0,0]
    # gaussian filter output
    blur = image.Image(img.width, img.height, img.channels)
    # gray
    gray = image.Image(img.width, img.height, 1)
    # box / averaging
    box = image.Image(img.width, img.height, img.channels)
    img.filter(blur,kernel,True)
    kernel = [1,1,1,1,1,1,1,1,1,1,1]
    img.filter(box,kernel,False)
    img.to_gray_scale(gray)
    # save images to disk
    blur.write(path+"board_gauss.jpg")
    box.write(path+"board_mean.jpg")
    gray.write(path+"board_gray.jpg")
def object_detect():
    # background
    b = image.Image(path + "2024-05-12_12:57:26.jpg")
    # background + object
    f = image.Image(path + "2024-05-12_12:56:10.jpg")

    # gray scales
    b_g = image.Image(b.width, b.height, 1)
    f_g = image.Image(f.width, f.height, 1)
    b.to_gray_scale(b_g)
    f.to_gray_scale(f_g)

    # frame differencing
    diff = image.Image(b.width, b.height, 1)
    b_g.absolute_diff(f_g, diff)

    # thresholding
    obj_th =  image.Image(b.width, b.height, 1)
    diff.otsu_1d(obj_th)
    # save to disk
    obj_th.write(path+"detect.jpg")

    if obj_th.detect():
        print("Object detected")
    else:
        print("No object detected")
def main():
    object_detect()
if __name__ == "__main__":
    main()


