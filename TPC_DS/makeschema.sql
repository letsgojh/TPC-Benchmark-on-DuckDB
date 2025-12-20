INSTALL tpcds;
LOAD tpcds;

CALL dbgen(sf={{SF}});

.quit