
from app.di import container
from app.dto.ai import CreatePromptRequest
from app.interactors.ai.create import CreatePromptInteractor



async def get_ai_response(data: CreatePromptRequest) -> str | None:
    try:
        async with container() as con:
            process_message = await con.get(CreatePromptInteractor)
            assistant_response = await process_message.execute(data)

            return assistant_response.response
    except Exception as e:
        print(f"Error in get_ai_response: {e}")
        return None