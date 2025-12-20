#!/bin/bash

DBFILE="tpch_sf${SF}.duckdb"
fileList=./sample_queries/*.sql
resPath=./result/
resName="elapsed_time_$(date +%Y%m%d_%H%M%S).out"

# 인자 체크
if [[ "$#" -ne 1 || ! "$1" =~ ^[0-9]+$ ]]; then
  echo
  echo "Usage: $0 <The number of Iterations>"
  echo
  exit 1
fi

# result 폴더 생성
mkdir -p result

echo

for ((repeatCnt=1; repeatCnt <= $1; repeatCnt++))
do
    repeatDir="./result/repeat_$repeatCnt"
    mkdir -p "$repeatDir"

    # repeat_n/log 파일 경로
    fullPath=$resPath'repeat'$repeatCnt'_'$resName

    for file in $fileList
    do
        name=$(basename "$file")
        name=${name%.*}

        output="${repeatDir}/${name}.out"

        echo -n "Repeat: ${repeatCnt}/$1, Execution: ${file}"

        # 시간 측정 시작 — 나노초 변환 (정확)
        start_time_sec=$(date +%s)
        start_time_nsec=$(date +%N)
        start_time=$((10#$start_time_sec*1000000000 + 10#$start_time_nsec))

        # DuckDB 실행
        duckdb "$DBFILE" > "$output" <<EOF
.headers on
.mode column
$(cat "$file")
EOF

        # 시간 측정 끝
        end_time_sec=$(date +%s)
        end_time_nsec=$(date +%N)
        end_time=$((10#$end_time_sec*1000000000 + 10#$end_time_nsec))
        elapsed=$((10#$end_time - 10#$start_time))

        echo " (Elapsed: ${elapsed} NanoSec.)"
        echo

        echo "Repeat: $repeatCnt/$1, Execution Name: $file (Elapsed: $elapsed NanoSec.)" >> "$fullPath"
    done
done
