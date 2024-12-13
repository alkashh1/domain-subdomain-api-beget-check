import dns.resolver
import time
import requests

def query_doh(domain, record_type):
    url = "https://cloudflare-dns.com/dns-query"
    headers = {
        "accept": "application/dns-json"
    }
    params = {
        "name": domain,
        "type": record_type
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Answer" in data:
            return {answer["data"].strip('"') for answer in data["Answer"]}
        return set()
    except requests.RequestException as e:
        log_message(f"Ошибка при использовании DoH для {domain} ({record_type}): {e}")
        return None

def retry_failed_domains(failed_domains):
    retry_results = []
    for domain, record_type in failed_domains:
        log_message(f"Повторная проверка: {domain}, тип записи: {record_type}")
        result = query_doh(domain, record_type)
        if result is not None:
            retry_results.append((domain, record_type, result))
        else:
            log_message(f"Сбой повторной проверки для {domain} ({record_type})")
    return retry_results

def log_message(message):
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

def check_domains(domains_file):
    clear_log()

    beget_patterns = {
        "A": {"5.101.153.235"},
        "MX": {"20 mx2.beget.com.", "10 mx1.beget.com."},
        "TXT": {"v=spf1 redirect=beget.com"},
        "CNAME": {"autoconfig.beget.com."}
    }

    standard_subdomains = {"autoconfig", "autodiscover", "www"}

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8", "1.1.1.1", "77.88.8.8", "208.67.222.222"]
    resolver.lifetime = 10
    resolver.timeout = 5

    free_domains = []
    close_domains = []
    failed_domains = []

    start_time = time.time()

    with open(domains_file, "r") as f:
        domains = [line.strip() for line in f.readlines() if line.strip()]

    for domain in domains:
        is_free = True
        all_records = {"A": set(), "MX": set(), "TXT": set(), "CNAME": set(), "critical": set()}
        try:
            log_message(f"Проверка домена: {domain}")

            a_records = query_doh(domain, "A")
            if a_records is None:
                failed_domains.append((domain, "A"))
            else:
                all_records["A"] = a_records
                if a_records and a_records != beget_patterns["A"]:
                    is_free = False

            mx_records = query_doh(domain, "MX")
            if mx_records is None:
                failed_domains.append((domain, "MX"))
            else:
                all_records["MX"] = mx_records
                if mx_records and mx_records != beget_patterns["MX"]:
                    is_free = False

            txt_records = query_doh(domain, "TXT")
            if txt_records is None:
                failed_domains.append((domain, "TXT"))
            else:
                all_records["TXT"] = txt_records
                if txt_records:
                    log_message(f"{domain}: Полученные TXT-записи: {txt_records}")
                    log_message(f"{domain}: Ожидаемые TXT-шаблоны: {beget_patterns['TXT']}")
                if not txt_records.issubset(beget_patterns["TXT"]):
                    is_free = False

            for subdomain in ["autoconfig", "autodiscover"]:
                cname_records = query_doh(f"{subdomain}.{domain}", "CNAME")
                if cname_records is None:
                    failed_domains.append((f"{subdomain}.{domain}", "CNAME"))
                else:
                    all_records["CNAME"].update(cname_records)
                    if cname_records and cname_records != beget_patterns["CNAME"]:
                        is_free = False

            subdomain_records = query_doh(f"*.{domain}", "TXT")
            if subdomain_records:
                log_message(f"{domain}: Найден нестандартный поддомен с записями: {subdomain_records}")
                all_records["critical"].add("non-standard subdomain")
                is_free = False

            subdomain_a_records = query_doh(f"*.{domain}", "A")
            if subdomain_a_records:
                for record in subdomain_a_records:
                    if not any(record.startswith(f"{std}.{domain}") for std in standard_subdomains):
                        log_message(f"{domain}: Найден нестандартный поддомен с A-записью: {record}")
                        all_records["critical"].add("non-standard subdomain")
                        is_free = False

            for record_type, records in all_records.items():
                if record_type != "critical" and records and records != beget_patterns.get(record_type, set()):
                    log_message(f"{domain}: Найдены нестандартные записи {record_type}: {records}")
                    is_free = False

        except Exception as e:
            log_message(f"Ошибка при проверке домена {domain}: {e}")

        if is_free:
            free_domains.append(domain)
        else:
            close_domains.append(domain)

    log_message("\nПовторная проверка для неудавшихся доменов:")
    retry_results = retry_failed_domains(failed_domains)
    for domain, record_type, records in retry_results:
        log_message(f"Повторная проверка успешна для {domain} ({record_type}): {records}")

    with open("free.txt", "w") as free_file:
        free_file.write("\n".join(free_domains))

    with open("close.txt", "w") as close_file:
        close_file.write("\n".join(close_domains))

    end_time = time.time()
    elapsed_time = end_time - start_time
    formatted_time = format_elapsed_time(elapsed_time)
    log_message(f"Проверка завершена. Свободные домены: {len(free_domains)}, Занятые домены: {len(close_domains)}")
    log_message(f"Время выполнения: {formatted_time}")

check_domains("auto.txt")
