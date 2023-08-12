import py7zr
import zipfile
import patoolib

if __name__ == '__main__':
    file = "models.7z"

    if file.endswith(".7z"):
        with py7zr.SevenZipFile(file, mode='r') as z:
            z.extractall("output")

    if file.endswith(".rar"):
        patoolib.extract_archive(file, outdir="output")

    if file.endswith(".zip"):
        with zipfile.ZipFile(file, 'r') as z:
            z.extractall("output")
