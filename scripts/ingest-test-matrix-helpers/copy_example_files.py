import os
import shutil

docs_to_copy = [
    "emoji.xlsx",
    "example-with-scripts.html",
    "all-number-table.pdf",
    "docx-tables.docx",
    "fake-email.msg",
]

destination_directory = "./example-docs/test-matrix/"

if not os.path.exists(destination_directory):
    os.mkdir(destination_directory)
    print("Folder %s created!" % destination_directory)
else:
    print("Folder %s already exists" % destination_directory)

for doc in docs_to_copy:
    file_to_copy = os.path.join("./example-docs/", doc)
    print("Copying %s to %s" % (file_to_copy, destination_directory))
    shutil.copy(file_to_copy, destination_directory)
