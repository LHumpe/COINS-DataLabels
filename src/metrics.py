import argparse
import utils

parser = argparse.ArgumentParser(
    description='Calculate IRR and equality of representation')
parser.add_argument('metric', action='store', choices=['irr', 'representation'],
                    help='Please provide one of the following arguments: "irr" for inter-rater reliability or "representation" for an analysis of the representation of gender, ethnicity and flow state in the annotations')


def calculate_irr():
    # TODO: implement
    pass


def calculate_representation():
    annotations = utils.get_bboxes()
    print('Currently we have',
          annotations.shape[0], 'frames.', 3000000-annotations.shape[0], 'to go - yippie!')

    # print('\nEthnicity representation:\n')
    # print(annotations['ETHNICITY'].value_counts(normalize=True) * 100)
    # print('\nGender representation:\n')
    # print(annotations['GENDER'].value_counts(normalize=True) * 100)

    print('\nRepresentation of combinations:\n')
    for index, row in annotations.groupby(['GENDER', 'ETHNICITY'])['frame'].count().reset_index().iterrows():
        print(row['GENDER'], row['ETHNICITY'], '-',
              "{0:.2%}".format(row['frame'] / len(annotations)))


if __name__ == "__main__":
    args = vars(parser.parse_args())

    if args['metric'] == 'irr':
        calculate_irr()
    else:
        calculate_representation()
