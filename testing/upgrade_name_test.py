import re
# taken from /lib/LegacyUpgrade.py
def get_new_name(old_name):
    new_name = old_name

    # remove occurrences of numbers in parentheses
    # i.e. auto naming convention for duplicates
    for par_num_str in str(re.findall(r"\(\d+\)", new_name)):
        new_name = new_name.replace(par_num_str, "").strip()

    new_name = new_name.replace("-", "_") # replace hyphens
    new_name = new_name.replace(" ", "_") # replace spaces
    new_name = new_name.replace(" ", "") # replace spaces

    if not new_name.startswith("MGCL_") and new_name.startswith("MGCL"):
        new_name = new_name.replace("MGCL", "MGCL_")
        
    # remove male / female distinction
    new_name = new_name.replace("_M", "")
    new_name = new_name.replace("_F", "")
    # new_name = new_name.replace("_C", "_CROPPED")

    # sub repeating underscores with single underscore
    new_name = re.sub("\_+", "_", new_name)

    return new_name

names = [
    "MGCL 1234567 (2)",
    "MGCL__1234567 (2)"
]

for name in names:
    print(f"{name} -> {get_new_name(name)}")