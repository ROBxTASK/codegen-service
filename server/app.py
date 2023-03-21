
from glob import glob
from io import BytesIO
from zipfile import ZipFile
import os, sys
sys.path.append('D:\\codegen dynamic\\robxtask_dynamic\\server\\source')
import codegen_xml_reader
import codegen_generator_ros
import codegen_generator_opcua

# ['assetName', 'blockName', 'blockSlotName', 'blockSlotValue', 'indent']

def generate_executable_code(bIsSimulEnv):
	with open('D:\\codegen dynamic\\robxtask_dynamic\\server\\test.xml', 'r') as file:
		input = file.read()
	xml_parser = codegen_xml_reader.XML_BlocklyProject_Parser(input)
	xml_parser.readAssets()
	outputFileName = 'output/generated_results/'

	# ros_gen = codegen_generator_ros.ROSGeneratorClass('_client_py', xml_parser.getList())
	# ros_gen.dump_all(outputFileName)

	ros_gen = codegen_generator_opcua.OPCUAGeneratorClass('_client_py', xml_parser.getList())
	ros_gen.dump_all(outputFileName)
	# print("123",ros_gen)
	# iterator = iter(ros_gen)

	# print(iterator)

		
	# check if real robot mode or simulated OPCUA mode
	# creates either ROS action clients for every found asset OR
	# creates OPCUA agent for every found asset
	
	# if bIsSimulEnv == 'false':
	# 	ros_gen = codegen_generator_ros.ROSGeneratorClass('_client_py', xml_parser.getList())
	# 	ros_gen.dump_all(outputFileName)
	# 	stream = BytesIO()
	# 	with ZipFile(stream, 'w') as zf:
	# 		for file in glob(os.path.join(outputFileName, '*')):
	# 			zf.write(file, os.path.basename(file))
	# 	stream.seek(0)
	# 	return 'true'
	# 	print ("-----------------------------------------------------")
	# 	print ("Generation of ROS action client files succesfull!")
	# 	print ("-----------------------------------------------------")

	# 	print ("-----------------------------------------------------")
	# 	print ("Generation of OPCUA agent files succesfull!")
	# 	print ("-----------------------------------------------------")
	# else:
	# 	return 'Codegen called with incorrect program argument. [bSimulEnv] is not a boolean!'
	# 	print('Codegen called with incorrect program argument. [bSimulEnv] is not a boolean!')
	# 	print('Program execution will stop now...')


if __name__ == "__main__":
    generate_executable_code('false')
