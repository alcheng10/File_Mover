import os
import glob
import sys
import shutil
import logging
import json

FORMAT = '%(asctime)-15s %(levelname)s | %(module)s | %(funcName)s | %(message)s'
logging.basicConfig(
    format=FORMAT,
    level=logging.INFO
    )

logger = logging.getLogger()


def get_filelists(dir, with_root=True):
    '''
    :param dir : str
    :param with_root : boolean
        optional parameter - if set to True, returns full filepaths

    :return filelist : list
    '''
    filelist = glob.glob(dir + "/*", recursive=True)

    logger.debug(f'filelist full path: {filelist}')

    # Only get filename without root if flag set to False
    if with_root == False:
        filelist = [os.path.basename(file) for file in filelist]

    return filelist


def filter_filelist_by_type(filelist, type):
    '''
    :param filelist : list of strings
    :param type: str

    :return filtered_filelist : list
    '''
    filtered_filelist = [file for file in filelist if os.splitext(file)[0] == type]

    logging.debug(f"filtered_filelist: {filtered_filelist}")

    return filtered_filelist


def get_net_filelist(source_list, target_list):
    '''
    Gets lists of filenames.

    Return all the files in source_list but NOT in target_list.

    Notes returns full filepath, but only checks whether filename is same.

    :param source_list : list
    :param target_list : list

    :return net_filelist: list
    '''

    net_filelist = []

    target_list_rootless = [os.path.basename(target_file) for target_file in target_list]

    for source_file in source_list:
        if os.path.basename(source_file) not in target_list_rootless:
            net_filelist.append(source_file)
            logger.info(f"Found source_file {source_file} not in target_list")
    
    logger.debug(f"net filelist: {net_filelist}")

    return net_filelist

def delete_files(filelist):
    '''
    Delete list of files
    '''
    for file in filelist:
        os.remove(file)
        logger.info(f"Deleted file {file}")
    
    return


def move_files(filelist, dir):
    '''
    Moves files to specified directory
    '''
    for file in filelist:
        filename = os.path.basename(file)
        dest_path = dir + "/" + filename
        shutil.move(file, dest_path)
        logger.info(f"Moved {file} to {dir}")

    return


def get_same_size_files(source_list, target_list):
    '''
    Returns files from both lists that are same

    :param source_list : list
    :param target_list : list

    :return same_size_filelist: list    
    '''

    same_size_filelist = []

    for source_file in source_list:
        for target_file in target_list:
            if os.path.getsize(source_file) == os.path.getsize(target_file):
                same_size_filelist.append({
                    "source_file": source_file,
                    "target_file": target_file,
                    "size": os.path.getsize(source_file)
                })
                logger.info(f"Found match in size: {source_file}:{os.path.getsize(source_file)} and {target_file}:{os.path.getsize(target_file)}")

    return same_size_filelist


def main(source_dirs, target_dirs, destination_path):
    '''
    Takes list of directories and processes.

    Get all the files in source but not in targets, then move all these files out from source into destination path
        :param source_dirs : list
        :param target_dirs : list
    '''
    source_filelist = get_filelists(source_dirs)

    target_filelist = []

    for dir in target_dirs:
        target_filelist+=get_filelists(dir)

    logger.debug(f"Moving the files from {source_filelist} to {target_filelist}.")

    # Get all the files in archive but not in targets, then move all these files out archive into destination path
    net_filelist = get_net_filelist(source_list=source_filelist, target_list=target_filelist)
    same_size_filelist = get_same_size_files(source_list=source_filelist, target_list=target_filelist)

    logger.info(f"Check - net_filelist: {len(same_size_filelist)} and source_list: {len(source_filelist)}")

    move_files(net_filelist, destination_path)

    return

if __name__ == "__main__":
    main(
        json.loads(os.environ['source_dirs']),
        json.loads(os.environ['target_dirs']),
        os.environ['destination_path']
    )