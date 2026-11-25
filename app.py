from flask import Flask, render_template, request, send_file, jsonify
from pypdf import PdfWriter
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')

    if not files or len(files) < 2:
        return jsonify({'error': 'Se necesitan al menos 2 PDFs'}), 400

    # Validar que todos sean PDFs
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({'error': f'{file.filename} no es un PDF válido'}), 400

    try:
        merger = PdfWriter()

        # Agregar cada PDF al merger
        for file in files:
            pdf_bytes = io.BytesIO(file.read())
            merger.append(pdf_bytes)

        # Crear el PDF unido en memoria
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='PDFs_Unidos.pdf'
        )

    except Exception as e:
        return jsonify({'error': f'Error al unir PDFs: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
