;; (if #f (+ 1 2) (+ 3 4))
;; (let x (if (!= 1 2) "yee" "yah"))
;; (print x)
;; (let x 1)
(let id (lambda (x) (if (= x 0) "Zero!" "one!")))
(print (id 0))