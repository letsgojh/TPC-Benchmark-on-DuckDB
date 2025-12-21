# TPC-H,TPC-DS Benchmark on DuckDB - Setup Guide


## Overview

DuckDB를 이용한 TPC-H,TPC-DS benchmark 세팅 가이드라인입니다.
dataset을 생성하고, makefile을 통해 benchmark queries들을 실행시키는 것을 도와줍니다.


## 0. clone this repository

- 해당 레포지토리를 clone 합니다

    ```bash
    git clone git@github.com:letsgojh/TPC-Benchmark-on-DuckDB.git
    cd TPC-Benchmark-on-DuckDB
    ```

## 1. Install DuckDB CLI

- duckdb를 설치하는 여러가지 방법이 있지만, ubuntu의 패키지 매니저인 apt를 통해 설치하였습니다.
- apt이외에 직접 duckdb 홈페이지에서 설치하는 방법도 있습니다.
    ```bash
    sudo apt install duckdb

    //설치되었다면 어느 디렉토리에 위치하는지 확인합니다.
    which duckdb

    //version을 확인합니다.
    duckdb --version
    ```

## 2. select the benchmark program that you want

- TPC-H와 TPC-DS중 Benchmark를 원하는 디렉토리로 접근한다

    ```bash
        //1. select TPC_DS
        cd TPC_DS

        //2. select TPC_H
        cd TPC_H
    ```

## 3. Execute the makefile scripts

| instruction | descript | example |
|----------|------|--------|
| make SF= {SF}| duckdb내에 TPC 관련 schema와 query들을 생성합니다.(SF값을 입력하지 않는다면 자동으로 1로 실행됩니다.)| make SF=10 |
| make queries| duckdb내에 있는 query들을 외부 sample_queries 디렉토리로 옮겨 적습니다. | make queries|
| make benchmark ITER= {ITER} | benchmarking를 ITER 횟수만큼 반복 실행합니다. 실행된 결과를 기록하여 result 디렉토리 내에 저장합니다. | make benchmark ITER=20 |
| make parse | result 디렉토리 내에 있는 정보를 excel 파일로 생성합니다. | make SF=10 |
| make clean| 생성된 sample_queries,result 디렉토리와 excel 파일을 삭제합니다. | make clean |

- make SF=<SF> -> make queries -> make benchmark ITER=<ITER> -> make parse 순으로 실행시키시면됩니다.
