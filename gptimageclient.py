import os
import base64
import json
from wsgiref import headers
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
                               prompt: str,
                               image_path: Optional[str] = None,
                               mask_path: Optional[str] = None,
                               additional_images: Optional[List[str]] = None,
                               size: str = "1024x1024",
                               quality: str = "auto",
                               n: int = 1,
                               output_file: Optional[str] = None,
                               images: Optional[List[Union[str, Path, bytes, bytearray]]] = None) -> Union[bytes, str]:
        """
        Asynchronous method to edit an existing image with a prompt and optional mask.
        
        Parameters:
            prompt (str): The editing prompt.
            image_path (str, optional): Path to the primary image file.
            mask_path (str, optional): Path to a mask image file.
            additional_images (list, optional): List of additional image file paths.
            size (str): Output image size.
            quality (str): Output image quality.
            n (int): Number of images to generate.
            output_file (str, optional): Path to save the output image.
            images (list, optional): List of images (file paths or bytes) to edit.
                Can be used as an alternative to image_path.
        """
        if image_path is None and images is None:
            raise ValueError("Either 'image_path' or 'images' must be provided")

        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/images/edits?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        files = []
        opened_files = []  # Pour garder track des fichiers ouverts

        try:
            if images is not None:
                # Use the 'images' list parameter
                for idx, img in enumerate(images):
                    if isinstance(img, (str, Path)):
                        img_file = open(img, "rb")
                        opened_files.append(img_file)
                        files.append(("image[]", (f"image_{idx}.png", img_file, "image/png")))
                    elif isinstance(img, (bytes, bytearray)):
                        files.append(("image[]", (f"image_{idx}.png", bytes(img), "image/png")))
                    else:
                        raise TypeError("Images must be file paths (str/Path) or bytes-like objects")
            else:
                # Use the legacy image_path parameter
                image_file = open(image_path, "rb")
                opened_files.append(image_file)
                files.append(("image[]", ("image.png", image_file, "image/png")))

            # Images supplémentaires avec la syntaxe tableau
            if additional_images:
                for idx, additional_image in enumerate(additional_images):
                    add_img_file = open(additional_image, "rb")
                    opened_files.append(add_img_file)
                    files.append(("image[]", (f"additional_image_{idx}.png", add_img_file, "image/png")))
            
            # Masque optionnel
            if mask_path:
                mask_file = open(mask_path, "rb")
                opened_files.append(mask_file)
                files.append(("mask", ("mask.png", mask_file, "image/png")))
            
            headers = self.headers.copy()
            del headers["Content-Type"]
            
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(url, headers=headers, data=payload, files=files)
                if response.status_code != 200:
                    logging.error(f"Azure OpenAI API Error: {response.status_code} - {response.text}")
                    raise Exception(f"Failed to edit image: {response.status_code} - {response.text}")
                
                response_data = response.json()
                if "data" not in response_data or len(response_data["data"]) == 0:
                    raise Exception("No image data returned from Azure OpenAI API")
                    
                image_b64 = response_data["data"][0]["b64_json"]
                image_data = base64.b64decode(image_b64)
                
                if output_file:
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "wb") as f:
                        f.write(image_data)
                    logging.info(f"Edited image saved to: {output_file}")
                    return output_file
                else:
                    return image_data
                    
        except httpx.RequestError as e:
            logging.error(f"Network error while calling Azure OpenAI: {e}")
            raise Exception(f"Network error: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error from Azure OpenAI: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HTTP error: {e.response.status_code}")
        except Exception as e:
            logging.error(f"Error editing image with Azure OpenAI: {e}")
            raise
        finally:
            # Fermer tous les fichiers ouverts de manière sûre
            for file_handle in opened_files:
                try:
                    if file_handle and not file_handle.closed:
                        file_handle.close()
                except Exception as close_error:
                    logging.warning(f"Error closing file handle: {close_error}")