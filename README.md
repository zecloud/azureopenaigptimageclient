# Azure OpenAI GPT Image & Video Client

An asynchronous Python client for interacting with the Azure OpenAI GPT-Image API and Azure AI Foundry Sora video generation. This library simplifies the process of making requests to both Azure OpenAI GPT-Image services and Sora video generation services, providing an easy-to-use interface for developers.

## Features

- **Asynchronous Design**: Fully asynchronous, making it ideal for high-performance applications.
- **Ease of Use**: Simplifies interaction with Azure OpenAI GPT-Image services and Azure AI Foundry Sora video generation.
- **Customizable**: Configure client settings to suit your application needs.
- **Image Generation**: Generate images from text prompts using GPT-Image.
- **Image Editing**: Edit existing images with text prompts and optional masks.
- **Video Generation**: Generate videos from text prompts using Azure AI Foundry Sora.
- **Multiple Authentication**: Support for API key and Azure DefaultCredential authentication.


## Usage

Here is an example of how to use the Python client:

```python
import asyncio
from gptimageclient import GPTImageClient

async def main():
    # Initialize the client with your Azure API key and endpoint
    client = GPTImageClient(api_key="your-api-key", endpoint="your-endpoint")

    # Generate an image
    response = await client.generate_image_async(prompt="A futuristic cityscape at sunset")
    print(response)

     # Edit an image
    await client.edit_image_async(
        image_path="image_to_edit.png",
        mask_path="mask.png",
        prompt="Make this black and white",
        output_file="edited_image.png"
    )

     # Make your portrait in star wars starry night style
    await client.edit_image_async(
        image_path="yout_portrait.png",
        prompt="""Transform it into A high-resolution digital portrait inspired by the Star Wars universe. He is sitting in a dimly lit sci-fi environment with soft, ambient lighting. He wears futuristic robes or gear that reflect a Jedi or rebel aesthetic. His surroundings include subtle sci-fi elements like control panels or holograms. Put A metallic high tech moon with an hole  in the sky. The image is photo-realistic and cinematic. Make it a pinting in the starry night style""",
        output_file="starwarsstarrynight.png"
    )
    

# Run the example
asyncio.run(main())
```

### SoraClient for Video Generation

Here is an example of how to use the SoraClient for video generation:

```python
import asyncio
from soraclient import SoraClient

async def main():
    # Initialize the client with your Azure AI Foundry endpoint and API key
    client = SoraClient(
        endpoint="your-azure-ai-foundry-endpoint",
        deployment_name="sora",
        api_key="your-api-key"
    )

    # Generate a video asynchronously
    video_data = await client.generate_video_async(
        prompt="A serene lake at sunset with gentle ripples on the water",
        n_seconds=10,
        height=1080,
        width=1920
    )
    
    # Save the video to a file
    with open("generated_video.mp4", "wb") as f:
        f.write(video_data)
    print("Video generated and saved to generated_video.mp4")

    # Generate a video synchronously
    sync_video_data = client.generate_video_sync(
        prompt="A bustling city street with people walking and cars passing by",
        n_seconds=5,
        height=720,
        width=1280
    )
    
    # Save the synchronous video
    with open("sync_video.mp4", "wb") as f:
        f.write(sync_video_data)
    print("Synchronous video generated and saved to sync_video.mp4")

# Run the example
asyncio.run(main())
```

Here is an example of how to use the C# client:

```csharp
using System;
using System.Threading.Tasks;

public class Program
{
    public static async Task Main(string[] args)
    {
        // Initialize the client with your Azure API key and endpoint
        var client = new GptImageClient("your-endpoint", "gpt-image-1", "your-api-key");

        // Generate an image asynchronously
        var imageData = await client.GenerateImageAsync("A futuristic cityscape at sunset");
        Console.WriteLine("Image generated asynchronously");

        // Edit an image asynchronously
        var editedImageData = await client.EditImageAsync("image_to_edit.png", "Make this black and white", "mask.png", null, "auto", "auto", "edited_image.png");
        Console.WriteLine("Image edited asynchronously");

        // Generate an image synchronously
        var syncImageData = client.GenerateImageSync("A futuristic cityscape at sunset");
        Console.WriteLine("Image generated synchronously");

        // Edit an image synchronously
        var syncEditedImageData = client.EditImageSync("image_to_edit.png", "Make this black and white", "mask.png", null, "auto", "auto", "edited_image.png");
        Console.WriteLine("Image edited synchronously");
    }
}
```

## Configuration

### Image Client Configuration

The image client requires the following:

- **API Key**: Your Azure API key for authentication.
- **Endpoint**: The endpoint URL for your Azure OpenAI GPT-Image service.

You can set these values when initializing the client.

For the C# client, you can set the API key using an environment variable `AZURE_API_KEY` or pass it directly to the `GptImageClient` constructor.

### SoraClient Configuration

The SoraClient supports the following configuration options:

- **Endpoint**: Azure AI Foundry endpoint URL (can be set via `SORA_ENDPOINT_URL` environment variable)
- **Deployment Name**: The deployment name for video generation (can be set via `SORA_DEPLOYMENT_NAME` environment variable, defaults to "sora")
- **API Key**: API key for authentication (can be set via `AZURE_OPENAI_API_KEY` environment variable)
- **Azure Credential**: Alternatively, you can use Azure DefaultAzureCredential for authentication (requires `azure-identity` package)

#### Environment Variables for SoraClient

```bash
export SORA_ENDPOINT_URL="your-azure-ai-foundry-endpoint"
export SORA_DEPLOYMENT_NAME="sora"
export AZURE_OPENAI_API_KEY="your-api-key"
```

#### Using Azure DefaultCredential

To use Azure DefaultCredential instead of API key authentication, install the optional dependency:

```bash
pip install azure-identity
```

Then initialize SoraClient without an API key:

```python
from soraclient import SoraClient

client = SoraClient(
    endpoint="your-azure-ai-foundry-endpoint",
    deployment_name="sora"
    # No api_key parameter - will use DefaultAzureCredential
)
```

## Development

To contribute to the development of this library, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/zecloud/azureopenaigptimageclient.git
    ```

2. Navigate to the project directory:

    ```bash
    cd azureopenaigptimageclient
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. For SoraClient with Azure DefaultCredential support, install the optional dependency:

    ```bash
    pip install azure-identity
    ```

`

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests for new features, bug fixes, or documentation improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, feel free to open an issue in the repository or reach out via email.

---

Happy coding! 🎉
```
