;; Parsing tests

; values
1
"val"
#t
#f

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
(assert #t)
(assert (not #f))

(let asseq 
    ; assert a == b
    (lambda (a b)
    (assert (= a b))))
(let assneq
    ; assert a != b
    (lambda (a b) (assert (!= a b))))

(asseq 1 1)
(asseq "val" "val")
(assert #t)
(assert (not #f))
(assneq #t #f)

(assert (> 1 0))
(assert (< 0 1))
(assert (not (< 1 0 )))
(assert (= 1 1))

(asseq (+ 1 1) 2)
(asseq (+ (+ 1 2) 1) 4)
(asseq (+ (+ 1 2) (+ 1 2)) 6)



;; (assert #t)
;; (assert (= 1 1))
;; (asseq #t #t)
;; (asseq 1 1)