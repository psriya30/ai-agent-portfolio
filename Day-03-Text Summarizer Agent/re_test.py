# import re
#
# text="Contact: 987654321"
# m=re.search(r"\d{10}",text)
# print(m)
# if m:
#     print(m.group())

import re
#phone number Extraction
# text = "Contact: 9876543210"
# m = re.search(r"\d{10}", text)
# print(m)
#
# if m:
#     print(m.group())  # 9876543210
#Skills extraction
text="skills:python,Java\n skills:SQL"
matches=re.findall(r"skills:\s*(.+)",text)
print(matches)