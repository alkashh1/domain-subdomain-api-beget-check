import socket

def check_a_records(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            domain = line.strip()
            if not domain:
                continue  
            try:
                a_record = socket.gethostbyname(domain)
                result = f"{domain} - {a_record}"
            except socket.gaierror:
                result = f"{domain} - Not Found"
            #print(result)
            outfile.write(result + '\n')

if __name__ == "__main__":
    input_file_A = '/home/zabbix/scripts/DomainTree/ssl_https.txt'
    output_file_a_all = '/home/zabbix/scripts/DomainTree/A.txt'
    # /Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/
    # input_file_A = '/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/ssl_https.txt'
    # output_file_a_all = '/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/A.txt'
    check_a_records(input_file_A, output_file_a_all)
    print(f"Результаты сохранены в {output_file_a_all}")
