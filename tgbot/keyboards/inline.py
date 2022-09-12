import logging
from aiogram import Bot
from aiogram.utils.callback_data import CallbackData
from aiogram.types.inline_keyboard import InlineKeyboardButton, \
    InlineKeyboardMarkup

from web.app.models import Worker

close_button = InlineKeyboardButton(
    text='Close',
    callback_data='close',
)

cancel_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            close_button,
        ]
    ]
)

worker_callback = CallbackData('worker', 'worker_id')
async def page_navigation_for_workers_markup(
    workers: list[Worker], page: int
) -> InlineKeyboardMarkup:
    COLUMN_LENTH = 3
    markup = InlineKeyboardMarkup()
    start = page * COLUMN_LENTH
    end = start + COLUMN_LENTH
    for worker in workers[start:end]:
        markup.add(
            InlineKeyboardButton(
                text=f'{"⛔" if worker.stop else "✅"}{worker.name}',
                callback_data=worker_callback.new(worker_id=worker.id),
            )
        )
    markup = await add_navigation_buttons(
        markup, page, COLUMN_LENTH, len(workers)
        )
    markup.add(close_button)
    return markup
    
worker_navigation_callback = CallbackData('worker_navigation', 'page')
async def add_navigation_buttons(
    markup: InlineKeyboardMarkup, page: int, column_lenth: int, total_items: int
    ) -> InlineKeyboardMarkup:
    if page == 0 and total_items > column_lenth:
        markup.row(
            InlineKeyboardButton(
                text='⠀',
                callback_data='first_page',
            ),
            InlineKeyboardButton(
                text='➡️',
                callback_data=worker_navigation_callback.new(page=page+1),
            )
        )
    elif page == 0:
        pass
    elif page == total_items // column_lenth:
        markup.row(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=worker_navigation_callback.new(page=page-1),
            ),
            InlineKeyboardButton(
                text='⠀',
                callback_data='last_page',
            )
        )
    else:
        markup.row(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=worker_navigation_callback.new(page=page-1),
            ),
            InlineKeyboardButton(
                text='➡️',
                callback_data=worker_navigation_callback.new(page=page+1),
            )
        )
    return markup

manage_worker_action_callback = CallbackData('manage','action', 'worker_id')
async def manage_worker_markup(worker: Worker) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if worker.stop is True:
        markup.add(
            InlineKeyboardMarkup(
                text='Activate worker',
                callback_data=manage_worker_action_callback.new(
                    action='activate', worker_id=worker.id
                )
            )
        )
    else: 
        markup.add(
            InlineKeyboardButton(
                text='Stop worker',
                callback_data=manage_worker_action_callback.new(
                    action='stop', worker_id=worker.id
                )
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='Delete worker',
            callback_data=manage_worker_action_callback.new(
                action='delete', worker_id=worker.id
            )
        )
    )
    markup.add(
        close_button
    )
    return markup
    
async def worker_profile_markup(worker: Worker) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if worker.stop is True:
        markup.add(
            InlineKeyboardButton(
                text='Activate',
                callback_data=manage_worker_action_callback.new(
                    action='activate', worker_id=worker.id
                )
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text='Stop',
                callback_data=manage_worker_action_callback.new(
                    action='stop', worker_id=worker.id
                )
            )
        )
    markup.add(close_button)
    return markup

admin_profile_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Add worker',
                callback_data='add',
            ),
            InlineKeyboardButton(
                text='View/manage workers',
                callback_data='view',
            )
        ],
        [
            close_button
        ]
    ]
)

async def start_work_markup(bot: Bot) -> InlineKeyboardMarkup:
    bot_username = (await bot.me).username
    return InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Start work',
                url='https://t.me/{}?start=0'.format(bot_username),
                
            )
        ]
    ]
)

async def pipedrive_deal_markup(
    deal_id: int,
    pipedrive_domain: str
    ) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='View deal',
                    url='https://{}.pipedrive.com/deal/{}'.format(
                        pipedrive_domain, deal_id
                    )
                )
            ]
        ]
    )