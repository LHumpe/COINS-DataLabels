import argparse
import utils

parser = argparse.ArgumentParser(
    description='Calculate IRR and equality of representation')
parser.add_argument('metric', action='store', choices=['irr', 'representation'],
                    help='Please provide one of the following arguments: "irr" for inter-rater reliability or "representation" for an analysis of the representation of gender, ethnicity and flow state in the annotations')
parser.add_argument('-v', '--video', action='store', default=None,
                    help='Provide this if you want to calculate the IRR for a single video only.')


def calculate_irr(video=None):
    annotations = utils.get_frames()
    if video is not None:
        print('Overall IRR for video', video, 'is:',
              annotations[annotations['video'] == video]['majority'].mean() / 3)

        # TODO: get more stats, like number of frames that have no, 2/3, full agreement
    else:
        print('Overall IRR is:', annotations['majority'].mean() / 3)


def calculate_representation():
    annotations = utils.get_frames()
    print('Currently we have',
          annotations.shape[0], 'frames.')

    # print('\nEthnicity representation:\n')
    # print(annotations['ETHNICITY'].value_counts(normalize=True) * 100)
    # print('\nGender representation:\n')
    # print(annotations['GENDER'].value_counts(normalize=True) * 100)

    print('\nRepresentation of combinations:\n')
    for index, row in annotations.groupby(['GENDER', 'ETHNICITY'])['frame'].count().reset_index().iterrows():
        print(row['GENDER'], row['ETHNICITY'], '-',
              "{0:.2%}".format(row['frame'] / len(annotations)))

    print('\nAbsolute frames of combinations including flow (only annotated):\n')
    for index, row in annotations.groupby(['FLOW_majority', 'GENDER', 'ETHNICITY'])['frame'].count().reset_index().iterrows():
        print('flow' if row['FLOW_majority'] > 0 else 'noflow',
              row['GENDER'], row['ETHNICITY'], '-', row['frame'])


if __name__ == "__main__":
    args = vars(parser.parse_args())

    if args['metric'] == 'irr':
        calculate_irr(args['video'])
    else:
        calculate_representation()
