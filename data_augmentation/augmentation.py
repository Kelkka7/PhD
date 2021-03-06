import Augmentor
import os
import glob
import cv2
import imghdr
from os.path import normpath, basename

cur_dir = os.getcwd()
cur_dir = str(cur_dir)

'''
    pollen image basic folder structure:
    images/*pollen_species*/*.jpg
    where pollen_species is any given pollen species
'''

# data augmentation function
def run_augmentor(output='output\\'):
    output = "\\" + output

    # make a new folder called images if not in existence
    image_folder = os.path.join(cur_dir, 'images\\')

    # make a list of subfolders for each pollen type
    folder_list = []
    for folder in glob.glob(image_folder + '*/'):
        folder_list.append(folder)

    # loop through pollen folders and make 1000 samples of each, then save them into *cur_dir*/output/"pollen_name"
    for img_folder in folder_list:
        base_name = img_folder.replace(str(image_folder), '')
        output_folder = cur_dir + output + base_name
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        p = Augmentor.Pipeline(source_directory=img_folder, output_directory=output_folder) # initialize a data augmentation pipeline
        p.rotate_random_90(probability=1.0) # rotate by 90, 180, or 270 degrees
        p.greyscale(probability=1.0) # convert the rotated image to greyscale
        #p.shear(probability=1, max_shear_left=10, max_shear_right=10)
        #p.random_color(probability=1.0, min_factor=0.2, max_factor=0.8)
        p.random_contrast(probability=1.0, min_factor=0.3, max_factor=0.9) # random contrast between a factor 0.3 and 0.9, where 0 is a solid grey image, 1 is the original
        p.histogram_equalisation(probability=1.0) # equalize the image histograms
        p.crop_centre(probability=1, percentage_area=0.65) # crop the images to the centre of the grains to exclude grain shape and only analyze texture
        p.random_distortion(probability=1.0, grid_height=10, grid_width=10, magnitude=3) # do random elastic distortion on the cropped images
        p.resize(probability=1.0, width=224, height=224) # resize the images to 224*224 size
        p.sample(1000) # create 1000 images based on the above rules


# check the image filetype and convert to .jpg if an invalid filetype is found
def check_output_filetype(output='output\\'):
    for folder in os.listdir(os.path.join(cur_dir, output)):
        output_path = os.path.join(cur_dir, output)
        full_path = os.path.join(output_path, folder)
        for img in os.listdir(full_path):
            image = cv2.imread(os.path.join(full_path, img))
            file_type = imghdr.what(os.path.join(full_path, img))
            if file_type != 'jpeg':
                print(img + " - invalid - " + str(file_type))
                return cv2.imwrite(os.path.join(folder, img), image)


# rename all images in the data augmentation output folder
def rename_output_images(output='output\\'):
    output_img_folder = os.path.join(cur_dir, output)
    output_folder_list = []
    for folder in glob.glob(output_img_folder + '*/'):
        output_folder_list.append(folder)

    for output_folder in output_folder_list:
        num = 1
        for img in os.listdir(output_folder):
            find_str = '('
            index_start = img.find(find_str)
            if (img[int(index_start+2)]).isnumeric():
                index_end = int(index_start) + 4
            else:
                index_end = int(index_start) + 3
            orig_num_str = img[index_start:index_end]
            img_renamed = img.replace(str(img), ('orig_num' + orig_num_str + '_(' + str(num) + ').jpg'))
            os.rename(os.path.join(output_folder, img), os.path.join(output_folder, img_renamed))
            print(img, "has been renamed as", img_renamed)
            num += 1


# select four images and all of the transformations and move to a training folder
def make_test_set(output='output\\'):
    output_img_folder = os.path.join(cur_dir, output)
    output_folder_list = []
    for folder in glob.glob(output_img_folder + '*/'):
        output_folder_list.append(folder)

    test_set = os.path.join(cur_dir, 'test_set')
    if not os.path.exists(test_set):
        os.makedirs(test_set)

    for img_folder in output_folder_list:
        renamed = basename(normpath(img_folder))
        for img in os.listdir(img_folder):
            output_folder = os.path.join(test_set, renamed)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            find_str = 'orig_num('
            index_start = int(img.find(find_str)) + len(find_str)

            if img[index_start:(index_start+2)] == "1)" or img[index_start:(index_start+2)] == "2)" or img[index_start:(index_start+2)] == "34" or img[index_start:(index_start+2)] == "35":
                os.rename(os.path.join(img_folder, img), os.path.join(output_folder, img))
            else:
                continue


output_folder_name = 'output\\' # which folder to send augmented images

run_augmentor(output_folder_name) # run augmentation
check_output_filetype(output_folder_name) # check filetype
rename_output_images(output_folder_name) # rename the images
#make_test_set(output_folder_name) - not currently in use
