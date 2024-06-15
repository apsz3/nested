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