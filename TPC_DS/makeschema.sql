INSTALL tpcds;
LOAD tpcds;

CALL dsdgen(sf={{SF}});

.quit
