import os

PATH = 'E:\\BSOD'

dmp_files = []
for root, dirs, files in os.walk(PATH):
    for file in files:
        if file.lower().endswith(".dmp"):
            dmp_files.append(os.path.join(root, file))

for dmp_filename in dmp_files:
    base_name = os.path.splitext(dmp_filename)[0]
    txt_filename = base_name + ".txt"
    if not os.path.exists(txt_filename):
        cmd = 'echo ' + txt_filename + ' && "C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x64\\kd.exe" -c "!analyze -vv;lmDsm;q" -z "' + dmp_filename + '" | findstr /V "^NatVis script unloaded from " > "' + txt_filename + '"'
        # print(cmd)
        os.system(cmd)
