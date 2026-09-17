# bot.py — aiogram 3.x | bad team
import asyncio
import json
import random
import string
import os
import re
import html
import aiosqlite
import aiohttp
from aiohttp import web
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, ChatPermissions
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties

# ── Конфигурация ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN is not set. Add it in Render → Environment.')
OWNERS = [8794223703]
TEAM_NAME = 'bad team'
TEAM_OWNER_USERNAME = '@bad_rip'
TEAM_CHAT_ID = -1004315886112
TEAM_TOP_TOPIC_ID = 2
TEAM_PAYOUT_TOPIC_ID = 7
TEAM_LINK = 'https://t.me/bad_team_ton'
# ── Наставники / Вбиверы ─────────────────────────────

MENTORS = {
    "@Balduin5": {
        "role": "mentor",
        "percent": 0.15
    }
}

SPECIALISTS = {
    "@bad_rip": {
        "role": "specialist",
        "percent": 0.20
    }
}
# Render persistent disk is mounted at /var/data in render.yaml.
# Locally, fall back to the project directory.
DATA_DIR = os.getenv('DATA_DIR', '/var/data' if os.path.isdir('/var/data') else os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, 'bot_database.db')
PAYOUT_CHAT_ID = -1004389232815
PAYOUT_TOPIC_ID = 9
PAYOUT_PERCENTAGE = 0.7 
CHANNEL_USERNAME = 'bad_team_ton'
VIDEO_URL = 'https://github.com/luvysex/video/raw/refs/heads/main/pay.mp4' 
WORK_TYPES = {
    'soon':  {'name': 'soon', 'default_percent': 0.6},
    'otc':      {'name': 'ОТС',     'default_percent': 0.7},
    'soon': {'name': 'soon','default_percent': 0.7},
    'guarantor':{'name': 'Гарант',  'default_percent': 0.7},
}

