import os
import json
import time
import httpx
import asyncio
from typing import Optional, Union, Dict, Any
import logging

try:
    from azure.identity import DefaultAzureCredential
    from azure.identity.aio import DefaultAzureCredential as DefaultAzureCredentialAsync
except ImportError:
    # Azure identity is optional when using API key authentication
    DefaultAzureCredential = None
    DefaultAzureCredentialAsync = None


class SoraClient:
    """
    Client for Azure AI Foundry Sora video generation capabilities using httpx.
    """
    
    def __init__(self, 
                 endpoint: str = "", 
                 deployment_name: str = "sora",
                 api_version: str = "preview",
                 api_key: Optional[str] = None):
        """
        Initialize the Azure AI Foundry Sora client.
        
        Parameters:
            endpoint (str): Azure AI Foundry endpoint URL
            deployment_name (str): The deployment name for video generation.
            api_version (str): API version to use.
            api_key (str, optional): API key for authentication. If not provided, will use DefaultAzureCredential.
        """
        self.endpoint = endpoint or os.environ.get("SORA_ENDPOINT_URL", "")
        self.deployment_name = deployment_name or os.environ.get("SORA_DEPLOYMENT_NAME", "sora")
        self.api_version = api_version
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        
        if not self.endpoint:
            raise ValueError("Endpoint must be provided or set in SORA_ENDPOINT_URL environment variable")
        
        # Check if we have authentication method available
        if not self.api_key and (DefaultAzureCredential is None):
            raise ValueError("Either api_key must be provided or azure-identity must be installed for DefaultAzureCredential")
        
        # Remove trailing slash if present
        self.endpoint = self.endpoint.rstrip('/')
        
        # Construct the API URL
        self.path = f'openai/v1/video/generations/jobs'
        self.videopath=f'openai/v1/video/generations'
        self.params = f'?api-version={self.api_version}'
        self.constructed_url = f"{self.endpoint}/{self.path}{self.params}"
        
    def _get_headers_sync(self) -> Dict[str, str]:
        """Get headers with authentication (synchronous)."""
        if self.api_key:
            # Use API key authentication
            return {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
        else:
            # Use Azure credential token
            if DefaultAzureCredential is None:
                raise ValueError("azure-identity package is required for DefaultAzureCredential authentication")
            
            credential = DefaultAzureCredential()
            token_response = credential.get_token("https://cognitiveservices.azure.com/.default")
            
            return {
                'Authorization': f'Bearer {token_response.token}',
                'Content-Type': 'application/json',
            }
    
    async def _get_headers_async(self) -> Dict[str, str]:
        """Get headers with authentication (asynchronous)."""
        if self.api_key:
            # Use API key authentication
            return {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
        else:
            # Use Azure credential token
            if DefaultAzureCredentialAsync is None:
                raise ValueError("azure-identity package is required for DefaultAzureCredential authentication")
            
            credential = DefaultAzureCredentialAsync()
            token_response = await credential.get_token("https://cognitiveservices.azure.com/.default")
            
            return {
                'Authorization': f'Bearer {token_response.token}',
                'Content-Type': 'application/json',
            }
    
    def _poll_job_status_sync(self, job_id: str, headers: Dict[str, str], 
                             timeout: int = 1800, poll_interval: int = 10) -> Dict[str, Any]:
        """Poll job status until completion (synchronous)."""
        status_url = f"{self.endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={self.api_version}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with httpx.Client(timeout=30) as client:
                    response = client.get(status_url, headers=headers)
                    if response.status_code != 200:
                        logging.error(f"Failed to get job status: {response.status_code} - {response.text}")
                        raise Exception(f"Failed to get job status: {response.status_code} - {response.text}")
                    
                    job_data = response.json()
                    status = job_data.get('status')
                    
                    logging.info(f"Job {job_id} status: {status}")
                    
                    if status == 'succeeded':
                        return job_data
                    elif status == 'failed':
                        error_message = job_data.get('error', {}).get('message', 'Unknown error')
                        raise Exception(f"Job failed: {error_message}")
                    elif status in ['cancelled', 'expired']:
                        raise Exception(f"Job {status}")
                    
                    # Wait before next poll
                    time.sleep(poll_interval)
                    
            except Exception as e:
                if "Job failed" in str(e) or "Job cancelled" in str(e) or "Job expired" in str(e):
                    raise
                logging.warning(f"Error polling job status: {e}, retrying...")
                time.sleep(poll_interval)
        
        raise Exception(f"Job polling timeout after {timeout} seconds")
    
    async def _poll_job_status_async(self, job_id: str, headers: Dict[str, str], 
                                   timeout: int = 1800, poll_interval: int = 10) -> Dict[str, Any]:
        """Poll job status until completion (asynchronous)."""
        status_url = f"{self.endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={self.api_version}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(status_url, headers=headers)
                    if response.status_code != 200:
                        logging.error(f"Failed to get job status: {response.status_code} - {response.text}")
                        raise Exception(f"Failed to get job status: {response.status_code} - {response.text}")
                    
                    job_data = response.json()
                    status = job_data.get('status')
                    
                    logging.info(f"Job {job_id} status: {status}")
                    
                    if status == 'succeeded':
                        return job_data
                    elif status == 'failed':
                        error_message = job_data.get('error', {}).get('message', 'Unknown error')
                        raise Exception(f"Job failed: {error_message}")
                    elif status in ['cancelled', 'expired']:
                        raise Exception(f"Job {status}")
                    
                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                if "Job failed" in str(e) or "Job cancelled" in str(e) or "Job expired" in str(e):
                    raise
                logging.warning(f"Error polling job status: {e}, retrying...")
                await asyncio.sleep(poll_interval)
        
        raise Exception(f"Job polling timeout after {timeout} seconds")
    
    def _download_video_sync(self, video_url: str) -> bytes:
        """Download video from URL (synchronous)."""
        try:
            headers = self._get_headers_sync()
            with httpx.Client(timeout=300) as client:
                response = client.get(video_url, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to download video: {response.status_code} - {response.text}")
                return response.content
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            raise
    
    async def _download_video_async(self, video_url: str) -> bytes:
        """Download video from URL (asynchronous)."""
        try:
            headers = await self._get_headers_async()
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.get(video_url, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to download video: {response.status_code} - {response.text}")
                return response.content
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            raise
    
    # Synchronous Method for Video Generation
    def generate_video_sync(self, 
                           prompt: str, 
                           n_variants: int = 1,
                           n_seconds: int = 5,
                           height: int = 1080,
                           width: int = 1920,
                           timeout: int = 1800) -> bytes:
        """
        Synchronous method to generate a video based on the provided prompt.
        
        Parameters:
            prompt (str): The prompt for video generation
            n_variants (int): Number of variants to generate
            n_seconds (int): Duration in seconds
            height (int): Video height
            width (int): Video width
            timeout (int): Timeout in seconds for job completion
            
        Returns:
            bytes: Video data as bytes
        """
        try:
            headers = self._get_headers_sync()
            
            body = {
                "prompt": prompt,
                "n_variants": str(n_variants),
                "n_seconds": str(n_seconds),
                "height": str(height),
                "width": str(width),
                "model": self.deployment_name,
            }
            
            logging.info(f"Creating video generation job with prompt: {prompt[:50]}...")
            
            # Create job
            with httpx.Client(timeout=60) as client:
                response = client.post(self.constructed_url, headers=headers, json=body)
                if response.status_code != 201:
                    logging.error(f"Failed to create video job: {response.status_code} - {response.text}")
                    raise Exception(f"Failed to create video job: {response.status_code} - {response.text}")
                
                job_response = response.json()
                job_id = job_response.get('id')
                
                if not job_id:
                    raise Exception("No job ID returned from video generation API")
                
                logging.info(f"Video generation job created with ID: {job_id}")
            
            # Poll for completion
            completed_job = self._poll_job_status_sync(job_id, headers, timeout)
            
            # Extract video URL
            videos = completed_job.get('generations', [])
            if not videos:
                raise Exception("No videos found in completed job")
            
            generation_id = videos[0].get("id")
            video_url = video_url = f'{self.endpoint}/{self.videopath}/{generation_id}/content/video{self.params}'
            if not video_url:
                raise Exception("No video URL found in completed job")
            
            logging.info(f"Video generation completed, downloading from: {video_url}")
            
            # Download video
            video_data = self._download_video_sync(video_url)
            
            logging.info(f"Video downloaded successfully, size: {len(video_data)} bytes")
            return video_data
            
        except Exception as e:
            logging.error(f"Error generating video: {e}")
            raise
    
    # Asynchronous Method for Video Generation
    async def generate_video_async(self, 
                                  prompt: str, 
                                  n_variants: int = 1,
                                  n_seconds: int = 5,
                                  height: int = 1080,
                                  width: int = 1920,
                                  timeout: int = 1800) -> bytes:
        """
        Asynchronous method to generate a video based on the provided prompt.
        
        Parameters:
            prompt (str): The prompt for video generation
            n_variants (int): Number of variants to generate
            n_seconds (int): Duration in seconds
            height (int): Video height
            width (int): Video width
            timeout (int): Timeout in seconds for job completion
            
        Returns:
            bytes: Video data as bytes
        """
        try:
            headers = await self._get_headers_async()
            
            body = {
                "prompt": prompt,
                "n_variants": str(n_variants),
                "n_seconds": str(n_seconds),
                "height": str(height),
                "width": str(width),
                "model": self.deployment_name,
            }
            
            logging.info(f"Creating video generation job with prompt: {prompt[:50]}...")
            
            # Create job
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(self.constructed_url, headers=headers, json=body)
                if response.status_code != 201:
                    logging.error(f"Failed to create video job: {response.status_code} - {response.text}")
                    raise Exception(f"Failed to create video job: {response.status_code} - {response.text}")
                
                job_response = response.json()
                job_id = job_response.get('id')
                
                if not job_id:
                    raise Exception("No job ID returned from video generation API")
                
                logging.info(f"Video generation job created with ID: {job_id}")
            
            # Poll for completion
            completed_job = await self._poll_job_status_async(job_id, headers, timeout)
            
            # Extract video URL
            videos = completed_job.get('generations', [])
            if not videos:
                raise Exception("No videos found in completed job")
            
            generation_id = videos[0].get("id")
            video_url = video_url = f'{self.endpoint}/{self.videopath}/{generation_id}/content/video{self.params}'
            if not video_url:
                raise Exception("No video URL found in completed job")
            
            logging.info(f"Video generation completed, downloading from: {video_url}")
            
            # Download video
            video_data = await self._download_video_async(video_url)
            
            logging.info(f"Video downloaded successfully, size: {len(video_data)} bytes")
            return video_data
            
        except Exception as e:
            logging.error(f"Error generating video: {e}")
            raise