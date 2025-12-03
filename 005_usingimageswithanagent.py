import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatMessage, TextContent, UriContent, DataContent, Role
import httpx
load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

def create_agent(client: AzureAIAgentClient, instructions: str, name: str):
    """Crea y retorna un agente con las instrucciones y nombre especificados."""
    return client.create_agent(
        instructions=instructions,
        name=name
    )

async def download_image(url: str) -> bytes:
    """Descarga una imagen desde una URL y retorna los bytes."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        return response.content

with open("./images/nature.jpg", "rb") as image_file:
    image_bytes = image_file.read()

message = ChatMessage(
    role=Role.USER,
    contents=[
        TextContent(text="¿Qué ves en esta imagen?"),
        DataContent(
            data =image_bytes,
            media_type="image/jpeg"
        )
    ]
)

messageuri = ChatMessage(
    role=Role.USER,
    contents=[
        TextContent(text="¿Qué ves en esta imagen?"),
        UriContent(
            uri="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            media_type="image/jpeg"
        )
    ]
)

async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
              async_credential=credential,
              endpoint=AZURE_ENDPOINT,
              model_deployment_name=AZURE_MODEL,
              should_cleanup_agent=True
          ) as client:

            agent = create_agent(
                client=client,
                instructions="Eres bueno describiendo imagenes.",
                name="ImageDescriptor"
            )

            # Descargar imagen de URL y crear mensaje con DataContent
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            print(f"Descargando imagen desde URL...")
            image_data = await download_image(image_url)
            print(f"Imagen descargada: {len(image_data)} bytes")

            message_from_url = ChatMessage(
                role=Role.USER,
                contents=[
                    TextContent(text="¿Qué ves en esta imagen?"),
                    DataContent(
                        data=image_data,
                        media_type="image/jpeg"
                    )
                ]
            )

            result = await agent.run(message_from_url)
            print(f"Agent: {result.text}")

asyncio.run(main())