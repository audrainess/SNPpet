import subprocess
import tempfile
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='/Users/audraniness/Documents/genomic_converter/static', template_folder='/Users/audraniness/Documents/genomic_converter/templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    input_data = request.form['input-data']
    try:
        chr, pos, ref, alt = parse_input(input_data)
    except ValueError as e:
        return jsonify({'error': str(e)})
    
    format1 = f"chr{chr}:{pos}-{ref}-{alt}"
    format2 = f"chr{chr}-{pos} {ref}>{alt}"
    format3 = f"{chr} {pos} {ref} {alt}"
    
    return jsonify({'format1': format1, 'format2': format2, 'format3': format3})

@app.route('/liftover', methods=['POST'])
def liftover():
    input_data = request.form['liftover-input']
    from_version = request.form['from-version']
    to_version = request.form['to-version']
    
    try:
        chr, start, end = parse_bed_input(input_data)
    except ValueError as e:
        return jsonify({'liftover_result': str(e)})
    
    input_position = f"chr{chr}\t{start}\t{end}"

    liftover_result = run_liftover(input_position, from_version, to_version)
    
    return jsonify({'liftover_result': liftover_result})

def parse_input(data):
    # Handle different formats for conversion
    if ':' in data and '-' in data:
        chr, rest = data.split(':')
        pos, ref, alt = rest.replace('-', ' ').split()
    elif '-' in data and ' ' in data:
        chr, pos_ref_alt = data.split('-')
        pos, ref_alt = pos_ref_alt.split()
        ref, alt = ref_alt.split('>')
    elif ' ' in data and len(data.split()) == 4:
        chr, pos, ref, alt = data.split()
    else:
        raise ValueError("Invalid input format. Expected formats: 'chr9:135800978-A-G', 'chr9-135800978 A>G', or '9 135800978 A G'")
    return chr.replace('chr', ''), pos, ref, alt

def parse_bed_input(data):
    # Ensure the input is in BED format: 'chr4 100000 100001'
    parts = data.split()
    if len(parts) != 3:
        raise ValueError("Invalid BED format. Expected format: 'chr4 100000 100001'")
    chr, start, end = parts
    if not start.isdigit() or not end.isdigit():
        raise ValueError("Invalid BED format. Positions must be integers.")
    return chr.replace('chr', ''), int(start), int(end)

def run_liftover(input_position, from_version, to_version):
    liftover_tool = '/Users/audraniness/Documents/genomic_converter/liftOver'  # Path to liftOver tool
    
    # Correct chain file names
    if from_version == "hg19" and to_version == "hg38":
        chain_file = '/Users/audraniness/Documents/genomic_converter/chain_files/hg19ToHg38.over.chain.gz'
    elif from_version == "hg38" and to_version == "hg19":
        chain_file = '/Users/audraniness/Documents/genomic_converter/chain_files/hg38ToHg19.over.chain.gz'
    else:
        return "Invalid version conversion requested"
    
    # Create a temporary file for the input position
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_input:
        temp_input.write(input_position + "\n")
        temp_input.flush()

        command = [liftover_tool, temp_input.name, chain_file, 'stdout', 'unmapped']
        print(f"Running command: {' '.join(command)}")  # Debugging line

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
            print(f"LiftOver output: {output}")  # Print the raw output for debugging
            if output:
                converted_chr, converted_start, converted_end = output.split('\t')[:3]
                return f"{converted_chr}:{converted_start}-{converted_end}"
            else:
                return "No result from LiftOver"
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode('utf-8')
            print(f"LiftOver error output: {error_output}")  # Print the error output for debugging
            return f"Error in LiftOver: {error_output}"

if __name__ == '__main__':
    app.run(debug=True)
