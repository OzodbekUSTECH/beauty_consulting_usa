from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.dto.ai import CreatePromptRequest, AssistantResponse, SetAssistantStateRequest, \
    AssistantStateResponse
from app.interactors.ai.create import CreatePromptInteractor
from app.utils.ai_state import AIAssistantStateService

router = APIRouter(prefix="/assistant", tags=["Assistant"], route_class=DishkaRoute)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_prompt(
        request: CreatePromptRequest,
        create_prompt_interactor: FromDishka[CreatePromptInteractor],
        assistant_state: FromDishka[AIAssistantStateService]
) -> AssistantResponse:
    if not await assistant_state.get_state():
        return AssistantResponse()

    return await create_prompt_interactor.execute(request)

@router.get('/state')
async def get_current_state(assistant_state: FromDishka[AIAssistantStateService]) -> AssistantStateResponse:
    return AssistantStateResponse(enabled=await assistant_state.get_state())

@router.post('/state')
async def set_state(
        request: SetAssistantStateRequest,
        assistant_state: FromDishka[AIAssistantStateService]
) -> AssistantStateResponse:
    await assistant_state.set_state(request)
    return await assistant_state.get_state()


