#!/usr/bin/python
import sys, os.path, glob, re

def parse_block(
    lines=None,
    output_type=None,
    filename=None,
    ):
    # rather adhoc parsing
    parsed_block={
        "check": filename[:-3],
        "output_type":output_type,
        "outcome_code":"",
        "check_item.outcome_level":"",
        "check_item.general_message": "",
        "check_item.row_specific_message": "",
        "simple_message":"",
        "descriptor":"",
        "value":"",
    }

    assembling=False
    for line in lines:
        stripped_line=line.strip()
        f=stripped_line.split("=")
        ff=stripped_line.split("==")
        if f and f[0] in ["simple_message", 
                          "descriptor",
                          "check_item.general_message",
                          "check_item.row_specific_message",
                          
                          ]:
            assembling=True
            what_assembling=f[0]
            strings_list=[]
        if f and f[0] and f[0][0]==")":
            assembling=False
            message="".join(strings_list[1:])
            message=re.sub('f"','',message)
            message=re.sub('"','',message)
            parsed_block[what_assembling]=message
        if assembling:
            strings_list.append(stripped_line)
        if ff and ff[0] in [
            "if outcome_code", 
            "elif outcome_code"
            ]:
            parsed_block["outcome_code"]=ff[1][1:-1]
        if f and f[0] =="check_item":
            if f[1] not in [
                "CheckItem(outcome_code",
                "None",
                ]:
                mObj=re.search(r'"(.*)"', f[1])
                parsed_block["outcome_code"]=mObj.groups(0)[0]
        if f and f[0] in[
            "value",
            "outcome_code",
            "check_item.outcome_level",
            ]:
            thing=re.sub('f"','',f[1])
            thing=re.sub('"','',thing)
            if thing[-1]==",":
                thing=thing[:-1]
            parsed_block[f[0]]=thing
    return parsed_block

def parse_file(
    filename_plus_path=None, 
    filename=None, 
    CHK_digits=None,
    output_types_list=None,
    output_tsv=None,
    ):

    if output_types_list=="ALL":
        output_types_list=[
            "check_item",
            "set_level_message",
            "set_level_count",
            ]
    if not output_tsv:
        print("##########################################")
        print("##########################################")
        print(f" {filename} ")
        print("##########################################")
        print("##########################################")

    for output_type in output_types_list:
        # print("=====================================")
        # print(f" {filename} :: {output_type}")
        # print("=====================================")
        printing_on=False
        i_line=0
        for line in open(filename_plus_path).readlines():
            i_line+=1
            f=line.split()
            if f and f[0]=="#<"+output_type+">":
                if printing_on is True:
                    print("Error: printing_on is already True; structured comment error?")
                    sys.exit()
                printing_on=True
                lines=[]
                if not output_tsv:
                    print(f"------------ {filename} line: {i_line} -----{output_type}--------------------")
            if printing_on:
                lines.append(line[:-1])
                if not output_tsv:
                    print(line[:-1])
            if f and f[0]=="#</"+output_type+">":
                if printing_on is False:
                    print("Error: printing_on is already False; structured comment error?")
                    sys.exit()
                printing_on=False
                parsed_block=parse_block(
                    lines=lines,
                    output_type=output_type,
                    filename=filename,
                    )
                # print(parsed_block)
                if output_tsv is True:
                    print("\t".join(list(parsed_block.values())))
        
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
checks_list=sys.argv[1]
output_types_list=sys.argv[2]
exec(sys.argv[3]) # e.g. output_tsv=True

row_headers=[
    "check",
    "type",
    "code",	
    "row outcome level",
    "row level general message",	
    "row specific message",
    "set level message",	
    "set level count descriptor",
    "set level count content"
    ]

if output_tsv:
    print("\t".join(row_headers))

if checks_list!="ALL":
    checks_list=eval(checks_list)

if output_types_list!="ALL":
    output_types_list=eval(output_types_list)

code_folder=script_directory+"/../setchks/individual_setchk_functions/"
filenames_plus_path=glob.glob(code_folder+"CHK*.py")

for filename_plus_path in filenames_plus_path:
    filename=os.path.basename(filename_plus_path)
    CHK_digits=filename.split("_")[0][3:]
    if checks_list=="ALL" or CHK_digits in checks_list:
        parse_file(
            filename_plus_path=filename_plus_path, 
            filename=filename, 
            CHK_digits=CHK_digits,
            output_types_list=output_types_list,
            output_tsv=output_tsv
            )
    if output_tsv:
        print("\t".join(["-------"]*8))
