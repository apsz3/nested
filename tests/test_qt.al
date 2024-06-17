;; ((eval (' (+ 1 2))))
;; (let foo 1)
;; (let bar (eval (' foo)))
;; (print bar)
;; ;; (let foo ('
;;     (a (b e (c) (d)))
;;     (e (f (g) (h)))))

; Let are evaluated as they stand,
; not lazily.
; Defn evaluated lazily.
;; (let add (lambda (a b) (+ a b)))
; THIS IS NOT LEGAL IN SCHEME: '(1 2 3) --eval expects a proc!
;; (let a (' + 1 2222 4 4 4))
;; (let b (' (+ 1 2) (+ 2 3) ( (+ 2 3))))
;; (print b)
;; (print (eval biz))

;; (let a (list #add #a #b))
;; (let b (list (#add #a #b)))

(let a (' 1))
(print (+ 1 (eval a)))

(let b (' 1 2 3))
(print (fst b))
(print (rst b))

(let empty ('))
(print empty)
(print (= empty (')))

(let big ('
    (a (b e (c) (d)))
    (e (f (g) (h)))))

(let tree ('
    (1 (2 3) (4 5))))

(let sum-tree (lambda (t)
    (if (= t #empty) 0 ; done
    (if (= (rst t) #empty) (print (fst t)) ; leaf
    (begin (print (fst t)) (sum-tree (fst t)) (sum-tree (rst t))))))) ; pair

;; (let print-tree (lambda (t)
;;     ()

(print (eval (' (+ 1 2))))