from pathlib import Path

classes_file = Path("classes.txt")
yaml_file = Path("data.yaml")

# Read IP102 class names
names = []

with open(classes_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split(maxsplit=1)

        if len(parts) == 2:
            class_id = int(parts[0])
            class_name = parts[1].strip()

            names.append(class_name)

# Verify class count
if len(names) != 102:
    raise ValueError(
        f"Expected 102 classes, but found {len(names)}"
    )

# Create data.yaml
with open(yaml_file, "w", encoding="utf-8") as f:
    f.write("path: datasets/pest_detection\n\n")
    f.write("train: images/train\n")
    f.write("val: images/val\n\n")
    f.write("nc: 102\n\n")
    f.write("names:\n")

    for i, name in enumerate(names):
        f.write(f"  {i}: {name}\n")

print("================================")
print("data.yaml created successfully!")
print("Number of classes:", len(names))
print("================================")