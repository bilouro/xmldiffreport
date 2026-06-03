#!/usr/bin/env python3
"""
Generate xmldiffreport's Control-M examples — 100% SYNTHETIC / FICTIONAL.

No real data: a made-up company "GLOBEX" with an invented pipeline (GLX_*).
Reproduces the structure of a Control-M export and the diff scenarios:

  GLX_INGEST_DAILY    3-way conflict at job/attribute level (prod/uat/bench)
  GLX_SUMMARY_DAILY   2-way conflict at folder level only (uat/bench)
  GLX_LEDGER_DAILY    2-way conflict, folder + a shared job (uat/bench)
  GLX_PRICING_DAILY   INFO: a job differs vs prod (prod/bench)
  GLX_RISK_SCAN       2-way conflict: one extra folder INCOND (uat/bench)
  GLX_NIGHTLY_START   clean (test only)
  GLX_DISK_CHECK      clean (test only)
"""

import xml.etree.ElementTree as ET
from pathlib import Path

ENV = Path(__file__).resolve().parent / "controlm"
APP = "GLOBEX_PIPELINE"
SUBAPP = "GLX_BATCH"
RUNAS = "svc_glx"
CAL = "CAL_GLX"
DOCLIB = "https://wiki.example.com/docs/glx"
CMD = "/opt/glx/bin/%%JOBSCRIPT %%P_DATE"


def mk_job(
    name,
    *,
    cmdline=CMD,
    interval="00001M",
    maxrerun="0",
    critical="0",
    run_as=RUNAS,
    nodeid="NODE_A",
    desc="Synthetic batch step",
    inconds=(),
    outconds=(),
    quants=(),
    ons=(),
):
    j = ET.Element(
        "JOB",
        {
            "APPLICATION": APP,
            "SUB_APPLICATION": SUBAPP,
            "MEMNAME": name,
            "JOBNAME": name,
            "DESCRIPTION": desc,
            "CREATED_BY": "user01",
            "RUN_AS": run_as,
            "PRIORITY": "AA",
            "CRITICAL": critical,
            "TASKTYPE": "Command",
            "CYCLIC": "0",
            "NODEID": nodeid,
            "DOCLIB": DOCLIB,
            "INTERVAL": interval,
            "CMDLINE": cmdline,
            "CONFIRM": "0",
            "MAXRERUN": maxrerun,
            "CREATION_USER": "apiuser",
            "CREATION_DATE": "20260101",
            "CREATION_TIME": "090000",
            "VERSION": "1",
            "VERSION_HOST": "host01",
            "PARENT_FOLDER": "",
        },
    )
    ET.SubElement(j, "VARIABLE", {"NAME": "%%JOBSCRIPT", "VALUE": "%%SUBSTR %%JOBNAME 2 63"})
    for n, odate, andor in inconds:
        ET.SubElement(j, "INCOND", {"NAME": n, "ODATE": odate, "AND_OR": andor})
    for nm, q in quants:
        ET.SubElement(j, "QUANTITATIVE", {"NAME": nm, "QUANT": str(q), "ONFAIL": "R", "ONOK": "R"})
    for n, sign in outconds:
        ET.SubElement(j, "OUTCOND", {"NAME": n, "ODATE": "ODAT", "SIGN": sign})
    ET.SubElement(j, "RULE_BASED_CALENDARS", {"NAME": CAL})
    for code, kids in ons:
        on = ET.SubElement(j, "ON", {"STMT": "*", "CODE": code, "AND_OR": "A"})
        for tag, attrs in kids:
            ET.SubElement(on, tag, attrs)
    return j


COPY_OUT = ("DOOUTPUT", {"OPTION": "Copy", "PAR": "/opt/glx/logs/%%JOBNAME"})
RERUN = ("DOACTION", {"ACTION": "RERUN"})


