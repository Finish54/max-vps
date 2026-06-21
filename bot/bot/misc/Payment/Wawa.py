import asyncio
import decimal
import logging
import uuid



from bot.misc.Payment.payment_systems import PaymentSystem
from bot.misc.Payment.wata import PaymentClient
from bot.misc.language import Localization, get_lang

log = logging.getLogger(__name__)

_ = Localization.text


class Wawa(PaymentSystem):
    CLIENT: PaymentClient
    TOKEN: str
    BASE_URL: str = 'https://api.wata.pro'
    ID: str
    STEP = 65

    def __init__(
        self,
        session,
        config,
        message, user_id,
        price, month_count,
        type_pay, key_id,
        id_prot, id_loc,
        data=None
    ):
        super().__init__(
            session,
            message, user_id,
            type_pay, key_id,
            id_prot, id_loc,
            price, month_count
        )
        self.TOKEN = config.wawa_token_card

    async def check_pay_wallet(self, client: PaymentClient, payment_id):
        tic = 0
        while tic < self.CHECK_PERIOD:
            info = await client.payment.get_link_by_uuid(payment_id)
            if info['status'] == "Closed":
                await self.successful_payment(
                    self.price,
                    'Wata'
                )
                return
            tic += self.STEP
            await asyncio.sleep(self.STEP)
            if self.CHECK_PERIOD - tic <= self.TIME_DELETE:
                await self.delete_pay_button('Wawa')
        return

    async def create_id(self):
        self.ID = str(uuid.uuid4())

    async def create_invoice(self, lang, client):
        bot = await self.message.bot.me()
        await self.create_id()
        return await client.payment.create(
            amount=decimal.Decimal(self.price),
            currency="RUB",
            description=_('description_payment', lang),
            order_id=self.ID,
            success_redirect_url=f'https://t.me/{bot.username}',
            fail_redirect_url=f'https://t.me/{bot.username}'
        )

    async def to_pay(self):
        client = PaymentClient.initialize(
            api_key=self.TOKEN,
            base_url=self.BASE_URL,
        )
        client.__init__(
            api_key=self.TOKEN,
            base_url=self.BASE_URL,
            parent_logger_name='wata',
            base_logger_name='wata',
            log_level=logging.ERROR
        )
        lang_user = await get_lang(self.session, self.user_id)
        payment = await self.create_invoice(lang_user, client)
        await self.pay_button(payment['url'], webapp=False)
        log.info(
            f'Create payment link Wawa '
            f'User: ID: {self.user_id}'
        )
        try:
            await self.check_pay_wallet(client, payment['id'])
        except BaseException as e:
            log.error(e, 'The payment period has expired')
            await client.close()
        finally:
            await self.delete_pay_button('Wawa')
            await client.close()
            log.info('exit check payment Wawa')

    def __str__(self):
        return 'Платежная система Wata'



class WawaSpb(Wawa):

    def __init__(
        self,
        session,
        config,
        message, user_id,
        price, month_count,
        type_pay, key_id,
        id_prot, id_loc,
        data=None
    ):
        super().__init__(
            session,
            config,
            message, user_id,
            price, month_count,
            type_pay, key_id,
            id_prot, id_loc,
            data=None
        )
        self.TOKEN = config.wawa_token_sbp


class WawaVisa(Wawa):

    def __init__(
        self,
        session,
        config,
        message, user_id,
        price, month_count,
        type_pay, key_id,
        id_prot, id_loc,
        data=None
    ):
        super().__init__(
            session,
            config,
            message, user_id,
            price, month_count,
            type_pay, key_id,
            id_prot, id_loc,
            data=None
        )
        self.TOKEN = config.wawa_token_visa


