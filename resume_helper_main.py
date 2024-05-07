import json
import pathlib
import shutil
import subprocess

import fitz
from flask import (Flask, redirect, render_template, request, send_file,
                   send_from_directory, session, url_for)

BASE_PATH: pathlib.Path = pathlib.Path(__file__).parent
ALLOWED_EXTENSIONS: dict = {'doc', 'docx', 'pdf'}


resume_helper_app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
def getAStrongResume(jd: str, resume_file_path: pathlib.Path, text_color: tuple=(255, 255, 255))->pathlib.Path:
    new_file_path: pathlib.Path = BASE_PATH.joinpath('files').joinpath('downloads').joinpath(f'UPDATED-{resume_file_path.stem}.pdf')
    customized_message: str = ''    
        
    
    customized_message = "I am really sorry for doing for I wasn't able to get past your AI assistant to get your attention."
    customized_message = f"{customized_message}\n. Kindly check my resume and you will find that I have indeed checked the JD and applied for this job"
    customized_message = f"{customized_message}\n. I promise that my profile will not be a waste of time for you"
    customized_message = f"{customized_message}\n. {jd}"
    
    try:
        doc = fitz.open(f'{resume_file_path}')
        doc_pages = list(doc.pages())
        x, y, width, height = doc_pages[0].bound()
        
        page = doc_pages[-1]#doc.new_page()
        page.insert_text((0, 0), customized_message, fontsize=1, color=(text_color[0]/ 255, text_color[1]/255, text_color[2]/255))       
        # page.insert_text((0, 0), customized_message, fontsize=1, color=fitz.utils.)       
        
        new_file_path.parent.mkdir(exist_ok=True, parents=True)
        doc.save(f'{new_file_path}')
        doc.close()
    except:
        return None
    
    return new_file_path


def docToPDF(docXPath: pathlib.Path, savePDFPath: pathlib.Path)->bool:    
    try:
        args = ['soffice', '--headless', '--convert-to pdf', f'{docXPath.absolute()}', '--outdir', f'{savePDFPath.parent.absolute()}']
        subprocess.run(' '.join(args), shell=True)
        return savePDFPath.exists()
    except: 
        pass        
    return savePDFPath.exists()  


@resume_helper_app.route('/', methods=['GET', 'POST'])
def index():
    messages = request.args.get('messages') or json.dumps({"hasError": False})
    messages = json.loads(messages)
    errors = {}
    if(messages.get('hasErrors')):
        errors['errorMessage'] = messages.get('errorMessage')
    
    return render_template('index_template.html', errors = errors), 200

@resume_helper_app.route('/modifiedresume', methods=['GET', 'POST'])
def hiringPersonShouldNotSlackAnymore():
    rgb_color_str = (request.form.get('background-color') or '#FF0000').lstrip('#')
    rgb = tuple(int(rgb_color_str[i:i+2], 16) for i in (0, 2, 4))
    print('RGB =', rgb)
    
    job_description: str = request.form.get('job-description')
    resume_file = request.files.get('resume-file')
    messages = {'hasErrors': False, "errorMessage": ""}
    upload_path: pathlib.Path = None
    temp_resume_filename: pathlib.Path = None
    if(not resume_file or job_description.strip() == '' ):
        messages['hasErrors'] = True
        messages['errorMessage'] = "Either no job description provided or resume file not provided"
        messages = json.dumps(messages)
        return redirect(url_for('.index', messages=messages)), 400
    
    temp_resume_filename = pathlib.Path(BASE_PATH).joinpath('files').joinpath('temp').joinpath(resume_file.filename)
    upload_file_path = BASE_PATH.joinpath('files').joinpath('uploads').joinpath(f'{temp_resume_filename.stem}.pdf')    
    
    temp_resume_filename.parent.mkdir(parents=True, exist_ok=True)
    upload_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if('pdf' not in temp_resume_filename.suffix):
        resume_file.save(temp_resume_filename)
        result = docToPDF(temp_resume_filename, upload_file_path)        
        if(not result):
            messages['hasErrors'] = True
            messages['errorMessage'] = f'Error converting "{temp_resume_filename.name}" to PDF file "{upload_file_path.name}"'
            messages = json.dumps(messages)
            return redirect(url_for('.index', messages=messages))
    else:
        resume_file.save(upload_file_path)
        
    modified_file_path = getAStrongResume(job_description, upload_file_path, text_color=rgb)
    if(modified_file_path):
        return send_file(f'{modified_file_path.resolve()}', download_name=f'{modified_file_path.name}', as_attachment=True)       
    
    messages = json.dumps(messages)
    return redirect(url_for('.index', messages=messages))

    
if __name__ == '__main__':
    resume_helper_app.run(host='0.0.0.0', port=5000, debug=True)