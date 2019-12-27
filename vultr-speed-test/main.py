#!/usr/bin/env python

import signal
import json
import sys
import subprocess

import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

signal.signal(signal.SIGINT, exit)
signal.signal(signal.SIGTERM, exit)
target_url = "https://www.vultr.com/faq/"


def exit(signum, frame):
    print('stop scan')
    exit()


def get_location_link():
    try:
        rsp = requests.get(target_url, timeout=5)
    except:
        print('Get vultr node web page error')
        exit()

    soup = BeautifulSoup(rsp.content, "lxml")
    geo_map = []
    for elem in soup.select('#speedtest_v4 > tr'):
        all_tds = elem.findAll('td')
        geo_location = all_tds[0].text.strip()
        ping_url = all_tds[1].findAll("a")[0].text.strip()
        download_url = all_tds[2].findAll("a")
        download_url_1 = download_url[0].get("href").strip()
        download_url_2 = download_url[1].get("href").strip()
        geo_map.append((geo_location, ping_url, download_url_1, download_url_2))
    return geo_map


def fmt_speed(speed):
    if speed < 1024:
        return "%s B/s" % speed
    elif speed < 1024 * 1024:
        return "%s KB/s" % (speed * 1.0 / 1024)
    else:
        return "%s MB/s" % (speed * 1.0 / 1024 / 1024)


def speed_str_2_float(speed_str):
    if speed_str.endswith("k"):
        return float(speed_str[:-1]) * 1024
    elif speed_str.endswith("M"):
        return float(speed_str[:-1]) * 1024 * 1024

    return float(speed_str)


def ping_test(ping_url):
    cmd = ["ping", "-c 5", ping_url]
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()
    return output


def download(download_url):
    cmd = ["curl", download_url, "-o", "/dev/null"]
    print("Downloading ... {}".format(download_url))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr)

    # for line in p.stderr:
    #     sys.stdout.write(line.decode('utf-8'))
    stdo, stde = p.communicate()

    print("Finished downloading")

    if p.returncode == 0:
        download_statistic_str = stde.decode("utf-8").split("\r")[-1]
        download_statistic_list = [i for i in download_statistic_str.split(" ") if i != ""]

        avg_speed = download_statistic_list[6]
        return download_statistic_list[6]

    return 0


def main():
    geo_map = get_location_link()

    ping_result_dict = {}
    print("=" * 20 + " start speed testing... " + "=" * 20)
    for geo_info in geo_map:
        geo_loc = geo_info[0]
        print(geo_loc)
        geo_addr = geo_info[1]

        ping_out = ping_test(geo_addr).decode('utf-8')
        print(ping_out)
        print("\n")
        print("-" * 60)

        ping_out_split = ping_out.split("\n")
        ping_out_packet = ping_out_split[-2]
        ping_out_round_trip = ping_out_split[-1]
        ping_out_round_trip_list = ping_out_round_trip.split(" = ")[1].split("/")
        ping_statistics_list = ping_out_round_trip_list[:-1]
        ping_statistics_list.insert(0, ping_out_packet.split(", ")[2].split(" ")[0][:-1])
        ping_statistics = tuple(map(float, ping_statistics_list))
        ping_result_dict[geo_loc] = ping_statistics

    print("=" * 20 + " start download test... " + "=" * 20)

    # print(ping_result_dict)
    ping_result_dict_sort_by_loss = sorted(ping_result_dict.items(), key=lambda item: item[1][0])
    ping_result_top = []
    count = 0
    pre_loss = 0.0
    for loc in ping_result_dict_sort_by_loss:
        if loc[1][0] == pre_loss:
            ping_result_top.append(loc)
        else:
            if count < 3:
                ping_result_top.append(loc)
                pre_loss = loc[1][0]

        count += 1

    top_3_ping_location = sorted(ping_result_top, key=lambda elem: elem[1][2])[0:3]

    download_location_dict = {}
    i = 0
    for geo_info in geo_map:
        geo_loc = geo_info[0]
        print(geo_loc)
        download_100_url = geo_info[2]
        download_speed_str = download(download_100_url)
        download_location_dict[geo_loc] = speed_str_2_float(download_speed_str)
        if i == 2:
            #break
            pass

        i += 1

    sorted_download_location = sorted(download_location_dict.items(), key=lambda item: item[1], reverse=True)
    top_3_download_location = sorted_download_location[:3]

    print("\n\n")
    print("="*33 + " Conclusion " + "="*33)

    print("=" * 78)
    print("=" * 28 + " Top 3 Ping Location " + "=" * 29)
    print("=" * 78)
    print("{:<30s}{:<15s}{:<15s}{:<20s}".format("Location", "Loss Packet", "Ping Delay", "Download Speed"))
    for loc in top_3_ping_location:
        location = loc[0]
        print("{:<30s}{:<15s}{:<15s}{:<20s}".format(location, str(loc[1][0])+"%", str(loc[1][2])+" ms",
                                                    fmt_speed(download_location_dict[location])))

    print("=" * 78)
    print("=" * 23 + " Top 3 Download Speed Location " + "=" * 24)
    print("=" * 78)
    print("{:<30s}{:<20s}{:<15s}{:<15s}".format("Location", "Download Speed", "Loss Packet", "Ping Delay"))
    for loc in top_3_download_location:
        location = loc[0]
        # print("{}{}{}{}".format(location, speed, ping_result_dict[location][0], ping_result_dict[location][2]))
        print("{:<30s}{:<20s}{:<15s}{:<15s}".format(location, fmt_speed(loc[1]), str(ping_result_dict[location][0])+"%",
                                                    str(ping_result_dict[location][2])+" ms"))


if __name__ == '__main__':
    main()
