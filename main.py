import os

import gradio as gr
import numpy as np
from dotenv import load_dotenv, find_dotenv

from fnllm.oci_genai import PublicOCIGenAIConfig, create_oci_genai_client, create_oci_genai_chat_llm, \
    create_oci_genai_embeddings_llm
from fnllm.openai import create_openai_client, create_openai_chat_llm, PublicOpenAIConfig

# read local .env file
load_dotenv(find_dotenv())


async def openai_chat(message, history):
    print(f"{message=}")
    if len(history) > 2:
        history = history[-2:]
        print(f"{history=}")
    print("create configuration start...")
    configuration = PublicOpenAIConfig(
        api_key=os.environ['OPENAI_API_KEY'],
        base_url=os.environ['OPENAI_BASE_URL'],
        model=os.environ['OPENAI_MODEL'],
        max_concurrency=4,
        tokens_per_minute=4000,
        requests_per_minute=20,
        requests_burst_mode=False,
    )
    print(f"{configuration=}")
    print("create configuration end...")

    print("create client start...")
    client = create_openai_client(configuration)
    print(f"{client=}")
    print("create client end...")

    print("create openai_chat_llm start...")
    openai_chat_llm = create_openai_chat_llm(
        configuration,
        client=client,
    )
    print(f"{openai_chat_llm=}")
    print("create openai_chat_llm end...")

    print("create response start...")
    response = await openai_chat_llm(
        prompt=message,
        stream=True,
        name="chat",
        history=history,
    )
    # print(f"{response=}")
    # print("create response end...")

    answer = ""
    async for chunk in response.output.content:
        # print(f"{chunk=}")
        answer += chunk
        yield answer

async def oci_genai_embedding(message, history):
    print(f"{message=}")
    print("create configuration start...")
    configuration = PublicOCIGenAIConfig(
        endpoint=os.environ['OCI_GENAI_ENDPOINT'],
        chat_parameters={
            "compartment_id": os.environ['OCI_COMPARTMENT_ID'],
            "model_id": os.environ['OCI_GENAI_EMBEDDING_MODEL_NAME'],
        },
        max_concurrency=4,
        tokens_per_minute=4000,
        requests_per_minute=20,
        requests_burst_mode=False,
    )
    print(f"{configuration=}")
    print("create configuration end...")

    print("create client start...")
    client = create_oci_genai_client(configuration)
    print(f"{client=}")
    print("create client end...")

    print("create openai_chat_llm start...")
    oci_genai_chat_llm = create_oci_genai_embeddings_llm(
        configuration,
        client=client,
    )
    print(f"{oci_genai_chat_llm=}")
    print("create openai_chat_llm end...")

    print("create response start...")
    response = await oci_genai_chat_llm(
        prompt=[message],
        name="chat",
        history=history,
    )
    # print(f"{response=}")
    # print(f"{response.output=}")
    # print(f"{response.output.embeddings=}")
    yield {"role": "assistant", "content": str(np.array(response.output.embeddings[0]).tolist())}


async def oci_genai_chat(message, history):
    print(f"{message=}")
    if len(history) > 2:
        history = history[-2:]
        print(f"{history=}")
    print("create configuration start...")
    configuration = PublicOCIGenAIConfig(
        endpoint=os.environ['OCI_GENAI_ENDPOINT'],
        chat_parameters={
            "compartment_id": os.environ['OCI_COMPARTMENT_ID'],
            "model_id": os.environ['OCI_GENAI_CHAT_MODEL_NAME'],
        },
        max_concurrency=4,
        tokens_per_minute=4000,
        requests_per_minute=20,
        requests_burst_mode=False,
    )
    print(f"{configuration=}")
    print("create configuration end...")

    print("create client start...")
    client = create_oci_genai_client(configuration)
    print(f"{client=}")
    print("create client end...")

    print("create openai_chat_llm start...")
    oci_genai_chat_llm = create_oci_genai_chat_llm(
        configuration,
        client=client,
    )
    print(f"{oci_genai_chat_llm=}")
    print("create openai_chat_llm end...")

    print("create response start...")
    response = await oci_genai_chat_llm(
        prompt=message,
        stream=False,
        name="chat",
        history=history,
    )
    print(f"{response=}")
    print(f"{response.history=}")
    print(f"{response.history[-1]=}")
    yield response.history[-1]
    # print(f"{response.output.content=}")
    # print("create response end...")
    #
    # answer = ""
    # async for chunk in response.output.content:
    #     answer += chunk
    #     yield answer


async def oci_genai_chat_stream(message, history):
    print(f"{message=}")
    if len(history) > 2:
        history = history[-2:]
        print(f"{history=}")
    print("create configuration start...")
    configuration = PublicOCIGenAIConfig(
        endpoint=os.environ['OCI_GENAI_ENDPOINT'],
        chat_parameters={
            "compartment_id": os.environ['OCI_COMPARTMENT_ID'],
            "model_id": os.environ['OCI_GENAI_CHAT_MODEL_NAME'],
        },
        max_concurrency=4,
        tokens_per_minute=4000,
        requests_per_minute=20,
        requests_burst_mode=False,
    )
    print(f"{configuration=}")
    print("create configuration end...")

    print("create client start...")
    client = create_oci_genai_client(configuration)
    print(f"{client=}")
    print("create client end...")

    print("create openai_chat_llm start...")
    oci_genai_chat_llm = create_oci_genai_chat_llm(
        configuration,
        client=client,
    )
    print(f"{oci_genai_chat_llm=}")
    print("create openai_chat_llm end...")

    print("create response start...")
    response = await oci_genai_chat_llm(
        prompt=message,
        stream=True,
        name="chat",
        history=history,
    )
    print(f"{response=}")
    print(f"{response.output.content=}")
    # print("create response end...")

    answer = ""
    async for chunk in response.output.content:
        answer += chunk
        yield answer

def vote(data: gr.LikeData):
    print(f"{data.value=}")
    print(f"Chatbot response: {data.value[-1]}")
    if data.liked:
        return "Good response. "
    else:
        return "Bad response. "


with gr.Blocks() as app:
    vote_output = gr.Textbox(label="vote output", visible=False)
    with gr.Row():
        with gr.Column():
            openai_chatbot = gr.Chatbot(
                label="OpenAI",
                type="messages",
                placeholder="<strong>Your Personal AI Teacher</strong><br>Ask Me Anything",
                height=600,
                min_height=600,
                max_height=600,
                show_copy_button=True,
            )
            openai_chatbot.like(
                vote,
                [],
                [vote_output]
            )
            gr.ChatInterface(
                fn=openai_chat,
                type="messages",
                chatbot=openai_chatbot
            )
        with gr.Column():
            oci_genai_chatbot = gr.Chatbot(
                label="OCI GenAI",
                type="messages",
                placeholder="<strong>Your Personal AI Teacher</strong><br>Ask Me Anything",
                height=600,
                min_height=600,
                max_height=600,
                show_copy_button=True,
            )
            oci_genai_chatbot.like(
                vote,
                [],
                [vote_output]
            )
            gr.ChatInterface(
                # fn=oci_genai_embedding,
                # fn=oci_genai_chat,
                fn=oci_genai_chat_stream,
                type="messages",
                chatbot=oci_genai_chatbot
            )

app.queue()

if __name__ == "__main__":
    app.launch()
