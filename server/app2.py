from flask import Flask, request, send_from_directory, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from glob import glob
from io import BytesIO
from zipfile import ZipFile
import os, sys
sys.path.append('/app/source')
import codegen_xml_reader
import codegen_generator_ros
import codegen_generator_opcua

app = Flask(__name__)
swagger_url = '/codegen/swagger-ui.html'

# enable file access to yaml
@app.route(f"{swagger_url}/api")
@app.route(f"/{swagger_url}/api/<path:path>")
def send_api(path):
	return send_from_directory("api", path)

api_url = 'api/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(swagger_url, api_url, config={'app_name': "Swagger UI Codegenerator API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
app.logger.info("Starting the platform.")

@app.route("/codegen/")
def hello():
    return "CodeGen is working."

########################################################
################# register swagger ui ##################
########################################################
@app.route(f"/codegen/<string:bIsSimulEnv>", methods=['POST', 'PUT'])
def generate_executable_code(bIsSimulEnv):
	
	content_type = request.headers.get('Content-Type')
	if (content_type == 'application/json'):
		# parse json string input to xml object
		input = request.json
		inputXmlString = input['BlocklyWorkspace']
		xml_parser = codegen_xml_reader.XML_BlocklyProject_Parser(inputXmlString)
		xml_parser.readAssets()
		outputFileName = 'output/generated_results/'
		# check if real robot mode or simulated OPCUA mode
		# creates either ROS action clients for every found asset OR
		# creates OPCUA agent for every found asset
		if bIsSimulEnv == 'false':
			ros_gen = codegen_generator_ros.ROSGeneratorClass('_client_py', xml_parser.getList())
			ros_gen.dump_all(outputFileName)
			stream = BytesIO()
			with ZipFile(stream, 'w') as zf:
				for file in glob(os.path.join(outputFileName, '*')):
					zf.write(file, os.path.basename(file))
			stream.seek(0)
			return send_file(
				stream,
				as_attachment=True,
				attachment_filename='ros_action_client.zip'
			)
			print ("-----------------------------------------------------")
			print ("Generation of ROS action client files succesfull!")
			print ("-----------------------------------------------------")
		elif bIsSimulEnv == 'true':
			ros_gen = codegen_generator_opcua.OPCUAGeneratorClass('_client_py', xml_parser.getList())
			ros_gen.dump_all(outputFileName)
			stream = BytesIO()
			with ZipFile(stream, 'w') as zf:
				for file in glob(os.path.join(outputFileName, '*')):
					zf.write(file, os.path.basename(file))
			stream.seek(0)
			return send_file(
				stream,
				as_attachment=True,
				attachment_filename='opcua_agent.zip'
			)
			print ("-----------------------------------------------------")
			print ("Generation of OPCUA agent files succesfull!")
			print ("-----------------------------------------------------")
		else:
			return 'Codegen called with incorrect program argument. [bSimulEnv] is not a boolean!'
			print('Codegen called with incorrect program argument. [bSimulEnv] is not a boolean!')
			print('Program execution will stop now...')
	else:
		return 'Content-Type not supported!'
		
@app.after_request
def add_cors_headers(response):
	if request.referrer:
		r = request.referrer[:-1]
		response.headers.add('Access-Control-Allow-Origin', r)
	else:
		response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Credentials', 'true')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
	response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
	response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
	response.headers.add('Access-Control-Allow-Headers', 'Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
	response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
	return response

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8083)
