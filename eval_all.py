import os
from output_scorer import score_output

path_to_inputs = "./all_inputs"
path_to_outputs = "./outputs"
avg = 0.0
index = 0

size_categories = ["small", "medium", "large"]
if not os.path.isdir(path_to_outputs):
    os.mkdir(path_to_outputs)

for size in size_categories:
    category_path = path_to_inputs + "/" + size
    output_category_path = path_to_outputs + "/" + size
    category_dir = os.fsencode(category_path)

    for input_folder in os.listdir(category_dir):
        input_name = os.fsdecode(input_folder) 
        print('group', input_name)
        thisscore = score_output(category_path + "/" + input_name, output_category_path + "/" + input_name + ".out")[0]
        avg = (avg*index+thisscore)/(index+1)
        index += 1
        print(avg)
        
