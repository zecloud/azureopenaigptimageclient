import os
import base64
import json
import httpx
from typing import Optional, Union, List
from pathlib import Path
import logging
from enum import Enum


class GptImageClient:
    """
    Client for Azure OpenAI image generation and editing capabilities using httpx.
    """
    
    class ImageModel(Enum):
        """Enum for supported image generation models."""
        GPT_IMAGE = "gpt-image"
        FLUX = "flux"

    def __init__(self, 
                 endpoint: str = "", 
                 deployment_name: str = "gpt-image-1",
                 model: ImageModel = ImageModel.GPT_IMAGE,
                 api_key: Optional[str] = None,
                 api_version: str = "2025-04-01-preview",
                 output_format: Optional[str] = None):
        """
        Initialize the Azure OpenAI Image client.
        
        Parameters:
            endpoint (str): Azure OpenAI endpoint URL
            deployment_name (str): The deployment name for image generation.
            model (ImageModel): The image generation model to use (GPT_IMAGE or FLUX).
            api_key (str): API key for Azure OpenAI. If None, will try to get from AZURE_API_KEY env var.
            api_version (str): API version to use.
            output_format (str): Output format for generated images.
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.endpointend = self.deployment_name
        self.model = model
        self.api_version = api_version
        if model == self.ImageModel.FLUX  and deployment_name == "FLUX.2-pro" :
            self.midurl="providers/blackforestlabs/v1/"
            self.api_version = "preview"
            self.endpointend = "flux-2-pro"
        else:
            self.midurl="openai/deployments/"
        self.api_key = api_key or os.environ.get("GPTIMAGE1KEY")
        self.output_format = output_format
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
        if self.model == self.ImageModel.FLUX and self.deployment_name == "FLUX.2-pro" :
            api_verb = ""
        else:
            api_verb = "/images/generations"
        url = f"{self.endpoint}{self.midurl}{self.endpointend}{api_verb}?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        if self.model == self.ImageModel.FLUX:
            payload["output_format"] = self.output_format
            payload.pop("quality", None)  # Remove quality if output_format is specified
            payload.pop("size", None)  # Remove size if output_format is specified
            payload["width"] = int(size.split('x')[0]) if 'x' in size else size
            payload["height"] = int(size.split('x')[1]) if 'x' in size else size

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
        if self.model == self.ImageModel.FLUX and self.deployment_name == "FLUX.2-pro" :
            api_verb = ""
        else:
            api_verb = "/images/generations"
        url = f"{self.endpoint}{self.midurl}{self.endpointend}{api_verb}?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        if self.model == self.ImageModel.FLUX:
            payload["output_format"] = self.output_format
            payload.pop("quality", None)  # Remove quality if output_format is specified
            if self.deployment_name == "FLUX.2-pro":
                payload["model"] = "flux.2-pro"
                payload["width"] = int(size.split('x')[0])
                payload["height"] = int(size.split('x')[1]) 
            #payload.pop("size", None)  # Remove size if output_format is specified
            #payload["width"] = int(size.split('x')[0]) if 'x' in size else size
            #payload["height"] = int(size.split('x')[1]) if 'x' in size else size

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
        api_verb = "/images/edits"
        url = f"{self.endpoint}{self.midurl}{self.endpointend}{api_verb}?api-version={self.api_version}"
        
        
        
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
                               size: str = "1024x1024",
                               quality: str = "auto",
                               n: int = 1,
                               output_file: Optional[str] = None) -> Union[bytes, str]:
        """
        Asynchronous method to edit an existing image with a prompt and optional mask.
        """
        api_verb = "/images/edits"
        url = f"{self.endpoint}{self.midurl}{self.endpointend}{api_verb}?api-version={self.api_version}"
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        if self.model == self.ImageModel.FLUX:
            payload["output_format"] = self.output_format
            payload.pop("quality", None)
            #payload.pop("size", None)  # Remove size if output_format is specified
            #width = int(size.split('x')[0])
            #height = int(size.split('x')[1])
            # if width > height:
            #     payload["aspect_ratio"] = "16:9"
            # else:
            #     payload["aspect_ratio"] = "9:16"
            payload["model"] = "flux.1-kontext-pro"

        files = []
        opened_files = []  # Pour garder track des fichiers ouverts

        try:
            # Image principale
            image_file = open(image_path, "rb")
            #if self.model == self.ImageModel.GPT_IMAGE:
            opened_files.append(image_file)
            files.append(("image[]", ("image.png", image_file, "image/png")))
            #elif self.model == self.ImageModel.FLUX:
            #    inputimgbase64 = base64.b64encode(image_file.read())
            #    payload["input_image"] = inputimgbase64.decode('utf-8')
            # Images supplémentaires avec la syntaxe tableau
            if additional_images:
                for idx, additional_image in enumerate(additional_images):
                    add_img_file = open(additional_image, "rb")
                    #if self.model == self.ImageModel.GPT_IMAGE:
                    opened_files.append(add_img_file)
                    files.append(("image[]", (f"additional_image_{idx}.png", add_img_file, "image/png")))
                    #elif self.model == self.ImageModel.FLUX:
                    #    add_img_base64 = base64.b64encode(add_img_file.read())
                    #    payload[f"input_image_{idx}"] = add_img_base64.decode('utf-8')

            # Masque optionnel
            if mask_path and self.model == self.ImageModel.GPT_IMAGE:
                mask_file = open(mask_path, "rb")
                opened_files.append(mask_file)
                files.append(("mask", ("mask.png", mask_file, "image/png")))
            
            headers = self.headers.copy()
            #if self.model == self.ImageModel.GPT_IMAGE:
            del headers["Content-Type"]
            
            async with httpx.AsyncClient(timeout=None) as client:
                #if self.model == self.ImageModel.GPT_IMAGE:
                response = await client.post(url, headers=headers, data=payload, files=files)
                #elif self.model == self.ImageModel.FLUX:
                #    response = await client.post(url, headers=headers, json=payload)
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

    async def flux2edit_image_async(self,
                                    prompt: str,
                                    images: List[Union[str, Path, bytes, bytearray]],
                                    size: str = "1024x1024", 
                                    output_file: Optional[str] = None) -> Union[bytes, str, dict]:
        """Edit images with FLUX.2 by sending up to 8 base64-encoded inputs."""
        model_name: str = "FLUX.2-pro"
        if self.model != self.ImageModel.FLUX:
            raise ValueError("flux2edit_image_async requires ImageModel.FLUX")
        if not images:
            raise ValueError("At least one image is required")
        if len(images) > 8:
            raise ValueError("A maximum of 8 images is supported")

        payload = {
            "model": model_name,
            "prompt": prompt,
            "output_format": self.output_format,
            "width": int(size.split('x')[0],
            "height" = int(size.split('x')[1]
        }

        encoded_images: List[str] = []
        for img in images:
            if isinstance(img, (str, Path)):
                with open(img, "rb") as f:
                    raw = f.read()
            elif isinstance(img, (bytes, bytearray)):
                raw = bytes(img)
            else:
                raise TypeError("Images must be paths or bytes-like objects")
            encoded_images.append(base64.b64encode(raw).decode("utf-8"))

        for idx, encoded in enumerate(encoded_images):
            key = "input_image" if idx == 0 else f"input_image_{idx + 1}"
            payload[key] = encoded
        api_verb = ""

        url = f"{self.endpoint}{self.midurl}{self.endpointend}{api_verb}?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                logging.error(f"FLUX.2 edit failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to edit image: {response.status_code} - {response.text}")

            response_data = response.json()

            if "data" in response_data and response_data["data"]:
                first_item = response_data["data"][0]
                image_b64 = first_item.get("b64_json") or first_item.get("base64") or first_item.get("image_base64")
                if image_b64:
                    image_data = base64.b64decode(image_b64)
                    if output_file:
                        output_path = Path(output_file)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        return output_file
                    return image_data

            return response_data
        except Exception as e:
            logging.error(f"Error editing images with FLUX.2: {e}")

            raise
