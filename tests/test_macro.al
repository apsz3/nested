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

(defn z '() '())
(print z)
