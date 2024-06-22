from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    input_data = request.form['input-data']
    chr, pos, ref, alt = parse_input(input_data)
    
    format1 = f"{chr}:{pos}-{ref}-{alt}"
    format2 = f"{chr}-{pos} {ref}>{alt}"
    format3 = f"{chr} {pos} {ref} {alt}"
    format_bed = f"{chr} {int(pos) - 1} {pos}"

    return jsonify(format1=format1, format2=format2, format3=format3, format_bed=format_bed)

def parse_input(data):
    parts = data.replace(':', ' ').replace('-', ' ').replace('>', ' ').split()
    if len(parts) == 4:
        return parts
    elif len(parts) == 3:
        chr, pos, change = parts
        ref, alt = change.split('>')
        return chr, pos, ref, alt
    else:
        raise ValueError("Invalid input format")

@app.route('/liftover', methods=['POST'])
def liftover():
    input_data = request.form['liftover-input']
    from_version = request.form['from-version']
    to_version = request.form['to-version']
    chr, start, end = input_data.split()
    
    chain_file = f"./chain_files/{from_version}To{to_version}.over.chain.gz"
    
    result = subprocess.run(['liftOver', f"{chr}:{start}-{end}", chain_file, 'stdout', 'unmapped'],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return jsonify(liftover_result=f"Error in LiftOver: {result.stderr}")
    
    converted_position = result.stdout.strip().split()[1]
    return jsonify(liftover_result=converted_position)

if __name__ == '__main__':
    app.run(debug=True)
