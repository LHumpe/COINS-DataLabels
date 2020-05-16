import json
import os
import pandas as pd
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
        content = xmltodict.parse(xml_file.read())
        # dirty but working - convert to dict, deep: all ordereddicts
        content = json.loads(json.dumps(content))

    # TODO: check if files with different structures might occur - multiple tracks?
    # e.g. multiple faces?
    track = content['annotations']['track']['box']

    frames = []

    for frame in track:
        attributes = {list(a.values())[0]: list(a.values())[1]
                      for a in frame['attribute']}
        attributes['frame'] = frame['@frame']
        frames.append(attributes)

    annotation = pd.DataFrame(frames)
    annotation['annotator'] = annotator
    annotation['video'] = video

    shutil.rmtree(path_temp, ignore_errors=True)
    return annotation


def get_annotations():
    annotations = []

    # TODO: this is only for one annotator - expand
    path_lukas = os.path.join(PATH, 'LHu')
    files_lukas = [f for f in os.listdir(path_lukas) if f.endswith('.zip')]

    for file in files_lukas:
        path_annotation = os.path.join(path_lukas, file)
        annotation = parse_annotation(path_annotation)
        annotations.append(annotation)

    all_annotations = pd.concat(annotations, axis=0, ignore_index=True)
    return all_annotations


if __name__ == "__main__":
    get_annotations()
