import asyncio
import re
import time

import aiohttp
import faker


async def __get_tool_baba_proxy_ip(page: int):
    http = []
    https = []
    url = f"https://www.toolbaba.cn/ip?p={page}"
    headers = {
        'cookie': f"""Hm_lvt_7b748a794d3c90cdc594298ab8b2e6a2=1680942688; __gads=ID=e57fb588d0b204f6-22edc56e16dd009b:T=1680942687:RT=1680942687:S=ALNI_MbRl_8oG_9kExWlTxgDslKWAV7THw; __gpi=UID=00000bef15223a8b:T=1680942687:RT=1680942687:S=ALNI_MaxeH9MTazEzMcYlIWLAF-hXPYC3A; Hm_lpvt_7b748a794d3c90cdc594298ab8b2e6a2={int(time.time())}""",
        'referer': url,
        'user-agent': faker.Factory().create().user_agent(),
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, timeout=5) as response:
            text = await response.text()
    for element in re.findall(
            '<tr>\s+<th.*?</th>\s+<td>(.*?)</td>\s+\s+<td>(.*?)</td>\s+\s+<td>(.*?)</td>\s+\s+<td>(.*?)'
            '</td>\s+\s+<td>(.*?)</td>\s+\s+<td>(.*?)</td>\s+\s+<td>(.*?)</td>\s+\s+<td>(.*?)</td>\s+\s+'
            '<td>(.*?)</td>\s+\s+</tr>', text, re.S):
        if element[4] == '高匿名' and int(element[6]) < 100:
            if element[2] == 'HTTP':
                http.append({'ip': element[0], 'port': element[1], 'type': element[2]})
            else:
                https.append({'ip': element[0], 'port': element[1], 'type': element[2]})
    return http, https


async def get_ip():
    for page in range(1):
        return await __get_tool_baba_proxy_ip(page)


loop = asyncio.get_event_loop()
print(loop.run_until_complete(get_ip()))
