import re

def parse_proxy_line(line: str) -> dict:
    line = line.strip()

    # user:pass@ip:port
    m = re.match(r'(?P<user>[^:@]+):(?P<pass>[^@]+)@(?P<ip>[^:]+):(?P<port>\d+)', line)
    if m:
        return m.groupdict()

    # ip:port:user:pass
    parts = line.split(':')
    if len(parts) == 4:
        return {
            'ip': parts[0],
            'port': parts[1],
            'user': parts[2],
            'pass': parts[3]
        }

    # ip:port
    if len(parts) == 2:
        return {
            'ip': parts[0],
            'port': parts[1],
            'user': None,
            'pass': None
        }

    raise ValueError(f"无法解析代理格式: {line}")