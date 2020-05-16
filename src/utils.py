import os
import shutil
import xmltodict
from zipfile import ZipFile

PATH = 'annotations/'


def parse_annotation(path):
    path_temp = os.path.abspath(os.path.join(path,  '..', 'temp/'))

    if not os.path.isdir(path_temp):
        os.mkdir(path_temp)

    with ZipFile(path, 'r') as zipobj:
        zipobj.extractall(path=path_temp)

    filename = path.split('/')[-1]
    video = filename.split('_')[0]
    annotator = filename.split('_')[-1].replace('.zip', '')

    file = os.listdir(path_temp)
    if len(file) > 1:
        raise Exception('More than one file exists in %s' % (path))
    else:
        # there is only one file as expected, work with that one
        file = file[0]

    with open(os.path.join(path_temp, file), 'r') as xml_file:
        content = dict(xmltodict.parse(xml_file.read()))

    # TODO: implement parsing of JSON content

    shutil.rmtree(path_temp, ignore_errors=True)
    return None


def get_annotations():
    annotations = []

    # TODO: this is only for one annotator - expand
    path_lukas = os.path.join(PATH, 'LHu')
    files_lukas = [f for f in os.listdir(path_lukas) if f.endswith('.zip')]
    for file in files_lukas:
        path_annotation = os.path.join(path_lukas, file)
        annotation = parse_annotation(path_annotation)
        annotations.extend(annotation)
    return annotations  # (bspw als dict, list, dataframe)


if __name__ == "__main__":
    get_annotations()
