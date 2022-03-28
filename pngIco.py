from PIL import Image
import os

# assign directory
directory = 'img'

# iterate over files in directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    # checking if it is a file; if so → convert to .ico
    if os.path.isfile(f):
        print(f'{filename}')
        img = Image.open(f)
        img.save(f'out/{filename}.ico', format='ICO', sizes=[(256, 256)])