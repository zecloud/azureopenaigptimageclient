import os
import base64
import json
import aiohttp
from typing import Optional, Dict, Any, Union
from pathlib import Path
import logging

class AzureOpenAIImageClient:
    """
    Asynchronous client for Azure OpenAI image generation and editing capabilities
    """
    
    def __init__(self, 
                 endpoint: str = "", 
                 deployment_name: str = "gpt-image-1",
                 api_key: Optional[str] = None,
                 api_version: str = "2025-04-01-preview"):
        """
        Initialize the Azure OpenAI Image client
        
        Parameters:
            endpoint (str): Azure OpenAI endpoint URL
            deployment_name (str): The deployment name for image generation
            api_key (str): API key for Azure OpenAI. If None, will try to get from AZURE_API_KEY env var
            api_version (str): API version to use
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_key = api_key or os.environ.get("AZURE_API_KEY")
        self.api_version = api_version
        
        if not self.api_key:
            raise ValueError("API key must be provided or set in AZURE_API_KEY environment variable")
            
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
    async def generate_image(self, 
                      prompt: str, 
                      size: str = "1024x1024", 
                      quality: str = "auto", 
                      n: int = 1,
                      output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Generate an image based on the provided prompt
        
        Parameters:
            prompt (str): The description for image generation
            size (str): Image size - "1024x1024" (square), "1536x1024" (landscape), 
                        "1024x1536" (portrait), or "auto" (default)
            quality (str): Image quality - "low", "medium", "high", or "auto" (default)
            n (int): Number of images to generate
            output_file (str): Optional path to save the image
            
        Returns:
            bytes or str: Image data as bytes or path to saved image
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/generations?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Failed to generate image: {response.status} - {error_text}")
                    
                    response_data = await response.json()
                    image_b64 = response_data["data"][0]["b64_json"]
                    image_data = base64.b64decode(image_b64)
                    
                    if output_file:
                        with open(output_file, "wb") as f:
                            f.write(image_data)
                        return output_file
                    else:
                        return image_data
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            raise
    
    async def edit_image(self, 
                    image_path: str, 
                    prompt: str,
                    mask_path: Optional[str] = None,
                    additional_images: Optional[list[str]] = None,
                    size: str = "auto",
                    quality: str = "auto",
                    output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Edit an existing image with a prompt and optional mask
        
        Parameters:
            image_path (str): Path to the image to edit
            prompt (str): Instruction for editing the image
            mask_path (str, optional): Path to mask image (optional)
            additional_images (list[str], optional): List of paths to additional images to use for editing
            size (str): Image size - "1024x1024" (square), "1536x1024" (landscape), 
                        "1024x1536" (portrait), or "auto" (default)
            quality (str): Image quality - "low", "medium", "high", or "auto" (default)
            output_file (str): Optional path to save the edited image
            
        Returns:
            bytes or str: Edited image data as bytes or path to saved image
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/edits?api-version={self.api_version}"
        
        # For multipart/form-data we need different headers
        headers = {
            "api-key": self.api_key,
        }
        
        form_data = aiohttp.FormData()
        
        # Add main image
        with open(image_path, "rb") as image_file:
            form_data.add_field('image', image_file, 
                            filename=os.path.basename(image_path),
                            content_type='image/png')
        
        # Add mask if provided
        if mask_path:
            with open(mask_path, "rb") as mask_file:
                form_data.add_field('mask', mask_file,
                                filename=os.path.basename(mask_path),
                                content_type='image/png')
        
        # Add additional images if provided
        if additional_images:
            for i, img_path in enumerate(additional_images):
                with open(img_path, "rb") as add_img_file:
                    form_data.add_field(f'image', add_img_file,
                                    filename=os.path.basename(img_path),
                                    content_type='image/png')
        
        # Add prompt and other parameters
        form_data.add_field('prompt', prompt)
        form_data.add_field('size', size)
        form_data.add_field('quality', quality)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=form_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to edit image: {response.status} - {error_text}")
                
                response_data = await response.json()
                image_b64 = response_data["data"][0]["b64_json"]
                image_data = base64.b64decode(image_b64)
                
                if output_file:
                    with open(output_file, "wb") as f:
                        f.write(image_data)
                    return output_file
                else:
                    return image_data