import argparse
import utils

utils.parse_annotations

parser = argparse.ArgumentParser(
    description='Calculate IRR and equality of representation')
parser.add_argument('metric', action='store', choices=['irr', 'representation'], required=True,
                    help='Please provide one of the following arguments: "irr" for inter-rater reliability or "representation" for an analysis of the representation of gender, ethnicity and flow state in the annotations')


def calculate_irr():
    # TODO: implement
    pass


def calculate_representation():
    # TODO: implement
    pass


if __name__ == "__main__":
    args = parser.parse_args()

    annotations = utils.get_annotations()

    if args['metric'] == 'irr':
        calculate_irr()
    else:
        calculate_representation()
