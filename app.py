from flask import Flask, render_template, request
from file_search import search_files_by_tag, query_metadata_from_database
from subprocess import run
from datetime import datetime
from flask import jsonify


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        google_drive_link = request.form['google_drive_link']
        # Run GDrive_PreProcessing.py with the provided Google Drive link
        run(['python', 'D:/PROJECTS_FINAL/DriveTrack/GDrive_PreProcessing.py', google_drive_link])
        # Redirect to index.html or any other page
        return render_template('index.html')
    return render_template('home.html')

@app.route('/search_files', methods=['POST', 'GET'])
def search_files():
    if request.method == 'POST':
        search_term = request.form['tag']
        date_str = request.form['date']

        # Convert date string to YYYY-MM-DD format
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                return render_template('search.html', error_message='Invalid date format. Please use YYYY-MM-DD.')

        # Call search_files_by_tag function with the tag and date
        search_results = search_files_by_tag(search_term, date=date if date_str else None)
        return render_template('index.html', search_results=search_results, search_term=search_term)
    return render_template('search.html')

@app.route('/get_file_metadata')
def get_file_metadata():
    filename = request.args.get('filename')

    # Query the database for metadata based on the filename
    # Replace this with your actual query
    metadata = query_metadata_from_database(filename)

    # Return metadata as JSON response
    return jsonify(metadata)

if __name__ == '__main__':
    app.run(debug=True)
