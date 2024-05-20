import threading
import requests
from PIL import Image
from io import BytesIO
import os
import json
import base64
from pathlib import Path
from tqdm import tqdm

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def encode_image_to_base64(image_path):
    """Encode image to Base64 string."""
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")  # You can change the format to PNG if required
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

import os
import shutil

def delete_contents(directory):
    """
    Delete all files and directories inside the given directory.
    
    :param directory: The path to the directory whose contents are to be deleted.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def send_image(model_path, face_path, version, 
               prompt = 'street', age = '20', bodyShape = 'slim', ethnic = 'asian', sex = 'female', skinColor = 'white'):
    """Sends a JSON payload with image URLs and additional parameters to the API."""
    api_url = ''
    if version == 'released': 
        api_url = 'https://tryon-advanced.tianlong.co.uk/upload/images'
    elif version == 'test': 
        api_url = 'https://tryon-advanced-test.tianlong.co.uk/upload/images'
        
    # face_name = Path(face_path).stem
    face_image_base64 = encode_image_to_base64(face_path)
    model_name = Path(model_path).stem
    model_image_base64 = encode_image_to_base64(model_path)
        
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'content-type': 'application/json',
        'cookie': 'notion_browser_id=002af42f-7cf4-4482-aadf-cb1a963d4333; intercom-id-gpfdrxfd=dae204e3-2158-4794-a9d5-806af9449033; intercom-device-id-gpfdrxfd=48b033f5-8ce4-4d8f-8f30-35af5f8dfff1; amp_af43d4=002af42f7cf44482aadfcb1a963d4333...1hs9k2j74.1hs9k2j75.d.0.d',
        'origin': 'chrome-extension://ommjpdpphbobbcnjkfdmfekajmhdiijf',
        'priority': 'u=1, i',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'none',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    data = {
        'model': f"{model_image_base64}",
        'face': f"{face_image_base64}",
        'prompt': prompt,
        'seed': 7894674637868,
        'enhanceTryOnData': {
            'age': age,
            'bodyShape': bodyShape,
            'ethnic': ethnic,
            'sex': sex,
            'skinColor': skinColor
        }
    }
    
    

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        response_data = response.json()
        if response_data.get('status') == 'success' and 'image' in response_data:
            # image_data = base64.b64decode(response_data['image'])
            # image = Image.open(BytesIO(image_data))
            # generated_image_path = f'./generated_folder/{version}/{model_name}_{version}.png'
            # image.save(generated_image_path, format='PNG')
            return response_data['image']
    print(f'Failed to retrieve an image from {version} version.')
    print('Status Code:', response.status_code)
    print('Response:', response.text)
    return None

def create_html(model_path, face_path, released_image_path, test_image_path, model_name):
    """Generate HTML content for a single comparison."""
    face_base64 = encode_image_to_base64(face_path)
    model_base64 = encode_image_to_base64(model_path)
    # released_base64 = encode_image_to_base64(released_image_path)
    # test_base64 = encode_image_to_base64(test_image_path)
    released_base64 = released_image_path
    test_base64 = test_image_path
    
    return f"""
    <div class="image-row">
        <div class="image-container">
            <h2>Face Image</h2>
            <img src="data:image/jpeg;base64,{face_base64}" alt="Face Image">
        </div>
        <div class="image-container">
            <h2>Model Image</h2>
            <img src="data:image/jpeg;base64,{model_base64}" alt="Model Image">
        </div>
        <div class="image-container">
            <h2>Generated Image (Released Version)</h2>
            <img src="data:image/jpeg;base64,{released_base64}" alt="Generated Image (Released)">
        </div>
        <div class="image-container">
            <h2>Generated Image (Test Version)</h2>
            <img src="data:image/jpeg;base64,{test_base64}" alt="Generated Image (Test)">
        </div>
    </div>
    <hr>
    """
    # html_file_path = f'./generated_folder/comparison/{model_name}_comparison.html'
    # with open(html_file_path, 'w') as file:
    #     file.write(html_content)
    # # print(f'HTML file created at {html_file_path}')


def main(model_folder, face_path, prompt, age, bodyShape, ethnic, sex, skinColor):

    ensure_directory_exists('./generated_folder/comparison')
    ensure_directory_exists('./generated_folder/released')
    ensure_directory_exists('./generated_folder/test')
    delete_contents('./generated_folder/comparison')
    delete_contents('./generated_folder/released')
    delete_contents('./generated_folder/test')
    
    model_list = list(Path(model_folder).glob('*.jpg'))
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Comparison</title>
        <style>
            .image-row {
                display: flex;
                justify-content: space-around;
                align-items: center;
                margin-top: 20px;
            }
            .image-row div {
                text-align: center;
            }
            img {
                max-width: 400px;
                margin: 10px;
                border: 2px solid #ccc;
            }
            hr {
                margin: 40px 0;
            }
        </style>
    </head>
    <body>
        <h1>Model to Face Image Comparison</h1>
    """

    for model_path in tqdm(model_list, total=len(model_list)):
        model_name = model_path.stem
        model_path = str(model_path)
        
        # Send to the released version
        released_image_path = send_image(model_path, face_path, 'released', prompt, age, bodyShape, ethnic, sex, skinColor)

        # Send to the test version
        test_image_path = send_image(model_path, face_path, 'test', prompt, age, bodyShape, ethnic, sex, skinColor)
    

        if released_image_path and test_image_path:
            face_path_ = f'{face_path}'
            model_path = f'{model_path}'
            # released_image_path = f'{str(Path(*Path(released_image_path).parts[-3:]))}'
            # test_image_path = f'{str(Path(*Path(test_image_path).parts[-3:]))}'
            # print(model_path, released_image_path, test_image_path)
            html_content += create_html(model_path, face_path_, released_image_path, test_image_path, model_name)
        else:
            print(f'{model_path}: Failed to generate comparison due to missing images.')
            
            
    html_content += """
        </body>
        </html>
        """
        
    with open('./generated_folder/comparison/model_face_comparison.html', 'w') as file:
        file.write(html_content)
    print('HTML file created at ./generated_folder/comparison/model_face_comparison.html')


if __name__ == '__main__': 
    model_folder = 'model_folder'
    # face_path = 'face_folder/000_yyqx.jpg'
    
    # prompt = 'street'
    # age = '20'
    # bodyShape = 'slim'
    # ethnic = 'asian'
    # sex = 'female'
    # skinColor = 'white'
    # model_folder = input("Model Folder: ").strip()
    face_path = input("Face Path (e.g., face_folder/000_yyqx.jpg): ").strip()
    prompt = input("Prompt: ").strip()
    age = input("Age: ").strip()
    bodyShape = input("Body Shape: ").strip()
    ethnic = input("Ethnic: ").strip()
    sex = input("Sex: ").strip()
    skinColor = input("Skin Color: ").strip()
    
                   
    main(model_folder, face_path, prompt, age, bodyShape, ethnic, sex, skinColor)


    
