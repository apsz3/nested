;; Parsing tests
;; (assert (= 1 1))
;; (assert (= "val" "val"))
(assert 't)
;; (assert '+ 1 2)

;; ; values
1
"val"
't
'f
'foo
(quote foo)
;; (quote foo (bar baz))
(cons 1 (cons 2 'empty))
(cons 1 (' qtd)) ; TODO: doesn't parse (' ())

; expressions
(+ 1 2)
(+ 1 2 3)
(- 1 2)
(> 1 2)
(< 1 2)
(= 1 2)
(!= 1 2)
(>= 1 2)
(<= 1 2)
(fst (cons 1 (cons 2 'empty)))
(rst (cons 1 (cons 2 'empty)))
(fst (list 1 2))
(print "Hello, world!")

; compound expressions
(+ (+ 1 2) 1)
(+ 1 (+ 1 2))
(+ (+ 1 2) (+ 1 2))

; lambdas
;; (lambda () ()
(lambda (a) a)
(lambda (a) (a))
(lambda (a b) (a b))
(lambda (a b) (lambda (a b) (a b)))

; let
(let x 1)
(let x (lambda (_) _))

;; Evaluation tests

(assert (= 1 1))
(assert (= "val" "val"))
;; (assert #t)
;; (assert (not #f))

(let asseq
    ; assert a == b
    (lambda (a b)
    (assert (= a b))))
(let assneq
    ; assert a != b
    (lambda (a b) (assert (!= a b))))

(asseq 1 1)
(asseq "val" "val")
(assert (not 'f))
;; (assneq #t #f)

(assert (> 1 0))
(assert (< 0 1))
(assert (not (< 1 0 )))
(assert (= 1 1))

(asseq (+ 1 1) 2)
(asseq (+ (+ 1 2) 1) 4)
(asseq (+ (+ 1 2) (+ 1 2)) 6)

(asseq (cons 1 2) (cons 1 2))
(assneq (cons 1 2) (cons 1 'empty))
(let x 1)
(asseq x 1)
(asseq (+ x 1) 2)
(let y (+ x 1))
(asseq y 2)

(let fib (lambda (n)
    (if (= n 0) 0
    (if (= n 1) 1
    (+ (fib (- n 1)) (fib (- n 2)))))))
(asseq (fib 7) 13)


