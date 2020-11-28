from time import sleep
import argparse
import json
import os


def main():
    args = get_arguments()
    exp_id = args.exp_id

    if not exp_id:
        raise Exception('The exp_id is missing!')

    sleep(10)

    json_dic = {
        'result': 'success',
        'content': '''Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'''
    }

    json_string = json.dumps(json_dic)
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(this_file_path, 'results', f'{exp_id}_log.json')

    if os.path.isfile(output_file_path):
        # delete file
        os.remove(output_file_path)

    with open(output_file_path, 'rw') as output_file:
        output_file.write(json_string)


def get_arguments():
    parser = argparse.ArgumentParser(
        description='TODO: Write the Description Here!'
    )

    parser.add_argument(
        '--exp_id',
        help='TODO: Its not clear yet, what exactly the exp_id is.'
    )

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
