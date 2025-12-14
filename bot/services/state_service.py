"""State management service."""
from typing import Dict, Any, Optional
from aiogram.fsm.context import FSMContext


class StateService:
    """Service for managing user state and context."""
    
    @staticmethod
    async def save_purchase_context(state: FSMContext, **kwargs):
        """Save purchase context to state."""
        data = await state.get_data()
        data.update(kwargs)
        await state.update_data(**data)
    
    @staticmethod
    async def get_purchase_context(state: FSMContext) -> Dict[str, Any]:
        """Get purchase context from state."""
        return await state.get_data()
    
    @staticmethod
    async def clear_purchase_context(state: FSMContext):
        """Clear purchase context."""
        await state.clear()


state_service = StateService()
