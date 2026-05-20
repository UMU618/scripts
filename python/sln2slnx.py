# AI generated from https://github.com/UMU618/gadgets/blob/main/src/umutech/sln2slnx/sln2slnx.cpp
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid

class SolutionModel:
    def __init__(self):
        self.projects = []
        self.folders = []
        self.global_sections = {}
        self.visual_studio_version = None
        self.minimum_visual_studio_version = None
        self.open_with = None

class Project:
    def __init__(self):
        self.type_id = ""
        self.name = ""
        self.path = ""
        self.id = ""
        self.sections = {}

class Folder:
    def __init__(self):
        self.name = ""
        self.id = ""

class Section:
    def __init__(self, name, scope):
        self.name = name
        self.scope = scope
        self.properties = {}

def parse_sln_file(sln_file_path):
    solution = SolutionModel()
    current_project = None
    current_section = None
    in_global = False
    
    with open(sln_file_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            # 处理格式版本行
            if line.startswith('Microsoft Visual Studio Solution File, Format Version'):
                continue
            
            # 处理 VisualStudioVersion 行
            elif line.startswith('VisualStudioVersion'):
                match = re.search(r'VisualStudioVersion = (\d+\.\d+)', line)
                if match:
                    solution.visual_studio_version = match.group(1)
            
            # 处理 MinimumVisualStudioVersion 行
            elif line.startswith('MinimumVisualStudioVersion'):
                match = re.search(r'MinimumVisualStudioVersion = (\d+\.\d+)', line)
                if match:
                    solution.minimum_visual_studio_version = match.group(1)
            
            # 处理注释行（可能是 OpenWith 信息）
            elif line.startswith('#'):
                if solution.open_with is None:
                    solution.open_with = line[1:].strip()
            
            # 处理 Project 行
            elif line.startswith('Project('):
                match = re.search(r'Project\("\{([0-9A-F-]+)\}"\) = "([^"]+)", "([^"]+)", "\{([0-9A-F-]+)\}"', line)
                if match:
                    project = Project()
                    project.type_id = match.group(1)
                    project.name = match.group(2)
                    project.path = match.group(3)
                    project.id = match.group(4)
                    solution.projects.append(project)
                    current_project = project
                    current_section = None
            
            # 处理 EndProject 行
            elif line == 'EndProject':
                current_project = None
                current_section = None
            
            # 处理 Global 行
            elif line == 'Global':
                in_global = True
            
            # 处理 EndGlobal 行
            elif line == 'EndGlobal':
                in_global = False
            
            # 处理 ProjectSection 或 GlobalSection 行
            elif 'Section(' in line:
                match = re.search(r'(Project|Global)Section\(([^)]+)\) = ([^\s]+)', line)
                if match:
                    section_name = match.group(2)
                    section_scope = match.group(3)
                    section = Section(section_name, section_scope)
                    
                    if in_global:
                        solution.global_sections[section_name] = section
                    elif current_project:
                        current_project.sections[section_name] = section
                    
                    current_section = section
            
            # 处理 EndProjectSection 或 EndGlobalSection 行
            elif 'EndSection' in line:
                current_section = None
            
            # 处理属性行
            elif current_section and '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    current_section.properties[name] = value
    
    return solution

def generate_slnx(solution, slnx_file_path):
    # 创建根元素
    root = ET.Element('Solution')
    
    # 提取平台信息
    platforms = set()
    # 提取构建类型信息
    build_types = set()
    if 'SolutionConfigurationPlatforms' in solution.global_sections:
        section = solution.global_sections['SolutionConfigurationPlatforms']
        for prop_name in section.properties:
            if '|' in prop_name:
                parts = prop_name.split('|')
                build_type = parts[0]
                platform = parts[1]
                # 转换 Win32 为 x86
                if platform == 'Win32':
                    platform = 'x86'
                platforms.add(platform)
                build_types.add(build_type)
    
    # 添加配置信息
    if platforms:
        configs_elem = ET.SubElement(root, 'Configurations')
        # 检查是否有非默认的构建类型（默认的是 Debug 和 Release）
        default_build_types = {'Debug', 'Release'}
        custom_build_types = build_types - default_build_types
        # 只有当有自定义构建类型时，才添加 BuildType 元素
        if custom_build_types:
            for build_type in sorted(build_types):
                build_type_elem = ET.SubElement(configs_elem, 'BuildType')
                build_type_elem.set('Name', build_type)
        # 添加平台
        for platform in sorted(platforms):
            platform_elem = ET.SubElement(configs_elem, 'Platform')
            platform_elem.set('Name', platform)
    
    # 添加项目
    for project in solution.projects:
        project_elem = ET.SubElement(root, 'Project')
        # 使用正斜杠作为路径分隔符
        project_path = project.path.replace('\\', '/')
        project_elem.set('Path', project_path)
        # 添加 Id 属性
        project_elem.set('Id', project.id.lower())
    
    # 美化 XML 并写入文件
    ET.indent(root, space='  ', level=0)
    slnx_content = ET.tostring(root, encoding='utf-8', method='xml', xml_declaration=False)
    # UMU: 换行符必须为 Windows 风格，哪怕在 Linux、macOS 运行
    slnx_content = slnx_content.replace(b'\n', b'\r\n')
    # UMU: 确保文件以空行结尾
    slnx_content += b'\r\n'
    with open(slnx_file_path, 'wb') as f:
        f.write(slnx_content)

def sln2slnx(sln_file_path, slnx_file_path):
    """
    将 .sln 文件转换为 .slnx 文件
    
    Args:
        sln_file_path: .sln 文件的完整路径
        slnx_file_path: 生成的 .slnx 文件的完整路径
    
    Returns:
        0 表示成功，非 0 表示失败
    """
    try:
        # 解析 .sln 文件
        solution = parse_sln_file(sln_file_path)
        
        # 生成 .slnx 文件
        generate_slnx(solution, slnx_file_path)
        
        print(f"已成功生成 slnx 文件: {slnx_file_path}")
        return 0
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    import glob
    
    if len(sys.argv) < 2:
        print('Usage: sln2slnx.py <file_or_directory>...')
        print("Note: This is an AI generated program, it's NOT perfect!")
        print('      You should use `dotnet sln migrate`.')
        sys.exit(1)
    
    target_files = set()
    
    # 处理命令行参数
    for arg in sys.argv[1:]:
        if os.path.isfile(arg) and arg.lower().endswith('.sln'):
            # 是 .sln 文件，直接添加
            target_files.add(os.path.abspath(arg))
        elif os.path.isdir(arg):
            # 是目录，查找目录下的所有 .sln 文件
            sln_files = glob.glob(os.path.join(arg, '**', '*.sln'), recursive=True)
            for sln_file in sln_files:
                target_files.add(os.path.abspath(sln_file))
    
    # 处理所有找到的 .sln 文件
    all_success = True
    for sln_file in target_files:
        # 生成对应的 .slnx 文件路径
        slnx_file = os.path.splitext(sln_file)[0] + '.slnx'
        
        print(f"正在处理: {sln_file} -> {slnx_file}")
        exit_code = sln2slnx(sln_file, slnx_file)
        if exit_code != 0:
            all_success = False
    
    sys.exit(0 if all_success else 1)
