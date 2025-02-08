from VkAuth import MobileAuth
from VkAuth.Types import Error, Credentials
from VkAuth.Enums import VerificationMethods
from collections.abc import AsyncGenerator, Iterable
from aiohttp import ClientSession
from m3u8 import load
from os import makedirs, mkdir
from aiofiles import open as aio_open
from asyncio import run, TaskGroup, create_subprocess_exec
from subprocess import DEVNULL
from dotenv import load_dotenv
from os import getenv
from shutil import rmtree
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from re import sub

load_dotenv('.env')


async def authorize() -> Credentials:
    async with MobileAuth(getenv("LOGIN"), getenv("PASSWORD")) as auth:
        anonym_token = await auth.getAnonymToken()
        validate_acc = await auth.validateAccount(anonym_token)
        if isinstance(validate_acc, Error):
            raise Exception(validate_acc)
        if validate_acc.nextStep.verMethod != VerificationMethods.password:
            await auth.sendCode(anonym_token, validate_acc, VerificationMethods.sms)
            check_code = await auth.checkCode(input("Enter code: "), anonym_token, validate_acc, VerificationMethods.sms)
            if isinstance(check_code, Error):
                raise Exception(check_code)
        return Credentials(await auth.authorize(anonym_token, validate_acc), auth.cookies)


async def getDefaultSection(cred: Credentials) -> str:
    async with ClientSession(cookie_jar=cred.cookies) as session:
        async with session.post(
            url="https://api.vk.com/method/catalog.getAudioMyAudios",
            data={
                "device_id": "cc199ca91e009c93:8a8bdae5c3a8a432135d465f42c86589",
                "v": "5.247",
                "need_blocks": 1,
                "access_token": cred.accessToken.accessToken
            },
            headers={"user-agent": "VKAndroidApp/8.114.2-28264 (Android 12; SDK 32; arm64-v8a; samsung SM-G988N; ru; 1280x720)"}
        ) as response:
            return (await response.json()).get("response").get("catalog").get("default_section")


async def loadSection(cred: Credentials, defaultSection: str) -> AsyncGenerator[Iterable[dict], None]:
    while getattr(loadSection, "__start_from__", True):
        async with ClientSession(cookie_jar=cred.cookies) as session:
            async with session.post(
                url="https://api.vk.com/method/catalog.getSection",
                data={
                    "device_id": "cc199ca91e009c93:8a8bdae5c3a8a432135d465f42c86589",
                    "v": "5.247",
                    "access_token": cred.accessToken.accessToken,
                    "section_id": defaultSection,
                    "start_from": getattr(loadSection, "__start_from__", "")
                },
                headers={"user-agent": "VKAndroidApp/8.114.2-28264 (Android 12; SDK 32; arm64-v8a; samsung SM-G988N; ru; 1280x720)"}
            ) as response:
                setattr(loadSection, "__start_from__", (data := await response.json()).get("response").get("section").get("next_from", False))
                yield iter(data.get("response").get("audios"))


async def writeFile(path: str, content: bytes) -> None:
    async with aio_open(path, "wb") as file:
        await file.write(content)


async def convertAudios(audio: dict) -> None:
    if audio.get("url"):
        filename = sub(r'[<>:"|?*]', '', f'{audio.get("artist")} - {audio.get("title")}')
        mkdir(path := f'temp/{filename}')
        async with ClientSession() as session:
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
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        await process.wait()


async def main():
    cred = await authorize()
    defaultSection = await getDefaultSection(cred)
    makedirs("temp", exist_ok=True)
    makedirs("audios", exist_ok=True)
    async with TaskGroup() as tg:
        async for audios in loadSection(cred, defaultSection):
            for audio in audios:
                tg.create_task(convertAudios(audio))
    rmtree("temp")


if __name__ == '__main__':
    run(main())

