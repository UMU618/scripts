# UMU @ 2025-04-10
import os

dmp_files = []
for root, dirs, files in os.walk("E:\\BSOD"):
    for file in files:
        if file.lower().endswith(".dmp"):
            dmp_files.append(os.path.join(root, file))

new_files = []
for dmp_filename in dmp_files:
    base_name = os.path.splitext(dmp_filename)[0]
    txt_filename = base_name + ".txt"
    if not os.path.exists(txt_filename):
        new_files.append(dmp_filename)

total = len(dmp_files)
dmp_files.clear()
print(str(len(new_files)) + '/' + str(total))
for dmp_filename in new_files:
    base_name = os.path.splitext(dmp_filename)[0]
    txt_filename = base_name + ".txt"
    cmd = 'echo python.exe E:\BSOD\dmp_sys.py ' + txt_filename + ' && "C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x64\\kd.exe" -c "!analyze -vv;lmDsm;q" -z "' + dmp_filename + '" | findstr /V "^NatVis script unloaded from " > "' + txt_filename + '"'
    # print(cmd)
    os.system(cmd)
