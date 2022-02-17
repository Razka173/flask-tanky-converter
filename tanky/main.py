from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath
import csv
from io import StringIO
from werkzeug.wrappers import Response
import pandas as pd

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Root URL


@app.route('/')
def index():
    # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')

# Get the uploaded files


@app.route("/", methods=['POST'])
def uploadFiles():
    # get the uploaded file
    input_csv_upload = request.files.get('input')
    ring_csv_upload = request.files.get('ring')

    df = pd.read_csv(input_csv_upload)
    ring = pd.read_csv(ring_csv_upload)
    ring['from'] = ring['from']*1000
    ring['to'] = ring['to']*1000

    baseInput = {}
    for index, row in df.iterrows():
          m_to_mm = int(row['m']) * 1000
          cm_to_mm = int(row['cm']) * 10
          liter = float(row['liter'])
          height = m_to_mm + cm_to_mm
          baseInput[height] = liter

    keys = baseInput.keys()
    minimum = min(keys)
    maximum = max(keys)

    ringInput = {}
    for x in range(minimum, maximum+1):
        if x not in baseInput:
            for key in baseInput:
                if key < x and x % key < 10 and x-key < 10:
                    x_base_liter = baseInput[key]
                    x_mm = x % key
                    for index, row in ring.iterrows():
                        ring_start = int(row['from'])
                        ring_end = int(row['to'])
                        ring_mm = int(row['mm'])
                        ring_liter = float(row['liter'])
                        if x > ring_start and x < ring_end and x_mm == ring_mm:
                            total_liter = x_base_liter + ring_liter
                            ringInput[x] = total_liter

    baseInput.update(ringInput)

    response = Response(generate(baseInput, minimum,
                          maximum), mimetype='text/csv')
    response.headers.set("Content-Disposition",
                           "attachment", filename="output.csv")
    return response


def generate(input_array, minimum, maximum):
    # f = open('output.csv', 'w', newline='', encoding='utf-8')
    f = StringIO()
    w = csv.writer(f)

    for i in range(minimum, maximum+1):
        if i in input_array:
            data = [i, format(input_array[i], ".2f")]
            w.writerow(data)
            yield f.getvalue()
            f.seek(0)
            f.truncate(0)


@app.route('/download/data')
def download():
    response = Response(generateTemplate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="template-data.csv")
    return response


def generateTemplate():
    url = 'https://raw.githubusercontent.com/Razka173/flask-tanky-converter/master/example-data.csv'
    df = pd.read_csv(url)
    f = StringIO()
    w = csv.writer(f)
    columns = df.columns
    w.writerow(columns)
    yield f.getvalue()
    f.seek(0)
    f.truncate(0)
    for index, row in df.iterrows():
        m = int(row[0])
        cm = int(row[1])
        liter = float(row[2])
        data = [m, cm, liter]
        w.writerow(data)
        yield f.getvalue()
        f.seek(0)
        f.truncate(0)


@app.route('/download/ring')
def downloadRing():
    response = Response(generateRing(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="template-ring.csv")
    return response

def generateRing():
    url = 'https://raw.githubusercontent.com/Razka173/flask-tanky-converter/master/example-ring.csv'
    df2 = pd.read_csv(url)
    f = StringIO()
    w = csv.writer(f)
    columns2 = df2.columns
    w.writerow(columns2)
    yield f.getvalue()
    f.seek(0)
    f.truncate(0)
    for index, row in df2.iterrows():
        r_ring = int(row[0])
        r_from = float(row[1])
        r_to = float(row[2])
        r_mm = int(row[3])
        r_liter = float(row[4])
        data = [r_ring, r_from, r_to, r_mm, r_liter]
        w.writerow(data)
        yield f.getvalue()
        f.seek(0)
        f.truncate(0)


if (__name__ == "__main__"):
    app.run(port=5000)






