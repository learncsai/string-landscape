import platform,resource,time

def peak_rss_bytes():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system()=='Darwin' else value*1024)
