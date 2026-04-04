from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

import macro_manager
from rpc.typescript_interface_generator import TypeScriptInterfaceGenerator

HTTP_SERVER_PORT = 8181

app = Flask(__name__)
CORS(app)

@app.route('/rpc', methods=['POST'])
def rpc_handler():
	try:
		rpc_data = request.json
		if rpc_data is None:
			raise ValueError("You didn't send any data")
		
		fn = rpc_data.get('fn')
		args = rpc_data.get('args')

		if fn is None or args is None:
			raise ValueError("Invalid RPC request format")

		if fn not in dir(macro_manager.MacroManager):
			raise ValueError(f"Function '{fn}' not found in MacroManager")

		print("Executing RPC: " + fn + "(" + str(args) + ")")

		result = getattr(macro_manager.MacroManager, fn)(*args)

		return jsonify({'error': False, 'data': result})

	except Exception as ex:
		print("Error Executing RPC ")
		print(ex)
		return jsonify({'error': True, 'error_msg': str(ex)})

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/_app/<path:filename>')
def serve_static(filename):
	directory = 'static/_app'
	return send_from_directory(directory, filename)

if __name__ == '__main__':
	try:
		iface = TypeScriptInterfaceGenerator.generate_typescript_interface_to_file(
			class_obj=macro_manager.MacroManager,
			out_file_path="../frontend/src/lib/types/IMacroManager.ts"
		)
		print("IMacroManager.ts generated successfully...")
	except Exception as ex:
		print("[Error generating typescript interface. Ignore if in not in DEVELOPMENT environment]:")
		print(ex)
		print("----------------------------")
	
	macro_manager.create_environment_if_not_exists()
	
	app.run(host="127.0.0.1", debug=False, port=HTTP_SERVER_PORT)