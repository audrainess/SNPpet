from flask import Flask, render_template, request, jsonify
import subprocess
import tempfile

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    print("Rendering index.html")
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return str(e), 500

@app.route('/convert', methods=['POST'])
def convert():
    input_data = request.form['genomic_data']
    print(f"Converting data: {input_data}")
    # Perform conversion logic here
    format1 = input_data
    format2 = input_data.replace(':', '-').replace('-', ' ')
    format3 = input_data.replace(':', ' ').replace('-', ' ').replace('>', ' ').replace('A', 'A>G')

    return jsonify({
        'format1': format1,
        'format2': format2,
        'format3': format3
    })

@app.route('/liftover', methods=['POST'])
def liftover():
    input_data = request.form['genomic_data']
    from_version = request.form['from_version']
    to_version = request.form['to_version']
    print(f"LiftOver input: {input_data}, from {from_version} to {to_version}")

    chr, start, end = parse_input(input_data)
    print(f"Parsed input: chr={chr}, start={start}, end={end}")

    with tempfile.NamedTemporaryFile(delete=False) as input_file, tempfile.NamedTemporaryFile(delete=False) as output_file, tempfile.NamedTemporaryFile(delete=False) as unmapped_file:
        input_file.write(f"{chr} {start} {end}\n".encode())
        input_file.flush()

        chain_file = f"./chain_files/{from_version}To{to_version}.over.chain.gz"
        command = ["/Users/audraniness/Documents/genomic_converter/liftOver", input_file.name, chain_file, output_file.name, unmapped_file.name]
        print(f"Running command: {' '.join(command)}")

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            with open(output_file.name, 'r') as f:
                result = f.read().strip().split()
            converted_position = f"chr{result[0]}:{result[1]}-{result[2]}"
            print(f"Converted position: {converted_position}")
        except subprocess.CalledProcessError as e:
            converted_position = f"Error in LiftOver: {e.output.decode()}"
            print(converted_position)

    return jsonify({'liftover_result': converted_position})

def parse_input(data):
    if '-' in data:
        chr, rest = data.split(':')
        pos, ref_alt = rest.split('-')
        ref, alt = ref_alt.split('>')
        return chr, pos, pos
    else:
        return data.split()

if __name__ == '__main__':
    app.run(debug=True)
