import asyncio
import json

async def mock_symptom_agent():
    raise RuntimeError("API Key Missing")

async def stream_agent_updates():
    yield {"type": "thought", "content": "Step 1"}
    yield {"type": "thought", "content": "Step 2"}
    await mock_symptom_agent()
    yield {"type": "thought", "content": "Step 3"}

async def agen():
    async for evt in stream_agent_updates():
        yield f"data: {json.dumps(evt)}\n\n"

def generate():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async_gen = agen()
    try:
        while True:
            chunk = loop.run_until_complete(async_gen.__anext__())
            yield chunk
    except StopAsyncIteration:
        pass
    except Exception as e:
        print(f"Caught Exception: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'The AI service could not complete your wellness plan. Please try again shortly.'})}\n\n"
    finally:
        loop.run_until_complete(async_gen.aclose())
        loop.close()

if __name__ == "__main__":
    for chunk in generate():
        print("YIELDED:", chunk)
