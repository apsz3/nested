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
(let biz (' add 1 2222))
;; (let biz (' (add 1 2)))

;; (print (eval biz))

;; (let a (list #add #a #b))
;; (let b (list (#add #a #b)))