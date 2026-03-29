import requests
import time
import concurrent.futures

# 1. Ссылка на список прокси
GITHUB_URL = "https://github.com/kodxuk/FTO/raw/refs/heads/main/socks5.txt"

# 2. Сайт, к которому измеряем пинг 
TEST_URL = "https://web.telegram.org/"
TIMEOUT = 5  # Максимальное время ожидания ответа в секундах

def check_proxy(proxy_line):
    proxy_line = proxy_line.strip()
    if not proxy_line:
        return None
    
    proxies = {
        "http": f"socks5://{proxy_line}",
        "https": f"socks5://{proxy_line}"
    }
    
    try:
        # Замеряем время начала запроса
        start_time = time.time()
        
        # Делаем запрос через прокси
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        
        # Если сайт ответил успешно, считаем пинг
        if response.status_code == 200:
            ping_ms = (time.time() - start_time) * 1000
            return {"proxy": proxy_line, "ping": ping_ms}
            
    except Exception:
        # Если прокси мертв, отвалился по таймауту или заблокирован
        pass
        
    return None

def main():
    print("📥 Скачиваем список прокси с GitHub...")
    try:
        response = requests.get(GITHUB_URL)
        response.raise_for_status()
        proxy_list = response.text.strip().split('\n')
        print(f"✅ Загружено прокси для проверки: {len(proxy_list)}")
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return

    print("⏳ Проверяем доступность и пинг (многопоточно)...")
    working_proxies = []
    
    # Запускаем проверку в 20 потоков для скорости
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, proxy_list)
        
        for res in results:
            if res:
                working_proxies.append(res)
                print(f"Работает: {res['proxy']} | Пинг: {res['ping']:.0f} мс")

    if not working_proxies:
        print("\n❌ Ни один прокси не прошел проверку.")
        return

    # Ищем прокси с минимальным пингом
    best_proxy = min(working_proxies, key=lambda x: x['ping'])
    
    print("\n" + "="*50)
    print(f"🏆 ОПТИМАЛЬНЫЙ ПРОКСИ: {best_proxy['proxy']}")
    print(f"⚡ Скорость отклика: {best_proxy['ping']:.0f} мс")
    print("="*50)

if __name__ == "__main__":
    main()
    # Эта строка не даст консоли закрыться, пока пользователь не нажмет Enter
    input("\nНажмите Enter для выхода...")
