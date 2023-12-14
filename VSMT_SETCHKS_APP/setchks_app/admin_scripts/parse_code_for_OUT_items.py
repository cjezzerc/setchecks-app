#!/usr/bin/python
import sys, os.path, glob

def parse_file(
    filename_plus_path=None, 
    filename=None, 
    CHK_digits=None,
    output_types_list=None,
    ):

    if output_types_list=="ALL":
        output_types_list=[
            "check_item",
            "set_level_message",
            "set_level_count",
            ]
    print("##########################################")
    print("##########################################")
    print(f" {filename} ")
    print("##########################################")
    print("##########################################")

    for output_type in output_types_list:
        print("=====================================")
        print(f" {filename} :: {output_type}")
        print("=====================================")
        printing_on=False
        i_line=0
        for line in open(filename_plus_path).readlines():
            i_line+=1
            f=line.split()
            # if f:
            #     print("#<"+output_type+">", f[0], printing_on)
            if f and f[0]=="#<"+output_type+">":
                printing_on=True
            if printing_on:
                print(line[:-1])
            if f and f[0]=="#</"+output_type+">":
                printing_on=False
                print(f"------------ {filename} line: {i_line} -------------------------")
        
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
checks_list=sys.argv[1]
output_types_list=sys.argv[2]

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
            )
