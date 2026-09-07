import os
import xml.etree.ElementTree as ET
from collections import Counter

annotation_path = input("Enter the path to the Annotations folder: ").strip()

if not os.path.isdir(annotation_path):
    print("Error: Annotation folder not found.")
    exit()

class_count = Counter()
xml_count = 0

for file in os.listdir(annotation_path):

    if file.lower().endswith(".xml"):

        xml_count += 1
        file_path = os.path.join(annotation_path, file)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            for obj in root.findall("object"):
                name = obj.find("name")

                if name is not None:
                    class_count[name.text.strip()] += 1

        except Exception as e:
            print("Error:", file, e)

print("\n========== RESULT ==========")
print("Total XML files:", xml_count)

print("\nClass IDs / Labels:")

for label, count in sorted(
    class_count.items(),
    key=lambda x: int(x[0]) if x[0].isdigit() else x[0]
):
    print(f"Class {label} : {count} objects")

print("============================")