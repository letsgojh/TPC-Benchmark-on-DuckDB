import os #디렉토리 탐색
import pandas as pd #엑셀

SF = os.environ.get("SF", "unknown")

#sf 값 가져오기. 없으면 unknown
RESULT_DIR = f"./result_sf{SF}"

data = {}

# result 디렉토리의 파일들 탐색
for filename in sorted(os.listdir(RESULT_DIR)):
    if not filename.startswith("repeat") or not filename.endswith(".out"):
        continue

    # repeat 번호 추출
    repeat_num = int(filename.split("_")[0].replace("repeat", ""))
    filepath = os.path.join(RESULT_DIR, filename)
    data[repeat_num] = {}

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            # 쿼리명 찾기
            # 예: Execution Name: ./sample_queries/q7.sql
            if "Query:" not in line or "Elapsed:" not in line:
                continue


            # q번호 추출
            # line.split("/")[-1] = q7.sql)
            # .split(".")[0] = q7
            query_part = line.split("/")[-1]
            query_name = line.split("Query:")[1].split(",")[0].strip()

            # 실행시간 찾기
            # Elapsed: 1234567890 NanoSec
            if "Elapsed:" in line:
                temp = line.split("Elapsed:")[1]
                elapsed_ns = int(temp.split("ns")[0].strip())

                elapsed_sec = elapsed_ns / 1_000_000_000
                data[repeat_num][query_name] = elapsed_sec


# DataFrame 생성
df = pd.DataFrame(data).sort_index()
df = df.sort_index(axis=1)

df.columns = [f"iter{c}" for c in df.columns]
df.index = [f"query{idx.replace('q','')}" for idx in df.index]

df["average"] = df.mean(axis=1)


output_file = f"TPC_H_SF={SF}.xlsx"
df.to_excel(output_file)

print(f"Excel 생성 완료 → {output_file}")