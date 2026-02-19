import os

file_path = r'c:\Users\Naveen\Desktop\automated-resume-analyzer\templates\matching.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific corrupted lines
corrupted_part = """        const ctx{{ loop.index0 }
    } = document.getElementById('radar-{{ loop.index0 }}').getContext('2d');"""

fixed_part = """        const ctx{{ loop.index0 }} = document.getElementById('radar-{{ loop.index0 }}').getContext('2d');"""

new_content = content.replace(corrupted_part, fixed_part)

# Also fix the data list formatting to be cleaner
corrupted_data = """                    data: [
                        {{ data.analysis.technical_score |default(0) }},
            {{ data.analysis.experience_score |default(0) }},
                        {{ data.analysis.formatting_score |default(0) }},
        {{ data.analysis.advanced_match |default(0) }},
        {{ data.analysis.soft_skills_score |default(0) }}
                    ],"""

fixed_data = """                    data: [
                        {{ data.analysis.technical_score|default(0) }},
                        {{ data.analysis.experience_score|default(0) }},
                        {{ data.analysis.formatting_score|default(0) }},
                        {{ data.analysis.advanced_match|default(0) }},
                        {{ data.analysis.soft_skills_score|default(0) }}
                    ],"""

new_content = new_content.replace(corrupted_data, fixed_data)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("File fixed successfully via Python script.")
