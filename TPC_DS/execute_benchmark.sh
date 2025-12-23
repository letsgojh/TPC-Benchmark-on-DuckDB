#!/bin/bash
set -e

# 필수 환경변수 체크
if [[ -z "$SF" ]]; then
  echo "ERROR: SF is not set (e.g. SF=30 ./execute_benchmark.sh 20)"
  exit 1
fi

# 인자 체크
if [[ "$#" -ne 1 || ! "$1" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 <Number of Iterations>"
  exit 1
fi

ITER=$1
DBFILE="tpcds_sf${SF}.duckdb"
QUERYDIR="./sample_queries_sf${SF}"
RESULTROOT="./result_sf${SF}"
LOGNAME="elapsed_time_$(date +%Y%m%d_%H%M%S).out"

mkdir -p "$RESULTROOT"

# DuckDB lock 사전 방어
if lsof "$DBFILE" >/dev/null 2>&1; then
  echo "ERROR: $DBFILE is already in use (duckdb lock detected)"
  exit 1
fi

# 벤치마크 시작
for ((r=1; r<=ITER; r++)); do
  echo "===== Repeat $r / $ITER ====="

  repeatDir="$RESULTROOT/repeat_$r"
  mkdir -p "$repeatDir"
  logFile="$RESULTROOT/repeat${r}_$LOGNAME"

  #duckdb를 한 번만 연다
  for q in "$QUERYDIR"/*.sql; do
    qname=$(basename "$q" .sql)
    outfile="$repeatDir/${qname}.out"

    echo -n "Repeat: $r/$ITER, Execution: $qname"

    start=$(date +%s%N)

    duckdb "$DBFILE" > "$outfile" <<EOF
.timer on
.headers on
.mode column
$(cat "$q")
EOF

    end=$(date +%s%N)
    elapsed=$((end - start))

    echo " (Elapsed: ${elapsed} ns)"
    echo "Repeat: $r/$ITER, Query: $qname, Elapsed: $elapsed ns" >> "$logFile"
  done
done

echo "=== Benchmark finished successfully ==="
