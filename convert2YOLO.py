import os

## directory path
root_dir = './aihub_dataset'
src_dir = os.path.join(root_dir,'이미지')
label_dir = os.path.join(root_dir, '[라벨]교통안전(Bbox)')
dest_dir = './dataset'

if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)

def store_files(src_dir, label_dir, dest_dir):
    folder_list = [f for f in os.listdir(src_dir) if not f.startswith('.')] # ingore '.DS_Store'
    idx = 1
    for folder in folder_list:
        dir_list = [f for f in os.listdir(os.path.join(src_dir,folder)) if not f.startswith('.')]
        for dir in dir_list:
            dir_path = os.path.join(folder, dir)
            img_dir = os.path.join(src_dir, dir_path)
            img_list = [f for f in os.listdir(img_dir) if not f.startswith('.')]

            # replace image file
            for img in img_list:
                img_name = str(idx) +'.jpg'
                idx += 1
                print(img_name)
                # os.replace(os.path.join(img_dir,img), os.path.join(dest_dir, img_name))

store_files(src_dir, label_dir,dest_dir)




