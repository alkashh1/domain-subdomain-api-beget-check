import asyncio
import aiohttp
import time
import dns.resolver

MAX_RETRIES = 5

# Add server retry limit
SERVER_RETRY_LIMIT = 3

def log_message(message, critical=False):
    #print(message)
    log_file = "critical_log.txt" if critical else "log_freed.txt"
    with open(log_file, "a") as log:
        log.write(message + "\n")

def clear_logs():
    with open("log_freed.txt", "w") as log_file:
        log_file.write("")
    with open("critical_log.txt", "w") as critical_log:
        critical_log.write("")

def format_elapsed_time(elapsed_time):
    days = int(elapsed_time // 86400)
    hours = int((elapsed_time % 86400) // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = elapsed_time % 60
    return f"{days} дней, {hours} часов, {minutes} минут, {seconds:.2f} секунд"

def query_dns(domain, record_type):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 10
        answers = resolver.resolve(domain, record_type)
        return {answer.to_text() for answer in answers}
    except dns.resolver.NXDOMAIN:
        log_message(f"{domain}: NXDOMAIN - Домен не существует для запроса {record_type}", critical=True)
        return set()
    except Exception as e:
        log_message(f"Ошибка при использовании локального DNS для {domain} ({record_type}): {e}", critical=True)
        return None

async def normalize_txt_records(records):
    """Remove surrounding quotes from TXT records."""
    return {record.strip('"') for record in records}

async def check_domain(session, domain, beget_patterns):
    try:
        log_message(f"Проверка домена: {domain}")

        # Step 1: Check A records to verify Beget DNS
        a_records = query_dns(domain, "A")

        log_message(f"{domain}: Полученные A-записи: {a_records}")
        log_message(f"{domain}: Ожидаемые A-записи: {beget_patterns['A']}")

        if a_records is None or not a_records:
            log_message(f"{domain}: Не удалось получить A-записи. Домен помечен как временно недоступный.", critical=True)
            return domain, False

        if not a_records.issubset(beget_patterns["A"]):
            log_message(f"{domain}: A-записи не совпадают с ожидаемыми.")
            return domain, False

        # Step 2: Check critical subdomains
        critical_subdomains = [f"_dmarc.{domain}", f"dm.{domain}"]

        # Dynamically check all selectors for _domainkey
        domainkey_subdomain = f"_domainkey.{domain}"
        txt_records = query_dns(domainkey_subdomain, "TXT")
        if txt_records is not None and len(txt_records) > 0:
            for record in txt_records:
                if not record.startswith("selector."):
                    log_message(f"{domain}: Найдена неизвестная запись {record} для _domainkey. Домен исключается.")
                    return domain, False

        for subdomain in critical_subdomains:
            txt_records = query_dns(subdomain, "TXT")
            if txt_records is not None and len(txt_records) > 0:
                log_message(f"{domain}: Найден критический поддомен {subdomain}. Домен исключается.")
                return domain, False

        # Step 3: Check TXT records for non-standard entries
        txt_records = query_dns(domain, "TXT")

        log_message(f"{domain}: Полученные TXT-записи: {txt_records}")
        log_message(f"{domain}: Ожидаемые шаблоны TXT: {beget_patterns['TXT']}")

        # Normalize TXT records
        if txt_records is not None:
            txt_records = await normalize_txt_records(txt_records)

        if txt_records is not None and not txt_records.issubset(beget_patterns["TXT"]):
            log_message(f"{domain}: TXT-записи содержат нестандартные данные: {txt_records}")
            return domain, False

        log_message(f"{domain}: Домен признан свободным.")
        return domain, True

    except Exception as e:
        log_message(f"Ошибка при проверке домена {domain}: {e}", critical=True)
        return domain, False

async def check_domains(domains_file):
    clear_logs()

    beget_patterns = {
        "A": {"5.101.153.235"},
        "TXT": {"v=spf1 redirect=beget.com"}
    }

    free_domains = []
    close_domains = []

    start_time = time.time()

    with open(domains_file, "r") as f:
        domains = [line.strip() for line in f.readlines() if line.strip()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_domain(session, domain, beget_patterns) for domain in domains]
        results = await asyncio.gather(*tasks)

    for domain, is_free in results:
        if is_free:
            free_domains.append(domain)
        else:
            close_domains.append(domain)

    with open("free.txt", "w") as free_file:
        free_file.write("\n".join(free_domains))

    with open("close.txt", "w") as close_file:
        close_file.write("\n".join(close_domains))

    end_time = time.time()
    elapsed_time = end_time - start_time
    formatted_time = format_elapsed_time(elapsed_time)
    log_message(f"Проверка завершена. Свободные домены: {len(free_domains)}, Занятые домены: {len(close_domains)}")
    log_message(f"Время выполнения: {formatted_time}")
    print(f"Время выполнения: {formatted_time}")

if __name__ == "__main__":
    asyncio.run(check_domains("auto.txt"))
    
