from PIL import Image
import os


def scanDirConvert() -> None:
    """
    converts all files in /img to .ico format onto the user's desktop,
    then removes the files
    :return:
    """
    directory = 'img'

    for filename in os.scandir(directory):
        if filename.is_file():
            n = filename.name
            name_no_ext = n.split('.')[0]

            print(name_no_ext)

            # convert images to 256x256 .ico files
            img = Image.open(filename.path)

            out_path = f'{os.path.expanduser("~")}/Desktop/{name_no_ext}.ico'
            print(out_path)
            img.save(out_path, format="ICO", sizes=[(256, 256)])

            # remove file
            os.remove(filename.path)


def listDirConvert():
    directory = 'img'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        # checking if it is a file; if so → convert to .ico
        if os.path.isfile(f):
            print(f'{filename}')
            img = Image.open(f)
            img.save(f'out/{filename}.ico', format='ICO', sizes=[(256, 256)])


scanDirConvert()