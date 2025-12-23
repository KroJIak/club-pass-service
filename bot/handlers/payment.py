"""Payment handlers for Telegram Payments."""
from aiogram import Router, F
from aiogram.types import PreCheckoutQuery, Message, SuccessfulPayment
from aiogram.fsm.context import FSMContext
import httpx
from bot.core.config import settings
from bot.core.i18n import get_user_locale, t
from bot.core.message_manager import safe_edit_or_send

router = Router()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Process pre-checkout query - approve payment."""
    # Approve payment
    await pre_checkout_query.bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True,
    )


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    """Process successful payment - create tickets via API."""
    locale = get_user_locale(message.from_user.language_code)
    payment: SuccessfulPayment = message.successful_payment
    
    # Extract order_id from payload (format: "order_{uuid}")
    order_id = payment.invoice_payload
    if order_id.startswith("order_"):
        order_id = order_id.replace("order_", "")
    
    # Call API to process payment and create tickets
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.API_URL}{settings.API_PREFIX}/v1/payments/process",
                json={
                    "order_id": order_id,
                    "telegram_payment_charge_id": payment.provider_payment_charge_id,
                }
            )
            response.raise_for_status()
            result = response.json()
            
            tickets_created = result.get("tickets_created", 0)
            
            if tickets_created > 0:
                text = t(
                    locale,
                    "messages.purchase.payment_success",
                    tickets_count=tickets_created,
                )
            else:
                text = t(locale, "messages.purchase.payment_processed")
            
            await safe_edit_or_send(
                message,
                text,
                locale=locale,
                screen_key="buy_ticket"
            )
            
            # Clear purchase state
            await state.clear()
            
    except httpx.HTTPError as e:
        print(f"Error processing payment: {e}")
        text = t(locale, "messages.purchase.payment_error")
        await safe_edit_or_send(
            message,
            text,
            locale=locale,
            screen_key="buy_ticket"
        )

