from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    pipedrive_api_key: str
    pipedrive_domain: str
    pipedrive_platform_key: str
    pipedrive_campaign_key: str
    pipedrive_adset_key: str
    pipedrive_ad_key: str
    other_params: str = None


@dataclass
class Facebook:
    access_token: str
    ad_account_id: int

@dataclass
class Redis:
    host: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    facebook: Facebook
    redis: Redis
    misc: Miscellaneous



def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        facebook=Facebook(
            access_token=env.str('FB_ACCESS_TOKEN'),
            ad_account_id=env.int('FB_AD_ACCOUNT_ID')
        ),
        redis=Redis(
            host=env.str('REDIS_HOST')
        ),
        misc=Miscellaneous(
            pipedrive_api_key=env.str('PIPEDRIVE_API_KEY'),
            pipedrive_domain=env.str('PIPEDRIVE_DOMAIN'),
            pipedrive_adset_key=env.str('PIPEDRIVE_ADSET_KEY'),
            pipedrive_platform_key=env.str('PIPEDRIVE_PLATFORM_KEY'),
            pipedrive_ad_key=env.str('PIPEDRIVE_AD_KEY'),
            pipedrive_campaign_key=env.str('PIPEDRIVE_CAMPAIGN_KEY'),
        )
    )
