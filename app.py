from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from summarize_async import  embed_and_polish

#from inbrief.recurse import recursively_summarize
from gpt_summ.pdf import pdf_to_txt


app = Flask(__name__)
app.config['UPLOAD_FOLER'] = "./files/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('hello.html')
	
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    # renders a loading screen that shows (for now) some metadata about your file.
   if request.method == 'POST':
      f = request.files['file']
      query = request.form['query']
      unsecure_fname = f.filename
      if not unsecure_fname:
          unsecure_fname = " "
      try:
          fname = f"./files/{secure_filename(unsecure_fname)}"
          f.save(fname)
          raw_str, num_pgs = pdf_to_txt(fname)
          num_words = len(raw_str.split(b" "))
          with open("infile.txt", "wb+") as temp:
            temp.write(raw_str)
            temp.close()
          
          with open("query.txt", "w+") as query_file:
              query_file.write(query)
              query_file.close()
          with open("metadata.txt", "w+") as info:
            info.write(f"{num_pgs}_{num_words}")
            info.close()
          return render_template("upload.html")
      except ValueError: 
          return "Oops. Not the right kind of file!"

@app.route('/processing')
def summarize():
    # summarizes whatever is currently in the file test.txt. 
    # returns a dummy template html until the summary is ready
    #summary = recursively_summarize_async("test.txt") # rewrites summary.txt
    with open("query.txt", "r+") as f:
        text = f.read()
        f.close()
    if text != '':
        query = text
    else:
        query = "The impact of the action on habitats"
    #summary = embed_and_polish("test.txt", query) # rewrites summary.txt
    summary = embed_and_polish("infile.txt", query, 10)
    return render_template("summary.html", summary="")

@app.route('/loading')
def loading():
    with open("metadata.txt") as f:
        metadata = f.read().split("_")
    return render_template("loading.html", pages=metadata[0], words=metadata[1])

@app.route("/summary")
def display_summary():
    with open("summary.txt") as f:
        text = f.read()
    return render_template("summary.html", summary=text)


if __name__ == '__main__':
    app.run()
