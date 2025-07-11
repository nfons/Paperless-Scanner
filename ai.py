import openai
import os
import requests
from PIL import Image
import io
import base64

def get_recommended_filename(file_path, api_key, max_tokens=50):
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
        client = openai.OpenAI(api_key=api_key)
        with open(file_path, "rb") as file:
            file_content = file.read()
        
        # Create the API request
        response = client.chat.completions.create(
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
            max_tokens=max_tokens,
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
        else:
            return None
            
    except Exception as e:
        print(f"Error getting recommended filename: {str(e)}")
        return None

def get_recommended_filename_from_pil_image(pil_image, api_key, max_tokens=50):
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
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Create the API request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
                                "url": f"data:image/jpeg;base64,{base64.b64encode(img_byte_arr).decode('utf-8')}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        # Extract the recommended filename
        recommended_filename = response.choices[0].message.content.strip()
        
        # Clean up the filename
        recommended_filename = recommended_filename.replace('"', '').replace("'", "").strip()
        recommended_filename = recommended_filename.replace(' ', '_')
        recommended_filename = ''.join(c for c in recommended_filename if c.isalnum() or c in '_-')
        
        if recommended_filename and len(recommended_filename) <= 50:
            return recommended_filename
        else:
            return None
            
    except Exception as e:
        print(f"Error getting recommended filename from PIL image: {str(e)}")
        return None

# only for debug / testing
if __name__ == "__main__":
    api_key = "your-openai-api-key-here"
    filename = get_recommended_filename("document.jpg", api_key)
    if filename:
        print(f"Recommended filename: {filename}")
    else:
        print("Failed to get recommended filename")