def mk_folder(name, jobs, *, desc="Synthetic folder", variables=(), inconds=(), outconds=()):
    sf = ET.Element(
        "SMART_FOLDER",
        {
            "APPLICATION": APP,
            "SUB_APPLICATION": SUBAPP,
            "JOBNAME": name,
            "DESCRIPTION": desc,
            "CREATED_BY": "user01",
            "RUN_AS": RUNAS,
            "PRIORITY": "AA",
            "CRITICAL": "0",
            "TASKTYPE": "SMART Table",
            "CYCLIC": "0",
            "DOCLIB": DOCLIB,
            "CREATION_USER": "apiuser",
            "CREATION_DATE": "20260101",
            "CREATION_TIME": "090000",
            "VERSION": "1",
            "VERSION_HOST": "host01",
            "PARENT_FOLDER": name,
            "DATACENTER": "dc01",
            "FOLDER_NAME": name,
            "TYPE": "2",
        },
    )
    for nm, val in variables:
        ET.SubElement(sf, "VARIABLE", {"NAME": nm, "VALUE": val})
    for n, andor in inconds:
        ET.SubElement(sf, "INCOND", {"NAME": n, "ODATE": "ODAT", "AND_OR": andor})
    for n, sign in outconds:
        ET.SubElement(sf, "OUTCOND", {"NAME": n, "ODATE": "ODAT", "SIGN": sign})
    for j in jobs:
        j.set("PARENT_FOLDER", name)
        sf.append(j)
    ET.SubElement(
        sf,
        "RULE_BASED_CALENDAR",
        {
            "NAME": CAL,
            "DAYS_AND_OR": "O",
            "WEEKDAYS": "1,2,3,4,5",
            "JAN": "1",
            "FEB": "1",
            "MAR": "1",
            "APR": "1",
            "MAY": "1",
            "JUN": "1",
            "JUL": "1",
            "AUG": "1",
            "SEP": "1",
            "OCT": "1",
            "NOV": "1",
            "DEC": "1",
        },
    )
    return sf


FOLDER_VARS = [
    ("%%P_APP", "glx"),
    ("%%P_ENV", "u"),
    ("%%P_DATE", "%%$ODATE"),
    ("%%JOBSCRIPT", "%%SUBSTR %%X 2 63"),
]


# --------------------------------------------------------------------------
# F1 GLX_INGEST_DAILY — 3-way conflict (jobs/attributes)
# --------------------------------------------------------------------------
SHARED_INC = "GLX_INGEST_STAGE-GLX_INGEST_LOAD_OK"


