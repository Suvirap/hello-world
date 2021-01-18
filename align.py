import os
import regex as re
import portion as P
import time
import logging


def get_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s', "%Y-%m-%d %H:%M:%S")
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

    return logging.getLogger(logger_name)


def get_del_ind_if(macros, code_content, f_path, white_list_flag):
    global del_index, overwrite_flag
    if white_list_flag:
        match_macro = r"\n\s*((#if\s*\!defined[\s\(]*)|(#ifndef\s*))((" + r"[\s\)])|(".join(macros) + r"[\s\)]))"
    else:
        match_macro = r"\n\s*((#if\s*defined[\s\(]*)|(#ifdef\s*))((" + r"[\s\)])|(".join(macros) + r"[\s\)]))"
    # \n\s* avoids #if in the comment
    # \s*\(* means there might be a ( or might not be
    # [\s\)] means the end of a macro
    s = re.compile(match_macro, re.DOTALL)
    marco_search_result = re.finditer(s, code_content)
    for search_result in marco_search_result:
        # Search given macros
        macro_start = search_result.regs[0][0]
        if macro_start in exclude_index:
            continue
        pattern_if_endif = re.compile(r'(\n\s*#if)|(#endif.*\b\)?)|(#else)|(#elif)')
        finditer_if_endif = re.finditer(pattern_if_endif, code_content, pos=macro_start)
        stack = 0
        else_detected = False
        for find_result in finditer_if_endif:
            # Search # and determine correspondence
            if find_result.group(1):
                stack += 1
            elif find_result.group(2):
                stack -= 1
                if stack == 0:
                    if else_detected:
                        del_index.append([find_result.span(0)[0], find_result.span(0)[1]+1])  # delete endif
                    else:
                        del_index.append([macro_start+1, find_result.span(0)[1]+1])  # delete all
                    break
            elif find_result.group(3):
                if stack == 1:
                    del_index.append([macro_start+1, find_result.span(0)[1]+1])  # delete from if to else
                    else_detected = True
            else:
                if stack == 1:
                    overwrite_flag = False
                    line_num = code_content[0:find_result.span(0)[0]].count("\n") + 1
                    logger1.info("Line " + str(line_num) + " #elif detected in " + f_path)
                    break


def get_del_ind_ifn(macros, code_content, f_path, white_list_flag):
    global del_index, overwrite_flag
    if white_list_flag:
        match_macro = r"\n\s*((#if\s*defined[\s\(]*)|(#ifdef\s*))((" + r"[\s\)])|(".join(macros) + r"[\s\)]))"
    else:
        match_macro = r"\n\s*((#if\s*\!defined[\s\(]*)|(#ifndef\s*))((" + r"[\s\)])|(".join(macros) + r"[\s\)]))"
    s = re.compile(match_macro, re.DOTALL)
    marco_search_result = re.finditer(s, code_content)
    for search_result in marco_search_result:
        # Search given macros
        macro_start = search_result.regs[0][0]
        if macro_start in exclude_index:
            continue
        if code_content[search_result.regs[0][1]-1] == "\n":
            del_index.append([search_result.regs[0][0], search_result.regs[0][1]-1])  # Delete if !defined
        else:
            del_index.append([search_result.regs[0][0], search_result.regs[0][1]])  # Delete if !defined

        pattern_if_endif = re.compile(r'(\n\s*#if)|(#endif.*\b\)?)|(#else)|(#elif)')
        finditer_if_endif = re.finditer(pattern_if_endif, code_content, pos=macro_start)
        # There might be overlap like #endif\n#if if match #endif.*?\n
        # However overlapped can not be set to true, otherwise \n\n#if will be matched more than once.

        stack = 0
        else_detected = False
        for find_result in finditer_if_endif:
            # Search # and determine correspondence
            if find_result.group(1):  # if
                stack += 1
            elif find_result.group(2):  # endif
                stack -= 1
                if stack == 0:
                    if else_detected:
                        del_index.append([else_start, find_result.span(0)[1]])  # Delete from else to endif
                    else:
                        del_index.append([find_result.span(0)[0], find_result.span(0)[1]+1])  # Delete endif
                    break
            elif find_result.group(3):  # else
                if stack == 1:
                    else_start = find_result.span(0)[0]
                    else_detected = True
            else:
                if stack == 1:
                    overwrite_flag = False
                    line_num = code_content[0:find_result.span(0)[0]].count("\n") + 1
                    logger1.info("Line " + str(line_num) + " #elif detected in " + f_path)
                    del del_index[-1]
                    break


