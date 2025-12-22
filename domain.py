import re

text = """
温
温州大唐盛世传媒有限公司

日访问量预估476

www.sscmwl.com


2

盛
盛世传媒

日访问量预估118

www.sscmwl.cn


2

盛
盛世传媒

日访问量预估1

www.sscmwl.net


1

温
温州大唐盛世传媒有限公司

日访问量预估1

www.chinaheyday.com


1

乐
乐清市大唐盛世传媒有限公司

www.ltzp.net

盛
盛世传媒

www.577sd.com

温
温州大唐盛世传媒有限公司

www.laigezhan.com

盛
盛世传媒

www.cnheyday.com

盛
盛世传媒网站

www.5ilt.cn

温
温州大唐盛世传媒有限公司

www.325604.net
"""

# Regular expression pattern to match domain names
pattern = r'www\.[a-zA-Z0-9.-]+'

# Find all matches in the text
domains = re.findall(pattern, text)

# Print the domains
for domain in domains:
    print(domain)