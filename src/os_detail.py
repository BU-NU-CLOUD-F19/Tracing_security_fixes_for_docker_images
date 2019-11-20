# Importing packages
import subprocess
import argparse

from tqdm import tqdm


class ScriptRunner:
    def __init__(self, script):
        self.__script = script

    def run(self, args):
        # returns the stdout of the script
        output = subprocess.check_output([self.__script, args]).decode('utf-8')
        # extract the last but one line printed(which is the OS name)
        return output.split('\n')[-2]


parser = argparse.ArgumentParser(description='Counts the number of images which rely on each OS')
parser.add_argument('--images', help='File containing list of images to analyse')

args = parser.parse_args()
if __name__ == '__main__':
    result = {}
    image_list = open(args.images, 'r')
    script_runner = ScriptRunner('./fetch_os_details.sh')

    for image in tqdm(image_list, desc="Images", position=2):
        os = script_runner.run(image.strip())
        if os in result:
            result[os] += 1
        else:
            result[os] = 1

    for key, value in result.items():
        print('{}: {}'.format(key, value))
