from telethon import TelegramClient, events
import asyncio
import requests
import re
from pystyle import Colors, Colorate

api_id = 123456789
api_hash = '1a2b3c4d5e6f7g8h9i'
session_name = 'wordgame_session'
chat_id = 77777777777777
bot_username = 'igravslova_bot'

used_words = set()
current_letter = None
pending_words = []
sending_in_progress = False

def intro():
    text = """
    github.com/PinProjectTEAM
        
    ██▓███   ██▓ ███▄    █  ██▓███   ██▀███   ▒█████   ▄▄▄██▀▀▀▓█████  ▄████▄  ▄▄▄█████▓
    ▓██░  ██▒▓██▒ ██ ▀█   █ ▓██░  ██▒▓██ ▒ ██▒▒██▒  ██▒   ▒██   ▓█   ▀ ▒██▀ ▀█  ▓  ██▒ ▓▒
    ▓██░ ██▓▒▒██▒▓██  ▀█ ██▒▓██░ ██▓▒▓██ ░▄█ ▒▒██░  ██▒   ░██   ▒███   ▒▓█    ▄ ▒ ▓██░ ▒░
    ▒██▄█▓▒ ▒░██░▓██▒  ▐▌██▒▒██▄█▓▒ ▒▒██▀▀█▄  ▒██   ██░▓██▄██▓  ▒▓█  ▄ ▒▓▓▄ ▄██▒░ ▓██▓ ░ 
    ▒██▒ ░  ░░██░▒██░   ▓██░▒██▒ ░  ░░██▓ ▒██▒░ ████▓▒░ ▓███▒   ░▒████▒▒ ▓███▀ ░  ▒██▒ ░ 
    ▒▓▒░ ░  ░░▓  ░ ▒░   ▒ ▒ ▒▓▒░ ░  ░░ ▒▓ ░▒▓░░ ▒░▒░▒░  ▒▓▒▒░   ░░ ▒░ ░░ ░▒ ▒  ░  ▒ ░░   
    ░▒ ░      ▒ ░░ ░░   ░ ▒░░▒ ░       ░▒ ░ ▒░  ░ ▒ ▒░  ▒ ░▒░    ░ ░  ░  ░  ▒       ░    
    ░░        ▒ ░   ░   ░ ░ ░░         ░░   ░ ░ ░ ░ ▒   ░ ░ ░      ░   ░          ░      
            ░           ░             ░         ░ ░   ░   ░      ░  ░░ ░               
                                                                    ░                 
    """
    gradient_text = Colorate.Vertical(Colors.red_to_black, text)
    print(gradient_text)

intro()
russian_words_url = 'https://gist.githubusercontent.com/kissarat/bd30c324439cee668f0ac76732d6c825/raw/147eecc9a86ec7f97f6dd442c2eda0641ddd78dc/russian-mnemonic-words.txt'

def load_russian_words():
    try:
        response = requests.get(russian_words_url)
        response.raise_for_status()
        words = response.text.splitlines()
        filtered_words = [
            word.lower() for word in words
            if word.isalpha() and len(word) > 2 and word.islower()
        ]
        return filtered_words
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке словаря: {e}")
        return []

russian_words = load_russian_words()

def get_russian_word(letter):
    global russian_words
    if not russian_words:
        print("Словарь пуст или не загружен")
        return None
    available_words = [
        word for word in russian_words
        if word.startswith(letter) and word not in used_words
    ]
    return available_words if available_words else None

def extract_letter(text):
    match = re.search(r'\*\*([А-Яа-я])\*\*', text)
    return match.group(1).lower() if match else None

async def send_next_word():
    global used_words, pending_words, sending_in_progress

    if sending_in_progress:
        return
    sending_in_progress = True

    while pending_words:
        word = pending_words.pop(0)

        if word in used_words:
            print(f"Слово {word} уже было использовано.")
            continue

        used_words.add(word)
        print(f"Отправка: {word}")
        await client.send_message(chat_id, word)
        await asyncio.sleep(1)  # Задержку выставлять тут

    sending_in_progress = False

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=chat_id))
async def handler(event):
    global used_words, current_letter, pending_words

    if event.sender_id == (await client.get_me()).id:
        return

    if not event.sender:
        return

    if event.sender.username == bot_username:
        text = event.message.text
        new_letter = extract_letter(text)
        if new_letter:
            current_letter = new_letter
            print(f"Новая буква: {current_letter}")
            pending_words.clear()
            available_words = get_russian_word(current_letter)
            if available_words:
                pending_words.extend(available_words)
            await send_next_word()

        if "нужно назвать слово, начинающийся с буквы" in text:
            available_words = get_russian_word(current_letter)
            if available_words:
                if not pending_words:
                    pending_words.extend(available_words)

                await send_next_word()
            else:
                print("Слово не найдено")

        elif "уже было" in text:
            if current_letter is None:
                print("Текущая буква не определена!")
                return
            available_words = get_russian_word(current_letter)
            if available_words:
                if not pending_words:
                    pending_words.extend(available_words)
                await send_next_word()
            else:
                print("Слово не найдено")

        if "существует, но оно не начинается с буквы" in text:
            current_letter_match = re.search(r'буквы "([А-Яа-я])"', text)
            if current_letter_match:
                current_letter = current_letter_match.group(1).lower()
                print(f"Обновлена новая буква: {current_letter}")
                pending_words.clear()
                available_words = get_russian_word(current_letter)
                if available_words:
                    pending_words.extend(available_words)
                await send_next_word()

async def main():
    await client.start(phone='+7 XXX XXX XX XX')
    print("Бот запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
