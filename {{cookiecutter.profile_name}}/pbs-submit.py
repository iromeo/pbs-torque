#!/usr/bin/env python3
import sys
import argparse
import subprocess

# TODO: rewrite this.., e.g.
# 1. use key dictionary for qsub args
# 2. take defaults if set from cluster params,
#        cluster_params = job_properties["cluster"]
# 3. add `job_properties["resources"]` values to cluster_params
# 4. consider using job_properties["params"] because resources expects numbers, not string values
# 5. is walltime in "HH:MM:SS" is possible?
# 6. specify queue: --config or params...
# 7. pass "-j oe" via cluster
# 8. by default do not add job dependencies (washu not support this)
#
# TODO: maybe accept general "mem" option and using --cluster-config chose how to pass it to
# cluster, like 'mem', 'vmem', etc
# also see: https://bitbucket.org/snakemake/snakemake/issues/279/unifying-resources-and-cluster-config
# Parameters defined in the cluster config file are now accessible in the job properties under the key “cluster”.


from snakemake.utils import read_job_properties

# Use this cmdline args in `config.yaml` cluster cmdline options:
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--depend",
                    help="Space separated list of ids for jobs this job should depend on.")
parser.add_argument("-a", help="Declare the time when the job becomes eligible for execution.")
parser.add_argument("-A", help="Define the account string.")
parser.add_argument("-b", help="PBS Server timeout.")
parser.add_argument("-c", help="Checkpoint options.")
parser.add_argument("-C", help="Directive prefix in script file.")
parser.add_argument("-d", help="Working directory to be used (default: ~). PBS_O_INITDIR")
parser.add_argument("-D", help="Root directory to be used. PBS_O_ROOTDIR")
parser.add_argument("-e", help="standard error path.")
parser.add_argument("-f", help="Fault tolerant.", action="store_true")
parser.add_argument("-h", help="Apply user hold at submission time", action="store_true")
parser.add_argument("-j", help="Merge standard error and standard out. (oe or eo)")
parser.add_argument("-l", help="Resource list.")
parser.add_argument("-m", help="Mail options.")
parser.add_argument("-M", help="Mail users.")
parser.add_argument("-N", help="Name for the job.")
parser.add_argument("-o", help="standard output path.")
parser.add_argument("-p", help="Set job priority.")
parser.add_argument("-P", help="Proxy user for job.")
parser.add_argument("-q", help="Set destination queue.")
parser.add_argument("-t", help="Array request.")
parser.add_argument("-u", help="Set user name for job.")
parser.add_argument("-v", help="Environment variables to export to the job.")
parser.add_argument("-V", help="Export all environment variables.", action="store_true")
parser.add_argument("-w", help="Set working directory. PBS_O_WORKDIR")
parser.add_argument("-W", help="Additional attributes.")
parser.add_argument("--help", help="Display help message.", action="store_true")

parser.add_argument("positional", action="append", nargs="?")
args = parser.parse_args()

if args.help:
    parser.print_help()
    sys.exit(0)

jobscript = sys.argv[-1]

job_properties = read_job_properties(jobscript)

atime = ""
acc_string = ""
pbs_time = ""
chkpt = ""
pref = ""
dd = ""
rd = ""
se = ""
ft = ""
hold = ""
j = ""
resource = ""
mail = ""
mailuser = ""
jname = ""
so = ""
priority = ""
proxy = ""
q = ""
ar = ""
user = ""
ev = ""
eall = ""
wd = ""
add = ""
depend = ""
extras = ""

# disabled
# if args.depend:
#     for m in args.depend.split(" "):
#         depend = depend + ":" + m
# if depend:
#     depend = " -W \"depend=afterok" + depend + "\""

if args.positional:
    for m in args.positional:
        extras = extras + " " + m

if args.a:
    atime = " -a " + args.a
if args.A:
    acc_string = " -A " + args.A
if args.b:
    pbs_time = " -b " + args.b
if args.c:
    chkpt = " -c " + args.c
if args.C:
    pref = " -C " + args.C
if args.d:
    dd = " -d " + args.d
if args.D:
    rd = " -D " + args.D
if args.e:
    se = " -e " + args.e
if args.f:
    ft = " -f"
if args.h:
    hold = " -h"
if args.j:
    j = " -j " + args.j
if args.l:
    resource = " -l " + args.l
if args.m:
    mail = " -m " + args.m
if args.M:
    mailuser = " -M " + args.M
if args.N:
    jname = " -N " + args.N
if args.o:
    so = " -o " + args.o
if args.p:
    priority = " -p " + args.p
if args.P:
    proxy = " -P " + args.P
if args.q:
    q = " -q " + args.q
if args.t:
    ar = " -t " + args.ar
if args.u:
    user = " -u " + args.u
if args.v:
    ev = " -v " + args.v
if args.V:
    eall = " -V"
if args.w:
    wd = " -w " + args.w
if args.W:
    add = " -W \"" + args.W + "\""

nodes = ""
ppn = ""
mem = ""
vmem = ""
walltime = ""

cluster_params = job_properties["cluster"]
if "j" in cluster_params:
    j = " -j " + cluster_params["j"]

if "threads" in job_properties:
    ppn = "ppn=" + str(job_properties["threads"])

# if "cluster_log" in job_properties["params"]:
#     so = " -o {}".format(job_properties["params"]["cluster_log"])
# else:
if "log" in job_properties:
    log = job_properties["log"]
    if log:
        so = " -o {}_job.log".format(log[0])

# TODO: else conider "log.cluster" if named logs

if "resources" in job_properties:
    resources = job_properties["resources"]
    if "nodes" in resources:
        nodes = "nodes=" + str(resources["nodes"])
    if ppn and not nodes:
        nodes = "nodes=1"
    if "mem" in resources:
        mem = "mem=" + str(resources["mem"])
    if "vmem_gb" in resources:
        vmem_value = resources["vmem_gb"]
        vmem = "vmem={}gb".format(resources["vmem_gb"])

    if "walltime" in resources:
        walltime = "walltime=" + str(resources["walltime"])
    elif "walltime_h" in resources:
        walltime = "walltime={}:00:00".format(resources["walltime_h"])
    elif "walltime_m" in resources:
        walltime = "walltime=00:{}:00".format(resources["walltime_m"])

# -l option: Resource params list:
resourceparams = ""
resourceparams_list = ["{}:{}".format(nodes, ppn) if ppn else nodes]
resourceparams_list.extend([mem, vmem, walltime])
resourceparams_list = [s for s in resourceparams_list if s]
if resourceparams_list:
    resourceparams = ' -l "{}"'.format(",".join(resourceparams_list))

cmd = "qsub {a}{A}{b}{c}{C}{d}{D}{e}{f}{h}{j}{l}{m}{M}{N}{o}{p}{P}{q}{t}{u}{v}{V}{w}{W}{rp}{dep}" \
      "{ex}".format(a=atime, A=acc_string, b=pbs_time, c=chkpt, C=pref, d=dd, D=rd, e=se, f=ft,
                    h=hold, j=j, l=resource, m=mail, M=mailuser, N=jname, o=so, p=priority,
                    P=proxy, q=q, t=ar, u=user, v=ev, V=eall, w=wd, W=add, rp=resourceparams,
                    dep=depend, ex=extras
                    )

print("Job qsub cmdline: ", cmd, file=sys.stderr)
try:
    res = subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE)
except subprocess.CalledProcessError as e:
    raise e

res = res.stdout.decode()
print(res.strip())