def f1_base():
    init = mk_job(
        "GLX_INGEST_INIT",
        desc="Init synthetic run",
        outconds=[("GLX_INGEST_INIT-GLX_INGEST_STAGE_OK", "+")],
        quants=[("RES_GLX", 1), ("RES_SUBMIT", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    stage = mk_job(
        "GLX_INGEST_STAGE",
        desc="Stage synthetic data",
        inconds=[("GLX_INGEST_INIT-GLX_INGEST_STAGE_OK", "ODAT", "A")],
        outconds=[(SHARED_INC, "+")],
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    load = mk_job(
        "GLX_INGEST_LOAD",
        interval="00002M",
        maxrerun="3",
        desc="Load synthetic data",
        inconds=[(SHARED_INC, "ODAT", "A")],
        outconds=[("GLX_INGEST_LOAD-GLX_INGEST_POST_OK", "+")],
        quants=[("RES_GLX", 1), ("RES_SUBMIT", 1), ("RES_GLX_INGEST", 1)],
        ons=[("NOTOK", [COPY_OUT]), ("NOTOK", [RERUN])],
    )
    return mk_folder(
        "GLX_INGEST_DAILY",
        [init, stage, load],
        desc="Synthetic ingest pipeline",
        variables=FOLDER_VARS,
        inconds=[("GLX_ROOT-GLX_INGEST_DAILY_OK", "A")],
    )


def job(folder, name):
    return next(j for j in folder.findall("JOB") if j.get("JOBNAME") == name)


def set_quant(j, nm, q):
    next(x for x in j.findall("QUANTITATIVE") if x.get("NAME") == nm).set("QUANT", str(q))


def set_cond(j, tag, name, attr, val):
    next(c for c in j.findall(tag) if c.get("NAME") == name).set(attr, val)


def add_inc(el, name, andor="A"):
    ET.SubElement(el, "INCOND", {"NAME": name, "ODATE": "ODAT", "AND_OR": andor})


def rm_rerun(j):
    for on in j.findall("ON"):
        a = on.find("DOACTION")
        if a is not None and a.get("ACTION") == "RERUN":
            j.remove(on)
            return


def f1_prod():
    f = f1_base()
    add_inc(job(f, "GLX_INGEST_LOAD"), "GLX_DISK_CHECK-GLX_INGEST_LOAD_OK")
    return f


def f1_uat():
    f = f1_base()
    f.set("VERSION", "7")
    j = job(f, "GLX_INGEST_LOAD")
    j.set("CMDLINE", CMD + " --retry")
    j.set("INTERVAL", "00003M")
    j.set("MAXRERUN", "5")
    add_inc(j, "GLX_EXTRA_UAT-GLX_INGEST_LOAD_OK")
    set_cond(j, "INCOND", SHARED_INC, "AND_OR", "O")
    f.remove(job(f, "GLX_INGEST_STAGE"))  # job removed
    return f


def f1_bench():
    f = f1_base()
    f.set("VERSION", "4")
    j = job(f, "GLX_INGEST_LOAD")
    j.set("CMDLINE", CMD + " --force")
    j.set("MAXRERUN", "0")
    set_quant(j, "RES_GLX_INGEST", 3)
    rm_rerun(j)
    set_cond(j, "INCOND", SHARED_INC, "ODATE", "STAT")
    set_cond(j, "OUTCOND", "GLX_INGEST_LOAD-GLX_INGEST_POST_OK", "SIGN", "-")
    extra = mk_job(
        "GLX_INGEST_EXTRA",
        desc="Extra synthetic step",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    f.append(extra)  # job added
    return f


# --------------------------------------------------------------------------
# F2 GLX_SUMMARY_DAILY — 2-way conflict, folder level only
# --------------------------------------------------------------------------
def f2_base():
    agg = mk_job(
        "GLX_SUMMARY_AGG",
        desc="Aggregate synthetic data",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    return mk_folder(
        "GLX_SUMMARY_DAILY",
        [agg],
        desc="Synthetic summary",
        variables=FOLDER_VARS,
        inconds=[("GLX_INGEST_DAILY-GLX_SUMMARY_DAILY_OK", "A")],
        outconds=[("GLX_SUMMARY_DAILY-GLX_EXPORT_OK", "+")],
    )


def f2_uat():
    f = f2_base()
    f.set("VERSION", "7")
    next(v for v in f.findall("VARIABLE") if v.get("NAME") == "%%P_DATE").set(
        "VALUE", "%%$ODATE-1"
    )
    add_inc(f, "GLX_DISK_CHECK-GLX_SUMMARY_DAILY_OK")
    return f


def f2_bench():
    f = f2_base()
    f.set("VERSION", "4")
    ET.SubElement(
        f, "OUTCOND", {"NAME": "GLX_SUMMARY_DAILY-GLX_NEXT_BENCH_OK", "ODATE": "ODAT", "SIGN": "+"}
    )
    f.remove(next(v for v in f.findall("VARIABLE") if v.get("NAME") == "%%P_ENV"))
    return f


# --------------------------------------------------------------------------
# F3 GLX_LEDGER_DAILY — 2-way conflict, folder + a shared job
# --------------------------------------------------------------------------
def f3_base():
    cache = mk_job(
        "GLX_LEDGER_CACHE",
        desc="Cache synthetic ledger",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    run = mk_job(
        "GLX_LEDGER_RUN",
        desc="Run synthetic ledger",
        outconds=[("GLX_LEDGER_RUN-GLX_LEDGER_POST_OK", "+")],
        quants=[("RES_GLX", 1), ("RES_GLX_LEDGER", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    return mk_folder(
        "GLX_LEDGER_DAILY", [cache, run], desc="Synthetic ledger", variables=FOLDER_VARS
    )


def f3_uat():
    f = f3_base()
    f.set("VERSION", "7")
    f.set("DESCRIPTION", "Synthetic ledger (variant uat)")
    j = job(f, "GLX_LEDGER_RUN")
    j.set("CRITICAL", "1")
    j.set("DESCRIPTION", "Run synthetic ledger - priority")
    j.set("CMDLINE", CMD + " --mode-uat")
    set_quant(j, "RES_GLX_LEDGER", 2)
    return f


def f3_bench():
    f = f3_base()
    f.set("VERSION", "4")
    f.set("DESCRIPTION", "Synthetic ledger (variant bench)")
    add_inc(f, "GLX_DISK_CHECK-GLX_LEDGER_DAILY_OK")
    j = job(f, "GLX_LEDGER_RUN")
    j.set("RUN_AS", "svc_glx_b")
    j.set("NODEID", "NODE_B")
    j.set("CMDLINE", CMD + " --mode-bench")
    set_cond(j, "OUTCOND", "GLX_LEDGER_RUN-GLX_LEDGER_POST_OK", "SIGN", "-")
    return f


# --------------------------------------------------------------------------
# F4 GLX_PRICING_DAILY — INFO: a job differs vs prod
# --------------------------------------------------------------------------
def f4_base():
    calc = mk_job(
        "GLX_PRICING_CALC",
        desc="Compute synthetic prices",
        outconds=[("GLX_PRICING_CALC-GLX_PRICING_POST_OK", "+")],
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    post = mk_job(
        "GLX_PRICING_POST",
        desc="Post synthetic prices",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    return mk_folder(
        "GLX_PRICING_DAILY", [calc, post], desc="Synthetic pricing", variables=FOLDER_VARS
    )


def f4_bench():
    f = f4_base()
    f.set("VERSION", "4")
    j = job(f, "GLX_PRICING_CALC")
    j.set("CMDLINE", CMD + " --px-bench")
    j.set("MAXRERUN", "2")
    return f


# --------------------------------------------------------------------------
# F5 GLX_RISK_SCAN — 2-way conflict: one extra folder INCOND
# --------------------------------------------------------------------------
def f5_base():
    scan = mk_job(
        "GLX_RISK_SCANJOB",
        desc="Scan synthetic risk",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    sens = mk_job(
        "GLX_RISK_SENS",
        desc="Sensitivity synthetic",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    return mk_folder(
        "GLX_RISK_SCAN",
        [scan, sens],
        desc="Synthetic risk scan",
        variables=FOLDER_VARS,
        inconds=[("GLX_PRICING_DAILY-GLX_RISK_SCAN_OK", "A")],
    )


def f5_bench():
    f = f5_base()
    f.set("VERSION", "4")
    add_inc(f, "GLX_INGEST_DAILY-GLX_RISK_SCAN_OK")  # the only difference
    return f


# --------------------------------------------------------------------------
# F6/F7 — clean folders (test only)
# --------------------------------------------------------------------------
def f6():
    top = mk_job(
        "GLX_NIGHTLY_TOP",
        desc="Nightly synthetic start",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    return mk_folder(
        "GLX_NIGHTLY_START", [top], desc="Synthetic nightly start", variables=FOLDER_VARS
    )


def f7():
    chk = mk_job(
        "GLX_DISK_CHECKJOB",
        desc="Check synthetic disk",
        quants=[("RES_GLX", 1)],
        ons=[("NOTOK", [COPY_OUT])],
    )
    mail = mk_job(
        "GLX_DISK_MAIL",
        desc="Mail synthetic disk report",
        inconds=[("GLX_DISK_CHECKJOB-GLX_DISK_MAIL_OK", "ODAT", "A")],
        quants=[("RES_GLX", 1)],
    )
    return mk_folder(
        "GLX_DISK_CHECK", [chk, mail], desc="Synthetic disk check", variables=FOLDER_VARS
    )


def write(env, fname, folders):
    root = ET.Element(
        "DEFTABLE",
        {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": "Folder.xsd",
        },
    )
    for f in folders:
        root.append(f)
    out = ENV / env / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    print(f"  {env}/{fname}: {[f.get('FOLDER_NAME') for f in folders]}")


def main():
    # clear old examples
    for old in ENV.rglob("*.xml"):
        old.unlink()
    print("A gerar exemplos sintéticos:")
    write("prod", "hotfix-c.xml", [f1_prod(), f4_base()])
    write("uat", "patch-b.xml", [f1_uat(), f2_uat(), f3_uat()])
    write("bench", "patch-a.xml", [f1_bench(), f2_bench(), f4_bench(), f3_bench()])
    write("bench", "patch-x.xml", [f5_bench()])
    write("test", "patch-d.xml", [f6(), f7()])
    write("uat", "patch-e.xml", [f5_base()])
    print("Feito.")


if __name__ == "__main__":
    main()
