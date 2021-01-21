#!/usr/bin/env python

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for SLURM cmsRun submission")

    argParser.add_argument('--logLevel',    action='store',         nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
    argParser.add_argument('--DASName',     action='store',         nargs='?',  type=str, required=True, help="DAS Name of the sample." )
    argParser.add_argument('--instance',    action='store',         nargs='?',  type=str, default='global', help="DAS instance." )
    argParser.add_argument('--redirector',  action='store',         nargs='?',  type=str, default='root://cms-xrd-global.cern.ch/', help="redirector for xrootd" )
    argParser.add_argument('--targetDir',   action='store',         nargs='?',  type=str, required=True, help="output director" )
    argParser.add_argument('--cfg',         action='store',         nargs='?',  type=str, help="Which config." )
    argParser.add_argument('--limit',       action='store',         nargs='?',  type=int, default=0, help="Limit DAS query?" )
    argParser.add_argument('--split',       action='store',         nargs='?',  type=int, help="Number of jobs." )
    #argParser.add_argument('--targetDir',   action='store',         nargs='?',  type=str, default=user.postprocessing_output_directory, help="Name of the directory the post-processed files will be saved" )

    return argParser

args = get_parser().parse_args()

# general imports
import os

# Logger
import logger
logger = logger.get_logger( args.logLevel, logFile=None )

def _dasPopen(dbs):
    logger.info('DAS query\t: %s',  dbs)
    return os.popen(dbs)

query, qwhat = args.DASName, "dataset"
if "#" in args.DASName: qwhat = "block"

# Deal with the sample
logger.info("Sample: %s", args.DASName)

dbs='dasgoclient -query="file %s=%s instance=prod/%s" --limit %i'%(qwhat,query, args.instance, args.limit)
dbsOut = _dasPopen(dbs).readlines()

files = []
for line in dbsOut:
    if line.startswith('/store/'):
        files.append(line.rstrip())

def partition(lst, n):
    ''' Partition list into chunks of approximately equal size'''
    # http://stackoverflow.com/questions/2659900/python-slicing-a-list-into-n-nearly-equal-length-partitions
    n_division = len(lst) / float(n)
    return [ lst[int(round(n_division * i)): int(round(n_division * (i + 1)))] for i in xrange(n) ]

# 1 job / file as default
if args.split is None:
    args.split=len(files)
chunks = partition( files, min(args.split , len(files) ) ) 
logger.info( "Got %i files and split into %i jobs of %3.2f files/job on average." % ( len(files), len(chunks), len(files)/float(len(chunks))) )
for chunk in chunks:
    pass


# Deal with the config
logger.info("Config: %s", args.cfg)
import importlib
if os.path.exists( args.cfg ):
    module = importlib.import_module(os.path.expandvars(args.cfg.rstrip('.py')))
    logger.info( "Loaded config" )
else:
    logger.error( "Did not find cfg %s", args.cfg )
    sys.exit(-1)

targetDir = os.path.join( args.targetDir, args.DASName.lstrip('/').replace('/','_') )
if not os.path.exists( targetDir ):
    os.makedirs( targetDir )
    logger.info( 'Created output directory %s', targetDir )

user          = os.getenv("USER")
batch_tmp     = "/scratch/%s/batch_input/"%(user)

if not os.path.exists( batch_tmp):
    os.makedirs( batch_tmp )
    logger.info( 'Created directory %s', batch_tmp)

# write the configs
import FWCore.ParameterSet.Config as cms
import uuid
with file('jobs.sh', 'a+') as job_file:
    for i_chunk, chunk in enumerate(chunks):
        # set input
        module.process.source.fileNames = cms.untracked.vstring(map(lambda filename: args.redirector+filename, chunk))
        move_cmds = []
        # set output
        for out_name, output_module in module.process.outputModules.iteritems():
            output_filename = '%s_%i.root'%(out_name, i_chunk)
            output_module.fileName  = cms.untracked.string(os.path.join('/tmp/', output_filename))
            move_cmds.append( (os.path.join('/tmp/', output_filename), os.path.join(targetDir, output_filename)) )
        # set maxEvents to -1
        if hasattr( module.process, "maxEvents" ):
            module.process.maxEvents.input = cms.untracked.int32(1)
        # dump cfg
        out_cfg_name = os.path.join( batch_tmp, str(uuid.uuid4()).replace('-','_')+'.py' )
        with file(out_cfg_name, 'w') as out_cfg:
            out_cfg.write(module.process.dumpPython())
        logger.info("Written %s", out_cfg_name)

        move_string =  ";" if len(move_cmds)>0 else ""
        move_string += ";".join(["mv %s %s"%move_cmd for move_cmd in move_cmds])
        job_file.write('cmsRun %s'%out_cfg_name + move_string + '\n')
