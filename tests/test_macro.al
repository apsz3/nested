;(defmacro foo (+ 1 a))
;(let a 2)

;(foo)
;(print (foo))

(defmacro bar (x y z) (+ x (+ y z)))
(bar 1 2 3)