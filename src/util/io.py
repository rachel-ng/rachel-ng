import json



def read_file(file_name: str, lines=True) -> str:
    with open(file_name, "r") as f:
        if lines:
            contents = f.readlines()
        else:
            contents = f.read()

        f.close()

        return contents

def write_file(file_name: str, content: str, lines=True):
    with open(file_name, "w") as f:
        if lines:
            f.writelines(content)
        else:
            f.write(content)

        f.close()

def read_json(file_name: str) -> dict:
    with open(file_name, 'r') as f:
        return json.load(f)
