import os
from zipfile import ZipFile
import io
import pathlib

def getFilePaths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths


def generateGCZip():
    '''
    # path to folder which needs to be zipped
    directory = 'static/GameChangerFiles'

    # calling function to get all file paths in the directory
    file_paths = getFilePaths(directory)
    print(file_paths)
    # printing the list of all files to be zipped
    for file_name in file_paths:
        print(file_name)

        # writing files to a zipfile
    with ZipFile('gcFiles.zip', 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)
    '''
    base_path = pathlib.Path('./static/GameChangerFiles')
    data = io.BytesIO()
    with ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='static/gameChangerFiles.zip'
    )


if __name__ == '__main__':
    generateGCZip()


