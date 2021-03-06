import os
from clipHelpers import read_from_subprocess

def renew_proxy( filename = None, rfc = False, request_time = 192, min_time = 0):

    if not min_time:     min_time     = 192
    if not request_time: request_time = 192

    min_time     = int(min_time)
    request_time = int(request_time)
    proxy        = None
    timeleft     = 0

    # Make voms-proxy-info look for a specific proxy
    if filename:
        os.environ["X509_USER_PROXY"] = filename

    # Check proxy path
    try:
        proxy = read_from_subprocess( 'voms-proxy-info --path'.split() )[0]
    except IndexError:
        pass

    try:
        tl       = read_from_subprocess( 'voms-proxy-info --timeleft'.split() )
        timeleft = int( float( tl[0] ))
    except IndexError:
        pass
    except ValueError:
        pass

    # Return existing proxy from $X509_USER_PROXY, the default location or filename
    if proxy is not None and os.path.exists( proxy ):
        if not filename or os.path.abspath( filename ) == proxy:
            print( "Found proxy %s with lifetime %i hours"%(proxy, timeleft/3600))
            if timeleft > 0 and timeleft >= min_time*3600 :
                os.environ["X509_USER_PROXY"] = proxy
                print( "Proxy still valid! Using existing proxy!" )
                return proxy
            else:
                print( "Lifetime %i not sufficient (require %i, will request %i hours)."%(timeleft/3600, min_time, request_time) )

    
    arg_list = ['voms-proxy-init', '-voms', 'cms']

    if filename is not None:
        arg_list += [ '-out', filename ]

    arg_list += ['--valid', "%i:0"%request_time ]

    if rfc:
        arg_list += ['-rfc']

    # make proxy
    p = read_from_subprocess( arg_list )
    if not p:
        raise RuntimeError( "Failed to make proxy!" )
    
    # read path
    new_proxy = None
    try:
        new_proxy = read_from_subprocess( 'voms-proxy-info --path'.split() )[0]
    except IndexError:
        pass

    if new_proxy and os.path.exists( new_proxy ):
        os.environ["X509_USER_PROXY"] = new_proxy
        print( "Successfully created new proxy %s"%new_proxy )
        return new_proxy
    else:
        raise RuntimeError( "Failed to make proxy %s" % new_proxy )