# ── Премиум-эмодзи ────────────────────────────────────────────────────────────
def e(emoji_id: int, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

E = {
    'ok':       e(5895514131896733546, '✅'),
    'no':       e(5893163582194978381, '❌'),
    'no2':      e(5893081007153746175, '❌'),
    'clock':    e(5893102202817352158, '🕞'),
    'alarm':    e(5902050947567194830, '⏰'),
    'bolt':     e(5893450623449305489, '⚡️'),
    'gear':     e(5893161718179173515, '⚙️'),
    'gear2':    e(5902432207519093015, '⚙️'),
    'warn':     e(5904692292324692386, '⚠️'),
    'stop':     e(5960671702059848143, '⛔️'),
    'user':     e(5902335789798265487, '👤'),
    'link':     e(5902449142575141204, '🔗'),
    'rocket':   e(5195033767969839232, '🚀'),
    'star':     e(5924870095925942277, '⭐️'),
    'rocket2':  e(5258332798409783582, '🚀'),
    'n1':       e(5794164805065514131, '1⃣'),
    'n2':       e(5794085322400733645, '2⃣'),
    'n3':       e(5794280000383358988, '3⃣'),
    'n4':       e(5794241397217304511, '4⃣'),
    'n5':       e(5793985348446984682, '5⃣'),
    'n6':       e(5794324702402976226, '6⃣'),
    'n7':       e(5793942849745591465, '7⃣'),
    'n8':       e(5793926687783655907, '8⃣'),
    'n9':       e(5793979472931723221, '9⃣'),
    'gift':     e(6037175527846975726, '🎁'),
    'user2':    e(5904630315946611415, '👤'),
    'user3':    e(6032693626394382504, '👤'),
    # старые
    'warn_old': e(5447644880824181073, '⚠️'),
    'stop2':    e(5240241223632954241, '🚫'),
    'check':    e(5206607081334906820, '✅'),
    'xmark':    e(5210952531676504517, '❌'),
    'money':    e(5224257782013769471, '💰'),
    'chart':    e(5231200819986047254, '📊'),
    'cash':     e(5201691993775818138, '💸'),
    'hourglass':e(5451646226975955576, '⌛️'),
    'sparkle':  e(5325547803936572038, '✨'),
    'party':    e(5461151367559141950, '🎉'),
    'sad':      e(5386856460632201117, '😢'),
    'trophy':   e(5409008750893734809, '🏆'),
    'gold':     e(5440539497383087970, '🥇'),
    'silver':   e(5447203607294265305, '🥈'),
    'bronze':   e(5453902265922376865, '🥉'),
    'info':     e(5334544901428229844, 'ℹ️'),
    'crown':    e(5217822164362739968, '👑'),
    'bolt2':    e(5456140674028019486, '⚡️'),
    'phone':    e(5363858422590619939, '📱'),
    'cal':      e(5274055917766202507, '🗓'),
    'down':     e(5301038027601098171, '👇'),
    'mail':     e(5253742260054409879, '✉️'),
    'write':    e(5197269100878907942, '✍️'),
    'pencil':   e(5956143844457189176, '✏️'),
    'arrow':    e(6037622221625626773, '➡️'),
    'search':   e(5188217332748527444, '🔍'),
    'refresh':  e(6030657343744644592, '🔁'),
    'hat':      e(5895605369887004463, '🎩'),
    'diamond':  e(5776023601941582822, '💎'),
    'users':    e(6032609071373226027, '👥'),
    'chartup':  e(5244837092042750681, '📈'),
    'chartdn':  e(5246762912428603768, '📉'),
    'question': e(5436113877181941026, '❓'),
    'hi':       e(6041921818896372382, '👋'),
    'ban':      e(5960671702059848143, '⛔️'),
}

# ── FSM ───────────────────────────────────────────────────────────────────────
class Survey(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

class Payout(StatesGroup):
    deal_code  = State()
    media      = State()
    gift_link  = State()
    ton_addr   = State()

class SpecialistSurvey(StatesGroup):
    goy_username = State()
    screenshots = State()
    method = State()

class AdminAction(StatesGroup):
    waiting_profit_add    = State()
    waiting_profit_remove = State()
    waiting_percent       = State()
    waiting_global_pct    = State()
    waiting_amount_approve= State()
    waiting_reject_reason = State()
    search_user           = State()
    add_admin             = State()
    remove_admin          = State()
    search_payout_code    = State()
    waiting_mirror_token  = State()
    # OTS management
    waiting_ots_token     = State()
    waiting_ots_setting   = State()
    waiting_ots_banner    = State()
    waiting_ots_owner_ids = State()

# ── OTS конфигурация ──────────────────────────────────────────────────────────
import shutil
import signal
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OTS_INSTANCES_DIR = os.path.join(DATA_DIR, 'ots_instances')
# The template MUST be committed to the repository as ./отс/
OTS_SOURCE_DIR = os.path.join(PROJECT_DIR, 'отс')
if not os.path.isdir(OTS_SOURCE_DIR):
    # Also accept an ASCII folder name for Git/CI environments.
    alt = os.path.join(PROJECT_DIR, 'ots')
    if os.path.isdir(alt):
        OTS_SOURCE_DIR = alt
# Живые процессы: ots_id -> subprocess.Popen
ots_processes: dict[int, subprocess.Popen] = {}

# ── Инициализация ─────────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp  = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ── Модерация и команды командного чата ────────────────────────────────────────
def _is_team_chat(msg: Message) -> bool:
    return msg.chat.id == TEAM_CHAT_ID

def _is_team_top(msg: Message) -> bool:
    return _is_team_chat(msg) and msg.message_thread_id == TEAM_TOP_TOPIC_ID

def _duration_seconds(value: str) -> int | None:
    m = re.fullmatch(r'(\d+)(s|m|h|d|w)', value.lower())
    if not m:
        return None
    n = int(m.group(1))
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    seconds = n * units[m.group(2)]
    return seconds if 1 <= seconds <= 30 * 86400 else None

async def _reply_target_user(msg: Message):
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user
    return None

def _user_mention(user) -> str:
    name = html.escape(user.full_name or user.username or str(user.id))
    return f'<a href="tg://user?id={user.id}">{name}</a>'

@router.message(Command('mute'), F.chat.id == TEAM_CHAT_ID)
async def team_mute(msg: Message):
    if not await is_admin(msg.from_user.id):
        return
    target = await _reply_target_user(msg)
    if not target:
        await msg.reply('Использование: ответь на сообщение пользователя: /mute 1m')
        return
    parts = (msg.text or '').split()
    if len(parts) != 2:
        await msg.reply('Использование: /mute 1m (s/m/h/d/w)')
        return
    seconds = _duration_seconds(parts[1])
    if seconds is None:
        await msg.reply('Неверное время. Пример: /mute 1m')
        return
    from datetime import timedelta, timezone
    until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    try:
        await bot.restrict_chat_member(
            TEAM_CHAT_ID, target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        await msg.reply(f'🔇 {_user_mention(target)} получил мут на {parts[1]}.')
    except Exception as ex:
        await msg.reply(f'❌ Не удалось выдать мут: <code>{html.escape(str(ex))}</code>')

@router.message(Command('unmute'), F.chat.id == TEAM_CHAT_ID)
async def team_unmute(msg: Message):
    if not await is_admin(msg.from_user.id):
        return
    target = await _reply_target_user(msg)
    if not target:
        await msg.reply('Ответь на сообщение пользователя командой /unmute.')
        return
    try:
        await bot.restrict_chat_member(
            TEAM_CHAT_ID, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await msg.reply(f'🔊 {_user_mention(target)} размучен.')
    except Exception as ex:
        await msg.reply(f'❌ Не удалось снять мут: <code>{html.escape(str(ex))}</code>')

@router.message(Command('ban'), F.chat.id == TEAM_CHAT_ID)
async def team_ban(msg: Message):
    if not await is_admin(msg.from_user.id):
        return
    target = await _reply_target_user(msg)
    if not target:
        await msg.reply('Ответь на сообщение пользователя командой /ban.')
        return
    try:
        await bot.ban_chat_member(TEAM_CHAT_ID, target.id)
        if target.id not in OWNERS:
            async with db_connect() as conn:
                await conn.execute(
                    'UPDATE users SET approved=0 WHERE user_id=?',
                    (target.id,)
                )
                await conn.commit()
        await msg.reply(f'⛔️ {_user_mention(target)} заблокирован в чате.')
    except Exception as ex:
        await msg.reply(f'❌ Не удалось заблокировать: <code>{html.escape(str(ex))}</code>')

@router.message(Command('my'), F.chat.id == TEAM_CHAT_ID)
async def team_my(msg: Message):
    if not await is_admin(msg.from_user.id):
        return
    target = await _reply_target_user(msg)
    if target is None:
        target = msg.from_user
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT user_id,nickname,username,role,total_profits,join_date '
            'FROM users WHERE user_id=?', (target.id,)
        ) as c:
            row = await c.fetchone()
    if not row:
        await msg.reply('Профиль пользователя ещё не найден в базе.')
        return
    uid, nickname, username, role, profits, join_date = row
    await msg.reply(format_profile(
        uid,
        html.escape(nickname or target.full_name or '—'),
        html.escape(username or target.username or str(uid)),
        role,
        profits or 0,
        join_date
    ))

@router.message(Command('cal'), F.chat.id == TEAM_CHAT_ID)
async def team_cal(msg: Message):
    if not await is_admin(msg.from_user.id):
        return
    parts = (msg.text or '').split(maxsplit=1)
    text = parts[1].strip() if len(parts) > 1 else ''
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT user_id, nickname, username FROM users '
            'WHERE approved=1 ORDER BY nickname'
        ) as c:
            rows = await c.fetchall()
    mentions = []
    for uid, nickname, username in rows:
        label = nickname or (f'@{username}' if username else str(uid))
        mentions.append(f'<a href="tg://user?id={uid}">{html.escape(label)}</a>')
    if not mentions:
        await msg.reply('В базе пока нет участников для упоминания.')
        return
    prefix = html.escape(text) + '\n\n' if text else ''
    chunks, current = [], prefix
    for mention in mentions:
        if len(current) + len(mention) + 1 > 3800:
            chunks.append(current)
            current = mention
        else:
            current += (' ' if current else '') + mention
    if current:
        chunks.append(current)
    for chunk in chunks:
        await msg.answer(chunk)

@router.message(F.chat.id == TEAM_CHAT_ID, F.new_chat_members)
async def team_welcome(msg: Message):
    for user in msg.new_chat_members:
        await msg.answer(
            f'👋 Добро пожаловать, {_user_mention(user)}!\n\n'
            'Прежде, чем приступить к работе, пожалуйста, ознакомьтесь '
            'с правилами и мануалами. Желаем удачи! 🍀.'
        )

def _blocked_team_command(msg: Message) -> bool:
    if not msg.text:
        return False
    command = msg.text.split()[0].split('@')[0].lower()
    if command == '/top' and _is_team_top(msg):
        return False
    if command in {'/mute', '/unmute', '/ban', '/my', '/cal'}:
        return False
    return True

@router.message(F.chat.id == TEAM_CHAT_ID, F.text.startswith('/'), _blocked_team_command)
async def ignore_team_commands(msg: Message):
    return


# Временное хранилище данных выплат и контекста одобрения
payout_temp: dict = {}       # user_id -> dict с данными выплаты
worker_mentor = {}
worker_specialist = {}
specialist_forms = {}
approve_ctx: dict = {}       # admin_id -> dict с данными для одобрения
reject_ctx: dict  = {}       # admin_id -> dict с данными для отклонения
payout_media_store: dict = {}  # payout_id -> list of (type, file_id)

# Хранилище зеркал: token -> {bot, task, username}
mirrors: dict = {}

# ── БД: пул соединений через контекстный менеджер ────────────────────────────
_db_lock = asyncio.Lock()

async def get_db() -> aiosqlite.Connection:
    """Создаёт новое соединение с БД для использования в async with."""
    conn = await aiosqlite.connect(DB_NAME)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    await conn.execute("PRAGMA busy_timeout=10000")
    return conn

class _db_ctx:
    """Контекстный менеджер: открывает соединение, фиксирует lock, закрывает."""
    def __init__(self, autocommit=False):
        self._autocommit = autocommit
        self._conn = None

    async def __aenter__(self) -> aiosqlite.Connection:
        self._conn = await get_db()
        return self._conn

    async def __aexit__(self, exc_type, exc, tb):
        if self._conn:
            try:
                if exc_type is None and self._autocommit:
                    await self._conn.commit()
            finally:
                await self._conn.close()
                self._conn = None

def db_connect():
    return _db_ctx()

# ── БД ───────────────────────────────────────────────────────────────────────
async def init_db():
    async with db_connect() as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, nickname TEXT,
            role TEXT DEFAULT 'worker', total_profits REAL DEFAULT 0,
            join_date TEXT, approved INTEGER DEFAULT 0,
            profile_gender TEXT DEFAULT '', profile_avatar_category TEXT DEFAULT '',
            profile_avatar_quality TEXT DEFAULT '', profile_filter_notes TEXT DEFAULT '')''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS payouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            payout_code TEXT, work_type TEXT, deal_code TEXT,
            gift_link TEXT, ton_address TEXT,
            status TEXT DEFAULT 'pending', created_at TEXT,
            profit_amount REAL DEFAULT 0, user_percentage REAL,
            mentor_username TEXT DEFAULT '', mentor_percent REAL DEFAULT 0,
            specialist_username TEXT DEFAULT '', specialist_percent REAL DEFAULT 0
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS surveys (
            user_id INTEGER PRIMARY KEY, answer1 TEXT, answer2 TEXT,
            answer3 TEXT, status TEXT DEFAULT 'pending')''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS work_types (
            work_type TEXT PRIMARY KEY, name TEXT,
            default_percent REAL, enabled INTEGER DEFAULT 1)''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS user_work_percentages (
            user_id INTEGER, work_type TEXT, percentage REAL,
            PRIMARY KEY (user_id, work_type))''')
        try:
            await conn.execute('ALTER TABLE work_types ADD COLUMN enabled INTEGER DEFAULT 1')
        except Exception:
            pass
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN profile_gender TEXT DEFAULT ""')
        except Exception:
            pass
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN profile_avatar_category TEXT DEFAULT ""')
        except Exception:
            pass
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN profile_avatar_quality TEXT DEFAULT ""')
        except Exception:
            pass
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN profile_filter_notes TEXT DEFAULT ""')
        except Exception:
            pass
        await conn.execute('''CREATE TABLE IF NOT EXISTS payout_media (
            payout_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            file_id TEXT NOT NULL
        )''')
        try:
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_pm_payout ON payout_media(payout_id)')
        except Exception:
            pass
        # OTS instances table
        await conn.execute('''CREATE TABLE IF NOT EXISTS ots_instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_token TEXT NOT NULL UNIQUE,
            bot_username TEXT DEFAULT '',
            bot_fullname TEXT DEFAULT '',
            service_name TEXT DEFAULT '',
            manager_username TEXT DEFAULT 'otc_help',
            manager_ton_wallet TEXT DEFAULT '',
            manager_card TEXT DEFAULT '',
            manager_usdt_wallet TEXT DEFAULT '',
            manager_btc_wallet TEXT DEFAULT '',
            notification_channel TEXT DEFAULT '',
            gift_recipient TEXT DEFAULT '',
            min_deals_withdraw INTEGER DEFAULT 3,
            log_channel TEXT DEFAULT '',
            log_topic_id TEXT DEFAULT '',
            owner_ids TEXT DEFAULT '',
            instance_dir TEXT DEFAULT '',
            status TEXT DEFAULT 'stopped',
            created_at TEXT DEFAULT '',
            creator_id INTEGER DEFAULT 0
        )''')
        try:
            await conn.execute('ALTER TABLE ots_instances ADD COLUMN creator_id INTEGER DEFAULT 0')
        except Exception:
            pass
        for wt, data in WORK_TYPES.items():
            await conn.execute(
                'INSERT OR IGNORE INTO work_types (work_type, name, default_percent, enabled) VALUES (?,?,?,1)',
                (wt, data['name'], data['default_percent']))
        await conn.commit()

async def check_and_fix_database():
    print(f"{E['search']} Проверяю структуру базы данных...")
    async with db_connect() as conn:
        async with conn.execute("PRAGMA table_info(payouts)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        required_columns = {
            'payout_code': 'TEXT', 'work_type': 'TEXT', 'deal_code': 'TEXT',
            'gift_link': 'TEXT', 'ton_address': 'TEXT',
            'status': 'TEXT DEFAULT "pending"', 'created_at': 'TEXT',
            'profit_amount': 'REAL DEFAULT 0', 'user_percentage': 'REAL',
            'mentor_username': 'TEXT DEFAULT ""',
            'mentor_percent': 'REAL DEFAULT 0',
            'specialist_username': 'TEXT DEFAULT ""',
            'specialist_percent': 'REAL DEFAULT 0'
        }
        missing = {c: t for c, t in required_columns.items() if c not in columns}
        if not missing:
            try:
                await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_payout_code ON payouts(payout_code)')
            except Exception:
                await fix_payouts_table_with_data(conn, columns, required_columns)
            await conn.commit()
            return
        if 'payout_code' in missing:
            await fix_payouts_table_with_data(conn, columns, required_columns)
        else:
            for col, col_type in missing.items():
                try:
                    await conn.execute(f"ALTER TABLE payouts ADD COLUMN {col} {col_type}")
                except Exception as e:
                    print(f"❌ Ошибка при добавлении {col}: {e}")
        try:
            await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_payout_code ON payouts(payout_code)')
        except Exception:
            pass
        await conn.commit()

async def fix_payouts_table_with_data(db, existing_columns, required_columns):
    await db.execute('DROP TABLE IF EXISTS payouts_temp')
    await db.execute('''
        CREATE TABLE payouts_temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, payout_code TEXT, work_type TEXT, deal_code TEXT,
            gift_link TEXT, ton_address TEXT,
            status TEXT DEFAULT 'pending', created_at TEXT,
            profit_amount REAL DEFAULT 0, user_percentage REAL,
            mentor_username TEXT DEFAULT '', mentor_percent REAL DEFAULT 0,
            specialist_username TEXT DEFAULT '', specialist_percent REAL DEFAULT 0
        )
    ''')
    existing_cols_in_old = [c for c in [
        'id','user_id','work_type','deal_code',
        'gift_link','ton_address','status','created_at','profit_amount',
        'user_percentage','mentor_username','mentor_percent',
        'specialist_username','specialist_percent'
    ] if c in existing_columns] or ['id', 'user_id']
    async with db.execute(f"SELECT {', '.join(existing_cols_in_old)} FROM payouts") as cursor:
        old_data = await cursor.fetchall()
    for row in old_data:
        data_dict = dict(zip(existing_cols_in_old, row))
        while True:
            code = '#' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            async with db.execute("SELECT COUNT(*) FROM payouts_temp WHERE payout_code = ?", (code,)) as c:
                if (await c.fetchone())[0] == 0:
                    break
        all_cols = [
            'user_id','payout_code','work_type','deal_code',
            'gift_link','ton_address','status','created_at',
            'profit_amount','user_percentage','mentor_username',
            'mentor_percent','specialist_username','specialist_percent'
        ]
        values = []
        for col in all_cols:
            if col == 'payout_code':
                values.append(code)
            elif col in data_dict:
                values.append(data_dict[col])
            else:
                values.append({
                    'work_type':'drainer',
                    'status':'pending',
                    'profit_amount':0.0,
                    'user_percentage':PAYOUT_PERCENTAGE,
                    'mentor_username':'',
                    'mentor_percent':0,
                    'specialist_username':'',
                    'specialist_percent':0
                }.get(col))
        await db.execute(f"INSERT INTO payouts_temp ({', '.join(all_cols)}) VALUES ({', '.join(['?']*len(all_cols))})", values)
    await db.execute('DROP TABLE payouts')
    await db.execute('ALTER TABLE payouts_temp RENAME TO payouts')

# ── DB-утилиты ────────────────────────────────────────────────────────────────
async def db_get_user(user_id: int):
    async with db_connect() as conn:
        async with conn.execute('SELECT * FROM users WHERE user_id=?', (user_id,)) as c:
            return await c.fetchone()

async def db_upsert_user(user_id, username, nickname):
    async with db_connect() as conn:
        await conn.execute(
            'INSERT OR IGNORE INTO users (user_id,username,nickname,role,join_date,approved) VALUES (?,?,?,"worker",?,0)',
            (user_id, username, nickname, datetime.now().strftime('%Y-%m-%d')))
        await conn.execute(
            'UPDATE users SET username=COALESCE(?,username), nickname=COALESCE(?,nickname) WHERE user_id=?',
            (username, nickname, user_id))
        await conn.commit()

async def get_approved(user_id: int):
    async with db_connect() as conn:
        async with conn.execute('SELECT approved FROM users WHERE user_id=?', (user_id,)) as c:
            row = await c.fetchone()
            return row[0] if row else None

async def is_admin(user_id: int) -> bool:
    if user_id in OWNERS: return True
    async with db_connect() as conn:
        async with conn.execute('SELECT role FROM users WHERE user_id=? AND approved=1', (user_id,)) as c:
            row = await c.fetchone()
            return bool(row and row[0] == 'admin')

async def get_admins():
    admins = list(OWNERS)
    async with db_connect() as conn:
        async with conn.execute('SELECT user_id FROM users WHERE role="admin" AND approved=1') as c:
            rows = await c.fetchall()
    for row in rows:
        admins.append(row[0])
    return list(set(admins))

async def has_pending_survey(user_id: int) -> bool:
    async with db_connect() as conn:
        async with conn.execute('SELECT status FROM surveys WHERE user_id=?', (user_id,)) as c:
            row = await c.fetchone()
            return bool(row and row[0] == 'pending')

async def update_profile_filter_notes(user_id: int, gender: str, avatar_category: str, avatar_quality: str, notes: str):
    try:
        async with db_connect() as conn:
            await conn.execute(
                'UPDATE users SET profile_gender=COALESCE(?, profile_gender), profile_avatar_category=COALESCE(?, profile_avatar_category), profile_avatar_quality=COALESCE(?, profile_avatar_quality), profile_filter_notes=COALESCE(?, profile_filter_notes) WHERE user_id=?',
                (gender, avatar_category, avatar_quality, notes, user_id))
            await conn.commit()
    except Exception:
        pass

def _normalize_text(*parts: str) -> str:
    return ' '.join(str(p).strip().lower() for p in parts if p).replace('\n', ' ')

def _guess_gender(full_name: str, username: str, bio: str) -> str:
    text = _normalize_text(full_name, username, bio)
    female_keywords = ['девушка', 'девушка', 'женщина', 'girl', 'female', 'girl_', 'girl', 'секс', 'милая', 'милая', 'леди', 'женский']
    male_keywords = ['парень', 'мужчина', 'boy', 'man', 'guy', 'mr', 'king', 'супермен', 'дядя', 'мужской']
    if any(word in text for word in female_keywords):
        return 'female'
    if any(word in text for word in male_keywords):
        return 'male'
    if full_name:
        first_name = full_name.split()[0]
        if re.search(r'[ая]$', first_name, re.IGNORECASE):
            return 'female'
        if re.search(r'(ов|ев|ёв|ин|ский|цкий|ый|ий)$', first_name, re.IGNORECASE):
            return 'male'
    return 'unknown'

def _guess_nft_or_brand_profile(full_name: str, username: str, bio: str) -> bool:
    text = _normalize_text(full_name, username, bio)
    nft_keywords = ['nft', 'opensea', 'collection', 'crypto', 'wallet', 'token', 'mint', 'floor', 'airdrop', 'metamask', 'rarible', 'looksrare']
    return any(word in text for word in nft_keywords)

def _guess_closed_or_paid_messages(full_name: str, username: str, bio: str) -> bool:
    text = _normalize_text(full_name, username, bio)
    keywords = ['платно', 'paid', 'donat', 'донат', 'только подписчики', 'закрыт', 'closed', 'only subscribers', 'за подписку', 'за донат', 'pay to write', 'платные сообщения', 'платные мессаджи']
    return any(word in text for word in keywords)

def _guess_low_activity(full_name: str, username: str, bio: str) -> bool:
    text = _normalize_text(full_name, username, bio)
    if not username or username.startswith('user') or re.fullmatch(r'\d{5,}', username):
        return True
    if len(bio) < 15 and len(full_name) < 5:
        return True
    return False

def _guess_avatar_category(bio: str) -> str:
    text = _normalize_text(bio)
    if any(word in text for word in ['anime', 'аниме', 'арт', 'рисунок', 'иллюстрация', 'cartoon', 'мульт', 'pixel', 'manga']):
        return 'anime / art / cartoon'
    if any(word in text for word in ['лицо', 'без лица', 'скрыто', 'маска']):
        return 'face absent / hidden'
    return 'real photo / unknown'

async def analyze_profile(user_id: int, username: str, full_name: str) -> dict:
    bio = ''
    avatar_category = ''
    avatar_quality = 'unknown'
    gender = 'unknown'
    reasons = []
    auto_reject = False

    try:
        chat = await bot.get_chat(user_id)
        bio = getattr(chat, 'bio', '') or ''
    except Exception:
        bio = ''

    gender = _guess_gender(full_name, username, bio)
    avatar_category = _guess_avatar_category(bio)

    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos and photos.total_count:
            best = photos.photos[0][-1] if photos.photos and photos.photos[0] else None
            if best is not None:
                width = getattr(best, 'width', 0)
                height = getattr(best, 'height', 0)
                size = getattr(best, 'file_size', 0)
                if size and size >= 50000 and width >= 300 and height >= 300:
                    avatar_quality = 'high'
                else:
                    avatar_quality = 'low'
        else:
            avatar_quality = 'missing'
    except Exception:
        avatar_quality = 'unknown'

    if not username or username == 'без_username':
        reasons.append('Отсутствует username')
        auto_reject = True
    if avatar_quality == 'missing':
        reasons.append('Отсутствует аватарка')
        auto_reject = True
    if gender == 'male':
        reasons.append('Профиль похоже мужской')
        auto_reject = True
    if _guess_nft_or_brand_profile(full_name, username, bio):
        reasons.append('Профиль похож на NFT / брендовый / коммерческий аккаунт')
        auto_reject = True
    if _guess_closed_or_paid_messages(full_name, username, bio):
        reasons.append('Закрытые или платные сообщения')
        auto_reject = True
    if _guess_low_activity(full_name, username, bio):
        reasons.append('Низкая активность или профиль выглядит ботом')
        auto_reject = True

    if gender == 'unknown':
        reasons.append('Не удалось однозначно определить гендер профиля')

    summary = [f'Пол: {gender}', f'Аватар: {avatar_category}', f'Качество: {avatar_quality}']
    if reasons:
        summary.append('Проблемы: ' + '; '.join(reasons))
    else:
        summary.append('Проверка прошла без явных замечаний')

    await update_profile_filter_notes(user_id, gender, avatar_category, avatar_quality, '; '.join(reasons))
    return {
        'gender': gender,
        'avatar_category': avatar_category,
        'avatar_quality': avatar_quality,
        'reasons': reasons,
        'auto_reject': auto_reject,
        'summary': '\n'.join(summary)
    }

async def get_user_percentage(user_id: int, work_type: str) -> float:
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT percentage FROM user_work_percentages WHERE user_id=? AND work_type=?',
            (user_id, work_type)) as c:
            row = await c.fetchone()
            if row: return row[0]
        async with conn.execute('SELECT default_percent FROM work_types WHERE work_type=?', (work_type,)) as c:
            row = await c.fetchone()
            return row[0] if row and row[0] is not None else WORK_TYPES.get(work_type, {}).get('default_percent', PAYOUT_PERCENTAGE)

async def get_work_type_percentage(work_type: str) -> float:
    async with db_connect() as conn:
        async with conn.execute('SELECT default_percent FROM work_types WHERE work_type=?', (work_type,)) as c:
            row = await c.fetchone()
            return row[0] if row and row[0] is not None else WORK_TYPES.get(work_type, {}).get('default_percent', PAYOUT_PERCENTAGE)

async def set_user_percentage(user_id: int, work_type: str, pct: float):
    async with db_connect() as conn:
        await conn.execute(
            'INSERT OR REPLACE INTO user_work_percentages (user_id,work_type,percentage) VALUES (?,?,?)',
            (user_id, work_type, pct))
        await conn.commit()

async def set_work_type_percentage(work_type: str, pct: float):
    async with db_connect() as conn:
        await conn.execute('UPDATE work_types SET default_percent=? WHERE work_type=?', (pct, work_type))
        await conn.commit()

async def get_all_work_types():
    async with db_connect() as conn:
        async with conn.execute('SELECT work_type, name, default_percent, enabled FROM work_types') as c:
            rows = await c.fetchall()
    result = []
    for wt, name, pct, enabled in rows:
        if pct is None: pct = WORK_TYPES.get(wt, {}).get('default_percent', PAYOUT_PERCENTAGE)
        result.append({'type': wt, 'name': name, 'percent': pct, 'enabled': bool(enabled)})
    return result

async def get_enabled_work_types():
    return [w for w in await get_all_work_types() if w['enabled']]

async def toggle_work_type(work_type: str) -> bool:
    async with db_connect() as conn:
        async with conn.execute('SELECT enabled FROM work_types WHERE work_type=?', (work_type,)) as c:
            row = await c.fetchone()
        new_val = 0 if (row and row[0]) else 1
        await conn.execute('UPDATE work_types SET enabled=? WHERE work_type=?', (new_val, work_type))
        await conn.commit()
    return bool(new_val)

async def find_user(query: str):
    q = query.strip().lstrip('@')
    async with db_connect() as conn:
        if q.lstrip('-').isdigit():
            async with conn.execute(
                'SELECT user_id,nickname,username,role,total_profits,join_date,approved FROM users WHERE user_id=?',
                (int(q),)) as c:
                return await c.fetchone()
        else:
            async with conn.execute(
                'SELECT user_id,nickname,username,role,total_profits,join_date,approved FROM users WHERE username=?',
                (q,)) as c:
                return await c.fetchone()

def generate_payout_code():
    return '#' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def is_valid_nft_link(link: str) -> bool:
    if not link: return False
    link = link.lower().strip()
    for pat in [r'^https://t\.me/nft/', r'^t\.me/nft/', r'^https://telegram\.me/nft/']:
        if re.match(pat, link): return True
    return False

def is_valid_ton(addr: str) -> bool:
    if not addr: return False
    addr = addr.strip()
    return (addr.upper().startswith('UQ') or addr.upper().startswith('EQ')) and \
           bool(re.match(r'^[A-Za-z0-9_-]+$', addr))

async def check_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(f'@{CHANNEL_USERNAME}', user_id)
        return member.status not in ('left', 'kicked')
    except Exception:
        return False

async def download_video() -> str | None:
    path = 'pay_video.mp4'
    if os.path.exists(path): return path
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(VIDEO_URL) as r:
                if r.status == 200:
                    with open(path, 'wb') as f:
                        async for chunk in r.content.iter_chunked(8192):
                            f.write(chunk)
                    return path
    except Exception:
        return None

# ── Клавиатуры ───────────────────────────────────────────────────────────────
def kb(*rows) -> InlineKeyboardMarkup:
    """Быстрое создание клавиатуры из списков кнопок."""
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

def btn(text: str, callback: str, emoji_id: int = None, style: str = None) -> InlineKeyboardButton:
    extra: dict = {}
    if emoji_id:
        extra['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        extra['style'] = style
    return InlineKeyboardButton.model_construct(
        text=text,
        callback_data=callback,
        **extra
    )

def main_menu(is_admin_user=False) -> InlineKeyboardMarkup:
    rows = [
        [
            btn('Профиль', 'profile', 5879770735999717115),
            btn('Топ', 'top', 5409008750893734809)
        ],

        [
            btn('Выплата', 'payout', 5201691993775818138),
            btn('Инфо', 'info', 5334544901428229844)
        ],

        [
            btn('Наставники', 'mentors_menu', 6032609071373226027),
            btn('Вбиверы', 'specialists_menu', 5893450623449305489)
        ],

        [
            btn('Мои заявки', 'my_payouts_0', 5363858422590619939)
        ],

        [
            btn('⚙️ Мои боты', 'ots_my_list', 5893161718179173515)
        ],

        [
            InlineKeyboardButton.model_construct(
                text='Переходник',
                url=f'https://t.me/{CHANNEL_USERNAME}',
                icon_custom_emoji_id='5424818078833715060'
            )
        ],
    ]
    if is_admin_user:
        rows.insert(2, [btn('Настройки', 'admin_settings', 5893161718179173515)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Наставники ───────────────────────────────────────
@router.callback_query(F.data == 'mentors_menu')
async def mentors_menu(cb: CallbackQuery):

    current = worker_mentor.get(cb.from_user.id)

    text = (
        '<b>🎓 Наставники — опытные воркеры и учителя</b>\n\n'
        'Наставники доведут вас до первого профита за руку. У них есть авторские мануалы, пасты, постоянная помощь и обучение всему, что от вас требуется для большого заработка.\n\n'
    )

    if current:
        text += f'Текущий наставник: <code>@{current}</code>\n\n'

    text += 'Наставник получает процент из вашей доли.'

    await cb.message.edit_text(
        text,
        reply_markup=kb(
            [btn('Я ознакомился', 'mentors_list', 5895514131896733546)],
            [btn('Назад', 'back_main', 5960671702059848143)]
        )
    )

    await cb.answer()

@router.callback_query(F.data == 'mentors_list')
async def mentors_list(cb: CallbackQuery):

    rows = []

    for username, data in MENTORS.items():
        percent = int(data['percent'] * 100)
        rows.append([
            InlineKeyboardButton(
                text=f'@{username} — {percent}%',
                callback_data=f'select_mentor_{username}'
            )
        ])
    rows.append([
        btn('Назад', 'back_main', 5960671702059848143)
    ])

    current = worker_mentor.get(cb.from_user.id)
    text = '<b>🎓 Выберите наставника</b>\n\n'
    if current:
        text += f'Текущий наставник: <code>@{current}</code>\n\n'
    text += 'Наставник получает процент из вашей доли.'

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await cb.answer()

@router.callback_query(F.data.startswith('select_mentor_'))
async def select_mentor(cb: CallbackQuery):

    username = cb.data.replace('select_mentor_', '')

    worker_mentor[cb.from_user.id] = username

    async with db_connect() as conn:
        await conn.execute('UPDATE users SET role="mentor" WHERE username=?', (username,))
        await conn.commit()

    await cb.answer(
        f'Наставник @{username} выбран',
        show_alert=True
    )

    await mentors_menu(cb)

# ── Вбиверы ───────────────────────────────────────
@router.callback_query(F.data == 'specialists_menu')
async def specialists_menu(cb: CallbackQuery):

    current = worker_specialist.get(cb.from_user.id)

    text = (
        '<b>⚡ Вбиверы — профессиональные воркеры</b>\n\n'
        'Вбиверы помогут вам обмануть человека, если у вас это не получается. Для этого необходимо предоставить полную переписку с мамонтом или свой аккаунт в Telegram.\n'
        'Они получают 20% от вашего профита — лучший вариант для новичков, которые не умеют заводить мамонтов и общаться с ними.\n\n'
        'Сначала ознакомьтесь с условиями, а потом выбирайте вбивера.'
    )

    if current:
        text += f'\nТекущий вбивер: <code>@{current}</code>\n'

    await cb.message.edit_text(
        text,
        reply_markup=kb(
            [btn('Я ознакомился', 'specialists_list', 5895514131896733546)],
            [btn('Назад', 'back_main', 5960671702059848143)]
        )
    )

    await cb.answer()

@router.callback_query(F.data == 'specialists_list')
async def specialists_list(cb: CallbackQuery):

    rows = []

    for username, data in SPECIALISTS.items():
        percent = int(data['percent'] * 100)
        rows.append([
            InlineKeyboardButton(
                text=f'@{username} — {percent}%',
                callback_data=f'select_specialist_{username}'
            )
        ])
    rows.append([
        btn('Назад', 'back_main', 5960671702059848143)
    ])

    current = worker_specialist.get(cb.from_user.id)
    text = '<b>⚡ Выберите вбивера</b>\n\n'
    if current:
        text += f'Текущий вбивер: <code>@{current}</code>\n\n'
    text += 'Вбивер помогает догревать клиента.'

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )

    await cb.answer()

@router.callback_query(F.data.startswith('select_specialist_'))
async def select_specialist(cb: CallbackQuery, state: FSMContext):

    username = cb.data.replace('select_specialist_', '')

    await state.update_data(
        selected_specialist=username
    )

    specialist_forms[cb.from_user.id] = {
        "specialist": username,
        "screenshots": []
    }

    await state.set_state(SpecialistSurvey.goy_username)

    await cb.message.edit_text(
        '<b>⚡ Анкета для передачи клиента</b>\n\n'
        '<b>1.</b> Отправьте юз гоя\n\n'
        '<i>Пример:</i> @username'
    )

    await cb.answer()


def back_btn() -> InlineKeyboardMarkup:
    return kb([btn('Назад', 'back_main', 5960671702059848143)])

def sub_check_kb() -> InlineKeyboardMarkup:
    return kb(
        [InlineKeyboardButton.model_construct(text='Перейти в переходник', url=f'https://t.me/{CHANNEL_USERNAME}', icon_custom_emoji_id='5424818078833715060')],
        [btn('Проверить подписку', 'check_sub', 5895514131896733546, 'success')]
    )

def survey_kb(step: int, user_id: int) -> InlineKeyboardMarkup:
    return kb([
        InlineKeyboardButton.model_construct(text='Да', callback_data=f'survey_yes_{step}_{user_id}', icon_custom_emoji_id='5895514131896733546', style='success'),
        InlineKeyboardButton.model_construct(text='Нет', callback_data=f'survey_no_{step}_{user_id}', icon_custom_emoji_id='5893163582194978381', style='danger'),
    ])

def work_type_kb(types: list) -> InlineKeyboardMarkup:
    num_ids = [5794164805065514131, 5794085322400733645, 5794280000383358988,
               5794241397217304511, 5793985348446984682, 5794324702402976226,
               5793942849745591465, 5793926687783655907, 5793979472931723221]
    rows = []
    for i, wt in enumerate(types):
        eid = num_ids[i] if i < len(num_ids) else None
        rows.append([btn(wt['name'], f'work_{wt["type"]}', eid)])
    rows.append([btn('Назад', 'back_main', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def payout_approve_kb(payout_id: int) -> InlineKeyboardMarkup:
    return kb([
        InlineKeyboardButton.model_construct(text='Принять', callback_data=f'approve_payout_{payout_id}', icon_custom_emoji_id='5895514131896733546', style='success'),
        InlineKeyboardButton.model_construct(text='Отклонить', callback_data=f'reject_payout_{payout_id}', icon_custom_emoji_id='5893163582194978381', style='danger'),
    ])

def survey_approve_kb(user_id: int) -> InlineKeyboardMarkup:
    return kb([
        InlineKeyboardButton.model_construct(text='Принять', callback_data=f'approve_survey_{user_id}', icon_custom_emoji_id='5895514131896733546', style='success'),
        InlineKeyboardButton.model_construct(text='Отклонить', callback_data=f'reject_survey_{user_id}', icon_custom_emoji_id='5893163582194978381', style='danger'),
    ])

def media_done_kb(count: int = 0) -> InlineKeyboardMarkup:
    label = f'Готово ({count} фото)' if count else 'Я отправил все фото'
    return kb(
        [InlineKeyboardButton.model_construct(text=label, callback_data='media_done', icon_custom_emoji_id='5895514131896733546', style='success')],
        [InlineKeyboardButton.model_construct(text='Отмена', callback_data='back_main', icon_custom_emoji_id='5893163582194978381', style='danger')],
    )

def admin_settings_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn('Список пользователей', 'user_list_0', 6032609071373226027)],
        [btn('Поиск пользователя', 'search_user_btn', 5188217332748527444)],
        [btn('Поиск по коду выплаты', 'search_payout_code_btn', 5363858422590619939)],
        [btn('Изменить проценты', 'edit_global_percent', 5231200819986047254)],
        [btn('Управление ворками', 'manage_work_types', 5893161718179173515)],
        [btn('Добавить админа', 'add_admin_btn', 5217822164362739968, 'success'),
         btn('Снять админа', 'remove_admin_btn', 5210952531676504517, 'danger')],
        [btn('⚙️ Все боты (овнер)', 'ots_owner_panel', 5893161718179173515)],
        [btn('➕ Добавить зеркало', 'add_mirror', 5217822164362739968, 'success')],
        [btn('🪞 Мои зеркала', 'list_mirrors', 5363858422590619939)],
        [btn('Назад', 'back_main', 5960671702059848143)],
    )

async def require_approved(user_id: int, msg_or_cb) -> bool:
    """
    Проверяет, одобрен ли пользователь.
    Если нет — отправляет соответствующее сообщение и возвращает False.
    """
    approved = await get_approved(user_id)
    if approved == 1 or user_id in OWNERS:
        return True

    text = (
        f'<b>{E["warn"]} Для использования бота необходимо пройти анкету.</b>\n\n'
        f'{E["arrow"]} Напишите /start чтобы начать.'
    )
    if isinstance(msg_or_cb, Message):
        await msg_or_cb.answer(text)
    else:  # CallbackQuery
        await msg_or_cb.answer('⚠️ Сначала пройдите анкету', show_alert=True)
        try:
            await msg_or_cb.message.answer(text)
        except Exception:
            pass
    return False

def format_profile(user_id, nickname, username, role, profits, join_date) -> str:
    days = 0
    if join_date:
        try: days = (datetime.now() - datetime.strptime(join_date, '%Y-%m-%d')).days
        except: pass
    if role == 'admin':
        role_e = E['crown']
        role_t = 'Администратор'
    elif role == 'mentor':
        role_e = E['star']
        role_t = 'Наставник'
    elif role == 'specialist':
        role_e = E['bolt']
        role_t = 'Вбивер'
    else:
        role_e = E['bolt2']
        role_t = 'Воркер'
    return (
        f'<b>{E["user3"]} {nickname}</b> (@{username})\n\n'
        f'<blockquote>'
        f'<b>{E["phone"]} ID:</b> <code>{user_id}</code>\n'
        f'<b>Роль:</b> {role_e} {role_t}\n'
        f'<b>{E["money"]} Профит:</b> <code>{profits:.2f} TON</code>\n'
        f'<b>{E["cal"]} Дней в команде:</b> {days}\n'
        f'<b>{E["cal"]} Дата вступления:</b> {join_date or "—"}'
        f'</blockquote>'
    )
# ── /start ────────────────────────────────────────────────────────────────────

@router.message(Command('cancel'))
async def cmd_cancel(msg: Message, state: FSMContext):
    """Отмена текущего действия (ввод суммы, причина отклонения и т.д.)"""
    admin_id = msg.from_user.id
    current = await state.get_state()
    if current is None:
        await msg.answer(f'<b>{E["info"]} Нет активного действия для отмены.</b>')
        return
    # Чистим approve_ctx если был в процессе одобрения
    if admin_id in approve_ctx:
        ctx = approve_ctx.pop(admin_id)
        prompt_id = ctx.get('prompt_msg_id')
        if prompt_id:
            try: await bot.delete_message(admin_id, prompt_id)
            except: pass
    # Чистим reject_ctx если был в процессе отклонения
    if admin_id in reject_ctx:
        ctx = reject_ctx.pop(admin_id)
        prompt_id = ctx.get('prompt_msg_id')
        if prompt_id:
            try: await bot.delete_message(admin_id, prompt_id)
            except: pass
    await state.clear()
    is_adm = await is_admin(admin_id)
    await msg.answer(
        f'<b>{E["ok"]} Действие отменено.</b>',
        reply_markup=main_menu(is_adm))

@router.message(Command('start'))
async def cmd_start(msg: Message, state: FSMContext):
    user_id  = msg.from_user.id
    username = msg.from_user.username or 'без_username'
    name     = msg.from_user.full_name or 'Без имени'
    await db_upsert_user(user_id, username, name)
    await state.clear()

    in_channel = await check_subscribed(user_id)
    if not in_channel:
        await msg.answer(
            f'<b>{E["stop2"]} Для использования бота нужна подписка на переходник.</b>',
            reply_markup=sub_check_kb())
        return

    approved = await get_approved(user_id)
    is_adm   = await is_admin(user_id)

    if approved is None:
        await state.set_state(Survey.q1)
        await state.update_data(in_chat=msg.chat.type != 'private')
        await msg.answer(
            f'<b>{E["hi"]} @{username}, привет!</b>\n'
            f'Перед началом ответь на 3 коротких вопроса.\n\n'
            f'<b>{E["question"]} Знаете ли вы, что такое ворк?</b>',
            reply_markup=survey_kb(1, user_id))
        return

    if approved == 0:
        if await has_pending_survey(user_id):
            await msg.answer(f'<b>{E["hourglass"]} Ваша анкета на рассмотрении.</b>\nОжидайте решения администратора.')
            return
        await state.set_state(Survey.q1)
        await msg.answer(
            f'<b>{E["hi"]} Нужно пройти анкету.</b>\n\n'
            f'<b>{E["question"]} Знаете ли вы, что такое ворк?</b>',
            reply_markup=survey_kb(1, user_id))
        return

    await msg.answer(
        f'<b>{E["sparkle"]} Добро пожаловать в bad team!</b>\n\n'
        f'{E["user3"]} <b>{name}</b>, рады видеть вас! {E["down"]}',
        reply_markup=main_menu(is_adm))

# ── check_sub ─────────────────────────────────────────────────────────────────
@router.callback_query(F.data == 'check_sub')
async def cb_check_sub(cb: CallbackQuery, state: FSMContext):
    user_id  = cb.from_user.id
    username = cb.from_user.username or 'без_username'
    name     = cb.from_user.full_name or 'Без имени'
    await db_upsert_user(user_id, username, name)

    in_channel = await check_subscribed(user_id)
    if not in_channel:
        await cb.answer('❌ Подписка не найдена!')
        await cb.message.edit_text(
            f'<b>{E["stop2"]} Для использования бота нужна подписка.</b>',
            reply_markup=sub_check_kb())
        return

    approved = await get_approved(user_id)
    is_adm   = await is_admin(user_id)

    if approved is None:
        await state.set_state(Survey.q1)
        await cb.message.edit_text(
            f'<b>{E["hi"]} Спасибо за подписку!</b>\n\n'
            f'<b>{E["question"]} Знаете ли вы, что такое ворк?</b>',
            reply_markup=survey_kb(1, user_id))
    elif approved == 0:
        if await has_pending_survey(user_id):
            await cb.message.edit_text(f'<b>{E["hourglass"]} Ваша анкета на рассмотрении.</b>')
        else:
            await state.set_state(Survey.q1)
            await cb.message.edit_text(
                f'<b>{E["hi"]} Пройдите анкету.</b>\n\n'
                f'<b>{E["question"]} Знаете ли вы, что такое ворк?</b>',
                reply_markup=survey_kb(1, user_id))
    else:
        await cb.message.edit_text(
            f'<b>{E["check"]} Подписка подтверждена!</b>\n\nДобро пожаловать в bad team.',
            reply_markup=main_menu(is_adm))
    await cb.answer()

# ── Анкета — кнопки ──────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith('survey_'))
async def cb_survey(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split('_')
    action, step, target_id = parts[1], int(parts[2]), int(parts[3])

    if cb.from_user.id != target_id:
        await cb.answer('❌ Это сообщение не для вас.')
        return

    current = await state.get_state()
    if current not in (Survey.q1, Survey.q2):
        await cb.answer('Пожалуйста, начните с /start.')
        return

    answer = 'Да' if action == 'yes' else 'Нет'
    data   = await state.get_data()
    answers = data.get('answers', {})
    answers[f'q{step}'] = answer
    await state.update_data(answers=answers)

    if step == 1:
        await state.set_state(Survey.q2)
        await cb.message.edit_text(
            f'<b>{E["check"]} Ответ принят:</b> {answer}\n\n'
            f'<b>{E["question"]} Разбираетесь ли вы в NFT?</b>',
            reply_markup=survey_kb(2, target_id))
    elif step == 2:
        await state.set_state(Survey.q3)
        await cb.message.edit_text(
            f'<b>{E["check"]} Ответ принят:</b> {answer}\n\n'
            f'<b>{E["question"]} Сколько времени готовы уделять ворку?</b>\n<i>(Напишите текстом)</i>')
    await cb.answer()

# Анкета — шаг 3 (текст)
@router.message(Survey.q3)
async def survey_q3(msg: Message, state: FSMContext):
    user_id  = msg.from_user.id
    username = msg.from_user.username or 'без_username'
    name     = msg.from_user.full_name or 'Без имени'
    data     = await state.get_data()
    answers  = data.get('answers', {})
    answers['q3'] = msg.text
    await state.clear()

    async with db_connect() as conn:
        await conn.execute(
            'INSERT OR REPLACE INTO surveys (user_id,answer1,answer2,answer3,status) VALUES (?,?,?,?,"pending")',
            (user_id, answers.get('q1'), answers.get('q2'), answers.get('q3')))
        await conn.execute(
            'INSERT OR IGNORE INTO users (user_id,username,nickname,role,join_date,approved) VALUES (?,?,?,"worker",?,0)',
            (user_id, username, name, datetime.now().strftime('%Y-%m-%d')))
        await conn.execute('UPDATE users SET approved=0, username=?, nickname=? WHERE user_id=?', (username, name, user_id))
        await conn.commit()

    profile_check = await analyze_profile(user_id, username, name)
    if profile_check['auto_reject']:
        reasons_text = '\n'.join(f'- {reason}' for reason in profile_check['reasons'])
        await msg.answer(
            f'<b>{E["no2"]} Ваша анкета отклонена автоматически.</b>\n\n'
            f'<b>Причины:</b>\n{reasons_text}\n\n'
            f'Проверьте профиль, удалите NFT / коммерческие метки, платные или закрытые сообщения и попробуйте снова.')
        async with db_connect() as conn:
            await conn.execute('UPDATE surveys SET status="rejected" WHERE user_id=?', (user_id,))
            await conn.execute('UPDATE users SET approved=0 WHERE user_id=?', (user_id,))
            await conn.commit()
        admins = await get_admins()
        for adm in admins:
            try:
                await bot.send_message(adm,
                    f'<b>{E["no2"]} Авто-отклонение анкеты @{username}</b>\n'
                    f'<b>ID:</b> <code>{user_id}</code>\n\n'
                    f'<blockquote>'
                    f'<b>{E["n1"]} Что такое ворк:</b> {answers.get("q1")}\n'
                    f'<b>{E["n2"]} NFT:</b> {answers.get("q2")}\n'
                    f'<b>{E["n3"]} Время:</b> {answers.get("q3")}\n'
                    f'</blockquote>\n\n'
                    f'<b>Фильтр:</b>\n{profile_check["summary"]}')
            except Exception:
                pass
        return

    await msg.answer(
        f'<b>{E["mail"]} Спасибо!</b>\nВаша анкета отправлена на рассмотрение администратора.')

    admins = await get_admins()
    for adm in admins:
        try:
            await bot.send_message(adm,
                f'<b>{E["write"]} Новая анкета от @{username}</b>\n'
                f'<b>ID:</b> <code>{user_id}</code>\n\n'
                f'<blockquote>'
                f'<b>{E["n1"]} Что такое ворк:</b> {answers.get("q1")}\n'
                f'<b>{E["n2"]} NFT:</b> {answers.get("q2")}\n'
                f'<b>{E["n3"]} Время:</b> {answers.get("q3")}\n'
                f'</blockquote>\n\n'
                f'<b>Проверка профиля:</b>\n{profile_check["summary"]}',
                reply_markup=survey_approve_kb(user_id))
        except Exception:
            pass

# ── Анкета: одобрение/отклонение ─────────────────────────────────────────────
@router.callback_query(F.data.startswith('approve_survey_'))
async def cb_approve_survey(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав администратора')
        return
    user_id = int(cb.data.split('_')[-1])
    async with db_connect() as conn:
        async with conn.execute('SELECT status,answer1,answer2,answer3 FROM surveys WHERE user_id=?', (user_id,)) as c:
            row = await c.fetchone()
        if not row: await cb.answer('Анкета не найдена'); return
        if row[0] == 'approved': await cb.answer('Уже одобрена'); return
        if row[0] == 'rejected': await cb.answer('Уже отклонена'); return
        status, a1, a2, a3 = row
        async with conn.execute('SELECT username FROM users WHERE user_id=?', (user_id,)) as c:
            u = await c.fetchone()
        uname = u[0] if u else str(user_id)
        await conn.execute('UPDATE users SET approved=1 WHERE user_id=?', (user_id,))
        await conn.execute('UPDATE surveys SET status="approved" WHERE user_id=?', (user_id,))
        await conn.commit()
    try:
        await cb.message.edit_text(
            f'<b>{E["ok"]} Анкета одобрена</b>\n\n'
            f'<b>{E["user2"]} Пользователь:</b> @{uname} (<code>{user_id}</code>)\n\n'
            f'<blockquote>'
            f'<b>{E["n1"]} Что такое ворк:</b> {a1}\n'
            f'<b>{E["n2"]} NFT:</b> {a2}\n'
            f'<b>{E["n3"]} Время:</b> {a3}'
            f'</blockquote>')
    except Exception: pass

    is_adm = await is_admin(user_id)
    try:
        await bot.send_message(user_id,
            f'<b>{E["party"]} Ваша анкета одобрена!</b>\n\n{E["rocket"]} Добро пожаловать в команду!',
            reply_markup=main_menu(is_adm))
    except Exception: pass
    await cb.answer('Анкета одобрена ✅')

@router.callback_query(F.data.startswith('reject_survey_'))
async def cb_reject_survey(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав администратора')
        return
    user_id = int(cb.data.split('_')[-1])
    async with db_connect() as conn:
        async with conn.execute('SELECT status,answer1,answer2,answer3 FROM surveys WHERE user_id=?', (user_id,)) as c:
            row = await c.fetchone()
        if not row: await cb.answer('Анкета не найдена'); return
        if row[0] != 'pending': await cb.answer('Уже обработана'); return
        status, a1, a2, a3 = row
        async with conn.execute('SELECT username FROM users WHERE user_id=?', (user_id,)) as c:
            u = await c.fetchone()
        uname = u[0] if u else str(user_id)
        await conn.execute('UPDATE surveys SET status="rejected" WHERE user_id=?', (user_id,))
        await conn.execute('UPDATE users SET approved=0 WHERE user_id=?', (user_id,))
        await conn.commit()
    try:
        await cb.message.edit_text(
            f'<b>{E["no2"]} Анкета отклонена</b>\n\n'
            f'<b>{E["user2"]} Пользователь:</b> @{uname} (<code>{user_id}</code>)\n\n'
            f'<blockquote>'
            f'<b>{E["n1"]} Что такое ворк:</b> {a1}\n'
            f'<b>{E["n2"]} NFT:</b> {a2}\n'
            f'<b>{E["n3"]} Время:</b> {a3}'
            f'</blockquote>')
    except Exception: pass
    try:
        await bot.send_message(user_id,
            f'<b>{E["no2"]} Ваша анкета отклонена</b>\n\n'
            f'{E["warn"]} Обратитесь к администратору за уточнениями.')
    except Exception: pass
    await cb.answer('Анкета отклонена ❌')


# ── Навигация ─────────────────────────────────────────────────────────────────
@router.callback_query(F.data == 'back_main')
async def cb_back_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = cb.from_user.id
    is_adm  = await is_admin(user_id)
    text = f'<b>{E["down"]} Выберите пункт меню:</b>'
    try:
        await cb.message.edit_text(text, reply_markup=main_menu(is_adm))
    except Exception:
        try:
            await cb.message.delete()
        except Exception:
            pass
        await bot.send_message(user_id, text, reply_markup=main_menu(is_adm))
    await cb.answer()

# ── Профиль ───────────────────────────────────────────────────────────────────
@router.callback_query(F.data == 'profile')
async def cb_profile(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not await require_approved(user_id, cb):
        return
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT username,nickname,role,total_profits,join_date FROM users WHERE user_id=?',
            (user_id,)) as c:
            row = await c.fetchone()
    if not row: await cb.answer('Профиль не найден'); return
    username, nickname, role, profits, join_date = row
    await cb.message.edit_text(
        format_profile(user_id, nickname or 'Без имени', username or '—', role, profits, join_date),
        reply_markup=back_btn())
    await cb.answer()

# ── Топ ───────────────────────────────────────────────────────────────────────
async def render_top() -> str:
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT nickname,total_profits,username,role FROM users WHERE approved=1 ORDER BY total_profits DESC LIMIT 10') as c:
            users = await c.fetchall()
        async with conn.execute('SELECT SUM(total_profits) FROM users WHERE approved=1') as c:
            total = (await c.fetchone())[0] or 0
    if not users:
        return f'{E["chart"]} Топ воркеров пока пуст.'
    medals = [E['gold'], E['silver'], E['bronze']]
    nums   = [E['n4'],E['n5'],E['n6'],E['n7'],E['n8'],E['n9'],e(5794375786743995258,'0️⃣')]
    text   = f'<b>{E["trophy"]} ТОП 10 ВОРКЕРОВ</b>\n\n'
    for i, (nick, profit, uname, role) in enumerate(users, 1):
        if i <= 3: medal = medals[i-1]
        elif i <= 10: medal = nums[i-4]
        else: medal = f'{i}.'
        name = nick or (f'@{uname}' if uname else f'Воркер {i}')
        role_t = ' <i>(Админ)</i>' if role == 'admin' else ''
        text += f'{medal} <b>{name}</b>{role_t} — <code>{profit:.2f} TON</code>\n'
    text += f'\n<b>{E["cash"]} Касса команды:</b> <code>{total:.2f} TON</code>'
    return text

@router.callback_query(F.data == 'top')
async def cb_top(cb: CallbackQuery):
    if not await require_approved(cb.from_user.id, cb):
        return
    await cb.message.edit_text(await render_top(), reply_markup=back_btn())
    await cb.answer()

@router.message(Command('top'))
async def cmd_top(msg: Message):
    if _is_team_chat(msg):
        if not _is_team_top(msg):
            return
        await msg.answer(await render_top())
        return
    if not await require_approved(msg.from_user.id, msg):
        return
    await msg.answer(await render_top(), reply_markup=back_btn())

# ── Инфо ──────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == 'info')
async def cb_info(cb: CallbackQuery):
    if not await require_approved(cb.from_user.id, cb):
        return
    await cb.message.edit_text(
        f'<b>{E["info"]} bad team</b>\n\n'
        f'{E["crown"]} <b>Владелец:</b> @bad_rip\n'
        f'{E["hat"]} <b>Совладелец:</b> @no',
        reply_markup=kb(
            [InlineKeyboardButton.model_construct(text='Чат команды', url='https://t.me/+WkYR_Vgz4eBmNzVi', icon_custom_emoji_id='5443038326535759644')],
            [btn('Назад', 'back_main', 5960671702059848143)]))
    await cb.answer()

# ── Мои заявки ────────────────────────────────────────────────────────────────
PAYOUTS_PER_PAGE = 5

STATUS_LABELS = {
    'pending':  ('⏳', 'На рассмотрении'),
    'approved': ('✅', 'Выплачено'),
    'rejected': ('❌', 'Отклонено'),
}

STATUS_ICON_IDS = {
    'pending':  5902050947567194830,
    'approved': 5895514131896733546,
    'rejected': 5893163582194978381,
}
STATUS_FALLBACK = {
    'pending':  '⏳',
    'approved': '✅',
    'rejected': '❌',
}

def my_payouts_kb(payouts: list, page: int, total: int, per_page: int) -> InlineKeyboardMarkup:
    rows = []
    for p in payouts:
        pid, code, wt, status, created_at, profit = p
        wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
        label = f'{code}  •  {wt_name}'
        icon_id = STATUS_ICON_IDS.get(status)
        btn_kwargs = dict(text=label, callback_data=f'my_payout_detail_{pid}')
        if icon_id:
            btn_kwargs['icon_custom_emoji_id'] = str(icon_id)
        rows.append([InlineKeyboardButton.model_construct(**btn_kwargs)])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton.model_construct(
            text='Назад', callback_data=f'my_payouts_{page-1}',
            icon_custom_emoji_id='5960671702059848143'))
    total_pages = (total + per_page - 1) // per_page
    if total_pages > 1:
        nav.append(InlineKeyboardButton.model_construct(text=f'{page+1}/{total_pages}', callback_data='noop'))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton.model_construct(
            text='Вперёд', callback_data=f'my_payouts_{page+1}',
            icon_custom_emoji_id='6037622221625626773'))
    if nav:
        rows.append(nav)
    rows.append([btn('Главное меню', 'back_main', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def payout_detail_kb(payout_id: int, page: int) -> InlineKeyboardMarkup:
    return kb(
        [btn('К списку заявок', f'my_payouts_{page}', 5960671702059848143)],
    )

@router.callback_query(F.data.startswith('my_payouts_'))
async def cb_my_payouts(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not await require_approved(user_id, cb):
        return
    try:
        page = int(cb.data.split('_')[-1])
    except Exception:
        page = 0
    per_page = PAYOUTS_PER_PAGE
    offset = page * per_page
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT COUNT(*) FROM payouts WHERE user_id=?', (user_id,)) as c:
            total = (await c.fetchone())[0]
        async with conn.execute(
            'SELECT id,payout_code,work_type,status,created_at,profit_amount FROM payouts WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?',
            (user_id, per_page, offset)) as c:
            payouts = await c.fetchall()
    if total == 0:
        try:
            await cb.message.edit_text(
                f'<b>{E["phone"]} Мои заявки</b>\n\n'
                f'<i>У вас ещё нет заявок.</i>\n'
                f'Нажмите <b>Выплата</b> чтобы создать первую!',
                reply_markup=kb([btn('Главное меню', 'back_main', 5960671702059848143)]))
        except Exception:
            pass
        await cb.answer()
        return
    total_pages = (total + per_page - 1) // per_page
    counts = {'pending': 0, 'approved': 0, 'rejected': 0}
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT status,COUNT(*) FROM payouts WHERE user_id=? GROUP BY status', (user_id,)) as c:
            for row in await c.fetchall():
                counts[row[0]] = row[1]
    text = (
        f'<b>{E["phone"]} Мои заявки</b> · <i>стр. {page+1}/{total_pages}</i>\n\n'
        f'<blockquote>'
        f'{e(5895514131896733546,"✅")} Выплачено: <b>{counts["approved"]}</b>   '
        f'{e(5902050947567194830,"⏳")} Ожидают: <b>{counts["pending"]}</b>   '
        f'{e(5893163582194978381,"❌")} Откл: <b>{counts["rejected"]}</b>'
        f'</blockquote>\n'
        f'<i>Нажмите на заявку для деталей:</i>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=my_payouts_kb(payouts, page, total, per_page))
    except Exception:
        pass
    await cb.answer()

@router.callback_query(F.data == 'noop')
async def cb_noop(cb: CallbackQuery):
    await cb.answer()

@router.callback_query(F.data.startswith('my_payout_detail_'))
async def cb_my_payout_detail(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not await require_approved(user_id, cb):
        return
    try:
        payout_id = int(cb.data.split('_')[-1])
    except Exception:
        await cb.answer()
        return
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT id,payout_code,work_type,status,created_at,profit_amount,gift_link,deal_code,user_id FROM payouts WHERE id=?',
            (payout_id,)) as c:
            row = await c.fetchone()
    if not row or row[8] != user_id:
        await cb.answer('Заявка не найдена')
        return
    pid, code, wt, status, created_at, profit, gift_link, deal_code, _ = row
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    status_map = {
        'pending':  (e(5902050947567194830,"⏳"), 'На рассмотрении'),
        'approved': (e(5895514131896733546,"✅"), 'Выплачено'),
        'rejected': (e(5893163582194978381,"❌"), 'Отклонено'),
    }
    sem, slabel = status_map.get(status, ('❓', status))
    profit_line = f'\n<b>{E["money"]} Сумма:</b> <code>{profit:.2f} TON</code>' if status == 'approved' and profit else ''
    deal_line = f'\n<b>Код сделки:</b> <code>{deal_code}</code>' if deal_code else ''
    gift_lines = [l.strip() for l in (gift_link or '').splitlines() if l.strip()]
    if gift_lines:
        gift_block = f'\n\n<b>{E["gift"]} Подарки:</b>\n<blockquote>' + '\n'.join(gift_lines) + '</blockquote>'
    else:
        gift_block = ''
    text = (
        f'<b>{E["phone"]} Заявка {code}</b>\n\n'
        f'<blockquote>'
        f'<b>Статус:</b> {sem} {slabel}\n'
        f'<b>Тип:</b> {wt_name}'
        f'{deal_line}'
        f'<b>\n{E["cal"]} Дата:</b> {created_at or "—"}'
        f'{profit_line}'
        f'</blockquote>'
        f'{gift_block}'
    )
    # Вычисляем страницу для кнопки назад
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT COUNT(*) FROM payouts WHERE user_id=? AND id>?', (user_id, payout_id)) as c:
            pos_from_end = (await c.fetchone())[0]
    back_page = pos_from_end // PAYOUTS_PER_PAGE

    # Отправляем медиафайлы отдельно если заявка approved
    detail_kb = payout_detail_kb(payout_id, back_page)
    try:
        await cb.message.edit_text(text, reply_markup=detail_kb)
    except Exception:
        pass
    await cb.answer()

# ── Выплата ───────────────────────────────────────────────────────────────────
@router.callback_query(F.data == 'payout')
async def cb_payout(cb: CallbackQuery):
    user_id  = cb.from_user.id
    if not await require_approved(user_id, cb):
        return
    types = await get_enabled_work_types()
    if not types:
        await cb.message.edit_text(
            f'<b>{E["warn"]} Все типы ворка временно отключены.</b>',
            reply_markup=back_btn())
        await cb.answer()
        return
    await cb.message.edit_text(
        f'<b>{E["cash"]} Выберите способ ворка:</b>',
        reply_markup=work_type_kb(types))
    await cb.answer()

@router.callback_query(F.data.startswith('work_'))
async def cb_work_type(cb: CallbackQuery, state: FSMContext):
    user_id   = cb.from_user.id
    if not await require_approved(user_id, cb):
        return
    work_type = cb.data.split('_', 1)[1]

    # Проверка что тип включён
    async with db_connect() as conn:
        async with conn.execute('SELECT enabled FROM work_types WHERE work_type=?', (work_type,)) as c:
            row = await c.fetchone()
    if not row or not row[0]:
        await cb.answer('❌ Этот тип ворка временно недоступен')
        return

    pct       = await get_user_percentage(user_id, work_type)
    wt_name   = WORK_TYPES.get(work_type, {}).get('name', work_type)

    payout_temp[user_id] = {
        'work_type': work_type,
        'work_type_name': wt_name,
        'percentage': pct,
        'media_files': [],
        'deal_code': None,
        'gift_link': None,
        'ton_address': None,
        'bot_msg_id': cb.message.message_id,
        'chat_id': cb.message.chat.id,
    }

    if work_type == 'otc':
        await state.set_state(Payout.deal_code)
        await cb.message.edit_text(
            f'<b>{E["cash"]} Заявка: {wt_name}</b>\n'
            f'<blockquote><b>Процент:</b> {int(pct*100)}%</blockquote>\n\n'
            f'<b>{E["n1"]} Введите код сделки (<code>#код</code>):</b>',
            reply_markup=kb([InlineKeyboardButton.model_construct(text='Отмена', callback_data='back_main', icon_custom_emoji_id='5893163582194978381', style='danger')]))
    else:
        await state.set_state(Payout.media)
        await cb.message.edit_text(
            f'<b>{E["cash"]} Заявка: {wt_name}</b>\n'
            f'<blockquote><b>Процент:</b> {int(pct*100)}%</blockquote>\n\n'
            f'<b>{E["n1"]} Отправьте скриншоты.</b>\n'
            f'Нажмите «Готово», когда загрузите всё.\n\n'
            f'<i>Загружено: <b>0</b> фото</i>',
            reply_markup=media_done_kb(0))
    await cb.answer()

@router.message(Payout.deal_code)
async def payout_deal_code(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    try: await msg.delete()
    except: pass
    cancel_kb = kb([InlineKeyboardButton.model_construct(text='Отмена', callback_data='back_main', icon_custom_emoji_id='5893163582194978381', style='danger')])
    if not msg.text or not msg.text.startswith('#'):
        if user_id in payout_temp:
            try:
                await bot.edit_message_text(
                    f'<b>{E["no"]} Введите код сделки начиная с #</b>\n\n'
                    f'<b>{E["n1"]} Введите код сделки (<code>#код</code>):</b>',
                    chat_id=payout_temp[user_id]['chat_id'],
                    message_id=payout_temp[user_id]['bot_msg_id'],
                    reply_markup=cancel_kb)
            except: pass
        return
    payout_temp[user_id]['deal_code'] = msg.text
    await state.set_state(Payout.media)
    media_text = (
        f'<b>{E["n2"]} Отправьте скриншоты (можно несколько).</b>\n'
        f'Нажмите «Готово», когда загрузите всё.\n\n'
        f'<i>Загружено: <b>0</b> фото</i>'
    )
    try:
        await bot.edit_message_text(
            media_text,
            chat_id=payout_temp[user_id]['chat_id'],
            message_id=payout_temp[user_id]['bot_msg_id'],
            reply_markup=media_done_kb(0))
    except:
        sent = await msg.answer(media_text, reply_markup=media_done_kb(0))
        payout_temp[user_id]['bot_msg_id'] = sent.message_id
        payout_temp[user_id]['chat_id'] = sent.chat.id

@router.message(Payout.media, F.photo | F.document)
async def payout_media(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    if user_id not in payout_temp: return
    if msg.photo:
        payout_temp[user_id]['media_files'].append(('photo', msg.photo[-1].file_id))
    elif msg.document:
        payout_temp[user_id]['media_files'].append(('document', msg.document.file_id))
    count = len(payout_temp[user_id]['media_files'])
    # Удаляем сообщение пользователя с фото
    try: await msg.delete()
    except: pass
    # Обновляем сообщение бота счётчиком
    try:
        await bot.edit_message_text(
            f'<b>{E["cash"]} Заявка: {payout_temp[user_id]["work_type_name"]}</b>\n'
            f'<blockquote><b>Процент:</b> {int(payout_temp[user_id]["percentage"]*100)}%</blockquote>\n\n'
            f'<b>{E["n1"]} Отправьте скриншоты.</b>\n'
            f'Нажмите «Готово», когда загрузите всё.\n\n'
            f'<i>Загружено: <b>{count}</b> фото</i>',
            chat_id=payout_temp[user_id]['chat_id'],
            message_id=payout_temp[user_id]['bot_msg_id'],
            reply_markup=media_done_kb(count))
    except: pass


@router.callback_query(F.data == 'media_done')
async def cb_media_done(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    if user_id not in payout_temp:
        await cb.answer('Сессия истекла. Начните заново.')
        return
    if not payout_temp[user_id]['media_files']:
        await cb.answer('❌ Отправьте хотя бы один скриншот!')
        return
    count = len(payout_temp[user_id]['media_files'])
    await state.set_state(Payout.gift_link)
    nft_text = (
        f'<b>{E["n2"]} Введите ссылку(и) на NFT:</b>\n'
        f'<code>https://t.me/nft/...</code>\n'
        f'<i>(Можно несколько, каждая с новой строки)</i>\n\n'
        f'<i>Скриншотов загружено: <b>{count}</b></i>'
    )
    try:
        await cb.message.edit_text(nft_text)
    except Exception:
        try: await cb.message.delete()
        except: pass
        await bot.send_message(user_id, nft_text)
    await cb.answer()

@router.message(Payout.gift_link)
async def payout_gift_link(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    try: await msg.delete()
    except: pass
    raw_links = [l.strip() for l in (msg.text or '').splitlines() if l.strip()]
    valid_links = [l for l in raw_links if is_valid_nft_link(l)]
    if not valid_links:
        if user_id in payout_temp:
            try:
                await bot.edit_message_text(
                    f'<b>{E["no"]} Неверный формат ссылки.</b>\n'
                    f'Формат: <code>https://t.me/nft/...</code>\n\n'
                    f'<b>{E["n2"]} Введите ссылку(и) на NFT:</b>\n'
                    f'<code>https://t.me/nft/...</code>\n'
                    f'<i>(Можно несколько, каждая с новой строки)</i>',
                    chat_id=payout_temp[user_id]['chat_id'],
                    message_id=payout_temp[user_id]['bot_msg_id'])
            except: pass
        return
    payout_temp[user_id]['gift_link'] = '\n'.join(valid_links)
    await state.set_state(Payout.ton_addr)
    ton_text = f'<b>{E["n3"]} Введите ваш TON-адрес:</b>'
    try:
        await bot.edit_message_text(
            ton_text,
            chat_id=payout_temp[user_id]['chat_id'],
            message_id=payout_temp[user_id]['bot_msg_id'])
    except:
        sent = await msg.answer(ton_text)
        payout_temp[user_id]['bot_msg_id'] = sent.message_id
        payout_temp[user_id]['chat_id'] = sent.chat.id


@router.message(Payout.ton_addr)
async def payout_ton_addr(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    try: await msg.delete()
    except: pass
    if not is_valid_ton(msg.text or ''):
        if user_id in payout_temp:
            try:
                await bot.edit_message_text(
                    f'<b>{E["no"]} Неверный TON-адрес.</b>\n'
                    f'Должен начинаться с <code>UQ</code> или <code>EQ</code>.\n\n'
                    f'<b>{E["n3"]} Введите ваш TON-адрес:</b>',
                    chat_id=payout_temp[user_id]['chat_id'],
                    message_id=payout_temp[user_id]['bot_msg_id'])
            except: pass
        return
    payout_temp[user_id]['ton_address'] = msg.text
    await state.clear()
    await submit_payout(msg, user_id)


@router.message(SpecialistSurvey.goy_username)
async def specialist_goy_username(msg: Message, state: FSMContext):
    specialist_forms[msg.from_user.id]["goy_username"] = msg.text

    await state.set_state(SpecialistSurvey.screenshots)

    await msg.answer(
        '<b>2.</b> Отправьте скрины переписки\n\n'
        'Максимум: <b>10 фото</b>\n\n'
        'Когда закончите — нажмите /done'
    )


@router.message(
    SpecialistSurvey.screenshots,
    F.photo
)
async def specialist_screenshots(msg: Message):
    files = specialist_forms[msg.from_user.id]["screenshots"]

    if len(files) >= 10:
        await msg.answer(
            '❌ Максимум 10 скриншотов'
        )
        return

    files.append(msg.photo[-1].file_id)

    await msg.answer(
        f'✅ Загружено: {len(files)}/10'
    )


@router.message(Command('done'))
async def specialist_done(msg: Message, state: FSMContext):
    current = await state.get_state()

    if current != SpecialistSurvey.screenshots:
        return

    files = specialist_forms[msg.from_user.id]["screenshots"]

    if not files:
        await msg.answer(
            '❌ Отправьте хотя бы 1 скрин'
        )
        return

    await state.set_state(SpecialistSurvey.method)

    await msg.answer(
        '<b>3.</b> Метод вбива:\n\n'
        '1. Вход на аккаунт воркера\n'
        '2. Передача клиента'
    )


@router.message(SpecialistSurvey.method)
async def specialist_method(msg: Message, state: FSMContext):
    user_id = msg.from_user.id

    method = msg.text

    specialist_forms[user_id]["method"] = method

    specialist = specialist_forms[user_id]["specialist"]

    worker_specialist[user_id] = specialist

    async with db_connect() as conn:
        await conn.execute('UPDATE users SET role="specialist" WHERE username=?', (specialist,))
        await conn.commit()

    data = specialist_forms[user_id]

    text = (
        '<b>⚡ Клиент передан вбиверу</b>\n\n'

        f'<b>Воркер:</b> @{msg.from_user.username}\n'
        f'<b>Вбивер:</b> @{specialist}\n\n'

        f'<b>Юз гоя:</b> {data["goy_username"]}\n'
        f'<b>Метод:</b> {method}\n'
        f'<b>Скринов:</b> {len(data["screenshots"])}'
    )

    admins = await get_admins()

    for admin in admins:

        try:

            await bot.send_message(
                admin,
                text
            )

            for photo in data["screenshots"]:

                await bot.send_photo(
                    admin,
                    photo
                )

        except:
            pass

    try:

        await bot.send_message(
            user_id,
            f'✅ Вбивер @{specialist} выбран'
        )

    except:
        pass

    specialist_forms.pop(user_id, None)

    await state.clear()


async def submit_payout(msg: Message, user_id: int):
    data      = payout_temp.pop(user_id, {})
    code      = generate_payout_code()
    username  = msg.from_user.username or 'без_username'
    wt_name   = data['work_type_name']
    pct       = data['percentage']
    files     = data.get('media_files', [])
    photo_count = len(files)

    mentor_username = worker_mentor.get(user_id) or ''
    specialist_username = worker_specialist.get(user_id) or ''

    mentor_percent = 0
    specialist_percent = 0

    mentor_text = ''
    specialist_text = ''

    if mentor_username:
        mentor_percent = MENTORS.get(mentor_username, {}).get('percent', 0)
        mentor_text = (
            f'\n<b>Наставник:</b> @{mentor_username} '
            f'({int(mentor_percent * 100)}%)'
        )

    if specialist_username:
        specialist_percent = SPECIALISTS.get(specialist_username, {}).get('percent', 0)
        specialist_text = (
            f'\n<b>Вбивер:</b> @{specialist_username} '
            f'({int(specialist_percent * 100)}%)'
        )

    async with db_connect() as conn:
        await conn.execute('''
            INSERT INTO payouts (
                user_id,
                payout_code,
                work_type,
                deal_code,
                gift_link,
                ton_address,
                status,
                created_at,
                user_percentage,
                mentor_username,
                mentor_percent,
                specialist_username,
                specialist_percent
            )
            VALUES (?,?,?,?,?,? ,"pending",?,?,?,?,?,?)''',
            (
                user_id,
                code,
                data['work_type'],
                data.get('deal_code'),
                data.get('gift_link'),
                data.get('ton_address'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                pct,
                mentor_username,
                mentor_percent,
                specialist_username,
                specialist_percent
            )
        )
        await conn.commit()
        async with conn.execute('SELECT last_insert_rowid()') as c:
            payout_id = (await c.fetchone())[0]
    # Сохраняем медиафайлы в БД (персистентно) и в кэш памяти
    if files:
        payout_media_store[payout_id] = list(files)
        async with db_connect() as conn:
            for ftype, fid in files:
                await conn.execute(
                    'INSERT INTO payout_media (payout_id, media_type, file_id) VALUES (?,?,?)',
                    (payout_id, ftype, fid))
            await conn.commit()

    admin_text = (
        f'<b>{E["cash"]} Новая заявка #{payout_id}</b>\n\n'
        f'<blockquote>'
        f'<b>Код:</b> <code>{code}</code>\n'
        f'<b>Тип:</b> {wt_name}\n'
        f'<b>{E["user"]} Воркер:</b> @{username} (<code>{user_id}</code>)\n'
        f'<b>Процент:</b> {int(pct*100)}%{mentor_text}{specialist_text}\n'
        f'<b>Скриншотов:</b> {photo_count}'
        f'</blockquote>\n\n'
        f'<b>NFT:</b>\n<blockquote>{data.get("gift_link","—")}</blockquote>\n'
        f'<b>Адрес:</b>\n<blockquote><code>{data.get("ton_address","—")}</code></blockquote>'
    )

    admins = await get_admins()
    for adm in admins:
        try:
            if files:
                from aiogram.types import InputMediaPhoto, InputMediaDocument
                media_group = []
                for ftype, fid in files:
                    if ftype == 'photo':
                        media_group.append(InputMediaPhoto(media=fid))
                    else:
                        media_group.append(InputMediaDocument(media=fid))
                await bot.send_media_group(adm, media_group)
            await bot.send_message(adm, admin_text, reply_markup=payout_approve_kb(payout_id))
        except Exception:
            pass

    gift_link_raw = data.get('gift_link', '') or ''
    gift_lines = [l.strip() for l in gift_link_raw.splitlines() if l.strip()]
    gift_block = ''
    if gift_lines:
        gift_block = f'\n<b>{E["gift"]} Подарки:</b>\n<blockquote>' + '\n'.join(gift_lines) + '</blockquote>'

    await msg.answer(
        f'<b>{E["check"]} Заявка отправлена на рассмотрение!</b>\n\n'
        f'<blockquote>'
        f'<b>{E["phone"]} Код выплаты:</b> <code>{code}</code>\n'
        f'<b>Скриншотов загружено:</b> {photo_count}'
        f'</blockquote>'
        f'{gift_block}')

# ── Одобрение выплаты ─────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith('approve_payout_'))
async def cb_approve_payout(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав администратора')
        return
    payout_id = int(cb.data.split('_')[-1])
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT status,payout_code,work_type,user_id,user_percentage,mentor_username,mentor_percent,specialist_username,specialist_percent FROM payouts WHERE id=?',
            (payout_id,)) as c:
            row = await c.fetchone()
    if not row or row[0] != 'pending':
        await cb.answer('❌ Заявка не актуальна')
        return
    status, code, wt, uid, u_pct, mentor_username, mentor_percent, specialist_username, specialist_percent = row
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)

    # Защита от двойного нажатия: если этот админ уже в процессе — отменяем
    if cb.from_user.id in approve_ctx:
        await cb.answer('⚠️ Вы уже обрабатываете заявку. Завершите или отмените её.')
        return

    approve_ctx[cb.from_user.id] = {
        'payout_id': payout_id,
        'payout_code': code,
        'work_type': wt,
        'work_type_name': wt_name,
        'payout_user_id': uid,
        'user_percentage': u_pct,
        'origin_msg_id': cb.message.message_id,
        'origin_chat_id': cb.message.chat.id,
    }
    await state.set_state(AdminAction.waiting_amount_approve)
    prompt = await bot.send_message(
        cb.from_user.id,
        f'<b>{E["money"]} Введите сумму профита (TON) для {wt_name}:</b>\n'
        f'<i>Для отмены нажмите /cancel</i>')
    approve_ctx[cb.from_user.id]['prompt_msg_id'] = prompt.message_id
    await cb.answer()

@router.message(AdminAction.waiting_amount_approve)
async def admin_enter_amount(msg: Message, state: FSMContext):
    admin_id = msg.from_user.id
    if admin_id not in approve_ctx:
        await state.clear()
        return
    try:
        amount = float(msg.text.replace(',', '.'))
        if amount <= 0: raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Введите корректное число, например: 12.5</b>')
        return

    ctx       = approve_ctx.pop(admin_id)
    payout_id = ctx['payout_id']
    code      = ctx['payout_code']
    wt        = ctx['work_type']
    wt_name   = ctx['work_type_name']
    uid       = ctx['payout_user_id']
    u_pct     = ctx['user_percentage']
    origin_id = ctx['origin_msg_id']
    prompt_id = ctx.get('prompt_msg_id')
    await state.clear()

    try: await msg.delete()
    except: pass
    try:
        if prompt_id:
            await bot.delete_message(admin_id, prompt_id)
    except: pass

    # Повторная проверка статуса — защита от race condition между двумя админами
    async with db_connect() as conn:
        async with conn.execute('SELECT status FROM payouts WHERE id=?', (payout_id,)) as c:
            status_check = await c.fetchone()
        if not status_check or status_check[0] != 'pending':
            await msg.answer(f'<b>{E["warn"]} Заявка уже обработана другим администратором.</b>')
            return
        async with conn.execute('SELECT gift_link,ton_address,mentor_username,mentor_percent,specialist_username,specialist_percent FROM payouts WHERE id=?', (payout_id,)) as c:
            info = await c.fetchone()
        gift_link  = info[0] if info else '—'
        ton_addr   = info[1] if info else '—'
        mentor_username = info[2] if info else None
        mentor_percent = info[3] if info else 0
        specialist_username = info[4] if info else None
        specialist_percent = info[5] if info else 0

        if mentor_username:
            await conn.execute('UPDATE users SET role="mentor" WHERE username=?', (mentor_username,))
        if specialist_username:
            await conn.execute('UPDATE users SET role="specialist" WHERE username=?', (specialist_username,))

        await conn.execute('UPDATE payouts SET status="approved", profit_amount=? WHERE id=?', (amount, payout_id))
        await conn.commit()
        async with conn.execute('SELECT username FROM users WHERE user_id=?', (uid,)) as c:
            u = await c.fetchone()
        worker_uname = u[0] if u else 'unknown'
    pct           = u_pct if u_pct else await get_user_percentage(uid, wt)
    mentor_cut    = amount * mentor_percent
    specialist_cut= amount * specialist_percent
    worker_profit = (amount * pct) - mentor_cut - specialist_cut
    user_sum      = worker_profit

    async with db_connect() as conn:
        await conn.execute('UPDATE users SET total_profits=total_profits+? WHERE user_id=?', (worker_profit, uid))
        await conn.commit()

    # Наставник
    if mentor_username:

        async with db_connect() as conn:

            await conn.execute(
                '''
                UPDATE users
                SET total_profits = total_profits + ?
                WHERE username = ?
                ''',
                (
                    mentor_cut,
                    mentor_username
                )
            )

            await conn.commit()

    # Вбивер
    if specialist_username:

        async with db_connect() as conn:

            await conn.execute(
                '''
                UPDATE users
                SET total_profits = total_profits + ?
                WHERE username = ?
                ''',
                (
                    specialist_cut,
                    specialist_username
                )
            )

            await conn.commit()

    report = (
        f'<b>{E["check"]} Выплата #{payout_id} одобрена!</b>\n\n'
        f'<blockquote>'
        f'<b>Код:</b> <code>{code}</code>\n'
        f'<b>Тип:</b> {wt_name}\n'
        f'<b>Сумма:</b> <code>{amount:.1f} TON</code>\n'
        f'<b>Процент:</b> {int(pct*100)}%\n'
        f'<b>{E["money"]} К выплате:</b> <code>{user_sum:.2f} TON</code>'
        f'</blockquote>\n\n'
        f'<b>NFT:</b>\n<blockquote>{gift_link}</blockquote>\n'
        f'<b>Адрес:</b>\n<blockquote><code>{ton_addr}</code></blockquote>'
    )

    try:
        await bot.edit_message_text(report, chat_id=admin_id, message_id=origin_id)
    except Exception:
        await bot.send_message(admin_id, report)

    # Уведомление другим админам
    try:
        approver_entity = await bot.get_chat(admin_id)
        approver_uname = approver_entity.username or str(admin_id)
    except Exception:
        approver_uname = str(admin_id)

    for other in await get_admins():
        if other == admin_id: continue
        try:
            await bot.send_message(other,
                f'<b>{E["ok"]} Выплата #{payout_id} одобрена!</b>\n\n'
                f'<blockquote>'
                f'<b>{E["user2"]} Одобрил:</b> @{approver_uname} (<code>{admin_id}</code>)\n'
                f'<b>{E["user"]} Воркер:</b> @{worker_uname} (<code>{uid}</code>)\n'
                f'<b>{E["phone"]} Код:</b> <code>{code}</code>\n'
                f'<b>Тип:</b> {wt_name}\n'
                f'<b>Сумма:</b> <code>{amount:.1f} TON</code>\n'
                f'<b>{E["money"]} Воркеру:</b> <code>{user_sum:.2f} TON</code>'
                f'</blockquote>')
        except Exception: pass

    # Воркеру
    payout_msg = (
        f'<b>{E["check"]} ВЫПЛАТА! ({code})</b>\n\n'
        f'<blockquote>'
        f'<b>Тип:</b> {wt_name}\n'
        f'<b>Воркер:</b> @{worker_uname} • <code>{uid}</code>\n'
        f'<b>{E["money"]} К получению:</b> <code>{user_sum:.2f} TON</code>'
        f'</blockquote>\n\n'
        f'<b>Подарки:</b>\n<blockquote>{gift_link}</blockquote>\n'
        f'<b>Адрес:</b>\n<blockquote><code>{ton_addr}</code></blockquote>'
    )
    try:
        video = await download_video()
        if video and os.path.exists(video):
            from aiogram.types import FSInputFile
            await bot.send_video(uid, FSInputFile(video), caption=payout_msg)
        else:
            await bot.send_message(uid, payout_msg)
    except Exception as ex:
        print(f'Ошибка отправки воркеру: {ex}')

    # В чат выплат
    if PAYOUT_CHAT_ID and PAYOUT_TOPIC_ID:
        try:
            profit_msg = (
                f'<b>{E["check"]} ВЫПЛАТА! ({code})</b>\n\n'
                f'<blockquote>'
                f'<b>Тип:</b> {wt_name}\n'
                f'<b>Воркер:</b> @{worker_uname}\n'
                f'<b>{E["diamond"]} Выплачено:</b> <code>{user_sum:.2f} TON</code>'
                f'</blockquote>\n\n'
                f'<b>Подарки:</b>\n<blockquote>{gift_link}</blockquote>'
            )
            video = await download_video()
            if video and os.path.exists(video):
                from aiogram.types import FSInputFile
                await bot.send_video(PAYOUT_CHAT_ID, FSInputFile(video),
                    caption=profit_msg, message_thread_id=PAYOUT_TOPIC_ID)
            else:
                await bot.send_message(PAYOUT_CHAT_ID, profit_msg,
                    message_thread_id=PAYOUT_TOPIC_ID)
        except Exception as ex:
            print(f'Ошибка отправки в топик: {ex}')

# ── Отклонение выплаты ────────────────────────────────────────────────────────
# Словарь для хранения контекста отклонения: admin_id -> dict
reject_ctx: dict = {}

@router.callback_query(F.data.startswith('reject_payout_'))
async def cb_reject_payout(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав администратора')
        return
    payout_id = int(cb.data.split('_')[-1])
    async with db_connect() as conn:
        async with conn.execute('SELECT user_id,status,payout_code,work_type,gift_link,ton_address FROM payouts WHERE id=?', (payout_id,)) as c:
            row = await c.fetchone()
    if not row: await cb.answer('Заявка не найдена'); return
    uid, status, code, wt, gift_link, ton_addr = row
    if status != 'pending': await cb.answer('Заявка уже обработана'); return

    # Сохраняем контекст и переходим в стейт ввода причины
    reject_ctx[cb.from_user.id] = {
        'payout_id': payout_id,
        'payout_code': code,
        'work_type': wt,
        'payout_user_id': uid,
        'gift_link': gift_link,
        'ton_addr': ton_addr,
        'origin_msg_id': cb.message.message_id,
        'origin_chat_id': cb.message.chat.id,
    }
    await state.set_state(AdminAction.waiting_reject_reason)

    reason_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton.model_construct(
            text='Без причины',
            callback_data=f'reject_no_reason_{payout_id}',
            icon_custom_emoji_id='5893163582194978381',
            style='danger')
    ]])
    prompt = await bot.send_message(
        cb.from_user.id,
        f'<b>{E["pencil"]} Укажите причину отклонения заявки <code>{code}</code>:</b>\n\n'
        f'<i>Или нажмите кнопку ниже, чтобы отклонить без причины.</i>',
        reply_markup=reason_kb)
    reject_ctx[cb.from_user.id]['prompt_msg_id'] = prompt.message_id
    await cb.answer()


async def do_reject_payout(admin_id: int, reason: str, state: FSMContext):
    """Общая логика отклонения выплаты."""
    if admin_id not in reject_ctx:
        await state.clear()
        return
    ctx        = reject_ctx.pop(admin_id)
    payout_id  = ctx['payout_id']
    code       = ctx['payout_code']
    wt         = ctx['work_type']
    uid        = ctx['payout_user_id']
    gift_link  = ctx['gift_link']
    ton_addr   = ctx['ton_addr']
    origin_id  = ctx['origin_msg_id']
    origin_cid = ctx['origin_chat_id']
    prompt_id  = ctx.get('prompt_msg_id')
    await state.clear()

    async with db_connect() as conn:
        async with conn.execute('SELECT status FROM payouts WHERE id=?', (payout_id,)) as c:
            row = await c.fetchone()
        if not row or row[0] != 'pending':
            return
        async with conn.execute('SELECT username FROM users WHERE user_id=?', (uid,)) as c:
            u = await c.fetchone()
        worker_uname = u[0] if u else str(uid)
        await conn.execute('UPDATE payouts SET status="rejected" WHERE id=?', (payout_id,))
        await conn.commit()
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    reason_line = f'\n<b>{E["warn"]} Причина:</b> {reason}' if reason else ''

    # Получаем данные отклонившего админа
    try:
        admin_entity = await bot.get_chat(admin_id)
        admin_uname = admin_entity.username or str(admin_id)
    except Exception:
        admin_uname = str(admin_id)

    # Удаляем prompt-сообщение
    if prompt_id:
        try: await bot.delete_message(admin_id, prompt_id)
        except: pass

    # Обновляем оригинальное сообщение с заявкой
    rejected_text = (
        f'<b>{E["no2"]} Заявка #{payout_id} отклонена</b>\n\n'
        f'<blockquote>'
        f'<b>{E["phone"]} Код:</b> <code>{code}</code>\n'
        f'<b>Тип:</b> {wt_name}\n'
        f'<b>{E["user"]} Воркер:</b> @{worker_uname} (<code>{uid}</code>)\n'
        f'<b>{E["user2"]} Отклонил:</b> @{admin_uname}'
        f'{reason_line}'
        f'</blockquote>\n\n'
        f'<b>NFT:</b>\n<blockquote>{gift_link or "—"}</blockquote>\n'
        f'<b>Адрес:</b>\n<blockquote><code>{ton_addr or "—"}</code></blockquote>'
    )
    try:
        await bot.edit_message_text(rejected_text, chat_id=origin_cid, message_id=origin_id)
    except Exception:
        await bot.send_message(admin_id, rejected_text)

    # Уведомление другим админам
    for other in await get_admins():
        if other == admin_id: continue
        try:
            await bot.send_message(other,
                f'<b>{E["no2"]} Заявка #{payout_id} отклонена</b>\n\n'
                f'<blockquote>'
                f'<b>{E["user2"]} Отклонил:</b> @{admin_uname} (<code>{admin_id}</code>)\n'
                f'<b>{E["user"]} Воркер:</b> @{worker_uname} (<code>{uid}</code>)\n'
                f'<b>{E["phone"]} Код:</b> <code>{code}</code>\n'
                f'<b>Тип:</b> {wt_name}'
                f'{reason_line}'
                f'</blockquote>')
        except Exception: pass

    # Уведомление воркеру
    try:
        await bot.send_message(uid,
            f'<b>{E["no2"]} Заявка отклонена</b>\n\n'
            f'<blockquote>'
            f'<b>{E["phone"]} Код:</b> <code>{code}</code>\n'
            f'<b>Тип:</b> {wt_name}'
            f'{reason_line}'
            f'</blockquote>\n\n'
            f'{E["warn"]} Обратитесь к администратору за уточнениями.')
    except Exception: pass


@router.callback_query(F.data.startswith('reject_no_reason_'))
async def cb_reject_no_reason(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    await do_reject_payout(cb.from_user.id, '', state)
    await cb.answer('Заявка отклонена ❌')


@router.message(AdminAction.waiting_reject_reason)
async def admin_enter_reject_reason(msg: Message, state: FSMContext):
    try: await msg.delete()
    except: pass
    reason = (msg.text or '').strip()
    await do_reject_payout(msg.from_user.id, reason, state)

# ── Админ: заявки пользователя ────────────────────────────────────────────────
# callback: admin_user_payouts_{uid}_{status_filter}_{page}
# status_filter: all | pending | approved | rejected

ADMIN_PAYOUTS_PER_PAGE = 8

def admin_user_payouts_filter_kb(uid: int, current_filter: str, page: int) -> InlineKeyboardMarkup:
    filters = [
        ('all',      'Все',         5188217332748527444),
        ('pending',  'Ожидает',     5902050947567194830),
        ('approved', 'Одобрено',    5895514131896733546),
        ('rejected', 'Отклонено',   5893163582194978381),
    ]
    rows = []
    row = []
    for f, label, eid in filters:
        is_active = (f == current_filter)
        style_kw = {'style': 'success'} if is_active else {}
        row.append(InlineKeyboardButton.model_construct(
            text=label,
            callback_data=f'admin_user_payouts_{uid}_{f}_0',
            icon_custom_emoji_id=str(eid),
            **style_kw))
    rows.append(row)
    return rows

def admin_user_payouts_kb(uid: int, payouts: list, status_filter: str,
                           page: int, total: int) -> InlineKeyboardMarkup:
    rows = admin_user_payouts_filter_kb(uid, status_filter, page)
    for p in payouts:
        pid, code, wt, status, created_at, profit = p
        wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
        label = f'{code}  •  {wt_name}'
        icon_id = STATUS_ICON_IDS.get(status, 5188217332748527444)
        rows.append([InlineKeyboardButton.model_construct(
            text=label,
            callback_data=f'admin_payout_view_{pid}_{uid}_{status_filter}_{page}',
            icon_custom_emoji_id=str(icon_id))])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton.model_construct(
            text='Назад', callback_data=f'admin_user_payouts_{uid}_{status_filter}_{page-1}',
            icon_custom_emoji_id='5960671702059848143'))
    total_pages = max(1, (total + ADMIN_PAYOUTS_PER_PAGE - 1) // ADMIN_PAYOUTS_PER_PAGE)
    if total_pages > 1:
        nav.append(InlineKeyboardButton.model_construct(
            text=f'{page+1}/{total_pages}', callback_data='noop'))
    if (page + 1) * ADMIN_PAYOUTS_PER_PAGE < total:
        nav.append(InlineKeyboardButton.model_construct(
            text='Вперёд', callback_data=f'admin_user_payouts_{uid}_{status_filter}_{page+1}',
            icon_custom_emoji_id='6037622221625626773'))
    if nav:
        rows.append(nav)
    rows.append([btn('К профилю', f'user_detail_{uid}', 5879770735999717115),
                 btn('Настройки', 'admin_settings', 5893161718179173515)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_payout_action_kb(payout_id: int, status: str,
                            uid: int, status_filter: str, page: int) -> InlineKeyboardMarkup:
    rows = []
    if status == 'pending':
        rows.append([
            InlineKeyboardButton.model_construct(
                text='Принять', callback_data=f'approve_payout_{payout_id}',
                icon_custom_emoji_id='5895514131896733546', style='success'),
            InlineKeyboardButton.model_construct(
                text='Отклонить', callback_data=f'reject_payout_{payout_id}',
                icon_custom_emoji_id='5893163582194978381', style='danger'),
        ])
    rows.append([btn('К заявкам', f'admin_user_payouts_{uid}_{status_filter}_{page}', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.callback_query(F.data.startswith('admin_user_payouts_'))
async def cb_admin_user_payouts(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    parts = cb.data.split('_')
    # admin_user_payouts_{uid}_{status_filter}_{page}
    uid = int(parts[3])
    status_filter = parts[4]
    page = int(parts[5])
    per_page = ADMIN_PAYOUTS_PER_PAGE
    offset = page * per_page

    where = 'user_id=?'
    params_count = [uid]
    params_list  = [uid, per_page, offset]
    if status_filter != 'all':
        where += ' AND status=?'
        params_count = [uid, status_filter]
        params_list  = [uid, status_filter, per_page, offset]

    async with db_connect() as conn:
        async with conn.execute(f'SELECT COUNT(*) FROM payouts WHERE {where}', params_count) as c:
            total = (await c.fetchone())[0]
        async with conn.execute(
            f'SELECT id,payout_code,work_type,status,created_at,profit_amount FROM payouts WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?',
            params_list) as c:
            payouts = await c.fetchall()
        async with conn.execute('SELECT nickname,username FROM users WHERE user_id=?', (uid,)) as c:
            urow = await c.fetchone()
    nick = (urow[0] if urow else None) or (urow[1] if urow else str(uid))
    status_labels = {'all': 'Все', 'pending': 'Ожидает', 'approved': 'Одобрено', 'rejected': 'Отклонено'}
    total_pages = max(1, (total + per_page - 1) // per_page)
    text = (
        f'<b>{E["cash"]} Заявки: {nick}</b>\n'
        f'<blockquote>Фильтр: <b>{status_labels.get(status_filter, status_filter)}</b> · Всего: <b>{total}</b> · Стр. {page+1}/{total_pages}</blockquote>'
    )
    if not payouts:
        text += '\n\n<i>Заявок не найдено.</i>'
    try:
        await cb.message.edit_text(text, reply_markup=admin_user_payouts_kb(uid, payouts, status_filter, page, total))
    except Exception:
        pass
    await cb.answer()

@router.callback_query(F.data.startswith('admin_payout_view_'))
async def cb_admin_payout_view(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    # admin_payout_view_{payout_id}_{uid}_{status_filter}_{page}
    parts = cb.data.split('_')
    payout_id    = int(parts[3])
    uid          = int(parts[4])
    status_filter = parts[5]
    page         = int(parts[6])

    async with db_connect() as conn:
        async with conn.execute(
            'SELECT id,payout_code,work_type,status,created_at,profit_amount,gift_link,deal_code,ton_address,user_percentage,user_id FROM payouts WHERE id=?',
            (payout_id,)) as c:
            row = await c.fetchone()
        if not row:
            await cb.answer('Заявка не найдена')
            return
        pid, code, wt, status, created_at, profit, gift_link, deal_code, ton_addr, user_pct, p_uid = row
        async with conn.execute('SELECT username,nickname FROM users WHERE user_id=?', (p_uid,)) as c:
            urow = await c.fetchone()
    worker_uname = (urow[0] if urow else None) or str(p_uid)
    worker_nick  = (urow[1] if urow else None) or worker_uname
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    sem = {'pending': e(5902050947567194830,"⏳"), 'approved': e(5895514131896733546,"✅"), 'rejected': e(5893163582194978381,"❌")}.get(status, '❓')
    slabel = {'pending': 'На рассмотрении', 'approved': 'Выплачено', 'rejected': 'Отклонено'}.get(status, status)
    deal_line  = f'\n<b>Код сделки:</b> <code>{deal_code}</code>' if deal_code else ''
    profit_line = f'\n<b>{E["money"]} Сумма:</b> <code>{profit:.2f} TON</code>' if status == 'approved' and profit else ''
    pct_line   = f'\n<b>Процент:</b> {int((user_pct or 0)*100)}%' if user_pct else ''
    gift_lines = [l.strip() for l in (gift_link or '').splitlines() if l.strip()]
    gift_block = ('\n\n<b>' + E["gift"] + ' Подарки:</b>\n<blockquote>' + '\n'.join(gift_lines) + '</blockquote>') if gift_lines else ''
    ton_block  = f'\n\n<b>TON адрес:</b>\n<blockquote><code>{ton_addr}</code></blockquote>' if ton_addr else ''

    text = (
        f'<b>{E["cash"]} Заявка {code}</b>\n\n'
        f'<blockquote>'
        f'<b>Статус:</b> {sem} {slabel}\n'
        f'<b>Тип:</b> {wt_name}'
        f'{deal_line}'
        f'\n<b>{E["user"]} Воркер:</b> @{worker_uname} · <code>{p_uid}</code>'
        f'\n<b>{E["cal"]} Дата:</b> {created_at or "—"}'
        f'{pct_line}'
        f'{profit_line}'
        f'</blockquote>'
        f'{gift_block}'
        f'{ton_block}'
    )

    # Сначала шлём скриншоты отдельными сообщениями
    # Достаём media_files из БД — они не хранятся в БД напрямую,
    # поэтому ищем по payout_id в payout_media_store
    media_list = payout_media_store.get(payout_id)
    if media_list is None:
        # Восстанавливаем из БД (актуально после рестарта)
        async with db_connect() as conn:
            async with conn.execute('SELECT media_type, file_id FROM payout_media WHERE payout_id=?', (payout_id,)) as c:
                rows = await c.fetchall()
        media_list = [(r[0], r[1]) for r in rows]
        if media_list:
            payout_media_store[payout_id] = media_list
    if media_list:
        from aiogram.types import InputMediaPhoto, InputMediaDocument
        media_group = []
        for ftype, fid in media_list:
            if ftype == 'photo':
                media_group.append(InputMediaPhoto(media=fid))
            else:
                media_group.append(InputMediaDocument(media=fid))
        try:
            await bot.send_media_group(cb.from_user.id, media_group)
        except Exception:
            pass

    try:
        await cb.message.edit_text(text, reply_markup=admin_payout_action_kb(payout_id, status, uid, status_filter, page))
    except Exception:
        pass
    await cb.answer()

# ── Админ: поиск по коду выплаты ──────────────────────────────────────────────
@router.callback_query(F.data == 'search_payout_code_btn')
async def cb_search_payout_code_btn(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    await state.set_state(AdminAction.search_payout_code)
    await cb.message.edit_text(
        f'<b>{E["search"]} Поиск по коду выплаты</b>\n\n'
        f'<blockquote>Введите код выплаты, например: <code>#abc123xyz</code></blockquote>',
        reply_markup=kb([btn('Отмена', 'admin_settings', 5893163582194978381, 'danger')]))
    await cb.answer()

@router.message(AdminAction.search_payout_code)
async def admin_search_payout_code(msg: Message, state: FSMContext):
    await state.clear()
    code = (msg.text or '').strip()
    if not code.startswith('#'):
        code = '#' + code
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT id,payout_code,work_type,status,created_at,profit_amount,gift_link,deal_code,ton_address,user_percentage,user_id FROM payouts WHERE payout_code=?',
            (code,)) as c:
            row = await c.fetchone()
    if not row:
        await msg.answer(
            f'<b>{E["no"]} Заявка с кодом <code>{code}</code> не найдена.</b>',
            reply_markup=kb([btn('Назад', 'admin_settings', 5960671702059848143)]))
        return
    pid, code, wt, status, created_at, profit, gift_link, deal_code, ton_addr, user_pct, p_uid = row
    async with db_connect() as conn:
        async with conn.execute('SELECT username,nickname FROM users WHERE user_id=?', (p_uid,)) as c:
            urow = await c.fetchone()
    worker_uname = (urow[0] if urow else None) or str(p_uid)
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    sem = {'pending': e(5902050947567194830,"⏳"), 'approved': e(5895514131896733546,"✅"), 'rejected': e(5893163582194978381,"❌")}.get(status, '❓')
    slabel = {'pending': 'На рассмотрении', 'approved': 'Выплачено', 'rejected': 'Отклонено'}.get(status, status)
    deal_line  = f'\n<b>Код сделки:</b> <code>{deal_code}</code>' if deal_code else ''
    profit_line = f'\n<b>{E["money"]} Сумма:</b> <code>{profit:.2f} TON</code>' if status == 'approved' and profit else ''
    pct_line   = f'\n<b>Процент:</b> {int((user_pct or 0)*100)}%' if user_pct else ''
    gift_lines = [l.strip() for l in (gift_link or '').splitlines() if l.strip()]
    gift_block = ('\n\n<b>' + E["gift"] + ' Подарки:</b>\n<blockquote>' + '\n'.join(gift_lines) + '</blockquote>') if gift_lines else ''
    ton_block  = f'\n\n<b>TON адрес:</b>\n<blockquote><code>{ton_addr}</code></blockquote>' if ton_addr else ''

    text = (
        f'<b>{E["cash"]} Заявка {code}</b>\n\n'
        f'<blockquote>'
        f'<b>Статус:</b> {sem} {slabel}\n'
        f'<b>Тип:</b> {wt_name}'
        f'{deal_line}'
        f'\n<b>{E["user"]} Воркер:</b> @{worker_uname} · <code>{p_uid}</code>'
        f'\n<b>{E["cal"]} Дата:</b> {created_at or "—"}'
        f'{pct_line}'
        f'{profit_line}'
        f'</blockquote>'
        f'{gift_block}'
        f'{ton_block}'
    )

    # Скрины — берём из кэша или из БД
    media_list = payout_media_store.get(pid)
    if media_list is None:
        async with db_connect() as conn:
            async with conn.execute('SELECT media_type, file_id FROM payout_media WHERE payout_id=?', (pid,)) as c:
                rows = await c.fetchall()
        media_list = [(r[0], r[1]) for r in rows]
        if media_list:
            payout_media_store[pid] = media_list
    if media_list:
        from aiogram.types import InputMediaPhoto, InputMediaDocument
        media_group = []
        for ftype, fid in media_list:
            if ftype == 'photo':
                media_group.append(InputMediaPhoto(media=fid))
            else:
                media_group.append(InputMediaDocument(media=fid))
        try:
            await bot.send_media_group(msg.from_user.id, media_group)
        except Exception:
            pass

    action_kb = InlineKeyboardMarkup(inline_keyboard=(
        [[InlineKeyboardButton.model_construct(
            text='Принять', callback_data=f'approve_payout_{pid}',
            icon_custom_emoji_id='5895514131896733546', style='success'),
          InlineKeyboardButton.model_construct(
            text='Отклонить', callback_data=f'reject_payout_{pid}',
            icon_custom_emoji_id='5893163582194978381', style='danger')],
         [btn('Назад в настройки', 'admin_settings', 5960671702059848143)]]
        if status == 'pending' else
        [[btn('Назад в настройки', 'admin_settings', 5960671702059848143)]])
    )
    await msg.answer(text, reply_markup=action_kb)

# ── Панель администратора ─────────────────────────────────────────────────────
@router.callback_query(F.data == 'admin_settings')
async def cb_admin_settings(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав администратора')
        return
    await cb.message.edit_text(
        f'<b>{E["gear"]} Панель администратора</b>\n\n'
        f'<blockquote>{E["bolt"]} Управление пользователями, процентами и настройками</blockquote>',
        reply_markup=admin_settings_kb())
    await cb.answer()

# Управление ворками
@router.callback_query(F.data == 'manage_work_types')
async def cb_manage_work_types(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    types = await get_all_work_types()
    rows  = []
    for wt in types:
        icon = 'ВКЛ' if wt['enabled'] else 'ВЫКЛ'
        eid  = '5895514131896733546' if wt['enabled'] else '5893163582194978381'
        rows.append([InlineKeyboardButton.model_construct(
            text=f'{wt["name"]} — {icon}',
            callback_data=f'toggle_work_{wt["type"]}',
            icon_custom_emoji_id=eid)])
    rows.append([btn('Назад', 'admin_settings', 5960671702059848143)])
    await cb.message.edit_text(
        f'<b>{E["gear"]} Управление способами ворка</b>\n\n'
        f'<blockquote>Нажмите на тип, чтобы включить или отключить его.</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith('toggle_work_'))
async def cb_toggle_work(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    wt   = cb.data.split('_', 2)[2]
    new  = await toggle_work_type(wt)
    name = WORK_TYPES.get(wt, {}).get('name', wt)
    await cb.answer(f'{name} {"включён" if new else "отключён"}')
    # обновляем список
    types = await get_all_work_types()
    rows  = []
    for w in types:
        icon  = 'ВКЛ' if w['enabled'] else 'ВЫКЛ'
        eid   = '5895514131896733546' if w['enabled'] else '5893163582194978381'
        rows.append([InlineKeyboardButton.model_construct(text=f'{w["name"]} — {icon}', callback_data=f'toggle_work_{w["type"]}', icon_custom_emoji_id=eid)])
    rows.append([btn('Назад', 'admin_settings', 5960671702059848143)])
    await cb.message.edit_text(
        f'<b>{E["gear"]} Управление способами ворка</b>\n\n'
        f'<blockquote>Нажмите на тип, чтобы включить или отключить его.</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

# Поиск пользователя
@router.callback_query(F.data == 'search_user_btn')
async def cb_search_user_btn(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    await state.set_state(AdminAction.search_user)
    await cb.message.edit_text(
        f'<b>{E["search"]} Поиск пользователя</b>\n\n'
        f'<blockquote>Введите <b>@username</b> или <b>ID</b>:</blockquote>',
        reply_markup=kb([btn('Отмена', 'admin_settings', 5893163582194978381, 'danger')]))
    await cb.answer()

@router.message(AdminAction.search_user)
async def admin_search_user(msg: Message, state: FSMContext):
    await state.clear()
    row = await find_user(msg.text or '')
    if not row:
        await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>',
                         reply_markup=kb([btn('Назад', 'admin_settings', 5960671702059848143)]))
        return
    uid, nick, uname, role, profits, join_date, approved = row
    status = f'{E["check"]} Одобрен' if approved else f'{E["hourglass"]} Не одобрен'
    await msg.answer(
        format_profile(uid, nick or '—', uname or '—', role, profits, join_date) +
        f'\n<b>Статус:</b> {status}',
        reply_markup=kb(
            [btn('Добавить профит', f'add_profit_{uid}', 5244837092042750681, 'success'),
             btn('Удалить профит', f'remove_profit_{uid}', 5246762912428603768, 'danger')],
            [btn('Изменить процент', f'edit_user_percent_{uid}', 5231200819986047254)],
            [btn('Заявки пользователя', f'admin_user_payouts_{uid}_all_0', 5201691993775818138)],
            [btn('Назад в настройки', 'admin_settings', 5960671702059848143)]))

# Добавить/убрать admin
@router.callback_query(F.data == 'add_admin_btn')
async def cb_add_admin_btn(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Только владельцы')
        return
    await state.set_state(AdminAction.add_admin)
    await cb.message.edit_text(
        f'<b>{E["crown"]} Добавить администратора</b>\n\n'
        f'<blockquote>Введите <b>@username</b> или <b>ID</b>:</blockquote>',
        reply_markup=kb([btn('Отмена', 'admin_settings', 5893163582194978381, 'danger')]))
    await cb.answer()

@router.message(AdminAction.add_admin)
async def admin_add_admin(msg: Message, state: FSMContext):
    await state.clear()
    query = (msg.text or '').strip().lstrip('@')
    try:
        try:
            uid = int(query)
            chat = await bot.get_chat(uid)
        except ValueError:
            chat = await bot.get_chat(f'@{query}')
            uid  = chat.id
        uname = chat.username or str(uid)
        name  = chat.full_name or 'Без имени'
        async with db_connect() as conn:
            await conn.execute(
                'INSERT OR IGNORE INTO users (user_id,username,nickname,role,join_date,approved) VALUES (?,?,?,"admin",?,1)',
                (uid, uname, name, datetime.now().strftime('%Y-%m-%d')))
            await conn.execute('UPDATE users SET role="admin", approved=1 WHERE user_id=?', (uid,))
            await conn.commit()
        await msg.answer(f'<b>{E["check"]} @{uname} назначен администратором!</b>')
        try:
            await bot.send_message(uid,
                f'<b>{E["party"]} Вы назначены администратором!</b>',
                reply_markup=main_menu(True))
        except Exception: pass
    except Exception as ex:
        await msg.answer(f'<b>{E["no"]} Ошибка: {ex}</b>')

@router.callback_query(F.data == 'remove_admin_btn')
async def cb_remove_admin_btn(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Только владельцы')
        return
    await state.set_state(AdminAction.remove_admin)
    await cb.message.edit_text(
        f'<b>{E["ban"]} Снять администратора</b>\n\n'
        f'<blockquote>Введите <b>@username</b> или <b>ID</b>:</blockquote>',
        reply_markup=kb([btn('Отмена', 'admin_settings', 5893163582194978381, 'danger')]))
    await cb.answer()

@router.message(AdminAction.remove_admin)
async def admin_remove_admin(msg: Message, state: FSMContext):
    await state.clear()
    query = (msg.text or '').strip().lstrip('@')
    try:
        try:
            uid = int(query)
            chat = await bot.get_chat(uid)
        except ValueError:
            chat = await bot.get_chat(f'@{query}')
            uid  = chat.id
        uname = chat.username or str(uid)
        async with db_connect() as conn:
            await conn.execute('UPDATE users SET role="worker" WHERE user_id=?', (uid,))
            await conn.commit()
        await msg.answer(f'<b>{E["check"]} @{uname} снят с должности администратора.</b>')
    except Exception as ex:
        await msg.answer(f'<b>{E["no"]} Ошибка: {ex}</b>')

# Список пользователей
@router.callback_query(F.data.startswith('user_list_'))
async def cb_user_list(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    page   = int(cb.data.split('_')[2])
    limit  = 10
    offset = page * limit
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT user_id,nickname,username FROM users WHERE approved=1 ORDER BY nickname LIMIT ? OFFSET ?',
            (limit, offset)) as c:
            users = await c.fetchall()
        async with conn.execute('SELECT COUNT(*) FROM users WHERE approved=1') as c:
            total = (await c.fetchone())[0]
    if not users:
        await cb.answer('Нет одобренных пользователей')
        return
    rows = []
    for uid, nick, uname in users:
        display = nick or (f'@{uname}' if uname else f'ID: {uid}')
        rows.append([InlineKeyboardButton.model_construct(text=display, callback_data=f'user_detail_{uid}', icon_custom_emoji_id='5879770735999717115')])
    nav = []
    if page > 0: nav.append(InlineKeyboardButton.model_construct(text='«', callback_data=f'user_list_{page-1}', icon_custom_emoji_id='5960671702059848143'))
    if offset + limit < total: nav.append(InlineKeyboardButton.model_construct(text='»', callback_data=f'user_list_{page+1}', icon_custom_emoji_id='5893450623449305489'))
    if nav: rows.append(nav)
    rows.append([btn('Назад в настройки', 'admin_settings', 5960671702059848143)])
    await cb.message.edit_text(
        f'<b>{E["users"]} Список пользователей</b>\n'
        f'<blockquote>Страница {page+1} · Всего: {total}</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith('user_detail_'))
async def cb_user_detail(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        await cb.answer('Нет прав')
        return
    uid = int(cb.data.split('_')[2])
    async with db_connect() as conn:
        async with conn.execute(
            'SELECT nickname,username,role,total_profits,join_date FROM users WHERE user_id=?', (uid,)) as c:
            user = await c.fetchone()
    if not user: await cb.answer('Пользователь не найден'); return
    nick, uname, role, profits, join_date = user
    types = await get_all_work_types()
    pct_lines = []
    for wt in types:
        p = await get_user_percentage(uid, wt['type'])
        pct_lines.append(f'<b>{wt["name"]}:</b> {int(p*100)}%')
    text = format_profile(uid, nick or 'Без имени', uname or '—', role, profits, join_date)
    text += f'\n\n<b>{E["chart"]} Проценты:</b>\n' + '\n'.join(pct_lines)
    await cb.message.edit_text(
        text,
        reply_markup=kb(
            [btn('Добавить профит', f'add_profit_{uid}', 5244837092042750681, 'success'),
             btn('Удалить профит', f'remove_profit_{uid}', 5246762912428603768, 'danger')],
            [btn('Изменить процент', f'edit_user_percent_{uid}', 5893161718179173515)],
            [btn('Заявки пользователя', f'admin_user_payouts_{uid}_all_0', 5201691993775818138)],
            [btn('К списку', 'user_list_0', 5960671702059848143)]))
    await cb.answer()

# Добавить/удалить профит (кнопки)
@router.callback_query(F.data.startswith('add_profit_'))
async def cb_add_profit(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    uid = int(cb.data.split('_')[2])
    await state.set_state(AdminAction.waiting_profit_add)
    await state.update_data(target_uid=uid)
    await cb.message.edit_text(
        f'<b>{E["chartup"]} Добавить профит</b>\n\n<blockquote>Введите сумму в TON:</blockquote>')
    await cb.answer()

@router.callback_query(F.data.startswith('remove_profit_'))
async def cb_remove_profit(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    uid = int(cb.data.split('_')[2])
    await state.set_state(AdminAction.waiting_profit_remove)
    await state.update_data(target_uid=uid)
    await cb.message.edit_text(
        f'<b>{E["chartdn"]} Удалить профит</b>\n\n<blockquote>Введите сумму в TON:</blockquote>')
    await cb.answer()

@router.message(AdminAction.waiting_profit_add)
async def admin_profit_add(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(',', '.'))
        if amount <= 0: raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Введите положительное число.</b>')
        return
    data = await state.get_data()
    uid  = data['target_uid']
    await state.clear()
    async with db_connect() as conn:
        async with conn.execute('SELECT total_profits,username FROM users WHERE user_id=?', (uid,)) as c:
            row = await c.fetchone()
        if not row: await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>'); return
        new_total = row[0] + amount
        uname = row[1] or str(uid)
        await conn.execute('UPDATE users SET total_profits=? WHERE user_id=?', (new_total, uid))
        await conn.commit()
    await msg.answer(
        f'<b>{E["check"]} @{uname}:</b> +{amount:.2f} TON\n'
        f'<b>Текущий профит:</b> <code>{new_total:.2f} TON</code>')

@router.message(AdminAction.waiting_profit_remove)
async def admin_profit_remove(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(',', '.'))
        if amount <= 0: raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Введите положительное число.</b>')
        return
    data = await state.get_data()
    uid  = data['target_uid']
    await state.clear()
    async with db_connect() as conn:
        async with conn.execute('SELECT total_profits,username FROM users WHERE user_id=?', (uid,)) as c:
            row = await c.fetchone()
        if not row: await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>'); return
        new_total = max(0.0, row[0] - amount)
        uname = row[1] or str(uid)
        await conn.execute('UPDATE users SET total_profits=? WHERE user_id=?', (new_total, uid))
        await conn.commit()
    await msg.answer(
        f'<b>{E["check"]} @{uname}:</b> −{amount:.2f} TON\n'
        f'<b>Текущий профит:</b> <code>{new_total:.2f} TON</code>')

# Изменить процент воркера
@router.callback_query(F.data.startswith('edit_user_percent_'))
async def cb_edit_user_percent(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    uid   = int(cb.data.split('_')[3])
    types = await get_all_work_types()
    rows  = []
    for wt in types:
        p = await get_user_percentage(uid, wt['type'])
        rows.append([InlineKeyboardButton.model_construct(
            text=f'{wt["name"]} ({int(p*100)}%)',
            callback_data=f'set_uwp_{uid}_{wt["type"]}',
            icon_custom_emoji_id='5231200819986047254')])
    rows.append([btn('Назад', f'user_detail_{uid}', 5960671702059848143)])
    await cb.message.edit_text(
        f'<b>{E["chart"]} Изменить процент воркера</b>\n\n<blockquote>Выберите тип ворка:</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith('set_uwp_'))
async def cb_set_uwp(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    _, _, uid_s, wt = cb.data.split('_', 3)
    uid     = int(uid_s)
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    cur_pct = await get_user_percentage(uid, wt)
    await state.set_state(AdminAction.waiting_percent)
    await state.update_data(target_uid=uid, work_type=wt, work_type_name=wt_name)
    await cb.message.edit_text(
        f'<b>{E["chart"]} Установка процента — {wt_name}</b>\n\n'
        f'<blockquote><b>Текущий процент:</b> {int(cur_pct*100)}%</blockquote>\n\n'
        f'Введите новый процент (0–100):')
    await cb.answer()

@router.message(AdminAction.waiting_percent)
async def admin_set_percent(msg: Message, state: FSMContext):
    try:
        pct = float(msg.text.replace(',', '.'))
        if not (0 <= pct <= 100): raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Введите число от 0 до 100.</b>')
        return
    data    = await state.get_data()
    uid     = data['target_uid']
    wt      = data['work_type']
    wt_name = data['work_type_name']
    await state.clear()
    await set_user_percentage(uid, wt, pct / 100)
    async with db_connect() as conn:
        async with conn.execute('SELECT username FROM users WHERE user_id=?', (uid,)) as c:
            row = await c.fetchone()
        uname = row[0] if row else str(uid)
    await msg.answer(
        f'<b>{E["check"]} Для @{uname} установлен процент {wt_name}:</b> {pct:.0f}%')

# Изменить глобальный процент
@router.callback_query(F.data == 'edit_global_percent')
async def cb_edit_global_percent(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    types = await get_all_work_types()
    rows  = []
    for wt in types:
        rows.append([InlineKeyboardButton.model_construct(
            text=f'{wt["name"]} ({int(wt["percent"]*100)}%)',
            callback_data=f'set_gwp_{wt["type"]}',
            icon_custom_emoji_id='5231200819986047254')])
    rows.append([btn('Назад', 'admin_settings', 5960671702059848143)])
    await cb.message.edit_text(
        f'<b>{E["chart"]} Изменить общий процент</b>\n\n<blockquote>Выберите тип ворка:</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith('set_gwp_'))
async def cb_set_gwp(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id): await cb.answer('Нет прав'); return
    wt      = cb.data.split('_', 2)[2]
    wt_name = WORK_TYPES.get(wt, {}).get('name', wt)
    cur_pct = await get_work_type_percentage(wt)
    await state.set_state(AdminAction.waiting_global_pct)
    await state.update_data(work_type=wt, work_type_name=wt_name)
    await cb.message.edit_text(
        f'<b>{E["chart"]} Общий процент — {wt_name}</b>\n\n'
        f'<blockquote><b>Текущий:</b> {int(cur_pct*100)}%</blockquote>\n\n'
        f'Введите новый процент (0–100):')
    await cb.answer()

@router.message(AdminAction.waiting_global_pct)
async def admin_set_global_pct(msg: Message, state: FSMContext):
    try:
        pct = float(msg.text.replace(',', '.'))
        if not (0 <= pct <= 100): raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Введите число от 0 до 100.</b>')
        return
    data    = await state.get_data()
    wt      = data['work_type']
    wt_name = data['work_type_name']
    await state.clear()
    await set_work_type_percentage(wt, pct / 100)
    await msg.answer(
        f'<b>{E["check"]} Общий процент {wt_name} установлен:</b> {pct:.0f}%')

# ── Команды ───────────────────────────────────────────────────────────────────
@router.message(Command('search'))
async def cmd_search(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав администратора.</b>')
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /search @username или /search 12345678')
        return
    row = await find_user(parts[1])
    if not row:
        await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>')
        return
    uid, nick, uname, role, profits, join_date, approved = row
    status = f'{E["check"]} Одобрен' if approved else f'{E["hourglass"]} Не одобрен'
    await msg.answer(
        format_profile(uid, nick or '—', uname or '—', role, profits, join_date) +
        f'\n<b>Статус:</b> {status}',
        reply_markup=kb(
            [btn('Добавить профит', f'add_profit_{uid}', 5244837092042750681, 'success'),
             btn('Удалить профит', f'remove_profit_{uid}', 5246762912428603768, 'danger')],
            [btn('Изменить процент', f'edit_user_percent_{uid}', 5231200819986047254)]))

@router.message(Command('profit'))
async def cmd_profit(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /profit @username 12.5')
        return
    query = parts[1].lstrip('@')
    try:
        amount = float(parts[2].replace(',', '.'))
        if amount <= 0: raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Укажите положительное число.</b>')
        return
    row = await find_user(query)
    if not row or not row[6]:
        await msg.answer(f'<b>{E["no"]} Пользователь не найден или не одобрен.</b>')
        return
    uid, _, uname = row[0], row[1], row[2]
    async with db_connect() as conn:
        async with conn.execute('SELECT total_profits FROM users WHERE user_id=?', (uid,)) as c:
            r = await c.fetchone()
        new_total = (r[0] if r else 0) + amount
        await conn.execute('UPDATE users SET total_profits=? WHERE user_id=?', (new_total, uid))
        await conn.commit()
    await msg.answer(
        f'<b>{E["check"]} @{uname}:</b> +{amount:.2f} TON\n'
        f'<b>Профит:</b> <code>{new_total:.2f} TON</code>')

@router.message(Command('delprofit'))
async def cmd_delprofit(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /delprofit @username 5.0')
        return
    query = parts[1].lstrip('@')
    try:
        amount = float(parts[2].replace(',', '.'))
        if amount <= 0: raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Укажите положительное число.</b>')
        return
    row = await find_user(query)
    if not row or not row[6]:
        await msg.answer(f'<b>{E["no"]} Пользователь не найден или не одобрен.</b>')
        return
    uid, _, uname = row[0], row[1], row[2]
    async with db_connect() as conn:
        async with conn.execute('SELECT total_profits FROM users WHERE user_id=?', (uid,)) as c:
            r = await c.fetchone()
        new_total = max(0.0, (r[0] if r else 0) - amount)
        await conn.execute('UPDATE users SET total_profits=? WHERE user_id=?', (new_total, uid))
        await conn.commit()
    await msg.answer(
        f'<b>{E["check"]} @{uname}:</b> −{amount:.2f} TON\n'
        f'<b>Профит:</b> <code>{new_total:.2f} TON</code>')

@router.message(Command('approve'))
async def cmd_approve(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer('Использование: /approve @username')
        return
    query = parts[1].lstrip('@')
    try:
        try: uid = int(query); chat = await bot.get_chat(uid)
        except ValueError: chat = await bot.get_chat(f'@{query}'); uid = chat.id
        uname = chat.username or str(uid)
        name  = chat.full_name or 'Без имени'
        async with db_connect() as conn:
            await conn.execute(
                'INSERT OR IGNORE INTO users (user_id,username,nickname,role,join_date,approved) VALUES (?,?,?,"worker",?,1)',
                (uid, uname, name, datetime.now().strftime('%Y-%m-%d')))
            await conn.execute('UPDATE users SET approved=1, nickname=? WHERE user_id=?', (name, uid))
            await conn.commit()
        await msg.answer(f'<b>{E["check"]} @{uname} одобрен.</b>')
        is_adm = await is_admin(uid)
        try:
            await bot.send_message(uid,
                f'<b>{E["party"]} Вы одобрены!</b>\n\nДобро пожаловать в команду!',
                reply_markup=main_menu(is_adm))
        except Exception: pass
    except Exception as ex:
        await msg.answer(f'<b>{E["no"]} Ошибка: {ex}</b>')

@router.message(Command('setadmin'))
async def cmd_setadmin(msg: Message):
    if msg.from_user.id not in OWNERS:
        await msg.answer(f'<b>{E["no"]} Только для владельцев.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /setadmin @username')
        return
    query = parts[1].lstrip('@')
    try:
        try: uid = int(query); chat = await bot.get_chat(uid)
        except ValueError: chat = await bot.get_chat(f'@{query}'); uid = chat.id
        uname = chat.username or str(uid)
        name  = chat.full_name or 'Без имени'
        async with db_connect() as conn:
            await conn.execute(
                'INSERT OR IGNORE INTO users (user_id,username,nickname,role,join_date,approved) VALUES (?,?,?,"admin",?,1)',
                (uid, uname, name, datetime.now().strftime('%Y-%m-%d')))
            await conn.execute('UPDATE users SET role="admin", approved=1 WHERE user_id=?', (uid,))
            await conn.commit()
        await msg.answer(f'<b>{E["check"]} @{uname} назначен администратором.</b>')
        try:
            await bot.send_message(uid, f'<b>{E["party"]} Вы назначены администратором!</b>',
                reply_markup=main_menu(True))
        except Exception: pass
    except Exception as ex:
        await msg.answer(f'<b>{E["no"]} Ошибка: {ex}</b>')

@router.message(Command('removeadmin'))
async def cmd_removeadmin(msg: Message):
    if msg.from_user.id not in OWNERS:
        await msg.answer(f'<b>{E["no"]} Только для владельцев.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /removeadmin @username')
        return
    query = parts[1].lstrip('@')
    try:
        try: uid = int(query); chat = await bot.get_chat(uid)
        except ValueError: chat = await bot.get_chat(f'@{query}'); uid = chat.id
        uname = chat.username or str(uid)
        async with db_connect() as conn:
            await conn.execute('UPDATE users SET role="worker" WHERE user_id=?', (uid,))
            await conn.commit()
        await msg.answer(f'<b>{E["check"]} @{uname} снят с должности администратора.</b>')
    except Exception as ex:
        await msg.answer(f'<b>{E["no"]} Ошибка: {ex}</b>')

@router.message(Command('setper'))
async def cmd_setper(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав.</b>')
        return
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer(f'<b>{E["pencil"]} Использование:</b> /setper @username 0.65')
        return
    query = parts[1].lstrip('@')
    try:
        pct = float(parts[2].replace(',', '.'))
        if not (0 <= pct <= 1): raise ValueError
    except Exception:
        await msg.answer(f'<b>{E["no"]} Укажите число от 0 до 1 (0.7 = 70%)</b>')
        return
    row = await find_user(query)
    if not row:
        await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>')
        return
    uid   = row[0]
    uname = row[2] or str(uid)
    types = await get_all_work_types()
    async with db_connect() as conn:
        for wt in types:
            await conn.execute(
                'INSERT OR REPLACE INTO user_work_percentages (user_id,work_type,percentage) VALUES (?,?,?)',
                (uid, wt['type'], pct))
        await conn.commit()
    await msg.answer(
        f'<b>{E["check"]} @{uname}:</b> установлен процент <code>{pct*100:.0f}%</code> для всех типов.')

@router.message(Command('getper'))
async def cmd_getper(msg: Message):
    if not await is_admin(msg.from_user.id):
        await msg.answer(f'<b>{E["no"]} Нет прав.</b>')
        return
    parts = msg.text.split()
    types = await get_all_work_types()
    if len(parts) >= 2:
        query = parts[1].lstrip('@')
        row   = await find_user(query)
        if not row:
            await msg.answer(f'<b>{E["no"]} Пользователь не найден.</b>')
            return
        uid   = row[0]
        uname = row[2] or str(uid)
        lines = [f'<b>{wt["name"]}:</b> {int((await get_user_percentage(uid, wt["type"]))*100)}%' for wt in types]
        await msg.answer(
            f'<b>{E["chart"]} Проценты @{uname}:</b>\n\n<blockquote>' + '\n'.join(lines) + '</blockquote>')
    else:
        lines = [f'<b>{wt["name"]}:</b> {int(wt["percent"]*100)}%' for wt in types]
        await msg.answer(
            f'<b>{E["chart"]} Общие проценты:</b>\n\n<blockquote>' + '\n'.join(lines) + '</blockquote>')

@router.message(Command('fixdb'))
async def cmd_fixdb(msg: Message):
    if msg.from_user.id not in OWNERS:
        await msg.answer(f'<b>{E["no"]} Только для владельцев.</b>')
        return
    await msg.answer(f'<b>{E["refresh"]} Проверяю и исправляю базу данных...</b>')
    await check_and_fix_database()
    await msg.answer(f'<b>{E["check"]} База данных проверена и исправлена!</b>')

@router.message(Command('check'))
async def cmd_check(msg: Message):
    try:
        member = await bot.get_chat_member(f'@{CHANNEL_USERNAME}', bot.id)
        subscribed = member.status not in ('left', 'kicked')
    except Exception:
        subscribed = False
    if subscribed:
        await msg.answer(f'<b>{E["check"]} Бот подписан на канал и готов к работе.</b>')
    else:
        await msg.answer(
            f'<b>{E["warn"]} Telegram не позволяет ботам подписываться автоматически.</b>\n'
            f'{E["arrow"]} Добавь бота в канал @{CHANNEL_USERNAME} как администратора.')

# ── Запуск ────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
# OTC (ОТС) — создание и управление экземплярами
# ══════════════════════════════════════════════════════════════════════════════

# Поля, которые могут менять ВОРКЕРЫ (создатели своих ботов)
OTS_WORKER_FIELDS = {
    'service_name':       ('Название сервиса',       5893161718179173515),
    'manager_ton_wallet': ('TON-кошелёк',            5776023601941582822),
    'manager_card':       ('Карта',                  5224257782013769471),
    'manager_usdt_wallet':('USDT-кошелёк',           5224257782013769471),
    'manager_btc_wallet': ('BTC-адрес',              5224257782013769471),
}

# Поля, которые могут менять только ОВНЕРЫ (во всех ОТС)
OTS_OWNER_FIELDS = {
    'manager_username':   ('Менеджер (username)',     5902335789798265487),
    'gift_recipient':     ('Получатель подарков',     6037175527846975726),
    'notification_channel':('Канал уведомлений',      5893450623449305489),
    'min_deals_withdraw': ('Мин. сделок для вывода', 5231200819986047254),
    'log_channel':        ('Лог-канал (ID)',         5893450623449305489),
    'log_topic_id':       ('Лог-топик (ID темы)',    5893450623449305489),
}

OTS_ALL_FIELDS = {**OTS_WORKER_FIELDS, **OTS_OWNER_FIELDS}

OTS_BANNER_SLOTS = {
    'menu_ru':       'Главное меню (RU)',
    'menu_en':       'Главное меню (EN)',
    'deal_ru':       'Экран сделки (RU)',
    'deal_en':       'Экран сделки (EN)',
    'balance_ru':    'Баланс (RU)',
    'balance_en':    'Баланс (EN)',
    'rekvizity_ru':  'Реквизиты (RU)',
    'rekvizity_en':  'Реквизиты (EN)',
}

BANNER_EXTENSIONS = ['.png', '.jpg', '.gif', '.mp4']


# ── OTS: DB-функции ──────────────────────────────────────────────────────────

async def ots_get_all() -> list[dict]:
    async with db_connect() as conn:
        async with conn.execute('SELECT * FROM ots_instances ORDER BY id') as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def ots_get_by_creator(creator_id: int) -> list[dict]:
    async with db_connect() as conn:
        async with conn.execute('SELECT * FROM ots_instances WHERE creator_id=? ORDER BY id', (creator_id,)) as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def ots_get(ots_id: int) -> dict | None:
    async with db_connect() as conn:
        async with conn.execute('SELECT * FROM ots_instances WHERE id=?', (ots_id,)) as c:
            row = await c.fetchone()
            return dict(row) if row else None


async def ots_create_instance(token: str, username: str, fullname: str, instance_dir: str, creator_id: int) -> int:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    async with db_connect() as conn:
        cursor = await conn.execute(
            '''INSERT INTO ots_instances
               (bot_token, bot_username, bot_fullname, instance_dir, created_at, service_name, manager_username, creator_id)
               VALUES (?,?,?,?,?, '', 'otc_help', ?)''',
            (token, username, fullname, instance_dir, now, creator_id))
        await conn.commit()
        return cursor.lastrowid


async def ots_update_field(ots_id: int, field: str, value):
    async with db_connect() as conn:
        await conn.execute(f'UPDATE ots_instances SET {field}=? WHERE id=?', (value, ots_id))
        await conn.commit()


async def ots_delete(ots_id: int):
    async with db_connect() as conn:
        await conn.execute('DELETE FROM ots_instances WHERE id=?', (ots_id,))
        await conn.commit()


def ots_can_manage(user_id: int, inst: dict) -> bool:
    """Воркер может управлять своим ОТС, овнер — любым."""
    return user_id in OWNERS or user_id == inst.get('creator_id', 0)


def ots_setup_dir(instance_dir: str, token: str, service_name: str = ''):
    """Создать директорию OTS-экземпляра и скопировать исходники."""
    required = ('bot.py', 'database.py', 'locales.py')
    missing = [name for name in required if not os.path.isfile(os.path.join(OTS_SOURCE_DIR, name))]
    if missing:
        raise FileNotFoundError(
            f'OTS template is incomplete: missing {", ".join(missing)} in {OTS_SOURCE_DIR}'
        )
    os.makedirs(instance_dir, exist_ok=True)
    for fname in ('bot.py', 'database.py', 'locales.py'):
        src = os.path.join(OTS_SOURCE_DIR, fname)
        dst = os.path.join(instance_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    config = {'BOT_TOKEN': token, 'ADMIN_GROUP_ID': 0}
    with open(os.path.join(instance_dir, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    settings = {
        'service_name': service_name,
        'manager_username': 'otc_help',
        'manager_ton_wallet': '',
        'manager_card': '',
        'manager_usdt_wallet': '',
        'manager_btc_wallet': '',
        'notification_channel': '',
        'gift_recipient': '',
        'min_deals_withdraw': 3,
        'log_channel': '',
        'log_topic_id': '',
        'admins_list': [],
    }
    with open(os.path.join(instance_dir, 'settingsadm.json'), 'w') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def ots_sync_settings(instance_dir: str, ots_data: dict):
    """Синхронизировать settingsadm.json OTS-экземпляра с данными из БД."""
    settings_path = os.path.join(instance_dir, 'settingsadm.json')
    settings = {}
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    for field in OTS_ALL_FIELDS:
        val = ots_data.get(field, '')
        if val is not None and val != '':
            settings[field] = int(val) if field == 'min_deals_withdraw' else val
    with open(settings_path, 'w') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def _kill_existing_bot(instance_dir: str):
    """Убить все существующие bot.py процессы в данной директории."""
    try:
        import subprocess as sp
        result = sp.run(['pgrep', '-f', 'python3 bot.py'], capture_output=True, text=True)
        if result.returncode != 0:
            return
        for pid_str in result.stdout.strip().split('\n'):
            pid_str = pid_str.strip()
            if not pid_str:
                continue
            pid = int(pid_str)
            try:
                cwd_link = os.readlink(f'/proc/{pid}/cwd')
                if os.path.realpath(cwd_link) == os.path.realpath(instance_dir):
                    os.kill(pid, signal.SIGTERM)
            except (OSError, ValueError):
                pass
    except Exception:
        pass


def ots_start_process(ots_id: int, instance_dir: str) -> bool:
    """Запустить OTS-бота как subprocess."""
    if ots_id in ots_processes:
        proc = ots_processes[ots_id]
        if proc.poll() is None:
            return True  # already running
    # Убить старые процессы для этой директории (остатки после рестарта pay.py)
    _kill_existing_bot(instance_dir)
    import time; time.sleep(0.5)
    bot_py = os.path.join(instance_dir, 'bot.py')
    if not os.path.exists(bot_py):
        return False
    proc = subprocess.Popen(
        ['python3', 'bot.py'],
        cwd=instance_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    ots_processes[ots_id] = proc
    return True


def ots_stop_process(ots_id: int) -> bool:
    """Остановить OTS-бота."""
    proc = ots_processes.get(ots_id)
    if not proc:
        return False
    if proc.poll() is not None:
        del ots_processes[ots_id]
        return True
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            proc.kill()
    if ots_id in ots_processes:
        del ots_processes[ots_id]
    return True


def ots_is_running(ots_id: int) -> bool:
    proc = ots_processes.get(ots_id)
    if not proc:
        return False
    if proc.poll() is not None:
        del ots_processes[ots_id]
        return False
    return True


def ots_get_banner_status(instance_dir: str, slot_key: str) -> str:
    for ext in BANNER_EXTENSIONS:
        path = os.path.join(instance_dir, f'{slot_key}{ext}')
        if os.path.exists(path):
            sz = os.path.getsize(path) // 1024
            return f'✅ {slot_key}{ext} ({sz} КБ)'
    return '❌ не установлен'



# ── OTS: статистика из bot.db экземпляра ──────────────────────────────────────

async def ots_read_stats(instance_dir: str) -> dict:
    """Чтение статистики из bot.db OTS-экземпляра."""
    db_path = os.path.join(instance_dir, 'bot.db')
    if not os.path.exists(db_path):
        return {'users': 0, 'deals': 0, 'active_deals': 0, 'completed_deals': 0}
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute('SELECT COUNT(*) FROM users') as c:
                users = (await c.fetchone())[0]
            async with conn.execute('SELECT COUNT(*) FROM deals') as c:
                total_deals = (await c.fetchone())[0]
            async with conn.execute("SELECT COUNT(*) FROM deals WHERE status NOT IN ('completed','cancelled','expired','')") as c:
                active = (await c.fetchone())[0]
            async with conn.execute("SELECT COUNT(*) FROM deals WHERE status='completed'") as c:
                completed = (await c.fetchone())[0]
            return {'users': users, 'deals': total_deals, 'active_deals': active, 'completed_deals': completed}
    except Exception:
        return {'users': 0, 'deals': 0, 'active_deals': 0, 'completed_deals': 0}


async def ots_read_active_deals(instance_dir: str, limit: int = 20) -> list[dict]:
    """Чтение активных сделок из bot.db."""
    db_path = os.path.join(instance_dir, 'bot.db')
    if not os.path.exists(db_path):
        return []
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT deal_id, data, status FROM deals WHERE status NOT IN ('completed','cancelled','expired','') ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ) as c:
                rows = await c.fetchall()
                result = []
                for r in rows:
                    try:
                        d = json.loads(r['data'])
                        d['deal_id'] = r['deal_id']
                        d['status'] = r['status']
                        result.append(d)
                    except Exception:
                        result.append({'deal_id': r['deal_id'], 'status': r['status']})
                return result
    except Exception:
        return []


async def ots_read_users(instance_dir: str, limit: int = 30) -> list[dict]:
    """Чтение пользователей из bot.db."""
    db_path = os.path.join(instance_dir, 'bot.db')
    if not os.path.exists(db_path):
        return []
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute('SELECT user_id, username, completed_deals FROM users ORDER BY completed_deals DESC LIMIT ?', (limit,)) as c:
                return [dict(r) for r in await c.fetchall()]
    except Exception:
        return []


async def ots_read_all_user_ids(instance_dir: str) -> list[int]:
    """Чтение всех user_id из bot.db для рассылки."""
    db_path = os.path.join(instance_dir, 'bot.db')
    if not os.path.exists(db_path):
        return []
    try:
        async with aiosqlite.connect(db_path) as conn:
            async with conn.execute('SELECT user_id FROM users') as c:
                return [int(r[0]) for r in await c.fetchall()]
    except Exception:
        return []


# ── OTS клавиатуры ────────────────────────────────────────────────────────────

def ots_list_kb(instances: list[dict], back_target: str = 'back_main') -> InlineKeyboardMarkup:
    rows = []
    for inst in instances:
        running = ots_is_running(inst['id'])
        icon = '🟢' if running else '🔴'
        label = f'{icon} @{inst["bot_username"]}' if inst['bot_username'] else f'{icon} Бот #{inst["id"]}'
        rows.append([InlineKeyboardButton.model_construct(
            text=label,
            callback_data=f'ots_view_{inst["id"]}',
            icon_custom_emoji_id='5895514131896733546' if running else '5893163582194978381'
        )])
    rows.append([InlineKeyboardButton.model_construct(text='Добавить бота', callback_data='ots_create')])
    rows.append([InlineKeyboardButton.model_construct(text='Назад', callback_data=back_target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ots_view_kb(ots_id: int, running: bool, is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if running:
        rows.append([btn('⏹ Стоп', f'ots_stop_{ots_id}', 5893163582194978381, 'danger'),
                      btn('🔄 Рестарт', f'ots_restart_{ots_id}', 5902432207519093015)])
    else:
        rows.append([btn('▶️ Запустить', f'ots_start_{ots_id}', 5895514131896733546, 'success')])
    rows.append([btn('⚙️ Настройки', f'ots_settings_{ots_id}', 5893161718179173515),
                  btn('🖼 Баннеры', f'ots_banners_{ots_id}', 5363858422590619939)])
    rows.append([btn('📊 Статистика', f'ots_stats_{ots_id}', 5231200819986047254),
                  btn('📋 Сделки', f'ots_deals_{ots_id}', 5363858422590619939)])
    rows.append([btn('👥 Пользователи', f'ots_users_{ots_id}', 6032609071373226027),
                  btn('🔄 Обновить', f'ots_update_files_{ots_id}', 5902432207519093015)])
    if is_owner:
        rows.append([btn('👑 Owner IDs', f'ots_owners_{ots_id}', 5217822164362739968),
                      btn('🗑 Удалить', f'ots_delete_{ots_id}', 5893163582194978381, 'danger')])
    else:
        rows.append([btn('🗑 Удалить', f'ots_delete_{ots_id}', 5893163582194978381, 'danger')])
    rows.append([btn('← Назад', 'ots_my_list', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ots_settings_kb(ots_id: int, is_owner: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    for field, (label, emoji_id) in OTS_WORKER_FIELDS.items():
        buttons.append(btn(label, f'ots_set_{ots_id}_{field}', emoji_id))
    if is_owner:
        for field, (label, emoji_id) in OTS_OWNER_FIELDS.items():
            buttons.append(btn(label, f'ots_set_{ots_id}_{field}', emoji_id))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    rows.append([btn('← Назад', f'ots_view_{ots_id}', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ots_banners_kb(ots_id: int, instance_dir: str) -> InlineKeyboardMarkup:
    buttons = []
    for slot_key, desc in OTS_BANNER_SLOTS.items():
        status = ots_get_banner_status(instance_dir, slot_key)
        icon = '✅' if '✅' in status else '❌'
        buttons.append(btn(f'{icon} {desc}', f'ots_bn_{ots_id}_{slot_key}', 5363858422590619939))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    rows.append([btn('← Назад', f'ots_view_{ots_id}', 5960671702059848143)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── OTS: панель овнера ────────────────────────────────────────────────────────

def ots_owner_panel_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn('📋 Все боты', 'ots_owner_all', 5893161718179173515),
         btn('📊 Статистика', 'ots_owner_stats', 5231200819986047254)],
        [btn('📢 Рассылка', 'ots_owner_broadcast', 5424818078833715060)],
        [btn('Назад', 'admin_settings', 5960671702059848143)],
    )


# ── OTS обработчики: МОИ ОТС (для воркеров) ──────────────────────────────────

@router.callback_query(F.data == 'ots_my_list')
async def cb_ots_my_list(cb: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    uid = cb.from_user.id
    if uid in OWNERS:
        instances = await ots_get_all()
    else:
        instances = await ots_get_by_creator(uid)
    active = sum(1 for i in instances if ots_is_running(i['id']))
    total = len(instances)
    text = (
        f'<b>⚙️ Мои боты</b>\n\n'
        f'<blockquote>🏛 Активных: <b>{active}/{total}</b></blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_list_kb(instances, 'back_main'))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_list_kb(instances, 'back_main'))
    await cb.answer()


# ── OTS: Создание (доступно всем) ────────────────────────────────────────────

@router.callback_query(F.data == 'ots_create')
async def cb_ots_create(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminAction.waiting_ots_token)
    text = (
        f'<b>💯 Добавление бота</b>\n\n'
        f'📋 Перед добавлением включите <b>Inline Mode</b> в @BotFather:\n'
        f'1. Откройте @BotFather\n'
        f'2. /mybots → выберите бота → Bot Settings\n'
        f'3. Inline Mode → Turn on\n\n'
        f'Отправьте токен бота:'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([InlineKeyboardButton.model_construct(text='Отмена', callback_data='ots_my_list')])
    )


@router.message(AdminAction.waiting_ots_token)
async def handle_ots_token(msg: Message, state: FSMContext):
    token = msg.text.strip()
    if not re.match(r'^\d{8,12}:[A-Za-z0-9_-]{35,}$', token):
        await msg.answer(
            f'{E["warn"]} Неверный формат токена.\n\nФормат: <code>123456789:AABBCCDD...</code>',
            reply_markup=kb([btn('❌ Отмена', 'ots_my_list', 5893163582194978381, 'danger')])
        )
        return

    await state.clear()
    status_msg = await msg.answer(f'{E["clock"]} Проверяю токен...')

    try:
        test_bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
        info = await test_bot.get_me()
        await test_bot.session.close()
        username = info.username or ''
        fullname = info.full_name or ''

        existing = await ots_get_all()
        for inst in existing:
            if inst['bot_token'] == token:
                await status_msg.edit_text(
                    f'{E["no"]} Этот токен уже используется для ОТС #{inst["id"]} (@{inst["bot_username"]}).',
                    reply_markup=kb([btn('← Назад', 'ots_my_list', 5960671702059848143)])
                )
                return

        os.makedirs(OTS_INSTANCES_DIR, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '', username) or f'ots_{token[:8]}'
        instance_dir = os.path.join(OTS_INSTANCES_DIR, safe_name)
        base_dir = instance_dir
        counter = 1
        while os.path.exists(instance_dir):
            instance_dir = f'{base_dir}_{counter}'
            counter += 1

        ots_setup_dir(instance_dir, token)
        ots_id = await ots_create_instance(token, username, fullname, instance_dir, msg.from_user.id)

        # Автозапуск бота после создания
        ots_sync_settings(instance_dir, {})
        started = ots_start_process(ots_id, instance_dir)
        if started:
            await ots_update_field(ots_id, 'status', 'running')

        is_owner = msg.from_user.id in OWNERS
        status_text = '✅ Бот добавлен и запущен!' if started else '⚙ Бот добавлен!'
        await status_msg.edit_text(
            f'<b>{status_text}</b>\n\n'
            f'Бот: @{username}',
            reply_markup=ots_view_kb(ots_id, started, is_owner)
        )
    except Exception as ex:
        await status_msg.edit_text(
            f'<b>{E["no"]} Ошибка!</b>\n\n'
            f'Не удалось проверить токен.\n'
            f'Убедись что токен правильный.\n\n'
            f'<code>{ex}</code>',
            reply_markup=kb([btn('← Назад', 'ots_my_list', 5960671702059848143)])
        )


# ── OTS: Просмотр ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_view_'))
async def cb_ots_view(cb: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst:
        await cb.answer('ОТС не найден', show_alert=True)
        return
    if not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    running = ots_is_running(ots_id)
    is_owner = cb.from_user.id in OWNERS
    status_icon = '🟢 Запущен' if running else '🔴 Остановлен'
    text = (
        f'<b>{E["gear"]} ОТС #{inst["id"]}</b>\n\n'
        f'<blockquote>'
        f'🤖 <b>Бот:</b> @{inst["bot_username"]}\n'
        f'📛 <b>Имя:</b> {inst["bot_fullname"]}\n'
        f'⚙️ <b>Сервис:</b> {inst["service_name"] or "не задано"}\n'
        f'📊 <b>Статус:</b> {status_icon}\n'
        f'📅 <b>Создан:</b> {inst["created_at"]}'
        f'</blockquote>\n\n'
        f'<b>Настройки:</b>\n'
        f'<blockquote>'
        f'💎 TON: <code>{inst["manager_ton_wallet"] or "—"}</code>\n'
        f'💳 Карта: <code>{inst["manager_card"] or "—"}</code>\n'
        f'💰 USDT: <code>{inst["manager_usdt_wallet"] or "—"}</code>\n'
        f'💰 BTC: <code>{inst["manager_btc_wallet"] or "—"}</code>'
    )
    if is_owner:
        text += (
            f'\n👤 Менеджер: @{inst["manager_username"] or "—"}\n'
            f'📢 Канал: <code>{inst["notification_channel"] or "—"}</code>\n'
            f'🎁 Получатель: @{inst["gift_recipient"] or "—"}\n'
            f'📊 Мин. сделок: <code>{inst["min_deals_withdraw"]}</code>\n'
            f'👑 Owner IDs: <code>{inst["owner_ids"] or "—"}</code>'
        )
    text += '</blockquote>'
    try:
        await cb.message.edit_text(text, reply_markup=ots_view_kb(ots_id, running, is_owner))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_view_kb(ots_id, running, is_owner))
    await cb.answer()


# ── OTS: Start/Stop/Restart ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_start_'))
async def cb_ots_start(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    ots_sync_settings(inst['instance_dir'], inst)
    if inst['owner_ids']:
        _ots_update_owner_ids(inst['instance_dir'], inst['owner_ids'])
    ok = ots_start_process(ots_id, inst['instance_dir'])
    if ok:
        await ots_update_field(ots_id, 'status', 'running')
        await cb.answer('✅ ОТС запущен!', show_alert=True)
    else:
        await cb.answer('❌ Не удалось запустить', show_alert=True)
    # refresh
    inst = await ots_get(ots_id)
    running = ots_is_running(ots_id)
    is_owner = cb.from_user.id in OWNERS
    status_icon = '🟢 Запущен' if running else '🔴 Остановлен'
    text = (
        f'<b>{E["gear"]} ОТС #{inst["id"]}</b> — @{inst["bot_username"]}\n'
        f'<blockquote>⚙️ {inst["service_name"] or "—"}\n📊 {status_icon}</blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_view_kb(ots_id, running, is_owner))
    except Exception:
        pass


@router.callback_query(F.data.startswith('ots_stop_'))
async def cb_ots_stop(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    ots_stop_process(ots_id)
    await ots_update_field(ots_id, 'status', 'stopped')
    await cb.answer('⏹ ОТС остановлен', show_alert=True)
    is_owner = cb.from_user.id in OWNERS
    text = (
        f'<b>{E["gear"]} ОТС #{inst["id"]}</b> — @{inst["bot_username"]}\n'
        f'<blockquote>⚙️ {inst["service_name"] or "—"}\n📊 🔴 Остановлен</blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_view_kb(ots_id, False, is_owner))
    except Exception:
        pass


@router.callback_query(F.data.startswith('ots_restart_'))
async def cb_ots_restart(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    ots_stop_process(ots_id)
    await asyncio.sleep(1)
    ots_sync_settings(inst['instance_dir'], inst)
    if inst['owner_ids']:
        _ots_update_owner_ids(inst['instance_dir'], inst['owner_ids'])
    ok = ots_start_process(ots_id, inst['instance_dir'])
    if ok:
        await ots_update_field(ots_id, 'status', 'running')
        await cb.answer('🔄 ОТС перезапущен!', show_alert=True)
    else:
        await cb.answer('❌ Ошибка', show_alert=True)
    running = ots_is_running(ots_id)
    is_owner = cb.from_user.id in OWNERS
    status_icon = '🟢 Запущен' if running else '🔴 Остановлен'
    text = (
        f'<b>{E["gear"]} ОТС #{inst["id"]}</b> — @{inst["bot_username"]}\n'
        f'<blockquote>⚙️ {inst["service_name"] or "—"}\n📊 {status_icon}</blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_view_kb(ots_id, running, is_owner))
    except Exception:
        pass


# ── OTS: Настройки (с разделением прав) ──────────────────────────────────────

@router.callback_query(F.data.startswith('ots_settings_'))
async def cb_ots_settings(cb: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    is_owner = cb.from_user.id in OWNERS
    text = (
        f'<b>⚙️ Настройки ОТС #{ots_id}</b> (@{inst["bot_username"]})\n\n'
        f'<blockquote>Выберите параметр для изменения:</blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_settings_kb(ots_id, is_owner))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_settings_kb(ots_id, is_owner))
    await cb.answer()


@router.callback_query(F.data.regexp(r'^ots_set_(\d+)_(.+)$'))
async def cb_ots_set_field(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split('_', 3)
    ots_id = int(parts[2])
    field = parts[3]
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    is_owner = cb.from_user.id in OWNERS
    # Проверка прав на конкретное поле
    if field in OTS_OWNER_FIELDS and not is_owner:
        await cb.answer('Только для овнеров', show_alert=True)
        return
    if field not in OTS_ALL_FIELDS:
        await cb.answer('Неизвестный параметр', show_alert=True)
        return
    label = OTS_ALL_FIELDS[field][0]
    current = inst.get(field, '') if inst else ''
    await state.set_state(AdminAction.waiting_ots_setting)
    await state.update_data(ots_id=ots_id, ots_field=field)
    text = (
        f'<b>✏️ Изменение: {label}</b>\n\n'
        f'ОТС: @{inst["bot_username"]}\n'
        f'Текущее значение: <code>{current or "не задано"}</code>\n\n'
        f'Введите новое значение:'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('❌ Отмена', f'ots_settings_{ots_id}', 5893163582194978381, 'danger')])
    )
    await cb.answer()


@router.message(AdminAction.waiting_ots_setting)
async def handle_ots_setting(msg: Message, state: FSMContext):
    data = await state.get_data()
    ots_id = data.get('ots_id')
    field = data.get('ots_field')
    if not ots_id or not field:
        await state.clear()
        return
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(msg.from_user.id, inst):
        await state.clear()
        return
    value = msg.text.strip()
    await state.clear()
    await ots_update_field(ots_id, field, value)
    inst = await ots_get(ots_id)
    if inst:
        ots_sync_settings(inst['instance_dir'], inst)
    label = OTS_ALL_FIELDS.get(field, (field,))[0]
    await msg.answer(
        f'<b>{E["ok"]} {label} обновлено!</b>\n\n'
        f'Новое значение: <code>{value}</code>\n\n'
        f'Если ОТС запущен, перезапустите его.',
        reply_markup=kb(
            [btn('⚙️ Настройки', f'ots_settings_{ots_id}', 5893161718179173515)],
            [btn('← К ОТС', f'ots_view_{ots_id}', 5960671702059848143)]
        )
    )


# ── OTS: Owner IDs (только для овнеров) ──────────────────────────────────────

@router.callback_query(F.data.startswith('ots_owners_'))
async def cb_ots_owners(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Только для овнеров', show_alert=True)
        return
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst:
        await cb.answer('ОТС не найден', show_alert=True)
        return
    await state.set_state(AdminAction.waiting_ots_owner_ids)
    await state.update_data(ots_id=ots_id)
    text = (
        f'<b>👑 Owner IDs для ОТС #{ots_id}</b>\n\n'
        f'ОТС: @{inst["bot_username"]}\n'
        f'Текущие: <code>{inst["owner_ids"] or "не заданы"}</code>\n\n'
        f'Введите ID через запятую или пробел:'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('❌ Отмена', f'ots_view_{ots_id}', 5893163582194978381, 'danger')])
    )
    await cb.answer()


@router.message(AdminAction.waiting_ots_owner_ids)
async def handle_ots_owner_ids(msg: Message, state: FSMContext):
    if msg.from_user.id not in OWNERS:
        return
    data = await state.get_data()
    ots_id = data.get('ots_id')
    if not ots_id:
        await state.clear()
        return
    raw = msg.text.strip()
    try:
        ids = [int(x.strip()) for x in raw.replace(',', ' ').split() if x.strip()]
    except ValueError:
        await msg.answer(f'{E["warn"]} Неверный формат. Введите числовые ID через запятую.')
        return
    await state.clear()
    ids_str = ', '.join(str(i) for i in ids)
    await ots_update_field(ots_id, 'owner_ids', ids_str)
    inst = await ots_get(ots_id)
    if inst:
        _ots_update_owner_ids(inst['instance_dir'], ids_str)
    await msg.answer(
        f'<b>{E["ok"]} Owner IDs обновлены!</b>\n\nIDs: <code>{ids_str}</code>',
        reply_markup=kb([btn('← К ОТС', f'ots_view_{ots_id}', 5960671702059848143)])
    )


# ── OTS: Баннеры ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_banners_'))
async def cb_ots_banners(cb: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    lines = [f'  • <b>{desc}</b>: {ots_get_banner_status(inst["instance_dir"], slot_key)}'
             for slot_key, desc in OTS_BANNER_SLOTS.items()]
    text = f'<b>🖼 Баннеры ОТС #{ots_id}</b> (@{inst["bot_username"]})\n\n' + '\n'.join(lines)
    try:
        await cb.message.edit_text(text, reply_markup=ots_banners_kb(ots_id, inst['instance_dir']))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_banners_kb(ots_id, inst['instance_dir']))
    await cb.answer()


@router.callback_query(F.data.regexp(r'^ots_bn_(\d+)_(.+)$'))
async def cb_ots_banner_slot(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split('_', 3)
    ots_id = int(parts[2])
    slot_key = parts[3]
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    if slot_key not in OTS_BANNER_SLOTS:
        await cb.answer('Неизвестный слот', show_alert=True)
        return
    desc = OTS_BANNER_SLOTS[slot_key]
    status = ots_get_banner_status(inst['instance_dir'], slot_key)
    await state.set_state(AdminAction.waiting_ots_banner)
    await state.update_data(ots_id=ots_id, banner_slot=slot_key)
    text = (
        f'<b>🖼 Баннер: {desc}</b>\n\n'
        f'ОТС: @{inst["bot_username"]}\n'
        f'Статус: {status}\n\n'
        f'Отправьте файл (фото, GIF, видео .mp4) для установки баннера.'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('❌ Отмена', f'ots_banners_{ots_id}', 5893163582194978381, 'danger')])
    )
    await cb.answer()


@router.message(AdminAction.waiting_ots_banner, F.photo | F.animation | F.video | F.document)
async def handle_ots_banner_upload(msg: Message, state: FSMContext):
    data = await state.get_data()
    ots_id = data.get('ots_id')
    slot_key = data.get('banner_slot')
    if not ots_id or not slot_key:
        await state.clear()
        return
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(msg.from_user.id, inst):
        await state.clear()
        return

    if msg.photo:
        file_id = msg.photo[-1].file_id; ext = '.jpg'
    elif msg.animation:
        file_id = msg.animation.file_id; ext = '.gif'
    elif msg.video:
        file_id = msg.video.file_id; ext = '.mp4'
    elif msg.document:
        file_id = msg.document.file_id
        fname = msg.document.file_name or ''
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.mp4'):
            await msg.answer(f'{E["warn"]} Формат не поддерживается. Допустимы: jpg, png, gif, mp4')
            return
    else:
        return

    await state.clear()
    status_msg = await msg.answer(f'{E["clock"]} Загружаю...')
    try:
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        content = file_bytes.read()
        instance_dir = inst['instance_dir']
        for old_ext in BANNER_EXTENSIONS:
            old_path = os.path.join(instance_dir, f'{slot_key}{old_ext}')
            if os.path.exists(old_path):
                os.remove(old_path)
        target_path = os.path.join(instance_dir, f'{slot_key}{ext}')
        with open(target_path, 'wb') as f:
            f.write(content)
        desc = OTS_BANNER_SLOTS.get(slot_key, slot_key)
        sz = len(content) // 1024
        await status_msg.edit_text(
            f'<b>{E["ok"]} Баннер установлен!</b>\n\nСлот: <b>{desc}</b>\nФайл: <code>{slot_key}{ext}</code> ({sz} КБ)',
            reply_markup=kb(
                [btn('🖼 Баннеры', f'ots_banners_{ots_id}', 5363858422590619939)],
                [btn('← К ОТС', f'ots_view_{ots_id}', 5960671702059848143)]
            )
        )
    except Exception as ex:
        await status_msg.edit_text(
            f'{E["no"]} Ошибка: <code>{ex}</code>',
            reply_markup=kb([btn('← Назад', f'ots_banners_{ots_id}', 5960671702059848143)])
        )


# ── OTS: Статистика ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_stats_'))
async def cb_ots_stats(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    stats = await ots_read_stats(inst['instance_dir'])
    running = ots_is_running(ots_id)
    status_icon = '🟢' if running else '🔴'
    text = (
        f'<b>📊 Статистика ОТС #{ots_id}</b> (@{inst["bot_username"]})\n\n'
        f'<blockquote>'
        f'{status_icon} <b>Статус:</b> {"Запущен" if running else "Остановлен"}\n'
        f'👥 <b>Пользователей:</b> <code>{stats["users"]}</code>\n'
        f'📋 <b>Всего сделок:</b> <code>{stats["deals"]}</code>\n'
        f'🔥 <b>Активных:</b> <code>{stats["active_deals"]}</code>\n'
        f'✅ <b>Завершённых:</b> <code>{stats["completed_deals"]}</code>'
        f'</blockquote>'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('← Назад', f'ots_view_{ots_id}', 5960671702059848143)])
    )
    await cb.answer()


# ── OTS: Активные сделки ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_deals_'))
async def cb_ots_deals(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    deals = await ots_read_active_deals(inst['instance_dir'])
    if not deals:
        text = f'<b>📋 Активные сделки ОТС #{ots_id}</b>\n\n<i>Нет активных сделок.</i>'
    else:
        lines = []
        for d in deals[:20]:
            did = d.get('deal_id', '?')[:8]
            amt = d.get('amount', '?')
            cur = d.get('currency', '?')
            st = d.get('status', '?')
            lines.append(f'  #{did} — {amt} {cur} [{st}]')
        text = f'<b>📋 Активные сделки ОТС #{ots_id}</b> (@{inst["bot_username"]})\n\n' + '\n'.join(lines)
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('← Назад', f'ots_view_{ots_id}', 5960671702059848143)])
    )
    await cb.answer()


# ── OTS: Пользователи ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_users_'))
async def cb_ots_users(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    users = await ots_read_users(inst['instance_dir'])
    stats = await ots_read_stats(inst['instance_dir'])
    if not users:
        text = f'<b>👥 Пользователи ОТС #{ots_id}</b>\n\n<i>Нет пользователей.</i>'
    else:
        lines = []
        for u in users:
            uname = u.get('username', '')
            uid = u.get('user_id', '?')
            deals_count = u.get('completed_deals', 0)
            label = f'@{uname}' if uname else str(uid)
            lines.append(f'  {label} — {deals_count} сделок')
        text = (
            f'<b>👥 Пользователи ОТС #{ots_id}</b> (@{inst["bot_username"]})\n'
            f'<blockquote>Всего: {stats["users"]}</blockquote>\n\n'
            + '\n'.join(lines[:30])
        )
        if stats['users'] > 30:
            text += f'\n\n<i>...и ещё {stats["users"] - 30}</i>'
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('← Назад', f'ots_view_{ots_id}', 5960671702059848143)])
    )
    await cb.answer()


# ── OTS: Обновление файлов ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_update_files_'))
async def cb_ots_update_files(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    instance_dir = inst['instance_dir']
    updated = []
    for fname in ('bot.py', 'database.py', 'locales.py'):
        src = os.path.join(OTS_SOURCE_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(instance_dir, fname))
            updated.append(fname)
    if inst['owner_ids']:
        _ots_update_owner_ids(instance_dir, inst['owner_ids'])
    ots_sync_settings(instance_dir, inst)
    await cb.answer(f'✅ Обновлены: {", ".join(updated)}', show_alert=True)


# ── OTS: Удаление ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('ots_delete_'))
async def cb_ots_delete(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    text = (
        f'<b>🗑 Удаление ОТС #{ots_id}</b>\n\n'
        f'🤖 @{inst["bot_username"]}\n⚙️ {inst["service_name"]}\n\n'
        f'<b>Вы уверены?</b> Все файлы и данные будут удалены.'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb(
            [btn('✅ Да, удалить', f'ots_confirm_del_{ots_id}', 5893163582194978381, 'danger')],
            [btn('❌ Отмена', f'ots_view_{ots_id}', 5960671702059848143)]
        )
    )
    await cb.answer()


@router.callback_query(F.data.startswith('ots_confirm_del_'))
async def cb_ots_confirm_delete(cb: CallbackQuery):
    ots_id = int(cb.data.split('_')[-1])
    inst = await ots_get(ots_id)
    if not inst or not ots_can_manage(cb.from_user.id, inst):
        await cb.answer('Нет доступа', show_alert=True)
        return
    ots_stop_process(ots_id)
    if inst['instance_dir'] and os.path.exists(inst['instance_dir']):
        shutil.rmtree(inst['instance_dir'], ignore_errors=True)
    await ots_delete(ots_id)
    await cb.answer(f'🗑 ОТС @{inst["bot_username"]} удалён', show_alert=True)
    # show list
    uid = cb.from_user.id
    if uid in OWNERS:
        instances = await ots_get_all()
    else:
        instances = await ots_get_by_creator(uid)
    active = sum(1 for i in instances if ots_is_running(i['id']))
    text = f'<b>⚙️ Мои боты</b>\n\n<blockquote>🏛 Активных: <b>{active}/{len(instances)}</b></blockquote>'
    try:
        await cb.message.edit_text(text, reply_markup=ots_list_kb(instances, 'back_main'))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_list_kb(instances, 'back_main'))


# ══════════════════════════════════════════════════════════════════════════════
# ПАНЕЛЬ ОВНЕРА: ВСЕ ОТС + СТАТИСТИКА + РАССЫЛКА
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == 'ots_owner_panel')
async def cb_ots_owner_panel(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Только для овнеров', show_alert=True)
        return
    if state:
        await state.clear()
    instances = await ots_get_all()
    running_count = sum(1 for i in instances if ots_is_running(i['id']))
    text = (
        f'<b>{E["crown"]} Панель овнера — ОТС</b>\n\n'
        f'<blockquote>'
        f'📋 Всего ОТС: <b>{len(instances)}</b>\n'
        f'🟢 Запущено: <b>{running_count}</b>\n'
        f'🔴 Остановлено: <b>{len(instances) - running_count}</b>'
        f'</blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_owner_panel_kb())
    except Exception:
        await cb.message.answer(text, reply_markup=ots_owner_panel_kb())
    await cb.answer()


@router.callback_query(F.data == 'ots_owner_all')
async def cb_ots_owner_all(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа', show_alert=True)
        return
    if state:
        await state.clear()
    instances = await ots_get_all()
    text = (
        f'<b>{E["crown"]} Все боты</b>\n\n'
        f'<blockquote>Всего: <b>{len(instances)}</b></blockquote>'
    )
    try:
        await cb.message.edit_text(text, reply_markup=ots_list_kb(instances, 'ots_owner_panel'))
    except Exception:
        await cb.message.answer(text, reply_markup=ots_list_kb(instances, 'ots_owner_panel'))
    await cb.answer()


@router.callback_query(F.data == 'ots_owner_stats')
async def cb_ots_owner_stats(cb: CallbackQuery):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа', show_alert=True)
        return
    instances = await ots_get_all()
    total_users = 0
    total_deals = 0
    total_active = 0
    total_completed = 0
    lines = []
    for inst in instances:
        stats = await ots_read_stats(inst['instance_dir'])
        total_users += stats['users']
        total_deals += stats['deals']
        total_active += stats['active_deals']
        total_completed += stats['completed_deals']
        running = ots_is_running(inst['id'])
        icon = '🟢' if running else '🔴'
        lines.append(
            f'{icon} <b>@{inst["bot_username"]}</b>: '
            f'👥{stats["users"]} | 📋{stats["deals"]} | 🔥{stats["active_deals"]} | ✅{stats["completed_deals"]}'
        )
    text = (
        f'<b>{E["chart"]} Общая статистика всех ОТС</b>\n\n'
        f'<blockquote>'
        f'👥 <b>Пользователей:</b> <code>{total_users}</code>\n'
        f'📋 <b>Всего сделок:</b> <code>{total_deals}</code>\n'
        f'🔥 <b>Активных:</b> <code>{total_active}</code>\n'
        f'✅ <b>Завершённых:</b> <code>{total_completed}</code>'
        f'</blockquote>\n\n'
        + '\n'.join(lines) if lines else '<i>Нет ОТС</i>'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('← Назад', 'ots_owner_panel', 5960671702059848143)])
    )
    await cb.answer()


# ── Рассылка по всем ОТС ─────────────────────────────────────────────────────

class OtsBroadcast(StatesGroup):
    waiting_message = State()


@router.callback_query(F.data == 'ots_owner_broadcast')
async def cb_ots_owner_broadcast(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа', show_alert=True)
        return
    await state.set_state(OtsBroadcast.waiting_message)
    instances = await ots_get_all()
    text = (
        f'<b>📢 Рассылка по всем ОТС</b>\n\n'
        f'Сообщение будет отправлено всем пользователям всех ОТС ({len(instances)} ботов).\n\n'
        f'Введите текст сообщения (поддерживается HTML):'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('❌ Отмена', 'ots_owner_panel', 5893163582194978381, 'danger')])
    )
    await cb.answer()


@router.message(OtsBroadcast.waiting_message)
async def handle_ots_broadcast(msg: Message, state: FSMContext):
    if msg.from_user.id not in OWNERS:
        return
    await state.clear()
    broadcast_text = msg.text or msg.caption or ''
    if not broadcast_text.strip():
        await msg.answer(f'{E["warn"]} Пустое сообщение.', reply_markup=kb([btn('← Назад', 'ots_owner_panel', 5960671702059848143)]))
        return

    status_msg = await msg.answer(f'{E["clock"]} Начинаю рассылку...')
    instances = await ots_get_all()
    total_sent = 0
    total_failed = 0
    total_bots = 0

    for inst in instances:
        user_ids = await ots_read_all_user_ids(inst['instance_dir'])
        if not user_ids:
            continue
        total_bots += 1
        try:
            ots_bot = Bot(token=inst['bot_token'], default=DefaultBotProperties(parse_mode='HTML'))
            for uid in user_ids:
                try:
                    await ots_bot.send_message(uid, broadcast_text)
                    total_sent += 1
                except Exception:
                    total_failed += 1
                await asyncio.sleep(0.05)  # anti-flood
            await ots_bot.session.close()
        except Exception:
            total_failed += len(user_ids)

    await status_msg.edit_text(
        f'<b>{E["ok"]} Рассылка завершена!</b>\n\n'
        f'<blockquote>'
        f'🤖 Ботов: <b>{total_bots}</b>\n'
        f'✅ Отправлено: <b>{total_sent}</b>\n'
        f'❌ Ошибок: <b>{total_failed}</b>'
        f'</blockquote>',
        reply_markup=kb([btn('← Назад', 'ots_owner_panel', 5960671702059848143)])
    )


# ── Автозапуск ОТС при старте pay.py ──────────────────────────────────────────

async def ots_autostart():
    """Автоматически запустить все ОТС со статусом 'running'."""
    instances = await ots_get_all()
    for inst in instances:
        if inst['status'] == 'running' and inst['instance_dir']:
            if os.path.exists(inst['instance_dir']):
                ots_sync_settings(inst['instance_dir'], inst)
                if inst['owner_ids']:
                    _ots_update_owner_ids(inst['instance_dir'], inst['owner_ids'])
                ok = ots_start_process(inst['id'], inst['instance_dir'])
                if ok:
                    print(f'  ✅ ОТС #{inst["id"]} @{inst["bot_username"]} запущен')
                else:
                    print(f'  ❌ ОТС #{inst["id"]} @{inst["bot_username"]} не удалось запустить')


# ══════════════════════════════════════════════════════════════════════════════
# ЗЕРКАЛА
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_MIRROR_RECIPIENT = 'OKXDeals'

def mirror_bot_code(token: str, recipient: str) -> str:
    """Генерирует минимальный код зеркала с нужным токеном и получателем."""
    return f'''# Зеркало — авто-сгенерировано панелью
