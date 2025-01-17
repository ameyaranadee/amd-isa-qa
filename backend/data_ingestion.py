import xml.etree.ElementTree as ET

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    instructions = []

    for instruction in root.findall(".//Instruction"):
        print("instruction: ", instruction)

    return instructions

data = parse_xml("../data/AMD_GPU_MR_ISA_XML-2024_08_22/amdgpu_isa_mi100.xml")
print('data:', data)