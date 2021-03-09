#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

import os, sys
import threading
import time
import socket

import shell


def __launch_ss(dur, ss_interval_second, log_path, sender_ip, sender_port):

    """Run ss command and append log to file.
    Args:
        dur: The duration of the experiment.
        log_path: The path of log file.
    """
    t0 = time.time()
    t = t0

    # port_cnt = sum([c.num for c in self.__conns])
    with open(log_path, 'w') as f:
        f.truncate()
    ss_ip =  sender_ip
    # ss_ip = 'localhost'
    port = int(sender_port)
    ss_cmd = 'ss -tin "dport = :%d and dst %s" >> %s' % (
        port, ss_ip,log_path,)
    while t < t0 + dur:
        with open(log_path, 'a') as f:
            f.write('# %f\n' % (time.time(),))
        shell.run(ss_cmd)
        t += ss_interval_second
        to_sleep = t - time.time()
        if to_sleep > 0:
            time.sleep(to_sleep)

def launch_ss(dur, path, sender_ip, sender_port):
    
    ss_interval_second = 0.1
    if ss_interval_second == 0:
        return None, None
    log_path = os.path.join(path, 'ss.log')
    t = threading.Thread(target=__launch_ss,
                         args=(dur, ss_interval_second, log_path,
                                sender_ip, sender_port))
    t.start()
    return t, log_path


if __name__ == '__main__':
    
    dur = float(sys.argv[1])
    sender_ip = sys.argv[2]
    sender_port = sys.argv[3]
    path = os.path.dirname(os.path.realpath('ss.py'))
    
    launch_ss(dur, path, sender_ip, sender_port)
    
    