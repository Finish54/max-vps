import logging

from aiogram.enums import ParseMode
from aiogram.types import Message, InputMediaPhoto, FSInputFile, User
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.methods.get import get_type_vpn, get_person, get_free_servers
from bot.keyboards.inline.user_inline import choose_type_vpn, choose_server
from bot.misc.language import Localization

_ = Localization.text
log = logging.getLogger(__name__)


async def edit_message(
    message: Message,
    photo=None,
    caption=None,
    reply_markup=None,
    text=None,
    parse_mode=ParseMode.HTML,
):
    try:
        if photo is not None:
            await message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(photo)
                )
            )
        if text is not None:
            await message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return
        await message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception as e:
        if photo is not None:
            await message.answer_photo(
                photo=FSInputFile(photo),
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        elif caption is not None:
            await message.answer(
                text=caption,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )


async def choosing_protocol_or_server(
    message: Message,
    session: AsyncSession,
    user_id: int,
    lang,
    key_id=0,
    back_data=None,
    payment:bool = False
) -> None:
    user = await get_person(session, user_id)
    all_types_vpn = await get_type_vpn(session, user.group)
    if len(all_types_vpn) != 1:
        await edit_message(
            message,
            photo='bot/img/type_vpn.jpg',
            caption=_('choosing_connect_type', lang),
            reply_markup=await choose_type_vpn(
                all_types_vpn,
                lang,
                key_id=key_id,
                back_data=back_data,
                payment=payment
            )
        )
    else:
        try:
            all_active_location = await get_free_servers(
                session, user.group, all_types_vpn[0]
            )
        except FileNotFoundError:
            log.info('Not free servers -- OK')
            await message.answer(_('not_server', lang))
            return
        await edit_message(
            message,
            photo='bot/img/locations.jpg',
            caption=_('choosing_connect_location', lang),
            reply_markup=await choose_server(
                all_active_location,
                all_types_vpn[0],
                lang,
                key_id,
                payment=payment
            )
        )