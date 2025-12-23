SF ?= 1
ITER ?= 5
DB := tpcds_sf$(SF).duckdb
QUERYDIR := sample_queries_sf$(SF)
RESULTDIR := result_sf$(SF)
EXCEL := TPCDS_SF=$(SF).xlsx

.PHONY : benchmark parse

# 1. make schma and data about sf
#<결과물> : <의존 파일>
#sed s/찾을문자열/바꿀문자열/옵션 => 찾을문자열을 바꿀문자열로 치환해준다.
$(DB) : makeschema.sql
	@echo "Generating TPC-DS DB (SF=$(SF))"
	sed "s/{{SF}}/$(SF)/g" makeschema.sql | duckdb $(DB)


#2. make sample queries about duckdb sql
queries : $(QUERYDIR)/q99.sql

$(QUERYDIR)/q99.sql: $(DB)
	@echo ">>> Exporting TPC-DS queries"
	mkdir -p $(QUERYDIR)
	for i in `seq 1 99`; do \
		duckdb $(DB) -c "\
		COPY ( \
		  SELECT query \
		  FROM tpch_queries() \
		  WHERE query_nr = $$i \
		) TO '$(QUERYDIR)/q$$i.sql' (HEADER false, QUOTE '');"; \
	done


#3. execute TPC-H benchmark for n iter
benchmark: $(QUERYDIR)/q99.sql
	@echo ">>> Running benchmark (ITER=$(ITER))"
	SF=$(SF) ./execute_benchmark.sh $(ITER)


#4. write execute time in 
parse:
	@echo ">>> Parsing benchmark results"
	SF=$(SF) python3 parse_elapsed_only.py

clean :
	rm -rf sample_queries_sf* result_sf* TPC_H_SF=*.xlsx