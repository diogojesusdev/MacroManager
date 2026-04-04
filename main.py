from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import os

import macro_manager
from rpc.typescript_interface_generator import TypeScriptInterfaceGenerator

HTTP_SERVER_PORT = 8181
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(BASE_DIR, "macro_manager.log")

def _configure_logging() -> None:
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
		handlers=[
			logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
			logging.StreamHandler()
		],
		force=True
	)

logger = logging.getLogger(__name__)

_configure_logging()

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

		logger.info("Executing RPC %s(%s)", fn, args)

		result = getattr(macro_manager.MacroManager, fn)(*args)

		return jsonify({'error': False, 'data': result})

	except Exception as ex:
		logger.exception("Error executing RPC")
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
			out_file_path="./frontend/src/lib/types/IMacroManager.ts"
		)
		logger.info("IMacroManager.ts generated successfully")
	except Exception as ex:
		logger.warning(
			"Error generating TypeScript interface. Ignore if not in development environment.",
			exc_info=ex
		)
	
	macro_manager.create_environment_if_not_exists()
	logger.info("Starting MacroManager server on http://127.0.0.1:%s", HTTP_SERVER_PORT)
	
	app.run(host="127.0.0.1", debug=False, port=HTTP_SERVER_PORT)