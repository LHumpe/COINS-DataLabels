import json
import numpy as np
import os
import pandas as pd
import shutil
import sys
from tqdm import tqdm
import xmltodict
from zipfile import ZipFile

PATH_ANNOTATIONS = 'annotations/'
PATH_BBOX = 'bboxes/'
ANNOTATORS = ['LHu', 'JMu', 'SFr']


def parse_track(track, flow=False):
    frames = []

    for frame in track['box']:

        if not flow:
            attributes = {list(a.values())[0]: list(a.values())[1]
                          for a in frame['attribute']}
            attributes['xtl'] = frame['@xtl']
            attributes['ytl'] = frame['@ytl']
            attributes['xbr'] = frame['@xbr']
            attributes['ybr'] = frame['@ybr']
            attributes['occluded'] = frame['@occluded']
            attributes['outside'] = frame['@outside']

            # flow is joined in a later parsing step for each annotator
            del attributes['FLOW']
        else:
            att = dict((item['@name'], item) for item in frame['attribute'])
            attributes = {'FLOW': att['FLOW']['#text']}
        attributes['frame'] = frame['@frame']
        frames.append(attributes)

    return pd.DataFrame(frames)


def parse_annotation(path, flow=False):
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

    # e.g. multiple faces?
    tracks = content['annotations']['track']
    if type(tracks) == list:
        # multiple faces/bboxes
        annotations = []
        for track in tracks:
            annotations.append(parse_track(track, flow=flow))
        annotation = pd.concat(annotations, axis=0, ignore_index=True)
    else:
        annotation = parse_track(tracks, flow=flow)

    if not flow:
        annotation['annotator_boxes'] = annotator
    else:
        annotation['annotator'] = annotator
    annotation['video'] = video

    shutil.rmtree(path_temp, ignore_errors=True)
    return annotation


def get_bboxes():
    bboxes = []

    print('parsing bboxes...')

    files = [f for f in os.listdir(PATH_BBOX) if f.endswith('.zip')]

    for file in tqdm(files, desc='Files'):
        path_annotation = os.path.join(PATH_BBOX, file)
        annotation = parse_annotation(path_annotation)
        bboxes.append(annotation)

    all_bboxes = pd.concat(bboxes, axis=0, ignore_index=True)
    all_bboxes['video'] = pd.to_numeric(
        all_bboxes['video'], downcast='integer')
    all_bboxes['frame'] = pd.to_numeric(
        all_bboxes['frame'], downcast='integer')
    return all_bboxes


def get_annotations():
    annotations = []

    print('parsing annotations...')

    for annotator in tqdm(ANNOTATORS, desc='Annotators:'):
        path = os.path.join(PATH_ANNOTATIONS, annotator)

        files = [f for f in os.listdir(path) if f.endswith('.zip')]

        for file in tqdm(files, desc='Files:'):
            path_annotation = os.path.join(path, file)
            annotation = parse_annotation(path_annotation, flow=True)
            annotations.append(annotation)

    all_annotations = pd.concat(annotations, axis=0, ignore_index=True)

    all_annotations['video'] = pd.to_numeric(
        all_annotations['video'], downcast='integer')
    all_annotations['frame'] = pd.to_numeric(
        all_annotations['frame'], downcast='integer')
    all_annotations['FLOW'] = pd.to_numeric(
        all_annotations['FLOW'], downcast='integer')
    all_annotations = all_annotations.pivot_table(values='FLOW', index=[
        'video', 'frame'], columns='annotator', aggfunc="sum").reset_index()
    all_annotations.rename(
        {'SFr': 'FLOW_SFr', 'LHu': 'FLOW_LHu', 'JMu': 'FLOW_JMu'}, axis=1, inplace=True)
    return all_annotations


def calc_irr(df):
    print('processing FLOW majority...')

    df['FLOW_majority'] = np.where(
        (df['FLOW_JMu'] + df['FLOW_LHu'] + df['FLOW_SFr']) >= 2, 1, 0)

    print('processing majority...')

    df['majority'] = np.where(((df['FLOW_JMu'] + df['FLOW_LHu'] + df['FLOW_SFr']) == 1)
                              | ((df['FLOW_JMu'] + df['FLOW_LHu'] + df['FLOW_SFr']) == 2), 2, 3)

    # clean FLOW_majority and majority when not all annotators have annotated
    df.loc[df[['FLOW_JMu', 'FLOW_LHu', 'FLOW_SFr']].isna().any(axis=1),
           ['FLOW_majority', 'majority']] = None

    return df


def process_frames():
    bboxes = get_bboxes()
    annotations = get_annotations()
    frames = bboxes.merge(annotations, how='left', on=['video', 'frame'])

    # remove frames that are occluded or outside
    n_all = len(frames)
    frames['occluded'] = pd.to_numeric(
        frames['occluded'], downcast='integer')
    frames['outside'] = pd.to_numeric(
        frames['outside'], downcast='integer')
    frames = frames[(frames['occluded'] == 0) &
                    (frames['outside'] == 0)]
    print('\nremoved', n_all-len(frames),
          'frames that were outside or occluded\n')

    frames = calc_irr(frames)
    if not os.path.isdir('data'):
        os.mkdir('data')
    frames.to_csv('data/frames.csv', index=False)


def get_frames():
    try:
        df = pd.read_csv('data/frames.csv')
    except FileNotFoundError:
        print('No such file: data/frames.csv - run utils.proces_frames() first!')
        sys.exit(1)

    return df


if __name__ == "__main__":
    process_frames()
