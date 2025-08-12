import io
import os
import sys
from PIL import Image

def check_image_format(file_path):
    with open(file_path, 'rb') as file:
        head = file.read(32 * 1024)
    image = Image.open(io.BytesIO(head))
    # print(image.format)
    return image.format

target_files = []
for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        for root, dirs, files in os.walk(arg):
            for file in files:
                if not os.path.splitext(file)[1]:
                    target_files.append(os.path.join(root, file))
    elif os.path.isfile(arg):
        if not os.path.splitext(arg)[1]:
            target_files.append(arg)

for target_file in target_files:
    ext = ""
    try:
        ext = check_image_format(target_file)
    except Exception as e:
        print(e)
        continue

    filename = target_file + "." + ext
    if not os.path.exists(filename):
        os.rename(target_file, filename)
        print(filename)
