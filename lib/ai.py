"""open ai api wrapper for filename recommendation"""
# pylint: disable=E1101, C0301, W0311, C0303, W0718
import base64
import io
import openai
from google import genai
from google.genai import types
from PIL import Image

## pretty much for debugging
def get_recommended_filename(file_path, apikey):
    """
    Upload a file to OpenAI API and get a recommended filename based on the document content.
    
    Args:
        file_path (str): Path to the file to analyze
        api_key (str): OpenAI API key
        max_tokens (int): Maximum tokens for the response
        
    Returns:
        str: Recommended filename (without extension) or None if failed
    """
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
        # Create the API request
        response = apirequest(apikey, file_content)
        return response           
    except Exception as e:
        print(f"Error getting recommended filename: {str(e)}")
        return None

def apirequest(api_key, file_content):
    """
    Make API request to OpenAI for filename recommendation.
    
    Args:
        api_key (str): OpenAI API key
        file_content (bytes): File content to analyze
        
    Returns:
        str: Recommended filename or None if failed
    """
    response = openai.OpenAI(api_key=api_key).chat.completions.create(
            model="gpt-4o-mini",  # idk, maybe allow for other models? let users choose?
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes documents and suggests appropriate filenames. Generate a concise, descriptive filename (without extension) based on the document content. Focus on the main subject, document type, and key identifiers. Use underscores instead of spaces and keep it under 50 characters."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this document and suggest a filename (without extension) that describes its content. Return only the filename, nothing else."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(file_content).decode('utf-8')}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,
            temperature=0.3
        )

    # Extract the recommended filename
    recommended_filename = response.choices[0].message.content.strip()

    # Clean up the filename (remove quotes, extra spaces, etc.)
    recommended_filename = recommended_filename.replace('"', '').replace("'", "").strip()

    # Replace spaces with underscores and remove any invalid characters
    recommended_filename = recommended_filename.replace(' ', '_')
    recommended_filename = ''.join(c for c in recommended_filename if c.isalnum() or c in '_-')

    # Ensure it's not empty and has reasonable length
    if recommended_filename and len(recommended_filename) <= 50:
        return recommended_filename
    return None

def get_recommended_filename_from_pil_image(pil_image, api_key):
    """
    Get a recommended filename from a PIL Image object.
    
    Args:
        pil_image (PIL.Image): PIL Image object to analyze
        api_key (str): OpenAI API key
        max_tokens (int): Maximum tokens for the response
        
    Returns:
        str: Recommended filename (without extension) or None if failed
    """
    try:
        # Convert PIL image to bytes
        img_byte_arr = PIL_to_bytes(pil_image)
        
        # Create the API request
        response = apirequest(api_key, img_byte_arr)
        return response
            
    except Exception as e:
        print(f"Error getting recommended filename from PIL image: {str(e)}")
        return ""

def PIL_to_bytes(pil_image):
    """
    Convert a PIL Image object to bytes.
    """
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def get_recommended_filename_from_pil_image_gemini(pil_image, api_key):
    """
    Get a recommended filename from a PIL Image object using Google Gemini.
    
    Args:
        pil_image (PIL.Image): PIL Image object to analyze
        api_key (str): Google Gemini API key
        
    Returns:
        str: Recommended filename (without extension) or empty string if failed
    """
    recommended_filename = ""
    try:
        # Configure Gemini
        client = genai.Client(api_key=api_key)
        model = 'gemini-2.5-pro'
        
        # Create the prompt
        prompt = "Analyze this document and suggest a filename (without extension) that describes its content. Return only the filename, nothing else. Use underscores instead of spaces and keep it under 25 characters."
        
        img_bytes = PIL_to_bytes(pil_image)
        # Generate response with the PIL image
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=[
                prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
            ],
        ):
            print(chunk.text)
            recommended_filename += chunk.text or ""
        
        return recommended_filename
            
    except Exception as e:
        print(f"Error getting recommended filename from PIL image with Gemini: {str(e)}")
        return ""

# only for debug / testing
if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY"
    pil_image = Image.open("document.jpg")
    filename = get_recommended_filename_from_pil_image_gemini(pil_image, API_KEY)
    if filename:
        print(f"Recommended filename: {filename}")
    else:
        print("Failed to get recommended filename")
