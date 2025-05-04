# Azure OpenAI GPT Image Client

An asynchronous Python client for interacting with the Azure OpenAI GPT-Image API. This library simplifies the process of making requests to the Azure OpenAI GPT-Image service, providing an easy-to-use interface for developers.

## Features

- **Asynchronous Design**: Fully asynchronous, making it ideal for high-performance applications.
- **Ease of Use**: Simplifies interaction with Azure OpenAI GPT-Image services.
- **Customizable**: Configure client settings to suit your application needs.


## Usage

Here is an example of how to use the client:

```python
import asyncio
from azureopenaigptimageclient import GPTImageClient

async def main():
    # Initialize the client with your Azure API key and endpoint
    client = GPTImageClient(api_key="your-api-key", endpoint="your-endpoint")

    # Generate an image
    response = await client.generate_image(prompt="A futuristic cityscape at sunset")
    print(response)

     # Edit an image
    await client.edit_image(
        image_path="image_to_edit.png",
        mask_path="mask.png",
        prompt="Make this black and white",
        output_file="edited_image.png"
    )

     # Make your portrait in star wars starry night style
    await client.edit_image(
        image_path="yout_portrait.png",
        prompt="""Transform it into A high-resolution digital portrait inspired by the Star Wars universe. He is sitting in a dimly lit sci-fi environment with soft, ambient lighting. He wears futuristic robes or gear that reflect a Jedi or rebel aesthetic. His surroundings include subtle sci-fi elements like control panels or holograms. Put A metallic high tech moon with an hole  in the sky. The image is photo-realistic and cinematic. Make it a pinting in the starry night style""",
        output_file="starwarsstarrynight.png"
    )
    

# Run the example
asyncio.run(main())
```

## Configuration

The client requires the following:

- **API Key**: Your Azure API key for authentication.
- **Endpoint**: The endpoint URL for your Azure OpenAI GPT-Image service.

You can set these values when initializing the client.

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
