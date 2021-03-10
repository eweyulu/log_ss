#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parse ss logs
"""

import os
import json
import pandas as pd


def __read_sslog(logfile):
    
    """Read the next entry in file.
    Args:
        i: The index of the file reader.
    Returns:
        The next entry in file f. None if there is no entry.
    """
    with open(logfile, 'r') as f:
        
        parameters = ['minrtt', 'retrans', 'rtt', 'rto', 'data_segs_out', 
                  'cwnd', 'unacked', 'bbr_pacing_gain', 'bbr_minrtt', 
                  'bbr_bw', 'bbr_cwnd_gain', 'bytes_acked', 'pacing_rate']
        
        results = pd.DataFrame(columns=parameters)
    
        data = {}
        for line in f:
            
            # line = f.readline()
            # if not line:
            #     return None
            if line.startswith('# '):
                time = float(line[2:])
                continue

            if line.startswith('State'):
                continue
            
            if line.startswith('ESTAB'):
                
                port = line.strip()
                port = int(port[port.rfind(':') + 1:])
                data['port'] = port
                continue
           
            if not line:
                return None
            data[time] = {}
            stat = line.strip().split()
            cc = stat[0]
            
            data[time][cc] = {}
            for item in stat:
                if item.startswith('bytes_acked:'):
                    data[time][cc]['bytes_acked'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('retrans:'):
                    data[time][cc]['retrans'] = int(item[item.rfind('/') + 1:])
                elif item.startswith('cwnd:'):
                    data[time][cc]['cwnd'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('ssthresh:'):
                    data[time][cc]['ssthresh'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('data_segs_out:'):
                    data[time][cc]['data_segs_out'] = int(item[item.rfind(':') + 1:])
                elif item.startswith('rto:'):
                    data[time][cc]['rto'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('rtt:'):
                    data[time][cc]['rtt'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('minrtt:'):
                    data[time][cc]['minrtt'] = (
                        float(item[item.find(':') + 1:item.rfind('/')]) / 1000)
                elif item.startswith('unacked:'):
                    data[time][cc]['unacked'] = int(item[item.find(':') + 1:])
                elif item.startswith('pacing_rate'):
                    idx = stat.index('pacing_rate') + 1
                    data[time][cc]['pacing_rate'] = float(stat[idx].split('M')[0])
                elif item.startswith('bbr:'):
                    # bbr_item = item.strip().split()
                    data[time][cc]['bbr_bw'] = float(item.strip().split(',')[0].split(':')[2].split('M')[0])
                    data[time][cc]['bbr_minrtt'] = (float(item.strip().split(',')[1].split(':')[1])/1000)
                    data[time][cc]['bbr_pacing_gain'] = float(item.strip().split(',')[2].split(':')[1])
                    data[time][cc]['bbr_cwnd_gain'] = float(item.strip().split(',')[3].split(':')[1].split(')')[0])
                
                res = results.append(data[time][cc], ignore_index=True)
                res[['port', 'time', 'cc_name']] = pd.DataFrame([[port,
                                                        time, cc]], 
                                                        index=res.index)
                res = res[['port', 'time', 'cc_name', 'minrtt', 'retrans', 
                           'rtt', 'rto', 'data_segs_out', 'cwnd', 'unacked', 
                           'bbr_pacing_gain', 'bbr_minrtt', 'bbr_bw', 
                           'bbr_cwnd_gain', 'bytes_acked', 'pacing_rate']]
                
            return data, res


if __name__ == '__main__':
    
    script_dir = os.path.dirname(os.path.realpath('ss.py'))
    rel_path = 'ss.log'
    log_file = os.path.join(script_dir, rel_path)
    
    data, res = __read_sslog(log_file)
    
    
    # Save output data to files
    res.to_csv(path_or_buf=os.path.join(script_dir, 'results.csv'), 
                   index=False) 
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)
    
    
    
    
    