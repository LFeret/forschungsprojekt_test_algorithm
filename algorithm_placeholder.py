from time import sleep
import argparse
import json
import os


def main():
    args = get_arguments()
    exp_id = args[0].exp_id

    if not exp_id:
        raise Exception('The exp_id is missing!')

    sleep(10)

    json_dic = {
        'result': f'{args[1]}'
    }

    json_string = json.dumps(json_dic)
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(this_file_path, 'test_results', f'{exp_id}_log.json')
    result_file_path = os.path.join(this_file_path, 'test_results')

    if os.path.isfile(output_file_path):
        # delete file
        os.remove(output_file_path)

    with open(output_file_path, 'w') as output_file:
        output_file.write(json_string)

    with open(os.path.join(result_file_path, 'SUCCESS'), 'w') as result_file:
        result_file.write('All went well!')


def get_arguments():
    parser = argparse.ArgumentParser(
        description='TODO: Write the Description Here!'
    )

    parser.add_argument(
        '--exp_id',
        help='TODO: Its not clear yet, what exactly the exp_id is.'
    )
    parser.add_argument('args', nargs='*')

    try:
        args = parser.parse_known_args()
    except Exception as ex:
        print(str(ex))

    return args


if __name__ == '__main__':
    main()
