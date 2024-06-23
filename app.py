from flask import Flask, request, jsonify, render_template
import re
from pyliftover import LiftOver
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
app.debug = os.environ.get('DEBUG', 'False').lower() == 'true'

# Initialize LiftOver objects
lo_38_to_37 = LiftOver('hg38', 'hg19')
lo_37_to_38 = LiftOver('hg19', 'hg38')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    input_data = request.form.get('input_data', '')
    if not input_data:
        return jsonify({'error': 'No input data provided'}), 400
    
    try:
        chr, start, end, ref, alt = parse_input(input_data)
        
        franklin = f"chr{chr}:{start}-{end}-{ref}-{alt}" if ref and alt else f"chr{chr}:{start}-{end}"
        ucsc = f"chr{chr}:{start}-{end}"
        clinvar = f"chr{chr}:{start}-{end}"
        gnomad = f"{chr}-{start}-{end}-{ref}-{alt}" if ref and alt else f"{chr}-{start}-{end}"
        other = f"{chr} {start} {end}"
        
        return jsonify({
            'franklin': franklin,
            'ucsc': ucsc,
            'clinvar': clinvar,
            'gnomad': gnomad,
            'other': other
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/liftover', methods=['POST'])
def liftover():
    input_data = request.form.get('input_data', '')
    from_version = request.form.get('from_version', '')
    to_version = request.form.get('to_version', '')

    if not input_data or not from_version or not to_version:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        chr, start, end = parse_liftover_input(input_data)
        result = perform_liftover(chr, int(start), int(end), from_version, to_version)
        return jsonify({'liftover_result': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def parse_input(input_data):
    input_data = input_data.strip()
    
    pattern = r'(?:chr)?(\d+|X|Y|MT?)[:|\s|-]?\s*(\d+)\s*[-|:]?\s*(\d+)?\s*(?:([ACGT])[\s>-]([ACGT]))?'
    match = re.match(pattern, input_data, re.IGNORECASE)
    
    if not match:
        raise ValueError("Unable to parse input. Please check the format.")
    
    chr, start, end, ref, alt = match.groups()
    
    end = end or start
    ref = ref.upper() if ref else None
    alt = alt.upper() if alt else None
    
    return chr, start, end, ref, alt

def parse_liftover_input(input_data):
    pattern = r'(?:chr)?(\d+|X|Y|MT?)[:|\s|-]?\s*(\d+)\s*[-|:]?\s*(\d+)?'
    match = re.match(pattern, input_data, re.IGNORECASE)
    
    if not match:
        raise ValueError("Unable to parse input. Please check the format.")
    
    chr, start, end = match.groups()
    end = end or start  # If end is not provided, use start
    
    return f"chr{chr}", start, end

def perform_liftover(chr, start, end, from_version, to_version):
    if from_version == 'GRCh38/hg38' and to_version == 'GRCh37/hg19':
        lo = lo_38_to_37
    elif from_version == 'GRCh37/hg19' and to_version == 'GRCh38/hg38':
        lo = lo_37_to_38
    else:
        raise ValueError("Unsupported genome versions")

    result = lo.convert_coordinate(chr, start)
    if result:
        new_chr, new_start, strand, _ = result[0]
        new_end = new_start + (end - start)
        return f"{new_chr}:{new_start}-{new_end}"
    else:
        return "Conversion failed. Coordinate not found in target assembly."

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
