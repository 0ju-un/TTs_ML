import os
import shutil
import json
from PIL import Image
from sklearn.model_selection import train_test_split

## directory path
root_dir = './교통안전(Bbox)'
src_dir = os.path.join(root_dir,'이미지')
label_dir = os.path.join(root_dir, '라벨')
dest_dir = './dataset'

if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)
if not os.path.exists(os.path.join(dest_dir, 'images')):
    os.mkdir(os.path.join(dest_dir, 'images'))
if not os.path.exists(os.path.join(dest_dir, 'labels')):
    os.mkdir(os.path.join(dest_dir, 'labels'))

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

def convert_label(category_list, bbox_list, img_w, img_h):
    labels = []
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

        label = [str(category), x_centre, y_centre, w, h]
        labels.append(label)
    return labels

def save_data(X, Y, dir, index):
    img_dir = os.path.join(dir,'images/'+index)
    label_dir = os.path.join(dir,'labels/'+index)
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if not os.path.exists(label_dir):
        os.mkdir(label_dir)

    for idx, origin_img in enumerate(X):
        # img.save(os.path.join(img_dir,f'{idx+1}.jpg'), 'JPEG')
        copy_path = os.path.join(img_dir,f'{idx+1}.jpg')
        if not os.path.exists(copy_path):
            shutil.copy(origin_img, copy_path)
        file_object = open(f"{label_dir}/{idx+1}.txt", "a")        # Opening file for current image
        for bbox in Y[idx]:
            file_object.write('\t'.join(bbox))
        file_object.close()

##

folder_list = [f for f in os.listdir(src_dir) if not f.startswith('.')] # ingore '.DS_Store'
img_list = []
label_list = []

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
                # Get image
                img_path = data['path']
                image = Image.open(img_path)
                img_list.append(img_path) # add image
                img_w, img_h = image.size

                # Get labels for yolo format
                bbox = convert_label(data['category_id'],data['bbox'], img_w, img_h)
                label_list.append(bbox)

## split train, val, test
x_train, x_test, y_train, y_test = train_test_split(img_list, label_list, test_size=0.1, shuffle=True, random_state=34)
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.11, shuffle=True, random_state=34)

print(len(x_train), len(x_val), len(x_test))

save_data(x_train, y_train, dest_dir, 'train')
save_data(x_val, y_val, dest_dir, 'val')
save_data(x_test, y_test, dest_dir, 'test')