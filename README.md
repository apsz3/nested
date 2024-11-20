`tests/demeo_readme.md`

```clojure
(defmacro asseq (a b) (assert (= a b)))
(let fib (lambda (n)
    (if (= n 0) 0
    (if (= n 1) 1
        (+ (fib (- n 1)) (fib (- n 2)))))))
(asseq (fib 10) 55)
```

# Complete
* Macros
# Mostly done
* Hygenic macros
# To Do
* REPL improvements