def detect_comb_logic(code_content, f_path):
    global overwrite_flag, exclude_index
    match_comb = re.finditer(
        r"\n\s*((#if\s*defined)|(#ifdef)|(#if\s*\!defined)|(#ifdef))(((.)|(\\\s*?\n))*?)((\|\|)|(\&\&))", code_content)
    for match_c in match_comb:
        overwrite_flag = False
        exclude_index.append(match_c.regs[0][0])
        line_num = code_content[0:match_c.span(1)[0]].count("\n") + 1
        logger2.info("Line " + str(line_num) + " in file " + f_path + " detect " + match_c.group(1) + match_c.group(
            6) + match_c.group(10))


def detect_define(code_content, f_path):
    global overwrite_flag
    match_comb = re.finditer(
        r"\n[ \t]*(#define((\s)|(\\\n))+?(\S|(,\s+))+?((\s)|(\\\s*?\n)|(//[^\n]*))*?\n)", code_content, overlapped=True)
    # match_comb = re.finditer(
    #     r"#define.*?\n", code_content)
    for match_c in match_comb:
        match_h = re.findall(r"#define\s*_\S*H_*\s",code_content, pos=match_c.span(0)[0], endpos=match_c.span(0)[1])
        if len(match_h):
            continue
        overwrite_flag = False
        line_num = code_content[0:match_c.span(1)[0]].count("\n") + 1
        logger3.info("Line " + str(line_num) + " in file " + f_path + " detect " + match_c.group(1))


start_time = time.time()
config_file = open("config.txt", "r").read()
blacklist_macros = re.findall(re.compile("BlackList.*?\n\n", re.DOTALL), config_file)[0].split("\n")[1:-2]
whitelist_macros = re.findall(re.compile("WhiteList.*?\n\n", re.DOTALL), config_file)[0].split("\n")[1:-2]
exceptionlist_macros = re.findall(re.compile("ExceptionList.*?\n\n", re.DOTALL), config_file)[0].split("\n")[1:-2]
folder_list = re.findall(re.compile("FolderList.*?\n\n", re.DOTALL), config_file)[0].split("\n")[1:-2]
file_list = re.findall(re.compile("FileList.*?\n\n", re.DOTALL), config_file)[0].split("\n")[1:-2]
for delete_file in file_list:
    if os.path.exists(delete_file):
        os.remove(delete_file)
    else:
        print(delete_file, "does not exist.")

overwrite_flag = True
keep_ind_dict = {}
logger1 = get_logger('else', "else.log")
logger2 = get_logger('combinationLogic', "comb.log")
logger3 = get_logger('defineMacro', "def.log")

for folder in folder_list:
    g = os.walk(folder)
    for path, dir_list, file_list in g:
        for file_name in file_list:
            # if file_name not in file_name_list:
            file_path = os.path.join(path, file_name)

            # Open and read code files
            code_file = open(file_path, 'r', encoding='utf-8')
            file_content = code_file.read()
            code_file.close()
            exclude_index = []
            detect_comb_logic(file_content, file_path)
            detect_define(file_content,file_path)
            del_index = []
            get_del_ind_if(blacklist_macros, file_content, file_path, False)  # False means blacklist
            get_del_ind_ifn(blacklist_macros, file_content, file_path, False)
            get_del_ind_if(whitelist_macros, file_content, file_path, True)  # True means whitelist
            get_del_ind_ifn(whitelist_macros, file_content, file_path, True)
            keep_code = P.closed(0, len(file_content))
            for [min_ind, max_ind] in del_index:
                keep_code = keep_code - P.closed(min_ind, max_ind)
            keep_ind_dict[file_path] = keep_code

# if overwrite_flag:
if 1:
    for file_path, keep_code in keep_ind_dict.items():
        # Open and read code files
        code_file = open(file_path, 'r', encoding='utf-8')
        file_content = code_file.read()
        code_file.close()

        file_content_new = ""
        for keep_code_index in keep_code:
            file_content_new += file_content[keep_code_index.lower:keep_code_index.upper]
        # Open and write code files
        code_file = open(file_path, 'w', encoding='utf-8')
        code_file.write(file_content_new)
        code_file.close()

end_time = time.time()
print("Execution Time: ", end_time - start_time)
