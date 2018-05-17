#!/usr/bin/python3.6
#coding: utf-8

# https://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux

import time


def gather():
    with open('/proc/stat', 'r') as f:
        cpu_stat = f.readlines()[0]

    cpu_stat = [part.strip() for part in cpu_stat.split(' ') if part]
    cpu_stat.remove('cpu')
    cpu_stat = [int(part) for part in cpu_stat]

    user = cpu_stat[0]
    nice = cpu_stat[1]
    system = cpu_stat[2]
    idle = cpu_stat[3]
    iowait = cpu_stat[4]
    irq = cpu_stat[5]
    softirq = cpu_stat[6]
    steal = cpu_stat[7]
    guest = cpu_stat[8]
    guest_nice = cpu_stat[9]

    idle = idle + iowait
    non_idle = user + nice + system + irq + softirq + steal
    total = idle + non_idle

    return idle, total

idle0, total0 = gather()
time.sleep(1)
idle1, total1 = gather()

total_dif = total1 - total0
idle_dif = idle1 - idle0

percentage = (total_dif - idle_dif) / total_dif
print(percentage)
