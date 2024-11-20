A simple Lisp-like language.

```clojure
-- tests/demo_readme.al
-- (cd tests && nst demo_readme.al)
(include ./math.al) -- defines `len` and `empty?`

(let filter (lambda (fn ls)
    (if (empty? ls)
        'empty
        (if (fn (fst ls))
            (cons (fst ls) (filter fn (rst ls)))
            (filter fn (rst ls))))))

(defmacro asseq (a b) (assert (= a b))) -- Macro expansion happens at compile time

(asseq (len (filter (lambda (x) (< x 3)) '(1 2 3))) 2)

(let fib (lambda (n)
    (if (= n 0) 0
    (if (= n 1) 1
        (+ (fib (- n 1)) (fib (- n 2)))))))

(asseq (fib 10) 55)
```

# Complete
* First-class functions
* Naive macros
* Basic imports
# Mostly done
* Hygenic macros
# To Do
* REPL improvements
* Module system
* Native functions
* And many more...

Aim: lower bytecode to LLVM or WASM.