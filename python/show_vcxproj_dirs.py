import glob
import os
import sys
import xml.etree.ElementTree as ET

OUT_DIR = '$(SolutionDir)bin\\$(PlatformTarget)\\$(Configuration)\\'
INT_DIR = '$(SolutionDir)tmp\\$(PlatformTarget)\\$(Configuration)\\$(ProjectName)\\'

RED = "\033[31m"
RESET = "\033[0m"

def show_vcxproj_dirs(filename, outdir, intdir):
    URL = 'http://schemas.microsoft.com/developer/msbuild/2003'
    NS = '{' + URL + '}'

    print(f'Processing {filename}...')
    # 解析 XML 文件
    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != NS + 'Project':
        print(f'  Invalid vcxproj file!')
        return

    plat_confs = []
    for ig in root.findall(NS + 'ItemGroup'):
        # print(ig)
        if ig.attrib.get('Label') == 'ProjectConfigurations':
            for proj_conf in ig.findall(NS + 'ProjectConfiguration'):
                plat_conf = proj_conf.attrib.get('Include')
                plat_confs.append(plat_conf)
    print('  ProjectConfigurations:', plat_confs)

    # 遍历所有的 <PropertyGroup> 元素
    user_macros = None
    plat_confs_found = []
    for group in root.iter(NS + 'PropertyGroup'):
        # 检查当前 <PropertyGroup> 是否包含平台和配置条件
        label = group.attrib.get('Label')
        if label:
            if label == 'UserMacros':
                user_macros = group
            continue

        if (user_macros is None):
            continue

        # UserMacros 之后，无 Label 属性
        conditions = group.attrib.get('Condition', '').strip()
        if conditions:
            plat_confs_found.append(group)

    if (user_macros is None):
        print("  Exception: UserMacros not found!")
        return
    
    # print(plat_confs_found)
    existed = set()
    for pc in plat_confs_found:
        condition = pc.attrib.get('Condition')
        _, value = condition.split('==')
        value = value.strip("'")
        existed.add(value)
        #print("  " + value)

        # 查找或添加 OutDir 属性
        outdir_elem = pc.find(NS + 'OutDir')
        if outdir_elem is None:
            print(f"{RED}  {value} OutDir is default.{RESET}")
        elif outdir_elem.text != outdir:
            print(f"  {value} OutDir: " + outdir_elem.text)
        #else:
        #    print(f"  {value} OutDir is expected.")

        # 查找或添加 IntDir 属性
        intdir_elem = pc.find(NS + 'IntDir')
        if intdir_elem is None:
            print(f"{RED}  {value} IntDir is default.{RESET}")
        elif intdir_elem.text != intdir:
            print(f"  {value} IntDir: " + intdir_elem.text)
        #else:
        #    print(f"  {value} IntDir is expected.")

    left = set(plat_confs) - existed
    if (len(left)):
        print(f"{RED}  Not all configurations are set: {left}{RESET}")

def add_vcxproj_file(vcxproj_files, filename):
    # 检查参数是否以 .vcxproj 结尾
    if filename.endswith('.vcxproj'):
        vcxproj_files.append(filename)

def main():
    if len(sys.argv) < 2:
        print("Please input at least a .vcxproj file!")
        sys.exit(1)

    vcxproj_files = []
    for arg in sys.argv[1:]:
        if not os.path.exists(arg):
            print(f"Skip none path: {arg}")
            continue

        if os.path.isfile(arg):
            add_vcxproj_file(vcxproj_files, arg)
        elif os.path.isdir(arg):
            vcxproj_files.extend(glob.glob(os.path.join(arg, '**', '*.vcxproj'), recursive=True))
        else:
            print(f"Skip path: {arg}")

    vcxproj_files.sort()
    for filename in vcxproj_files:
        show_vcxproj_dirs(filename, OUT_DIR, INT_DIR)

if __name__ == '__main__':  
    main()
