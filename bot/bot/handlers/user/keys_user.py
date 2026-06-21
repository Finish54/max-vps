import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.methods.get import (
    get_person,
    get_key_user,
    get_name_location_server,
    get_key_id,
    get_free_server_id,
)
from bot.database.methods.insert import add_key
from bot.database.methods.update import (
    person_trial_period,
    server_space_update,
    update_server_key
)
from bot.keyboards.inline.user_inline import (
    connect_vpn_menu,
    instruction_manual,
    renew, user_menu
)
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.language import Localization, get_lang
from bot.misc.callbackData import (
    ShowKey,
    EditKey,
    ExtendKey,
    DetailKey,
    TrialPeriod
)
from bot.misc.util import CONFIG
from bot.service.edit_message import edit_message, choosing_protocol_or_server
from bot.service.create_file_str import str_to_file, replace_spaces

log = logging.getLogger(__name__)

_ = Localization.text
btn_text = Localization.get_reply_button

key_router = Router()


@key_router.callback_query(F.data == 'vpn_connect_btn')
async def choose_server_user(
    call: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    keys = await get_key_user(session, call.from_user.id)
    if len(keys) != 0:
        await edit_message(
            call.message,
            photo='bot/img/keys_user.jpg',
            caption=_('user_key_list_message_connect', lang),
            reply_markup=await connect_vpn_menu(lang, keys)
        )
        return
    await choosing_protocol_or_server(
        call.message,
        session,
        call.from_user.id,
        lang,
        back_data='back_general_menu_btn',
        payment=True
    )


@key_router.callback_query(F.data.in_(btn_text('vpn_connect_btn')))
async def choose_server_user(
    call: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    keys = await get_key_user(session, call.from_user.id)
    if len(keys) != 0:
        await call.message.answer_photo(
            FSInputFile('bot/img/keys_user.jpg'),
            _('user_key_list_message_connect', lang),
            reply_markup=await connect_vpn_menu(lang, keys)
        )
        return

    await choosing_protocol_or_server(
        call.message,
        session,
        call.from_user.id,
        lang,
        back_data='back_general_menu_btn',
        payment=True
    )


@key_router.callback_query(TrialPeriod.filter())
async def choose_server_user(
    call: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: TrialPeriod
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    person = await get_person(session, call.from_user.id)
    await call.message.delete()
    await get_trial_period(
        session,
        call.message,
        call,
        lang,
        person,
        callback_data.id_prot,
        callback_data.id_loc
    )


async def get_trial_period(
    session: AsyncSession,
    message: Message,
    call: CallbackQuery,
    lang,
    person,
    id_prot,
    id_loc
):
    if person.trial_period:
        await message.answer(_('not_trial_message', lang))
        return
    server = await get_free_server_id(
        session,
        id_loc,
        id_prot
    )
    if server is None:
        await call.message.answer_photo(
            photo=FSInputFile('bot/img/main_menu.jpg'),
            reply_markup=await user_menu(lang, person.tgid)
        )
        await call.answer()
        return
    await person_trial_period(session, person.tgid)
    person.trial_period = True
    person.special_offer = True
    await message.answer(_('trial_message', lang))
    key = await add_key(
        session,
        person.tgid,
        CONFIG.trial_period,
        trial_period=True,
        server_id=server.id
    )
    try:
        download = await message.answer(_('download', lang))
        key = await get_key_id(session, key.id)
        server_manager = ServerManager(key.server_table)
        await server_manager.login()
        name_location = await get_name_location_server(
            session,
            key.server_table.id
        )
        config, sub_url = await server_manager.get_key(
            call.from_user.id,
            name_key=name_location,
            key_id=key.id
        )
        server_parameters = await server_manager.get_all_user()

        await server_space_update(
            session,
            server.id,
            len(server_parameters)
        )
    except Exception as e:
        await update_server_key(session, key.id)
        await message.answer(_('server_not_connected', lang))
        log.error(e)
        return
    await download.delete()
    await post_key_telegram(call, key, config, sub_url, lang)


async def post_key_telegram(call: CallbackQuery, key, config, sub_url, lang) -> None:
    photo = await get_img_type_vpn(key)
    connect_message = _('how_to_connect', lang).format(
        name_vpn=ServerManager.VPN_TYPES.get(key.server_table.type_vpn)
        .NAME_VPN,
        config=config,
    )
    # Добавляем ссылку подписки Happ если доступна
    if sub_url:
        connect_message += '\n\n' + _('happ_sub_url_text', lang).format(
            sub_url=sub_url
        )
    await edit_message(
        call.message,
        photo=photo,
        caption=connect_message,
        reply_markup=await instruction_manual(
            lang,
            key.server_table.type_vpn
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    await call.answer()


async def get_img_type_vpn(key):
    return 'bot/img/vless.jpg'


async def show_key(session: AsyncSession, callback, lang, key):
    try:
        server_manager = ServerManager(key.server_table)
        name_location = await get_name_location_server(
            session,
            key.server_table.id
        )
        await server_manager.login()
        config, sub_url = await server_manager.get_key(
            name=callback.from_user.id,
            name_key=name_location,
            key_id=key.id
        )
        if config is None:
            raise Exception('Server Not Connected')
    except Exception as e:
        await callback.message.answer(_('server_not_connected', lang))
        log.error(e)
        await callback.answer()
        return
    await post_key_telegram(callback, key, config, sub_url, lang)


@key_router.callback_query(DetailKey.filter())
async def choose_server_free(
    call: CallbackQuery,
    session: AsyncSession,
    callback_data: ShowKey,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    keys = await get_key_user(session, call.from_user.id)
    try:
        await edit_message(
            call.message,
            reply_markup=await connect_vpn_menu(
                lang,
                keys,
                id_detail=callback_data.key_id
            )
        )
    except Exception as e:
        await call.message.answer_photo(
            FSInputFile('bot/img/keys_user.jpg'),
            _('user_key_list_message_connect', lang),
            reply_markup=await connect_vpn_menu(
                lang,
                keys,
                id_detail=callback_data.key_id
            )
        )

    await call.answer()


@key_router.callback_query(ShowKey.filter())
async def choose_server_free(
    call: CallbackQuery,
    session: AsyncSession,
    callback_data: ShowKey,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    key = await get_key_id(session, callback_data.key_id)
    if key.server is None:
        await choosing_protocol_or_server(
            call.message,
            session,
            call.from_user.id,
            lang,
            key_id=key.id,
            back_data='vpn_connect_btn'
        )
        await call.answer()
        return
    await show_key(session, call, lang, key)
    await call.answer()


@key_router.callback_query(EditKey.filter())
async def choose_server_free(
    call: CallbackQuery,
    session: AsyncSession,
    callback_data: EditKey,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    await choosing_protocol_or_server(
        call.message,
        session,
        call.from_user.id,
        lang,
        key_id=callback_data.key_id,
        back_data='vpn_connect_btn'
    )
    await call.answer()


@key_router.callback_query(ExtendKey.filter())
async def choose_server_free(
    call: CallbackQuery,
    session: AsyncSession,
    callback_data: ExtendKey,
    state: FSMContext
) -> None:
    lang = await get_lang(session, call.from_user.id, state)
    await edit_message(
        call.message,
        photo='bot/img/pay_subscribe.jpg',
        caption=_('choosing_month_sub', lang),
        reply_markup=await renew(
            CONFIG,
            lang,
            CONFIG.type_payment.get(1),
            back_data='vpn_connect_btn',
            key_id=callback_data.key_id,
        )
    )
    await call.answer()
