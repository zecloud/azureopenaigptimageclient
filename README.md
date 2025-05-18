# Azure OpenAI GPT Image Client

An asynchronous Python client for interacting with the Azure OpenAI GPT-Image API. This library simplifies the process of making requests to the Azure OpenAI GPT-Image service, providing an easy-to-use interface for developers.

## Features

- **Asynchronous Design**: Fully asynchronous, making it ideal for high-performance applications.
- **Ease of Use**: Simplifies interaction with Azure OpenAI GPT-Image services.
- **Customizable**: Configure client settings to suit your application needs.


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

The client requires the following:

- **API Key**: Your Azure API key for authentication.
- **Endpoint**: The endpoint URL for your Azure OpenAI GPT-Image service.

You can set these values when initializing the client.

For the C# client, you can set the API key using an environment variable `AZURE_API_KEY` or pass it directly to the `GptImageClient` constructor.

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
