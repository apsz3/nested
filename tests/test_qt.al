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
(let add (lambda (a b c d) (+ a b c d)))
(print (eval (' add "a" "b" "c" "d")))

(let x (( (lambda (a b) 1))))
(print x)

(let apply (lambda (fn arg) (fn arg)))
(let say (lambda (msg) (print msg)))
(apply say "hello, world!")

(let biz (lambda (x) (begin
    (let foo 1)
    (let bar 2)
    (+ foo bar))))
(print (biz))
;; (print foo) -- should fail!


(let make-cls (lambda (name) ('
    (let name name)
    (let get-name (lambda (_) name))
    (let set-name (lambda (new-name) (begin
        (print "setting name")
        (let name new-name))))
    (let print-name (lambda (_) (print name)))
    (let self (lambda (fn) (eval fn))))))

(let foo (make-cls "foo"))
(print ((foo) (get-name #foo)))