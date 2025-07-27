from google import genai
import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
from flask import jsonify
import markdown

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    print(f"Creating {UPLOAD_FOLDER} directory.")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/upload', methods=['POST'])
def upload():
    if 'image_file' not in request.files:
        return 'No file part'

    file = request.files['image_file']

    if file.filename == '':
        return 'No selected file'


    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(os.path.join(os.path.dirname(__file__), 'uploads'), filename)
        
        file.save(filepath) 
        
        img = Image.open(filepath)
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        plant = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Return only the name of this plant nothing else.", img],
        )
        plant = plant.text

        is_edible_check = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Is this plant edible? Return only the word True or only the word False.", img],
        )
        is_edible_check = is_edible_check.text.strip().capitalize()

        is_edible_data = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["What parts are edible?", img],
        )
        is_edible_data = markdown.markdown(is_edible_data.text)

        is_not_edible_data = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Is this plant edible?", img],
        )
        is_not_edible_data = markdown.markdown(is_not_edible_data.text)

        if is_edible_check == "True":
            return render_template('food.html', is_edible=is_edible_data, plant=plant, edible=True)
        else:
            return render_template('food.html', is_edible=is_not_edible_data, plant=plant, edible=False)


@app.route('/disease', methods=['POST'])
def upload_image():
    if 'image_file' not in request.files:
        return 'No file part'

    file = request.files['image_file']

    if file.filename == '':
        return 'No selected file'


    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(os.path.join(os.path.dirname(__file__), 'uploads'), filename)
        
        file.save(filepath) 
        
        img = Image.open(filepath)
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Is this plant healthy? Does it have any diseases? \
            Exactly what does it need to grow stronger?", img]
        )
        response = markdown.markdown(response.text)

        return render_template('disease.html', response=response)


@app.route('/recipes', methods=['POST'])
def recipes():
    plant = request.form.get("plant")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=[
            "Can you give me meal ideas with clear instructions and ingredients based off of this food?", plant
        ]
    )
    response = markdown.markdown(response.text)
    return render_template('recipes.html', response=response)

@app.route('/garden', methods=['POST'])
def garden():
    plant = request.form.get("plant")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=[
            "Can you explain how to nurture the plant?", plant
        ]
    )
    response = markdown.markdown(response.text)
    return render_template('garden.html', response=response)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host = '0.0.0.0', port=8000)
        