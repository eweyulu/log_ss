#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parse ss logs
"""

import os, sys
import pandas as pd
import re


def __read_sslog(logfile):
    
    """Read the next entry in file.
    Args:
        i: The index of the file reader.
    Returns:
        The next entry in file f. None if there is no entry.
    """

    # logfile = 'test-log.log'

    with open(logfile, 'r') as f:
    
        lst = []
        for line in f:
            data = {}
            
            if line.startswith('FIN-WAIT'):
                break
    
            if line.startswith('# '):
                time = float(line[2:])
                continue
    
            if line.startswith('State'):
                continue
            
            if line.startswith('SYN-SENT'):
                tmp_item = line.strip().split()[0]
                continue
                               
            if line.startswith('ESTAB'):
                
                sport = line.strip()
                sport = int(sport[sport.rfind(':') + 1:])
                dport = int(line.split(':')[4].strip('   ['))
                tmp_item = ''
                continue
           
            if not line:
                # return None
                continue
            if tmp_item == 'SYN-SENT':
                continue
            data['time'] = time
            data['sport'] = sport
            data['dport'] = dport
            stat = line.strip().split()
            cc = stat[1]
            
            data['cc_name'] = cc
            for item in stat:
                if item.startswith(('wscale', 'mss', 'segs_out', 'segs_in', 
                                  'send', 'lastsnd', 'lastrcv', 'lastack', 
                                  'rcv_space', 'notsent')):
                    continue
                if item.startswith('skmem:'):
                    tmp=re.split(r'skmem:',item)[1].strip('(').strip(')').split(',')
                    data['rmem_alloc'] = int(tmp[0].replace('r',''))
                    data['rcv_buf'] = int(tmp[1].replace('rb',''))
                    data['wmem_alloc'] = int(tmp[2].replace('t',''))
                    data['snd_buf'] = int(tmp[3].replace('tb',''))
                    data['fwd_alloc'] = int(tmp[4].replace('f',''))
                    data['wmem_queued'] = int(tmp[5].replace('w',''))
                    data['opt_mem'] = int(tmp[6].replace('o',''))
                    data['back_log'] = int(tmp[7].replace('bl',''))
                    
                if item.startswith('bytes_acked:'):
                    data['bytes_acked'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('retrans:'):
                    data['retrans'] = int(item[item.rfind('/') + 1:])
                elif item.startswith('cwnd:'):
                    data['cwnd'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('ssthresh:'):
                    data['ssthresh'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('data_segs_out:'):
                    data['data_segs_out'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('rto:'):
                    data['rto'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('rtt:'):
                    data['rtt'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('minrtt:'):
                    data['minrtt'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('unacked:'):
                    data['unacked'] = int(item[item.find(':') + 1:])
                elif item.startswith('pacing_rate'):
                    idx = stat.index('pacing_rate') + 1
                    data['pacing_rate'] = float(re.split(r'M|K|b', stat[idx])[0])
                elif item.startswith('bbr:'):
                    data['bbr_bw'] = float(re.split(r'M|K|b', item.strip().split(',')[0].split(':')[2])[0])
                    data['bbr_minrtt'] = (float(item.strip().split(',')[1].split(':')[1])/1000)
                    data['bbr_pacing_gain'] = float(item.strip().split(',')[2].split(':')[1])
                    data['bbr_cwnd_gain'] = float(item.strip().split(',')[3].split(':')[1].split(')')[0])
                    
            lst.append(data)
            
                
        res = pd.DataFrame(lst)
        
        if res['cc_name'][0] == 'bbr':
            res = res[['sport', 'dport','time', 'cc_name', 'minrtt',  
                    'rtt', 'rto', 'data_segs_out', 'cwnd', 'unacked', 
                    'bbr_pacing_gain', 'bbr_minrtt', 'bbr_bw', 
                    'bbr_cwnd_gain', 'bytes_acked', 'pacing_rate']]
        elif res['cc_name'][0] == 'cubic':
            res = res[['sport', 'dport', 'time', 'cc_name', 'minrtt',  
                    'rtt', 'rto', 'rmem_alloc', 'rcv_buf', 'wmem_alloc', 
                    'snd_buf', 'fwd_alloc', 'wmem_queued', 'opt_mem', 
                    'back_log', 'data_segs_out', 'cwnd', 'unacked', 
                    'bytes_acked', 'pacing_rate']]
        elif res['cc_name'][0] == 'reno':
            res = res[['sport', 'dport', 'time', 'cc_name', 'minrtt',  
                    'rtt', 'rto', 'rmem_alloc', 'rcv_buf', 'wmem_alloc', 
                    'snd_buf', 'fwd_alloc', 'wmem_queued', 'opt_mem', 
                    'back_log', 'cwnd', 'pacing_rate']]
        else:
            pass
                
    return res


if __name__ == '__main__':
        
    script_dir = os.path.dirname(os.path.realpath('ss-ncf.py'))
    # rel_path = 'ss.log'
    rel_path = sys.argv[1]
    log_file = os.path.join(script_dir, rel_path)
    
    res = __read_sslog(log_file)
    fname = res['cc_name'][0]
    
    # Save output data to files
    res.to_csv(path_or_buf=os.path.join(script_dir, 'results-' +fname+'.csv'), 
                    index=False) 
    
    
    
    