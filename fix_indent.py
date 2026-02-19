import os
import re

file_path = r'c:\Users\Naveen\Desktop\automated-resume-analyzer\templates\matching.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_data_block = False
for line in lines:
    # Look for the start of the data array in the radar chart
    if 'data: [' in line and 'datasets:' in lines[lines.index(line)-1]:
        in_data_block = True
        new_lines.append(line)
        continue
    
    if in_data_block:
        if ']' in line:
            in_data_block = False
            new_lines.append(line)
        else:
            # Clean up the Jinja2 lines inside the data array
            # Preserve the default(0) and the comma
            match = re.search(r'\{\{.*\}\}', line)
            if match:
                clean_line = '                        ' + match.group(0) + ',\n'
                new_lines.append(clean_line)
            else:
                new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Indentation fixed.")
