USAGE_MSG ="""
PreBuildULTCoveryCheck.py is a tiny python code to execute the following function

1.Check diff if there's new files added, if yes, go to 2, if no, break with pass;
2.Search the path for new added file:
    a.If there's "codec" in the path,  go to 3, else, go to 2.b.
    b.If there's "cp" or "os" in the path, go to 4, if no, break with pass;
3.Search if there's "features" in the path for the new added file, if yes, go to 4, if no, break with pass;
4.Get the class name, search the all test data folders in gfx-driver\\Source\\media\\media_embargo\\media_driver_next\\ult ,  for each test_data foler, do:
    a.Check if folders(all the subfolders in test_data) which name start with the classname, if yes, go to b, if no, report error;
    b.Check the folder,
      i.for integrationt_test, check if xxxReference.xml,
      ii.for focus_test, check if .xml file, if no, report error, if yes, if there's "Output" item, if no , report warning, if yes, pass. 

Usage: python PreBuildULTCoverageCheck.py [OPTIONS]

OPTIONS:
             --tp=[check_diff|check_diff_staged|all]            // default:all

e.g.
>python PreCheckULTCoverageCheck.py --tp=check_diff
>python PreCheckULTCorageCheck.py --tp=check_diff_staged
>python PreCheckULTCorageCheck.py --tp=all
"""
import os
import re
import sys
import logging
import argparse

def CheckOutput(xml_path, file):
    OutputExisted = False
    with open(xml_path + '\\' + file, 'r', encoding='utf-8') as f:
        try:
            lines = file.readlines()
        except:
            logging.warning(" warnnig : "+ file +" didn't open correctly, ignore the file and continue")
            lines = ''
        for line in lines:
            root_begin = re.match(r'^\<([a-zA-Z0-9\_]+)\>\s*', line)
            output_item = re.search(r'\<Output\>', line)
            root_end = re.match(r'^\<\/([a-zA-Z0-9\_]+)\>\s*', line)
            if root_begin:
                testCase_name = root_begin.group(1)
                continue
            if output_item:
                OutputExisted = True
                continue
            if root_end and root_end.group(1) == testCase_name:
                if OutputExisted:
                    OutputExisted = False
                    continue
                else:
                    return False
    return True

def look_for_new_file_in_diff(diff_file):
    new_file_path_dict = {}
    new_class_name_list = []
    res = []
    IsNewFile = False
    pattern_for_new_file = re.compile(r'new file mode.*')
    pattern_for_old_file = re.compile(r'index\s*[^0]{11}\.+[a-z0-9]*.*')
    pattern_for_new_class = re.compile(r'\+\s*class\s*([a-zA-Z0-9\_]+)\s*[^\;]*\;?')
    with open(diff_file,'r',encoding='utf-8') as file:
        try:
            lines = file.readlines()
        except:
            logging.warning(" warnnig : the diff.file didn't open correctly, ignore the file and continue")
            lines = ''
        for line in lines:
            line = line.strip()
            if pattern_for_old_file.match(line):
                IsNewFile = False
                continue
            if pattern_for_new_file.match(line):
                IsNewFile = True
                continue
            if line[:3] == "+++" and IsNewFile:
                new_class_name_list.clear()
                new_file_path = line[5:].replace("/","\\")
                continue
            if pattern_for_new_class.match(line) and IsNewFile:
                class_name = pattern_for_new_class.search(line).group(1)
                new_class_name_list.append(class_name)
                new_file_path_dict[new_file_path] = new_class_name_list[:]
    return new_file_path_dict

def check_for_integration_test(test_data_path_list, class_name_list):
    for test_data_path in test_data_path_list:
        for maindir, subdir, file_name in os.walk(test_data_path):
            for dir in subdir:
                if dir == "integration_test":
                   for roots, dirs, files, in os.walk(os.path.join(maindir, dir)):
                       for file in files:
                           for class_name in class_name_list:
                               if re.search(r'Reference.xml', file) and re.search(class_name, file):
                                   logging.warning("   OK   : Find " + class_name + " Reference.xml.")
                                   class_name_list.remove(class_name)
                                   if len(class_name_list) == 0:
                                       return True
                               else:
                                   if class_name.endswith('_Plus'):
                                       classname=class_name[:-5]
                                       logging.warning(" Search test for " + classname)
                                       if re.search(r'Reference.xml', file) and re.search(classname, file):
                                           logging.warning("   OK   : Find " + classname + " Reference.xml.")
                                           class_name_list.remove(class_name)
                                           if len(class_name_list) == 0:
                                               return True

    for class_name in class_name_list:
        logging.warning(" Error  : Can't find " + class_name + " Reference.xml in all Integration_test directories.")
    return False

