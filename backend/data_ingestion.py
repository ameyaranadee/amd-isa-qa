import os
import json
import datetime
from lxml import etree

def parse_isa_xml(file_path):
    """ 
    Parse an AMD GPU ISA XML file and extract: 
    1. Metadata from <Document> 
    2. ISA details from <ISA> and its children (<Architecture>, <Instructions>, <Encodings>, <DataFormats>, <OperandTypes>, <FunctionalGroups>).
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    tree = etree.parse(file_path)
    print('tree: ', tree)
    root = tree.getroot()

    if root.tag != "Spec":
        raise ValueError(f"Expected <Spec> as root, got <{root.tag}>")
    
    parsed_data = {
        "instruction_docs": [],
        "instruction_encoding_docs": [],
        "encoding_docs": [],
        "data_format_docs": [],
        "operand_type_docs": [],
    }

    # Parse document metadata
    document_elem = root.find("Document")
    document_metadata = {}

    if document_elem is not None:
        # Collect document metdata
        for child in document_elem:
            document_metadata[child.tag] = child.text

    # Parse ISA
    isa_elem = root.find("ISA")
    # print('isa_elem: ', isa_elem.tag)
    if isa_elem is None:
        raise ValueError("No <ISA> element found in XML file")
    
    # Parse Architecture
    arch_elem = isa_elem.find("Architecture")
    print('arch_elem: ', arch_elem)
    isa_version = arch_elem.findtext("ArchitectureName") if arch_elem is not None else "Unknown"
    print('isa_version: ', isa_version)

    # Parse Instructions
    instructions_elem = isa_elem.find("Instructions")
    if instructions_elem is not None:
        for instr_elem in instructions_elem.findall("Instruction"):
            intruction_name = instr_elem.findtext("InstructionName", "Unknown")
            # print('intruction_name: ', intruction_name)
            description = instr_elem.findtext("Description", default="")
            # print('description: ', description)
            flags_elem = instr_elem.find("InstructionFlags")
            flags_text = []
            if flags_elem is not None:
                for flag in flags_elem:
                    flags_text.append(flag.text)

            instr_encodings_elem = instr_elem.find("InstructionEncodings")
            if instr_encodings_elem is not None:
                for enc_elem in instr_encodings_elem.findall("InstructionEncoding"):
                    encoding_name = enc_elem.findtext("EncodingName", "Unknown")
                    opcode = enc_elem.findtext("Opcode", default="")
                    operands_text = []
                    operands_elem = enc_elem.find("Operands")
                    if operands_elem is not None:
                        for op_elem in operands_elem:
                            field_name = op_elem.findtext("FieldName", "")
                            data_format = op_elem.findtext("DataFormatName", "")
                            operand_type = op_elem.findtext("OperandType", "")
                            operand_size = op_elem.findtext("OperandSize", "")
                            is_input = op_elem.get("Input", "False")
                            is_output = op_elem.get("Output", "False")
                            is_implicit = op_elem.get("IsImplicit", "False")
                    
                            operands_text.append(
                            f"Field: {field_name}, DataFormat: {data_format}, "
                            f"OperandType: {operand_type}, Size: {operand_size}, "
                            f"Input: {is_input}, Output: {is_output}, Implicit: {is_implicit}"
                        )
                    
                    text_content = (
                        f"Instruction: {intruction_name}. Encoding: {encoding_name}. "
                        f"Opcode: {opcode}."
                    )
            
                    if operands_text:
                        text_content += f" Operands: {', '.join(operands_text)}."
                    metadata = {
                        "ISA_version": isa_version,
                        "instruction_name": intruction_name,
                        "encoding_name": encoding_name,
                        **document_metadata
                    }
                parsed_data["instruction_encoding_docs"].append({"text": text_content, "metadata": metadata})
            functional_group_elem  = instr_elem.find("FunctionalGroup")
            functional_group = functional_group_elem.text if functional_group_elem is not None else ""

            text_content = (
                f"Instruction: {intruction_name}. "
                f"Description: {description}. "
                f"Flags: {', '.join(flags_text)}. "
                f"Functional Group: {functional_group}."
            )
            meta_data = {
                "ISA Version": isa_version,
                "instruction_name": intruction_name,
                **document_metadata
            }

            parsed_data["instruction_docs"].append({
                "text": text_content,
                "metadata": meta_data
            })

    # Parse Encodings
    # global_encodings_elem = isa_elem.find("Encodings")
    # if global_encodings_elem is not None:
    #     for enc_elem in global_encodings_elem.findall("Encoding"):
    #         encoding_name = enc_elem.findtext("EncodingName", "Unknown")
    #         bit_count = enc_elem.findtext("BitCount", default="")
    #         identifier_mask = enc_elem.findtext("EncodingIdentifierMask", default="")

    #         encoding_identifiers = []
    #         enc_ids_elem = enc_elem.find("EncodingIdentifiers")
    #         if enc_ids_elem is not None:
    #             for enc_id in enc_ids_elem.findall("EncodingIdentifier"):
    #                 if enc_id.text:
    #                     encoding_identifiers.append(enc_id.text.strip())
            
    #         description = enc_elem.findtext("Description", default="")

    #         # Parse EncodingConditions (note: the XML uses <EncodingConditions> with <EncodingCondition> elements)
    #         conditions_text = []
    #         conds_elem = enc_elem.find("EncodingConditions")
    #         if conds_elem is not None:
    #             for condition in conds_elem.findall("EncodingCondition"):
    #                 condition_name = condition.findtext("ConditionName", default="").strip()
    #                 cond_expr = condition.find("CondtionExpression")
    #                 cond_expr_text = ""
    #                 if cond_expr is not None:
    #                     # Concatenate all inner text from the condition expression
    #                     cond_expr_text = " ".join(cond_expr.itertext()).strip()
    #                 conditions_text.append(f"{condition_name}: {cond_expr_text}")

    #         # Optionally note if MicrocodeFormat is defined
    #         microcode_format = ""
    #         microcode_elem = enc_elem.find("MicrocodeFormat")
    #         if microcode_elem is not None:
    #             bitmap_elem = microcode_elem.find("BitMap")
    #             if bitmap_elem is not None:
    #                 fields = [field.findtext("FieldName", "") for field in bitmap_elem.findall("Field") if field.findtext("FieldName")]
    #                 microcode_format = f"Fields: {', '.join(fields)}" if fields else "MicrocodeFormat defined, no fields"
    #             else:
    #                 microcode_format = "MicrocodeFormat defined, no BitMap"
    #         else:
    #             microcode_format = ""
    #         text_parts.append(f"Microcode Format: {microcode_format}")

    #         # Compose text content for the encoding document
    #         text_parts = [
    #             f"Encoding: {encoding_name}.",
    #             f"Bit Count: {bit_count}.",
    #             f"Identifier Mask: {identifier_mask}.",
    #         ]
    #         if encoding_identifiers:
    #             text_parts.append(f"Identifiers: {', '.join(encoding_identifiers)}.")
    #         text_parts.append(f"Description: {description}.")
    #         if conditions_text:
    #             text_parts.append(f"Conditions: {', '.join(conditions_text)}.")
    #         if microcode_format:
    #             text_parts.append(microcode_format + ".")
    #         text_content = " ".join(text_parts)
            
    #         metadata = {
    #             "ISA_version": isa_version,
    #             "encoding_name": encoding_name,
    #             **document_metadata
    #         }

    #         parsed_data["encoding_docs"].append({
    #             "text": text_content,
    #             "metadata": metadata
    #         })

    return parsed_data

def main(): 
    """
    Example usage: 
    1. Parse the XML file. 
    2. Print or store the structured documents, ready for embedding and insertion into a vector database. 
    """ 
    xml_file_path = "../data/AMD_GPU_MR_ISA_XML-2024_08_22/amdgpu_isa_mi100.xml" 
    parsed_docs = parse_isa_xml(xml_file_path)

    # print('parsed_docs: ', parsed_docs)

    print("Document counts by type:")
    for doc_type, docs in parsed_docs.items():
        print(f"  {doc_type}: {len(docs)}")

    # # Example: Printing the first instruction document (if any) to see format
    if parsed_docs["instruction_docs"]:
        print("\nExample Instruction Document:")
        print(parsed_docs["instruction_docs"][0]["text"])
        print(parsed_docs["instruction_docs"][0]["metadata"])

    if parsed_docs["instruction_encoding_docs"]:
        print("\nExample Instruction Encoding Document:")
        print(parsed_docs["instruction_encoding_docs"][0]["text"])
        print(parsed_docs["instruction_encoding_docs"][0]["metadata"])

    # if parsed_docs["encoding_docs"]:
    #     print("\nExample Encoding Document:")
    #     print(parsed_docs["encoding_docs"][0]["text"])
    #     print(parsed_docs["encoding_docs"][0]["metadata"])

    json_folder = os.path.join("..", "data", "jsons")
    os.makedirs(json_folder, exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = os.path.join(json_folder, f"parsed_docs_{timestamp_str}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed_docs, f, indent=4)

if __name__ == "__main__":
    main()