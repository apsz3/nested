;; ;; (if #f (+ 1 2) (+ 3 4))
;; ;; (let x (if (!= 1 2) "yee" "yah"))
;; ;; (print x)
;; ;; (let x 1)
;; ;; (let id (lambda (x) (if (= x 0) "Zero!" "one!")))
;; ;; (print (id 1))

;; ; Not working, TODO
;; ;; (let fib (lambda (n)
;; ;;   (if (= n 0) 0
;; ;;   (if (= n 1) 1 2))))
;; ;; (print (fib 1))

;; (if #f (if #t 1 2) (if #f 2 3))
;; (let sum (lambda (n)
;;   (if (= n 0) 0
;;   (if (!= n 0)
;;   (+ n (sum (- n 1)))
;;   0))))
;; (print (sum 100))
;; (print (sum 100))
;; (print (sum 100))

(let fib (lambda (n)
  (if (= n 0) 0
  (if (= n 1) 1
  (+ (fib (- n 1)) (fib (- n 2)))))))

(print (fib 10))

;; (let map (lambda (f l)
;;   (if (= l (list)) (list)
;;   (list (f (hd l)) (map f (tl l))))))

;; (let unpack (lambda (l)
;;   (if (= l (list)) (list)
;;   ((hd l) (unpack (tl l))))))

;; (print (unpack (map (lambda (x) (+ x 1)) (list 1 2 3 4 5))))
;; (print)

;; ;; (let _range (lambda (n i)
;; ;;   (if (= i n) (list)
;; ;;   (cons i (_range (+ i 1))))))

;; ;; (let range (lambda (n)
;; ;;   (_range n 0)))

;; (let range (lambda (n)
;;     (if (= n 0) (list)
;;         (cons (range (- n 1)) n))))

;; (print (range 10))

;; (let range (lambda (n)
;;   (let _range (lambda (n i)
;;     (if (= i n) (list)
;;     (cons i (_range n (+ i 1))))))
;;   (_range n 0)))

(begin
(print "1")
(print "2"))

(let z (cons 1 2))
(print (fst z) (rst z))


;; (print (list x))

(print (cons 1 #empty))

(print (eval (' (+ 1 5))))

(' 1 2 3 4)