def check_for_focus_test(test_data_path_list, class_name_list):
    for test_data_path in test_data_path_list:
        for maindir, subdir, file_name in os.walk(test_data_path):
            for dir in subdir:
                if dir == "focus_test":
                   for roots, dirs, files, in os.walk(os.path.join(maindir, dir)):
                       for file in files:
                           for class_name in class_name_list:
                               if re.search(r'\.xml', file) and re.search(class_name, file):
                                   XmlExisted = True
                                   OutputExisted = CheckOutput(roots, file)
                                   if XmlExisted:
                                       if OutputExisted:
                                          logging.warning("   OK   : Find " + class_name + " xml.")
                                          class_name_list.remove(class_name)
                                          if len(class_name_list) == 0:
                                              return True
                                       else:
                                          logging.warnig("Warning : Can't find Output item in " + class_name + " xml. ")
    for class_name in class_name_list:
        logging.warning(" Error  : Can't find " + class_name + " xml file in all focus_test directories.")
    return False

def check_test_data_forder(driver_path, class_name_list):
    test_data_path_list = []
    path = driver_path + r'\Source\media\media_embargo\media_driver_next\ult' + '\\'
    for maindir, subdir, file_name_list in os.walk(path):
        for dir in subdir:
            if dir == "test_data":
                test_data_path = os.path.join(maindir, dir)
                test_data_path_list.append(test_data_path)
    Integration_test = check_for_integration_test(test_data_path_list, class_name_list[:])
    Focus_test = check_for_focus_test(test_data_path_list,class_name_list[:])
    if Integration_test or Focus_test:
        return True
    else:
        return False

def search_path(file_path_dict, driver_path):
    TestDataCheck = True
    if len(file_path_dict) == 0:
        return True
    else:
        for key, values in file_path_dict.items():
            values = list(set(values))
            (FilePath,FileName) = os.path.split(key)
            if re.search(r'media_driver_next',FilePath):
                if re.search(r'ult',FilePath):
                    continue
                else:
                    if re.search(r'\\codec', FilePath) or re.search(r'\\vp', FilePath):
                        if re.search(r'features', FilePath):
                            TestDataCheck = check_test_data_forder(driver_path, values[:])
                        else:
                            continue
                    else:
                        if re.search(r'\\os', FilePath) or re.search(r'\\cp', FilePath):
                            TestDataCheck = check_test_data_forder(driver_path, values[:])
                        else:
                            continue
            else:
                continue
    return TestDataCheck

def create_git_diff(commit_sha_1, commit_sha_2, driver_path):
    output_file = commit_sha_2[:4] + ".diff"
    file_path = os.path.join(os.getcwd(), output_file)
    cd_cmd = "cd " + driver_path
    git_cmd = "&& git diff " + commit_sha_1 + " " +commit_sha_2 + " -U100 > " + file_path
    cmd = cd_cmd + git_cmd
    os.system(cmd)
    return output_file

def create_git_diff_staged(driver_path):
    output_file = "staged.diff"
    file_path = os.path.join(os.getcwd(), output_file)
    cd_cmd = "cd " + driver_path
    git_cmd = "&& git diff --staged -U100 > " + file_path
    cmd = cd_cmd + git_cmd
    os.system(cmd)
    return output_file

def check_diff_staged(gfx_driver_source_path, commit_before="HEAD~1", commit_after="HEAD"):
    current_path = os.getcwd()
    file = create_git_diff_staged(gfx_driver_source_path)
    new_added_file = look_for_new_file_in_diff(file)
    DiffCheck = search_path(new_added_file, gfx_driver_source_path)
    if DiffCheck:
        logging.warning("   OK   : Success!")
    else:
        logging.warning(" Error  : Failed!")
    return DiffCheck

def check_diff(gfx_driver_source_path, commit_before="HEAD~1", commit_after="HEAD"):
    current_path = os.getcwd()
    file = create_git_diff(commit_before, commit_after, gfx_driver_source_path)
    new_added_file = look_for_new_file_in_diff(file)
    DiffCheck = search_path(new_added_file, gfx_driver_source_path)
    if DiffCheck:
        logging.warning("   OK   : Success!")
    else:
        logging.warning(" Error  : Failed!")
    return DiffCheck

def main():
    try:
        if sys.argv[1] in ["--help", "-h"]:
            logging.warning(USAGE_MSG)
            return 0
    except:
        pass
    parser = argparse.ArgumentParser()
    parser.add_argument('--tp', dest='tp',default="all",choices=["check_diff","check_diff_staged","all"])
    parser.add_argument('--gfx-driver', dest='gfx_driver', required=True)
    args = parser.parse_args()
    try:
        if args.tp=="check_diff":
            check_result=check_diff(args.gfx_driver)
        elif args.tp=="check_diff_staged":
            check_result=check_diff_staged(args.gfx_driver)
        else:
            check_result=(check_diff(args.gfx_driver)and check_diff_staged(args.gfx_driver))
    except:
        raise Exception("The PreBuildULTCoveryCheck.py didn't run correctly!")
    if check_result==True:
        return 0
    else: return 1

if __name__ == "__main__":
    logging.warning("Start Pre Build ULT Coverage Check")
    sys.exit(main())
    logging.warning("End of Pre Build ULT Coverage Check")
