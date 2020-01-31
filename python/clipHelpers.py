import os
import subprocess

def read_from_subprocess( arglist ):
    ''' Read line by line from subprocess
    '''

    proc = subprocess.Popen( arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    res = []
    while True:
        l = proc.stdout.readline()
        if l !=  '':
            res.append( l.rstrip() )
        else:
            break
    return res


def read_info_from_batchLine( line ):
    entries = line.split()
    return { "jobID":entries[0], "partition":entries[1], "title":entries[2], "user":entries[3], "status":entries[4], "time":entries[5], "nNodes":entries[6], "worker":entries[7] }

def format_batchInfo( batchOutput ):
    out = []
    for line in batchOutput:
        out.append( read_info_from_batchLine(line) )
    return out

def filter_with_wildcards( str, comp ):
    if comp.startswith("*") and comp.count("*") == 1:                          return str.endswith(comp[1:])
    elif comp.endswith("*") and comp.count("*") == 1:                          return str.startswith(comp[:-1])
    elif comp.endswith("*") and comp.startswith("*") and comp.count("*") == 2: return comp[1:-1] in str
    else:                                                                      return str == comp

def get_batchInfo( jobID=None, partition=None, title=None, user=None, status=None ):

    jobs = format_batchInfo( read_from_subprocess( ["squeue", "-u", os.getenv("USER")] )[1:] )

    if jobID and isinstance( jobID, str ):
        jobs = filter( lambda job: filter_with_wildcards(job["jobID"], jobID), jobs )
    if jobID and isinstance( jobID, list ):
        jobs = filter( lambda job: any( [filter_with_wildcards(job["jobID"], j) for j in jobID] ), jobs )
    if partition and isinstance( partition, str ) and partition in ["c","m","g"]:
        jobs = filter( lambda job: job["partition"] == partition, jobs )
    if partition and isinstance( partition, list ) and all( [p in ["c","m","g"] for p in partition] ):
        jobs = filter( lambda job: job["partition"] in partition, jobs )
    if user and isinstance( user, str ):
        jobs = filter( lambda job: user.startswith(job["user"]), jobs )
    if status and isinstance( status, str ) and status in ["R","PD","CG"]:
        jobs = filter( lambda job: job["status"] == status, jobs )
    if status and isinstance( status, list ) and all( [s in ["R","PD","CG"] for s in status] ):
        jobs = filter( lambda job: job["status"] in status, jobs )
    if title and isinstance( title, str ):
        jobs = filter( lambda job: filter_with_wildcards(job["title"], title), jobs )
    if title and isinstance( title, list ):
        jobs = filter( lambda job: any( [filter_with_wildcards(job["title"], j) for j in title] ), jobs )

    return jobs
