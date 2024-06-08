;; (if #f (+ 1 2) (+ 3 4))
;; (let x (if (!= 1 2) "yee" "yah"))
;; (print x)
;; (let x 1)
;; (let id (lambda (x) (if (= x 0) "Zero!" "one!")))
;; (print (id 1))

; Not working, TODO
;; (let fib (lambda (n)
;;   (if (= n 0) 0
;;   (if (= n 1) 1 2))))
;; (print (fib 1))

(if #f (if #t 1 2) (if #f 2 3))
;; (let sum (lambda (n)
;;   (if (= n 0) 0
;;   (if (!= n 0)
;;   (+ n (sum (- n 1)))
;;   0))))
;; (print (sum 100))
;; (print (sum 100))
;; (print (sum 100))