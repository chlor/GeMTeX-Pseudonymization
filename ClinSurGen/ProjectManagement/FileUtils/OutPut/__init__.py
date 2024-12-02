import os


def create_project_folders(out_directory, out_directory_zip_export, out_directory_surrogate):

    if not os.path.exists(path=out_directory):
        os.makedirs(name=out_directory)

    if not os.path.exists(path=out_directory_zip_export):
        os.makedirs(name=out_directory_zip_export)

    #out_directory_surrogate = out_directory + os.sep + 'surrogate'
    if not os.path.exists(path=out_directory_surrogate):
        os.makedirs(name=out_directory_surrogate)