# Получатель: @{recipient}
# Токен: {token}

# Запускай этот файл отдельно: python mirror_{token[:8]}.py
# Все настройки (логика, тексты) берутся из основного бота.
# Получатель подарков/товаров по умолчанию: @{recipient}
'''

async def launch_mirror(token: str, owner_id: int) -> dict:
    """Проверяет токен, запускает зеркало, возвращает инфо."""
    mirror_bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    info = await mirror_bot.get_me()
    await mirror_bot.session.close()
    return {'username': info.username, 'full_name': info.full_name}


@router.callback_query(F.data == 'add_mirror')
async def cb_add_mirror(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа.', show_alert=True)
        return
    await state.set_state(AdminAction.waiting_mirror_token)
    text = (
        f'<b>🪞 Добавление зеркала</b>\n\n'
        f'Создай нового бота через @BotFather (/newbot)\n'
        f'и отправь сюда его токен.\n\n'
        f'Формат: <code>123456789:AABBCCDD...</code>\n\n'
        f'По умолчанию получатель подарков: <b>@{DEFAULT_MIRROR_RECIPIENT}</b>'
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb([btn('❌ Отмена', 'admin_settings', 5893163582194978381, 'danger')])
    )


@router.message(AdminAction.waiting_mirror_token)
async def handle_mirror_token(msg: Message, state: FSMContext):
    if msg.from_user.id not in OWNERS:
        return
    token = msg.text.strip()
    # Базовая валидация формата токена
    if not re.match(r'^\d{8,12}:[A-Za-z0-9_-]{35,}$', token):
        await msg.answer(
            '⚠️ Неверный формат токена.\n\nФормат: <code>123456789:AABBCCDD...</code>',
            reply_markup=kb([btn('❌ Отмена', 'admin_settings', 5893163582194978381, 'danger')])
        )
        return

    await state.clear()
    status_msg = await msg.answer('⏳ Проверяю токен...')

    try:
        info = await launch_mirror(token, msg.from_user.id)
        username = info['username']
        full_name = info['full_name']

        # Сохраняем зеркало
        mirrors[token] = {
            'username': username,
            'full_name': full_name,
            'owner_id': msg.from_user.id,
            'recipient': DEFAULT_MIRROR_RECIPIENT,
        }

        await status_msg.edit_text(
            f'<b>✅ Зеркало добавлено!</b>\n\n'
            f'🤖 Бот: @{username}\n'
            f'📛 Имя: {full_name}\n'
            f'🎁 Получатель: @{DEFAULT_MIRROR_RECIPIENT}\n\n'
            f'Токен сохранён. Разверни бота с этим токеном — '
            f'он будет работать с логикой основного бота.',
            reply_markup=kb(
                [btn('🪞 Мои зеркала', 'list_mirrors', 5363858422590619939)],
                [btn('Назад', 'admin_settings', 5960671702059848143)]
            )
        )
    except Exception as e:
        await status_msg.edit_text(
            f'<b>❌ Ошибка!</b>\n\n'
            f'Не удалось проверить токен.\n'
            f'Убедись что токен правильный и бот не заблокирован.\n\n'
            f'<code>{e}</code>',
            reply_markup=kb([btn('Назад', 'admin_settings', 5960671702059848143)])
        )


@router.callback_query(F.data == 'list_mirrors')
async def cb_list_mirrors(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа.', show_alert=True)
        return

    if not mirrors:
        await cb.message.edit_text(
            '<b>🪞 Зеркала</b>\n\nЗеркал пока нет. Нажми «Добавить зеркало» чтобы создать.',
            reply_markup=kb(
                [btn('➕ Добавить зеркало', 'add_mirror', 5217822164362739968, 'success')],
                [btn('Назад', 'admin_settings', 5960671702059848143)]
            )
        )
        return

    lines = []
    btns_delete = []
    for i, (token, data) in enumerate(mirrors.items(), 1):
        lines.append(
            f'{i}. 🤖 @{data["username"]}\n'
            f'   🎁 Получатель: @{data["recipient"]}\n'
            f'   🔑 Токен: <code>{token[:10]}...{token[-5:]}</code>'
        )
        btns_delete.append(btn(f'❌ Удалить #{i}', f'del_mirror_{token[:10]}', 5893163582194978381, 'danger'))

    text = '<b>🪞 Мои зеркала</b>\n\n' + '\n\n'.join(lines)
    rows = [[b] for b in btns_delete]
    rows.append([btn('➕ Добавить', 'add_mirror', 5217822164362739968, 'success')])
    rows.append([btn('Назад', 'admin_settings', 5960671702059848143)])
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith('del_mirror_'))
async def cb_del_mirror(cb: CallbackQuery):
    if cb.from_user.id not in OWNERS:
        await cb.answer('Нет доступа.', show_alert=True)
        return
    prefix = cb.data[len('del_mirror_'):]
    to_del = next((t for t in mirrors if t.startswith(prefix)), None)
    if to_del:
        username = mirrors[to_del]['username']
        del mirrors[to_del]
        await cb.answer(f'✅ Зеркало @{username} удалено', show_alert=True)
    # Обновляем список
    await cb_list_mirrors(cb, None)


async def _health(request):
    return web.json_response({'status': 'ok', 'service': 'bad-team-bot'})

async def _start_health_server():
    port = int(os.getenv('PORT', '10000'))
    app = web.Application()
    app.router.add_get('/', _health)
    app.router.add_get('/health', _health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f'🌐 Health server listening on 0.0.0.0:{port}')
    return runner

async def main():
    await _start_health_server()
    await init_db()
    await check_and_fix_database()
    # Автозапуск ОТС, которые были запущены при прошлом запуске
    print('🔄 Автозапуск ОТС...')
    if os.path.isdir(OTS_SOURCE_DIR):
        await ots_autostart()
    else:
        print(f'⚠️ OTS template folder not found: {OTS_SOURCE_DIR}')
    await bot.set_my_commands([
        BotCommand(command='start', description='Главное меню'),
        BotCommand(command='top',   description='Топ воркеров'),
    ])
    print('✅ Бот запущен')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
