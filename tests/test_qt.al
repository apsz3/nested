;; ((eval (' (+ 1 2))))
(let foo (' 1 2 3))
(+ 1 (fst foo))
;; (let foo ('
;;     (a (b e (c) (d)))
;;     (e (f (g) (h)))))