# Benchmark

version-0.1.2

## container.get
| Scope         | Ops                |
| ------------- |:------------------:|
| transient     | 6623    |
| singleton     | 511665 |
| big_transient  | 5858 |
| big_singleton  | 508240 |

*Singleton scope is faster in 77 times*  
*With a large number of objects, singleton scope is faster 86 times*  

## container.get_all
| Scope         | Ops                |
| ------------- |:------------------:|
| transient     | 3758    |
| singleton     | 389158 |
| big_transient  | 157 |
| big_singleton  | 41588 |

*Singleton scope is faster in 103 times*  
*With a large number of objects, singleton scope is faster 264 times* 

version-0.1.0

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
