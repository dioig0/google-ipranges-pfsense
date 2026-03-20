#!/usr/bin/env python3

import json
import pathlib
import urllib.request
from netaddr import IPSet

GOOG_URL = "https://www.gstatic.com/ipranges/goog.json"
CLOUD_URL = "https://www.gstatic.com/ipranges/cloud.json"

OUT_V4 = pathlib.Path("output/google-apis-defaultdomains-ipv4.txt")
OUT_V6 = pathlib.Path("output/google-apis-defaultdomains-ipv6.txt")


def load_ipsets(url: str):
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)

    ipv4 = IPSet()
    ipv6 = IPSet()

    for item in data.get("prefixes", []):
        v4 = item.get("ipv4Prefix")
        v6 = item.get("ipv6Prefix")

        if v4:
            ipv4.add(v4)
        if v6:
            ipv6.add(v6)

    return ipv4, ipv6


def write_ipset(ipset: IPSet, outfile: pathlib.Path):
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with outfile.open("w", encoding="utf-8", newline="\n") as f:
        for cidr in ipset.iter_cidrs():
            f.write(f"{cidr}\n")


def main():
    goog_v4, goog_v6 = load_ipsets(GOOG_URL)
    cloud_v4, cloud_v6 = load_ipsets(CLOUD_URL)

    result_v4 = goog_v4 - cloud_v4
    result_v6 = goog_v6 - cloud_v6

    write_ipset(result_v4, OUT_V4)
    write_ipset(result_v6, OUT_V6)


if __name__ == "__main__":
    main()
