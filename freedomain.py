import asyncio
import aiohttp
import time
import dns.resolver

def log_message(message):
    print(message)
    with open("log_freed.txt", "a") as log_file:
        log_file.write(message + "\n")

def clear_log():
    with open("log_freed.txt", "w") as log_file:
        log_file.write("")

def format_elapsed_time(elapsed_time):
    days = int(elapsed_time // 86400)
    hours = int((elapsed_time % 86400) // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = elapsed_time % 60
    return f"{days} дней, {hours} часов, {minutes} минут, {seconds:.2f} секунд"

async def query_doh(session, domain, record_type, doh_servers):
    for server in doh_servers:
        url = f"{server}/dns-query"
        headers = {"accept": "application/dns-json"}
        params = {"name": domain, "type": record_type}
        try:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.headers.get("Content-Type") != "application/dns-json":
                    log_message(f"Некорректный формат ответа для {domain} ({record_type}) от {server}: {response.headers.get('Content-Type')}")
                    continue
                data = await response.json()
                if "Answer" in data:
                    return {answer["data"].strip('"') for answer in data["Answer"]}
                return set()
        except Exception as e:
            log_message(f"Ошибка при использовании DoH для {domain} ({record_type}) на {server}: {e}")
    return None

def query_dns(domain, record_type):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 10
        answers = resolver.resolve(domain, record_type)
        return {answer.to_text() for answer in answers}
    except Exception as e:
        log_message(f"Ошибка при использовании локального DNS для {domain} ({record_type}): {e}")
        return None

async def check_domain(session, domain, beget_patterns, standard_subdomains, doh_servers):
    is_free = True
    try:
        log_message(f"Проверка домена: {domain}")
        tasks = [
            query_doh(session, domain, "A", doh_servers),
            query_doh(session, domain, "MX", doh_servers),
            query_doh(session, domain, "TXT", doh_servers),
            query_doh(session, f"autoconfig.{domain}", "CNAME", doh_servers),
            query_doh(session, f"autodiscover.{domain}", "CNAME", doh_servers),
            query_doh(session, f"*.{domain}", "A", doh_servers)
        ]
        results = await asyncio.gather(*tasks)

        a_records, mx_records, txt_records, autoconfig_cname, autodiscover_cname, subdomain_a_records = results

        if a_records is None:
            a_records = query_dns(domain, "A")
        if a_records is None or a_records != beget_patterns["A"]:
            log_message(f"{domain}: A-записи не соответствуют ожиданиям.")
            is_free = False

        if mx_records is None:
            mx_records = query_dns(domain, "MX")
        if mx_records is None or mx_records != beget_patterns["MX"]:
            log_message(f"{domain}: MX-записи не соответствуют ожиданиям.")
            is_free = False

        if txt_records is None:
            txt_records = query_dns(domain, "TXT")
        if txt_records is None or not txt_records.issubset(beget_patterns["TXT"]):
            log_message(f"{domain}: TXT-записи не соответствуют ожиданиям.")
            is_free = False

        if autoconfig_cname is None:
            autoconfig_cname = query_dns(f"autoconfig.{domain}", "CNAME")
        if autoconfig_cname is None or autoconfig_cname != beget_patterns["CNAME"]:
            log_message(f"{domain}: CNAME-записи для autoconfig не соответствуют ожиданиям.")
            is_free = False

        if autodiscover_cname is None:
            autodiscover_cname = query_dns(f"autodiscover.{domain}", "CNAME")
        if autodiscover_cname is None or autodiscover_cname != beget_patterns["CNAME"]:
            log_message(f"{domain}: CNAME-записи для autodiscover не соответствуют ожиданиям.")
            is_free = False

        if subdomain_a_records is None:
            subdomain_a_records = query_dns(f"*.{domain}", "A")
        if subdomain_a_records:
            for record in subdomain_a_records:
                if not any(record.startswith(f"{std}.{domain}") for std in standard_subdomains):
                    log_message(f"{domain}: Найден нестандартный поддомен с A-записью: {record}")
                    is_free = False

    except Exception as e:
        log_message(f"Ошибка при проверке домена {domain}: {e}")
        is_free = False
    return domain, is_free

async def check_domains(domains_file):
    clear_log()

    beget_patterns = {
        "A": {"5.101.153.235"},
        "MX": {"20 mx2.beget.com.", "10 mx1.beget.com."},
        "TXT": {"v=spf1 redirect=beget.com"},
        "CNAME": {"autoconfig.beget.com."}
    }

    standard_subdomains = {"autoconfig", "autodiscover", "www"}

    doh_servers = [
        "https://dns.google",
        "https://cloudflare-dns.com",
        "https://doh.opendns.com"
    ]

    free_domains = []
    close_domains = []

    start_time = time.time()

    with open(domains_file, "r") as f:
        domains = [line.strip() for line in f.readlines() if line.strip()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_domain(session, domain, beget_patterns, standard_subdomains, doh_servers) for domain in domains]
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
