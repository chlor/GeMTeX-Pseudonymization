import glob
import os
import threading
import configparser
from surrogateGeneration import SurrogateGeneration


# threading
class PipeThread(threading.Thread):
    def __init__(self, threadName, subset, sg):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.subset = subset
        self.sg = sg

    # process files
    def run(self):
        print("starting {} with {} files".format(self.threadName, len(self.subset)))
        self.sg.collect_files(self.subset, self.threadName)
        print('Exiting {}'.format(self.threadName))


# run surrogate generation for subsets of files
def run_surrogate_generation(configuration):

    print(configuration['settings']['format'])

    sg = SurrogateGeneration(configuration)

    if configuration['settings']['format'] != 'webanno':

        files = glob.glob(
            os.path.join(configuration['settings']['path_input'], '**', '*.ann'),
            recursive=True
        )
        print('{} files to process'.format(len(files)))

        # TODO: das ist hier müsste Anschluss an Daten getauscht werden.

        threadNr = int(configuration['settings']['threads'])
        threads = []
        for i in range(0, threadNr):
            thread = PipeThread("Thread-{}".format(str(i)), files[i::threadNr], sg)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        print('{} files processed'.format(sg.nrFiles))

    elif configuration['settings']['format'] == 'webanno':
        print('do something')


def get_config():
    """
    # get configuration
    :return:
    """

    config = configparser.ConfigParser()
    config.read('param.conf')
    return config


if __name__ == '__main__':
    run_surrogate_generation(get_config())
