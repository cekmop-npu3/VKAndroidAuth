from VkAuth import MobileAuth
from VkAuth.Types import Error, AccessToken
from VkAuth.Enums import VerificationMethods
from collections.abc import AsyncGenerator, Iterable
from aiohttp import ClientSession
from m3u8 import load
from os import makedirs
from aiofiles import open as aio_open
from asyncio import run, TaskGroup, create_subprocess_exec
from asyncio import subprocess, TimeoutError, sleep
from dotenv import load_dotenv
from os import getenv
from shutil import rmtree
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from re import sub
from typing import Union
from logging import getLogger, basicConfig, INFO

load_dotenv('.env')

basicConfig(level=INFO)
logger = getLogger(__name__)


async def authorize(auth: MobileAuth) -> AccessToken:
    anonym_token = await auth.getAnonymToken()
    validate_acc = await auth.validateAccount(anonym_token)
    if isinstance(validate_acc, Error):
        raise Exception(validate_acc)
    if validate_acc.nextStep.verMethod != VerificationMethods.password:
        await auth.sendCode(anonym_token, validate_acc, VerificationMethods.sms)
        check_code = await auth.checkCode(input("Enter code: "), anonym_token, validate_acc, VerificationMethods.sms)
        if isinstance(check_code, Error):
            raise Exception(check_code)
    return await auth.authorize(anonym_token, validate_acc)


async def getDefaultSection(session: ClientSession, accessToken: AccessToken, ownerId: Union[str, int] = "") -> str:
    async with session.post(
        url=f"https://api.vk.com/method/catalog.getAudio{'' if ownerId else 'MyAudios'}",
        data={
            "device_id": "cc199ca91e009c93:8a8bdae5c3a8a432135d465f42c86589",
            "v": "5.247",
            "need_blocks": 1,
            "access_token": accessToken.accessToken,
            "owner_id": str(ownerId)
        }
    ) as response:
        logger.info(f"Default section is loaded")
        return (await response.json()).get("response").get("catalog").get("default_section")


async def loadSection(session: ClientSession, accessToken: AccessToken, defaultSection: str) -> AsyncGenerator[Iterable[dict], None]:
    while getattr(loadSection, "__start_from__", True):
        async with session.post(
            url="https://api.vk.com/method/catalog.getSection",
            data={
                "device_id": "cc199ca91e009c93:8a8bdae5c3a8a432135d465f42c86589",
                "v": "5.247",
                "access_token": accessToken.accessToken,
                "section_id": defaultSection,
                "start_from": getattr(loadSection, "__start_from__", "")
            }
        ) as response:
            setattr(loadSection, "__start_from__", (data := await response.json()).get("response").get("section").get("next_from", False))
            logger.info(f"section: {getattr(loadSection, '__start_from__')}")
            yield iter(data.get("response").get("audios"))


async def writeFile(path: str, content: bytes) -> None:
    async with aio_open(path, "wb") as file:
        await file.write(content)


async def unpackSection(session: ClientSession, tg: TaskGroup, audios: Iterable[dict]) -> None:
    for audio in audios:
        tg.create_task(convertAudios(session, audio))


async def convertAudios(session: ClientSession, audio: dict) -> None:
    if audio.get("url"):
        try:
            filename = sub(r'[<>:"./\\|?*]', '', f'{audio.get("artist")} - {audio.get("title")}')[:250]
            makedirs(path := f'temp/{filename}', exist_ok=True)
            async with session.get(url=audio.get("url")) as response:
                await writeFile(f"{path}/{filename}.m3u8", await response.read())
            m3u8_obj = load(f"{path}/{filename}.m3u8")
            for seg in m3u8_obj.segments:
                async with session.get(url=f'{audio.get("url").removesuffix("index.m3u8?siren=1")}{seg.uri}') as response:
                    data = await response.read()
                    if seg.key.uri is not None:
                        async with session.get(url=seg.key.uri) as rsp:
                            iv = int(seg.uri.split("-")[1]).to_bytes(length=16, byteorder="big")
                            cipher = AES.new(await rsp.read(), AES.MODE_CBC, iv=iv)
                            data = unpad(cipher.decrypt(data), AES.block_size)
                    await writeFile(f'{path}/{seg.uri.removesuffix("?siren=1")}', data)
            async with aio_open(f"{path}/{filename}.m3u8", "r+") as file:
                content = await file.read()
                await file.seek(0)
                await file.write(sub(',URI=".+?"', "", content.replace("?siren=1", "").replace("AES-128", "NONE")))
                await file.truncate()
            process = await create_subprocess_exec(
                *["ffmpeg", "-i", f"{path}/{filename}.m3u8", f"audios/{filename}.mp3"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            await process.wait()
            logger.info(f"{filename} process: {process.returncode}")
            rmtree(f"temp/{filename}")
        except TimeoutError:
            await sleep(10)
            await convertAudios(session, audio)


async def main():
    async with MobileAuth(getenv("LOGIN"), getenv("PASSWORD")) as auth:
        access_token = await authorize(auth)
        makedirs("temp", exist_ok=True)
        makedirs("audios", exist_ok=True)
        defaultSection = await getDefaultSection(auth.session, access_token, getenv("USERID"))
        async with TaskGroup() as tg:
            async for audios in loadSection(auth.session, access_token, defaultSection):
                await unpackSection(auth.session, tg, audios)
    rmtree("temp")


if __name__ == '__main__':
    run(main())

