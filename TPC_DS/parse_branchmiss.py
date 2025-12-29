#!/usr/bin/env python3
import re
import glob
import pandas as pd
import os
import sys

# ============================================================
# 0. 환경 변수 / 기본 설정
# ============================================================
SF = os.environ.get("SF", "10")
if SF is None:
    raise RuntimeError("SF environment variable not set. e.g. SF=10 python parse_branchmiss.py")

BASE_DIR = f"result_sf{SF}"
PERF_PATTERN = os.path.join(BASE_DIR, "repeat*_perf_all.txt")
OUTPUT_XLSX = f"branch_miss_summary_sf{SF}.xlsx"

PERF_FILES = sorted(glob.glob(PERF_PATTERN))

if not PERF_FILES:
    raise RuntimeError(
        f"No perf files found.\n"
        f"Expected path: {PERF_PATTERN}"
    )

print(f"[INFO] SF={SF}")
print(f"[INFO] Found {len(PERF_FILES)} perf files")

# ============================================================
# 1. 정규식
# ============================================================
query_re = re.compile(r"Query\s+(q\d+)", re.IGNORECASE)

branches_re = re.compile(r"([\d,]+)\s*,?\s*branches")
misses_re = re.compile(r"([\d,]+)\s*,?\s*branch-misses")

user_re = re.compile(r"([\d.]+)\s+seconds\s+user")
sys_re  = re.compile(r"([\d.]+)\s+seconds\s+sys")

repeat_re = re.compile(r"repeat(\d+)_perf_all\.txt")

# ============================================================
# 2. 파싱
# ============================================================
branch_rows = []
cpu_rows = []

for perf_file in PERF_FILES:
    m = repeat_re.search(perf_file)
    if not m:
        continue

    iter_num = int(m.group(1))
    print(f"[INFO] Parsing {perf_file} (iter={iter_num})")

    current_query = None
    current_branches = None
    current_user = None
    current_sys = None

    with open(perf_file, "r") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Query
            qm = query_re.search(line)
            if qm:
                current_query = qm.group(1)
                continue

            # branches
            bm = branches_re.search(line)
            if bm:
                current_branches = int(bm.group(1).replace(",", ""))
                continue

            # branch-misses
            mm = misses_re.search(line)
            if mm and current_query is not None and current_branches is not None:
                current_misses = int(mm.group(1).replace(",", ""))

                branch_rows.append({
                    "query": current_query,
                    "iter": iter_num,
                    "branches": current_branches,
                    "branch_misses": current_misses,
                    "miss_rate": current_misses / current_branches
                })

                current_branches = None
                continue

            # user seconds
            um = user_re.search(line)
            if um:
                current_user = float(um.group(1))
                continue

            # sys seconds
            sm = sys_re.search(line)
            if sm and current_query is not None and current_user is not None:
                current_sys = float(sm.group(1))

                cpu_rows.append({
                    "query": current_query,
                    "iter": iter_num,
                    "user_sec": current_user,
                    "sys_sec": current_sys
                })

                current_user = None
                current_sys = None
                continue

# ============================================================
# 3. 결과 검증
# ============================================================
if not branch_rows:
    raise RuntimeError("No branch-miss data parsed. Check perf output format.")

if not cpu_rows:
    raise RuntimeError("No CPU time data parsed. Check perf output format.")

df_branch = pd.DataFrame(branch_rows)
df_cpu = pd.DataFrame(cpu_rows)

print(f"[INFO] Parsed branch rows: {len(df_branch)}")
print(f"[INFO] Parsed CPU rows: {len(df_cpu)}")

# ============================================================
# 4. Branch miss pivot
# ============================================================
df_branch = df_branch.sort_values(["query", "iter"])

df_branch_matrix = df_branch.pivot(
    index="query",
    columns="iter",
    values="miss_rate"
).sort_index()

df_branch_matrix.columns = [f"iter{c}" for c in df_branch_matrix.columns]
df_branch_matrix["average"] = df_branch_matrix.mean(axis=1)

# ============================================================
# 5. CPU time 평균
# ============================================================
df_cpu_avg = (
    df_cpu
    .groupby("query")[["user_sec", "sys_sec"]]
    .mean()
    .reset_index()
)

# ============================================================
# 6. Excel 저장
# ============================================================
with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
    df_branch.to_excel(writer, sheet_name="BranchMissRaw", index=False)
    df_branch_matrix.to_excel(writer, sheet_name="BranchMissMatrix")
    df_cpu.to_excel(writer, sheet_name="CpuTimeRaw", index=False)
    df_cpu_avg.to_excel(writer, sheet_name="CpuTimeAverage", index=False)

print(f"[OK] Excel generated: {OUTPUT_XLSX}")
