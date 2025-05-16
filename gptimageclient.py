import os
import base64
import json
import httpx
from typing import Optional, Union, List
from pathlib import Path
import logging


class GptImageClient:
    """
    Client for Azure OpenAI image generation and editing capabilities using httpx.
    """
    
    def __init__(self, 
                 endpoint: str = "", 
                 deployment_name: str = "gpt-image-1",
                 api_key: Optional[str] = None,
                 api_version: str = "2025-04-01-preview"):
        """
        Initialize the Azure OpenAI Image client.
        
        Parameters:
            endpoint (str): Azure OpenAI endpoint URL
            deployment_name (str): The deployment name for image generation.
            api_key (str): API key for Azure OpenAI. If None, will try to get from AZURE_API_KEY env var.
            api_version (str): API version to use.
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_key = api_key or os.environ.get("GPTIMAGE1KEY")
        self.api_version = api_version
        
        if not self.api_key:
            raise ValueError("API key must be provided or set in AZURE_API_KEY environment variable")
            
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
    # Synchronous Method for Image Generation
    def generate_image_sync(self, 
                            prompt: str, 
                            size: str = "1024x1024", 
                            quality: str = "auto", 
                            n: int = 1,
                            output_file: Optional[str] = None) -> Union[bytes, str,None]:
        """
        Synchronous method to generate an image based on the provided prompt.
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/generations?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        
        try:
            with httpx.Client(timeout=None) as client:
                response = client.post(url, headers=self.headers, json=payload)
                if response.status_code != 200:
                    logging.error(f"Failed to generate image: {response.status_code} - {response.text}")
                    #raise Exception(f"Failed to generate image: {response.status_code} - {response.text}")
                
                response_data = response.json()
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
            return None
    
    # Asynchronous Method for Image Generation
    async def generate_image_async(self, 
                                   prompt: str, 
                                   size: str = "1024x1024", 
                                   quality: str = "auto", 
                                   n: int = 1,
                                   output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Asynchronous method to generate an image based on the provided prompt.
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/generations?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                if response.status_code != 200:
                    raise Exception(f"Failed to generate image: {response.status_code} - {response.text}")
                
                response_data = response.json()
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
    
    # Synchronous Method for Image Editing
    def edit_image_sync(self, 
                        image_path: str, 
                        prompt: str,
                        mask_path: Optional[str] = None,
                        additional_images: Optional[List[str]] = None,
                        size: str = "auto",
                        quality: str = "auto",
                        output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Synchronous method to edit an existing image with a prompt and optional mask.
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/edits?api-version={self.api_version}"
        
        
        
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            
            if mask_path:
                with open(mask_path, "rb") as mask_file:
                    files["mask"] = mask_file
            
            try:
                with httpx.Client(timeout=None) as client:
                    response = client.post(url, headers=self.headers, files=files)
                    if response.status_code != 200:
                        raise Exception(f"Failed to edit image: {response.status_code} - {response.text}")
                    
                    response_data = response.json()
                    image_b64 = response_data["data"][0]["b64_json"]
                    image_data = base64.b64decode(image_b64)
                    
                    if output_file:
                        with open(output_file, "wb") as f:
                            f.write(image_data)
                        return output_file
                    else:
                        return image_data
            except Exception as e:
                logging.error(f"Error editing image: {e}")
                raise
    
    #Asynchronous Method for Image Editing
    async def edit_image_async(self, 
                               image_path: str, 
                               prompt: str,
                               mask_path: Optional[str] = None,
                               additional_images: Optional[List[str]] = None,
                               size: str = "auto",
                               quality: str = "auto",
                               output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Asynchronous method to edit an existing image with a prompt and optional mask.
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/edits?api-version={self.api_version}"
        
    
        
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            
            if mask_path:
                with open(mask_path, "rb") as mask_file:
                    files["mask"] = mask_file
            
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    response = await client.post(url, headers=self.headers, files=files)
                    if response.status_code != 200:
                        raise Exception(f"Failed to edit image: {response.status_code} - {response.text}")
                    
                    response_data = response.json()
                    image_b64 = response_data["data"][0]["b64_json"]
                    image_data = base64.b64decode(image_b64)
                    
                    if output_file:
                        with open(output_file, "wb") as f:
                            f.write(image_data)
                        return output_file
                    else:
                        return image_data
            except Exception as e:
                logging.error(f"Error editing image: {e}")
                raise