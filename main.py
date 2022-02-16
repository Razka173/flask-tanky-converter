from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath

import pandas as pd

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = '/'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

# Root URL
@app.route('/')
def index():
     # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')

# Get the uploaded files
@app.route("/", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      input_csv_upload = request.files['input']
      ring_csv_upload = request.files['ring']
      if input_csv_upload.filename != '' and ring_csv_upload != '':
           file_input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_csv_upload.filename)
           file_ring_path = os.path.join(app.config['UPLOAD_FOLDER'], ring_csv_upload.filename)
          # set the file path
           input_csv_upload.save(file_input_path)
           ring_csv_upload.save(file_ring_path)
           parseCSV(file_input_path, file_ring_path)
          # save the file
      return redirect(url_for('index'))

def parseCSV(filePath, filePath2):
      # Use Pandas to parse the CSV file
      df = pd.read_csv(filePath)
      ring = pd.read_csv(filePath2)

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

      for i in range(minimum, maximum+1):
          if i in baseInput:
              print(i, baseInput[i])


if (__name__ == "__main__"):
     app.run(port = 5000)
