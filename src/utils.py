import json
import os
import pandas as pd
import shutil
from tqdm import tqdm
import xmltodict
from zipfile import ZipFile

PATH_ANNOTATIONS = 'annotations/'
PATH_BBOX = 'bboxes/'
ANNOTATORS = ['LHu', 'JMu', 'SFM']


def parse_track(track):
    frames = []

    for frame in track['box']:
        attributes = {list(a.values())[0]: list(a.values())[1]
                      for a in frame['attribute']}
        attributes['frame'] = frame['@frame']
        frames.append(attributes)

    return pd.DataFrame(frames)


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
    tracks = content['annotations']['track']
    if type(tracks) == list:
        # multiple faces/bboxes
        annotations = []
        for track in tracks:
            annotations.append(parse_track(track))
        annotation = pd.concat(annotations, axis=0, ignore_index=True)
    else:
        annotation = parse_track(tracks)

    annotation['annotator'] = annotator
    annotation['video'] = video

    shutil.rmtree(path_temp, ignore_errors=True)
    return annotation


def get_bboxes():
    bboxes = []

    files = [f for f in os.listdir(PATH_BBOX) if f.endswith('.zip')]

    for file in tqdm(files):
        path_annotation = os.path.join(PATH_BBOX, file)
        annotation = parse_annotation(path_annotation)
        bboxes.append(annotation)

    all_bboxes = pd.concat(bboxes, axis=0, ignore_index=True)
    return all_bboxes


def get_annotations():
    annotations = []

    for annotator in ANNOTATORS:
        path = os.path.join(PATH_ANNOTATIONS, annotator)

        files = [f for f in os.listdir(path) if f.endswith('.zip')]

        for file in files:
            path_annotation = os.path.join(path, file)
            annotation = parse_annotation(path_annotation)
            annotations.append(annotation)

    all_annotations = pd.concat(annotations, axis=0, ignore_index=True)
    return all_annotations


if __name__ == "__main__":
    get_bboxes()
