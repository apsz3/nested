;(defmacro foo (+ 1 a))
;(let a 2)

;(foo)
;(print (foo))


(defmacro asseq (a b) (assert (= a b)))
(asseq 1 1)

(defmacro bar (x y z) (+ x (+ y z)))
(asseq (bar 1 2 3) 6)

(defmacro defn (name args body)
    (let name (lambda args body)))

(defn fib (n) 
    (if (= n 0) 0
    (if (= n 1) 1
        (+ (fib (- n 1)) (fib (- n 2))))))
(asseq (fib 10) 55)
