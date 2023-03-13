import os
from zipfile import ZipFile


def project_files(path):
    result = []
    for root, dirs, files in os.walk(path):
        result += [os.path.join(root, f) for f in files if ".pyc" not in f]
    return result


if __name__ == "__main__":
    with ZipFile("LingqAnkiSync.ankiaddon", "w") as myzip:
        myzip.write("manifest.json")
        myzip.write("README.md")
        myzip.write("LICENSE")

        for f in project_files("addon"):
            zip_path = os.path.join(*f.split(os.path.sep)[1:])

            myzip.write(f, zip_path)