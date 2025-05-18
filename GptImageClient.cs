using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class GptImageClient
{
    private readonly string endpoint;
    private readonly string deploymentName;
    private readonly string apiKey;
    private readonly string apiVersion;
    private readonly HttpClient httpClient;

    public GptImageClient(string endpoint, string deploymentName = "gpt-image-1", string apiKey = null, string apiVersion = "2025-04-01-preview")
    {
        this.endpoint = endpoint;
        this.deploymentName = deploymentName;
        this.apiKey = apiKey ?? Environment.GetEnvironmentVariable("AZURE_API_KEY");
        this.apiVersion = apiVersion;

        if (string.IsNullOrEmpty(this.apiKey))
        {
            throw new ArgumentException("API key must be provided or set in AZURE_API_KEY environment variable");
        }

        this.httpClient = new HttpClient();
        this.httpClient.DefaultRequestHeaders.Add("api-key", this.apiKey);
        this.httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public async Task<byte[]> GenerateImageAsync(string prompt, string size = "1024x1024", string quality = "auto", int n = 1, string outputFile = null)
    {
        var url = $"{this.endpoint}/openai/deployments/{this.deploymentName}/images/generations?api-version={this.apiVersion}";

        var payload = new
        {
            prompt,
            size,
            quality,
            n
        };

        var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

        var response = await this.httpClient.PostAsync(url, content);
        response.EnsureSuccessStatusCode();

        var responseData = await response.Content.ReadAsStringAsync();
        var jsonResponse = JsonDocument.Parse(responseData);
        var imageB64 = jsonResponse.RootElement.GetProperty("data")[0].GetProperty("b64_json").GetString();
        var imageData = Convert.FromBase64String(imageB64);

        if (!string.IsNullOrEmpty(outputFile))
        {
            await File.WriteAllBytesAsync(outputFile, imageData);
            return null;
        }

        return imageData;
    }

    public async Task<byte[]> EditImageAsync(string imagePath, string prompt, string maskPath = null, string[] additionalImages = null, string size = "auto", string quality = "auto", string outputFile = null)
    {
        var url = $"{this.endpoint}/openai/deployments/{this.deploymentName}/images/edits?api-version={this.apiVersion}";

        using var form = new MultipartFormDataContent();

        form.Add(new StreamContent(File.OpenRead(imagePath)), "image", Path.GetFileName(imagePath));

        if (!string.IsNullOrEmpty(maskPath))
        {
            form.Add(new StreamContent(File.OpenRead(maskPath)), "mask", Path.GetFileName(maskPath));
        }

        if (additionalImages != null)
        {
            foreach (var imgPath in additionalImages)
            {
                form.Add(new StreamContent(File.OpenRead(imgPath)), "image", Path.GetFileName(imgPath));
            }
        }

        form.Add(new StringContent(prompt), "prompt");
        form.Add(new StringContent(size), "size");
        form.Add(new StringContent(quality), "quality");

        var response = await this.httpClient.PostAsync(url, form);
        response.EnsureSuccessStatusCode();

        var responseData = await response.Content.ReadAsStringAsync();
        var jsonResponse = JsonDocument.Parse(responseData);
        var imageB64 = jsonResponse.RootElement.GetProperty("data")[0].GetProperty("b64_json").GetString();
        var imageData = Convert.FromBase64String(imageB64);

        if (!string.IsNullOrEmpty(outputFile))
        {
            await File.WriteAllBytesAsync(outputFile, imageData);
            return null;
        }

        return imageData;
    }

    public byte[] GenerateImageSync(string prompt, string size = "1024x1024", string quality = "auto", int n = 1, string outputFile = null)
    {
        var url = $"{this.endpoint}/openai/deployments/{this.deploymentName}/images/generations?api-version={this.apiVersion}";

        var payload = new
        {
            prompt,
            size,
            quality,
            n
        };

        var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

        var response = this.httpClient.PostAsync(url, content).Result;
        response.EnsureSuccessStatusCode();

        var responseData = response.Content.ReadAsStringAsync().Result;
        var jsonResponse = JsonDocument.Parse(responseData);
        var imageB64 = jsonResponse.RootElement.GetProperty("data")[0].GetProperty("b64_json").GetString();
        var imageData = Convert.FromBase64String(imageB64);

        if (!string.IsNullOrEmpty(outputFile))
        {
            File.WriteAllBytes(outputFile, imageData);
            return null;
        }

        return imageData;
    }

    public byte[] EditImageSync(string imagePath, string prompt, string maskPath = null, string[] additionalImages = null, string size = "auto", string quality = "auto", string outputFile = null)
    {
        var url = $"{this.endpoint}/openai/deployments/{this.deploymentName}/images/edits?api-version={this.apiVersion}";

        using var form = new MultipartFormDataContent();

        form.Add(new StreamContent(File.OpenRead(imagePath)), "image", Path.GetFileName(imagePath));

        if (!string.IsNullOrEmpty(maskPath))
        {
            form.Add(new StreamContent(File.OpenRead(maskPath)), "mask", Path.GetFileName(maskPath));
        }

        if (additionalImages != null)
        {
            foreach (var imgPath in additionalImages)
            {
                form.Add(new StreamContent(File.OpenRead(imgPath)), "image", Path.GetFileName(imgPath));
            }
        }

        form.Add(new StringContent(prompt), "prompt");
        form.Add(new StringContent(size), "size");
        form.Add(new StringContent(quality), "quality");

        var response = this.httpClient.PostAsync(url, form).Result;
        response.EnsureSuccessStatusCode();

        var responseData = response.Content.ReadAsStringAsync().Result;
        var jsonResponse = JsonDocument.Parse(responseData);
        var imageB64 = jsonResponse.RootElement.GetProperty("data")[0].GetProperty("b64_json").GetString();
        var imageData = Convert.FromBase64String(imageB64);

        if (!string.IsNullOrEmpty(outputFile))
        {
            File.WriteAllBytes(outputFile, imageData);
            return null;
        }

        return imageData;
    }
}
