import os
import json
from PIL import Image

## directory path
root_dir = './교통안전(Bbox)'
src_dir = os.path.join(root_dir,'이미지')
label_dir = os.path.join(root_dir, '라벨')
dest_dir = './dataset'
dest_img_dir = os.path.join(dest_dir, 'images')
dest_label_dir = os.path.join(dest_dir, 'labels')

if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)
if not os.path.exists(dest_img_dir):
    os.mkdir(dest_img_dir)
if not os.path.exists(dest_label_dir):
    os.mkdir(dest_label_dir)

def get_img_and_ann(path, src_dir):
    with open(path, 'r') as f:
        data = json.load(f)
    f.close()

    img_list = []
    for img in data['images']:
        image = {}
        image['id'] = img['id']
        image['path'] = os.path.join(src_dir, img['file_name'])
        image['category_id'], image['bbox'] = get_ann(data['annotations'], image['id'])
        img_list.append(image)
    return img_list

def get_ann(annotations, id):
    for ann in annotations:
        if id == ann['image_id']:
            category_list = [x//7 for x in ann['category_id']]
            return category_list, ann['bbox']

def get_label_txt(file, category_list, bbox_list, img_w, img_h):
    for i, bbox in enumerate(bbox_list):
        category = category_list[i]
        x1,y1,x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        # Finding midpoints
        x_centre = (x1 + (x1 + w)) / 2
        y_centre = (y1 + (y1 + h)) / 2

        # Normalization
        x_centre = x_centre / img_w
        y_centre = y_centre / img_h
        w = w / img_w
        h = h / img_h

        # Limiting upto fix number of decimal places
        x_centre = format(x_centre, '.6f')
        y_centre = format(y_centre, '.6f')
        w = format(w, '.6f')
        h = format(h, '.6f')

        # Writing current object
        file.write(f"{category} {x_centre} {y_centre} {w} {h}\n")

##

folder_list = [f for f in os.listdir(src_dir) if not f.startswith('.')] # ingore '.DS_Store'
idx = 1
for folder in folder_list:
    label_folder = os.path.join(label_dir,folder)
    dir_list = [f for f in os.listdir(label_folder) if not f.startswith('.')]
    for dir in dir_list:
        json_dir = os.path.join(label_folder, dir)
        json_list = [f for f in os.listdir(json_dir) if not f.startswith('.')]

        for file in json_list:
            json_path = os.path.join(json_dir, file) ## annotation path
            data_list = get_img_and_ann(json_path, os.path.join(src_dir, folder))
            for data in data_list:
                # Get image size
                img_path = data['path']
                image = Image.open(img_path)
                img_w, img_h = image.size
                # Opening file for current image
                file_object = open(f"{dest_label_dir}/{idx}.txt", "a")
                # Get text file for yolo format
                get_label_txt(file_object, data['category_id'],data['bbox'], img_w, img_h)
                file_object.close()
                # Save image
                image.save(os.path.join(dest_img_dir, str(idx)+'.jpg'),'JPEG')
                idx+=1