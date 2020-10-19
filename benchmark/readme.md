# Benchmark

## container.get
| Scope         | Ops                |
| ------------- |:------------------:|
| transient     | 6500    |
| singleton     | 437690 |
| big_transient  | 5439 |
| big_singleton  | 432372 |

*Singleton scope is faster in 67 times*  
*With a large number of objects, singleton scope is faster 72 times*  

## container.get_all
| Scope         | Ops                |
| ------------- |:------------------:|
| transient     | 3802    |
| singleton     | 356515 |
| big_transient  | 153 |
| big_singleton  | 38886 |

*Singleton scope is faster in 93 times*  
*With a large number of objects, singleton scope is faster 254 times* 
